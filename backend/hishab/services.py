"""Hishab facade: one method per API resource, returning JSON-ready dicts. Used by the API and the LLM tools."""

from __future__ import annotations

import hashlib
import json
import re
import secrets
from datetime import date, datetime, timedelta

import numpy as np
import pandas as pd

from hishab.config import Settings
from hishab.data.loader import DataRepo
from hishab.engine.actions import rank_actions, simulate_action
from hishab.engine.bandit import Bandit
from hishab.engine.context import UserCtx, UserNotFound, build_ctx
from hishab.engine.forecast import band_from_flows, future_flows
from hishab.engine.health import indicators
from hishab.engine.lessons import rank_lessons
from hishab.engine.levels import compute_level
from hishab.engine.notifications import evaluate_triggers, message_strip
from hishab.engine.recurring import detect_recurring, next_income
from hishab.engine.risk import score
from hishab.engine.safe_spend import daily_budget, safe_to_spend
from hishab.engine.shortcuts import recent_payments
from hishab.engine.features import user_features
from hishab.engine.models import Models
from hishab.store.sqlite import Store
from hishab.jsonable import jsonable
from hishab.services_hub import HubMixin, InsufficientFunds  # noqa: F401

_MOBILE = re.compile(r"^01[3-9]\d{8}$")
_PIN = re.compile(r"^\d{6}$")


def demo_phone(user_id: str) -> str:
    digits = re.sub(r"\D", "", user_id) or "0"
    return "017" + f"{int(digits):08d}"


def mask_phone(phone: str) -> str:
    return phone[:3] + "•••••" + phone[-3:] if len(phone) == 11 else phone


def initials(name: str) -> str:
    parts = [p for p in str(name).split() if p]
    return "".join(p[0] for p in parts[:2]) or "?"


class Hishab(HubMixin):
    def __init__(self, repo: DataRepo, store: Store, models: Models, settings: Settings):
        self.repo, self.store, self.models, self.settings = repo, store, models, settings
        self.bandit = Bandit.from_dict(models.bandit_priors) if models.bandit_priors else None
        self.rng = np.random.default_rng()
        from hishab.llm.client import RateLimiter
        self.limiter = RateLimiter(limit=10, window=60.0)
        self.llm_client = None  # injected in tests; real client is created on demand when the LLM is enabled

    # --- context ---------------------------------------------------------------------------------------
    def ctx(self, uid: str) -> UserCtx:
        return build_ctx(uid, self.repo, self.store, self.settings)

    def _core(self, ctx: UserCtx) -> dict:
        recurring = detect_recurring(ctx.tx, ctx.today)
        flows = future_flows(ctx, self.models.forecaster, 30, recurring)
        fc = band_from_flows(ctx, self.models, flows)
        risk = score(ctx, fc, self.models)
        return {"recurring": recurring, "flows": flows, "fc": fc, "risk": risk}

    def _user_public(self, ctx: UserCtx) -> dict:
        u = ctx.user
        phone = u.get("demo_phone") or demo_phone(u["user_id"])
        return {"user_id": u["user_id"], "name": u.get("synthetic_name", ""), "persona": u.get("persona"),
                "area": u.get("area"), "phone_masked": mask_phone(phone), "avatar_initials": initials(u.get("synthetic_name", ""))}

    # --- users and auth ----------------------------------------------------------------------------------
    def users(self) -> list[dict]:
        out = []
        for u in self.repo.list_users()[:5] + self.repo.list_users()[5:12]:
            out.append({"user_id": u["user_id"], "name": u["synthetic_name"], "persona": u["persona"], "area": u["area"],
                        "phone": demo_phone(u["user_id"])})
        for u in self.store.extra_users():
            out.append({"user_id": u["user_id"], "name": u["synthetic_name"], "persona": u["persona"],
                        "area": u["area"], "phone": u.get("demo_phone", "")})
        return out

    def _find_by_phone(self, mobile: str) -> dict | None:
        for u in self.store.extra_users():
            if u.get("demo_phone") == mobile:
                return u
        m = re.fullmatch(r"017(\d{8})", mobile)
        if m:
            uid = f"U{int(m.group(1)):04d}"
            u = self.repo.user(uid)
            if u is not None:
                return u
        return None

    @staticmethod
    def _hash(pin: str) -> str:
        return hashlib.sha256(("hishab-demo:" + pin).encode()).hexdigest()

    def login(self, mobile: str, pin: str) -> dict:
        if not _MOBILE.match(mobile or ""):
            raise ValueError("সঠিক মোবাইল নম্বর দিন")
        u = self._find_by_phone(mobile)
        ok = False
        if u is not None:
            ok = (u.get("pin_hash") == self._hash(pin)) if u.get("pin_hash") else (pin == u.get("demo_pin"))
        if not ok:
            raise PermissionError("PIN সঠিক নয়")
        return {"token": self.store.create_session(u["user_id"]), "user_id": u["user_id"]}

    def register_start(self, mobile: str) -> dict:
        if not _MOBILE.match(mobile or ""):
            raise ValueError("সঠিক মোবাইল নম্বর দিন")
        if self._find_by_phone(mobile) is not None:
            raise ValueError("এই নম্বরে আগেই অ্যাকাউন্ট আছে")
        otp = f"{secrets.randbelow(10**6):06d}"
        self.store.set_meta(f"otp:{mobile}", otp)
        return {"otp": otp, "demo": True}

    def register_verify(self, mobile: str, otp: str, name: str, pin: str) -> dict:
        from hishab.data.generator import generate_one
        if self.store.get_meta(f"otp:{mobile}") != otp:
            raise ValueError("OTP সঠিক নয়")
        name = (name or "").strip()
        if not (2 <= len(name) <= 40):
            raise ValueError("নাম লিখুন")
        if not _PIN.match(pin or ""):
            raise ValueError("৬ সংখ্যার PIN দিন")
        uid = f"N{len(self.store.extra_users()) + 1:04d}"
        seed = int(mobile[-6:])
        user, tx = generate_one(uid, name, "garment_worker", seed=seed)
        user.update(demo_phone=mobile, pin_hash=self._hash(pin))
        self.store.add_user(user, tx)
        self.store.set_meta(f"otp:{mobile}", "")
        return {"token": self.store.create_session(uid), "user_id": uid}

    # --- home and shell ----------------------------------------------------------------------------------
    def home(self, uid: str) -> dict:
        ctx = self.ctx(uid)
        base = {"user": self._user_public(ctx), "balance": ctx.balance, "today": ctx.today,
                "insufficient_history": ctx.insufficient_history}
        if ctx.insufficient_history:
            return jsonable(base | {"forecast": None, "risk": None, "safe_today": 0, "daily_budget": 0,
                                   "actions": [], "health": None, "lesson": None, "level": None})
        core = self._core(ctx)
        fc, risk, rec = core["fc"], core["risk"], core["recurring"]
        ind = indicators(ctx)
        prev = indicators(ctx, ctx.today - timedelta(days=30))
        level = compute_level(ctx, ind)
        lessons = rank_lessons(ctx, user_features(ctx), ind, self.bandit, self.store.responses(uid, "lesson"), self.rng)
        cards = rank_actions(ctx, self.models, self.bandit, extras=self._extras(ctx),
                             responses=self.store.responses(uid, "action"), rng=self.rng)
        return jsonable(base | {
            "forecast": {"dates": fc.dates, "p10": fc.p10, "p50": fc.p50, "p90": fc.p90,
                         "shortfall_date": fc.shortfall_date, "shortfall_amount": fc.shortfall_amount},
            "risk": {"prob": risk.prob, "level": risk.level, "drivers": risk.drivers},
            "safe_today": safe_to_spend(ctx, fc, rec), "daily_budget": daily_budget(ctx, rec),
            "next_income": next_income(rec, ctx.today),
            "actions": cards, "health": ind, "health_previous": prev,
            "lesson": lessons[0] if lessons else None, "level": level,
        })

    def _extras(self, ctx: UserCtx) -> dict:
        from hishab.engine.dps import dps_advice
        from hishab.engine.eid import plan_eid
        extras = {"eid": plan_eid(ctx)}
        if not ctx.state.dps:
            try:
                extras["dps"] = dps_advice(ctx, self.models)
            except Exception:  # advice is optional for ranking
                pass
        return extras

    def shell(self, uid: str) -> dict:
        ctx = self.ctx(uid)
        pub = self._user_public(ctx)
        if ctx.insufficient_history:
            self._touch(ctx)
            return jsonable({**pub, "balance": ctx.balance, "today": ctx.today, "insufficient_history": True,
                             "nav_badge": None, "strip": [{"priority": 5, "text_bn": "আরও কিছু দিনের লেনদেন লাগবে",
                                                           "text_en": "A few more days of activity needed",
                                                           "link": "/app/hishab"}],
                             "safe_today": 0, "daily_budget": 0, "recent": [], "unread": self._unread(uid)})
        core = self._core(ctx)
        fc, risk, rec = core["fc"], core["risk"], core["recurring"]
        safe, budget = safe_to_spend(ctx, fc, rec), daily_budget(ctx, rec)
        ind = indicators(ctx)
        level = compute_level(ctx, ind)
        shortcuts = recent_payments(ctx, rec)
        lessons = rank_lessons(ctx, user_features(ctx), ind, self.bandit, self.store.responses(uid, "lesson"), self.rng)
        nxt = next_income(rec, ctx.today)
        strip = message_strip(ctx, risk, safe, budget, shortcuts, lessons[0] if lessons else None, level, nxt)
        new = evaluate_triggers(ctx, risk, rec, level, self.store.notifications(uid), ctx.state.last_active)
        for n in new:
            self.store.add_notification(uid, jsonable(n) | {"read": False})
        self._touch(ctx)
        days_left = (fc.shortfall_date - ctx.today).days if fc.shortfall_date else None
        return jsonable({**pub, "balance": ctx.balance, "today": ctx.today, "insufficient_history": False,
                         "nav_badge": {"level": risk.level, "days_left": days_left if risk.level != "green" else None},
                         "strip": strip, "safe_today": safe, "daily_budget": budget, "recent": shortcuts,
                         "unread": self._unread(uid)})

    def _touch(self, ctx: UserCtx) -> None:
        ctx.state.last_active = ctx.today
        self.store.save_state(ctx.user_id, ctx.state)

    def _unread(self, uid: str) -> int:
        return sum(1 for n in self.store.notifications(uid) if not n.get("read"))

    def notifications(self, uid: str) -> list[dict]:
        self.ctx(uid)  # 404 for unknown users
        items = list(reversed(self.store.notifications(uid)))
        self.store.mark_notifications_read(uid)
        return items

    # --- actions ------------------------------------------------------------------------------------------
    def simulate(self, uid: str, action_id: str) -> dict:
        ctx = self.ctx(uid)
        fc, risk = simulate_action(ctx, self.models, action_id, self._extras(ctx))
        return jsonable({"action_id": action_id, "forecast": {"dates": fc.dates, "p10": fc.p10, "p50": fc.p50,
                                                              "p90": fc.p90, "shortfall_date": fc.shortfall_date,
                                                              "shortfall_amount": fc.shortfall_amount},
                         "risk": {"prob": risk.prob, "level": risk.level}})

    def respond(self, uid: str, kind: str, item_id: str, accepted: bool) -> dict:
        self.ctx(uid)
        if kind not in ("action", "lesson"):
            raise ValueError("ভুল ধরন")
        self.store.record_response(uid, kind, item_id, bool(accepted))
        return {"ok": True}

    # --- chat ----------------------------------------------------------------------------------------------
    def chat(self, uid: str, message: str) -> dict:
        from hishab.llm.client import answer
        self.ctx(uid)  # 404 for unknown users
        return jsonable(answer(uid, message, self, self.settings, client=self.llm_client, limiter=self.limiter))

    # --- demo controls ------------------------------------------------------------------------------------
    def time_travel(self, days: int) -> dict:
        if days not in (7, 14, 30):
            raise ValueError("শুধু ৭, ১৪ বা ৩০ দিন এগোনো যায়")
        if self.store.clock_offset() + days > 60:
            raise ValueError("demo-তে মোট ৬০ দিনের বেশি এগোনো যায় না — আগে Demo reset করুন")
        self.store.set_clock_offset(self.store.clock_offset() + days)
        return {"today": (self.settings.demo_today + timedelta(days=self.store.clock_offset())).isoformat(),
                "offset_days": self.store.clock_offset()}

    def reset(self) -> dict:
        self.store.reset()
        return {"ok": True, "today": self.settings.demo_today.isoformat()}
