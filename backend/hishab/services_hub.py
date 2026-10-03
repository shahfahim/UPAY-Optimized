"""Hub, savings, flows and impact methods of the Hishab facade (mixed into services.Hishab)."""

from __future__ import annotations

import calendar as _cal
import functools
import json
import re
import secrets
from datetime import date, datetime, timedelta

import numpy as np
import pandas as pd

from hishab.engine import validate
from hishab.engine.category import suggest_category
from hishab.engine.dps import dps_advice as _dps_advice
from hishab.engine.eid import plan_eid
from hishab.engine.emergency import emergency_options
from hishab.engine.features import CATEGORIES, user_features
from hishab.engine.goals import plan_goal as _plan_goal
from hishab.engine.health import health_report, indicators
from hishab.engine.lessons import rank_lessons
from hishab.engine.levels import compute_level
from hishab.engine.readiness import readiness as _readiness
from hishab.engine.recurring import detect_recurring
from hishab.engine.route import detect_costly_habits, routes as _routes
from hishab.engine.savings import apply_paisa
from hishab.engine.text import CATEGORY_BN, POCKET_BN, bn_num
from hishab.errors import UserError
from hishab.jsonable import jsonable
from hishab.rules import load_rules
from hishab.store.sqlite import POCKETS

SPEND_TYPES = ["merchant_pay", "cash_out", "mobile_recharge", "send_money", "bill_pay"]
PERIOD_DAYS = {"day": 1, "week": 7, "month": 30}
_EVENT_LABELS = {"salary_in": "বেতন", "bonus_in": "বোনাস"}


class InsufficientFunds(Exception):
    pass


def locked(fn):
    """Run a method that reads, checks and writes one user's balance or state under that user's lock."""
    @functools.wraps(fn)
    def wrapper(self, uid, *args, **kwargs):
        with self.user_lock(uid):
            return fn(self, uid, *args, **kwargs)
    return wrapper


def _dates(tx: pd.DataFrame) -> pd.Series:
    return pd.to_datetime(tx["ts"]).dt.date


class HubMixin:
    # --- health, lessons, readiness, levels -----------------------------------------------------------
    def health(self, uid):
        ctx = self.ctx(uid)
        if ctx.insufficient_history:
            return {"insufficient_history": True}
        return jsonable(health_report(ctx)) | {"insufficient_history": False}

    def lessons(self, uid):
        ctx = self.ctx(uid)
        if ctx.insufficient_history:
            return []
        return jsonable(rank_lessons(ctx, user_features(ctx), indicators(ctx), self.bandit,
                                     self.store.responses(uid, "lesson"), self.rng))

    def lesson_respond(self, uid, lesson_id, accepted):
        return self.respond(uid, "lesson", lesson_id, accepted)

    def readiness(self, uid):
        ctx = self.ctx(uid)
        return jsonable(_readiness(ctx, indicators(ctx)))

    def levels(self, uid):
        ctx = self.ctx(uid)
        return jsonable(compute_level(ctx, indicators(ctx)))

    # --- calendar and budget ------------------------------------------------------------------------------
    def calendar(self, uid, month: str):
        if not re.fullmatch(r"\d{4}-(0[1-9]|1[0-2])", month or ""):
            raise UserError("মাস সঠিক নয় (YYYY-MM)")
        y, m = int(month[:4]), int(month[5:])
        ctx = self.ctx(uid)
        days = [date(y, m, k) for k in range(1, _cal.monthrange(y, m)[1] + 1)]
        tx = ctx.tx[~ctx.tx["type"].isin(["pocket_in", "pocket_out", "dps_installment_missed"])]
        d = _dates(tx)
        fc = None if ctx.insufficient_history else self._core(ctx)["fc"]
        th = load_rules("guardrails")["shortfall_threshold"]
        out = []
        for day in days:
            if day <= ctx.today:
                rows = tx[d == day]
                ev = set()
                for r in rows.itertuples(index=False):
                    if r.type in _EVENT_LABELS:
                        ev.add(_EVENT_LABELS[r.type])
                    elif r.category in ("rent", "family_support", "utilities", "festival"):
                        ev.add(CATEGORY_BN[r.category])
                out.append({"date": day, "out_total": round(float(rows.loc[rows.direction == -1, "amount"].sum())),
                            "in_total": round(float(rows.loc[rows.direction == 1, "amount"].sum())),
                            "events": sorted(ev), "predicted": False, "risk": None})
                continue
            item = {"date": day, "out_total": 0, "in_total": 0, "events": [], "predicted": True, "risk": None}
            if fc is not None and day in fc.dates:
                i = fc.dates.index(day)
                f = fc.flows[fc.flows["date"] == day]
                item["out_total"] = round(-float(f.loc[f.amount < 0, "amount"].sum()))
                item["in_total"] = round(float(f.loc[f.amount > 0, "amount"].sum()))
                item["events"] = sorted({CATEGORY_BN.get(c, c) for c in f.loc[f.kind == "recurring", "category"]})
                item["risk"] = "red" if fc.p50[i] < th else ("amber" if fc.p10[i] < th else "green")
            out.append(item)
        return jsonable({"month": month, "today": ctx.today, "days": out})

    def budget(self, uid, period: str):
        return {"period": period, "mode": "disabled", "items": [], "reason_bn": "বাজেট ফিচারটি এখন বন্ধ আছে"}

    @locked
    def set_budget(self, uid, mode, manual):
        return {"mode": "disabled", "manual": {}}

    # --- savings --------------------------------------------------------------------------------------------
    def savings(self, uid):
        ctx = self.ctx(uid)
        st = ctx.state
        pockets = []
        for p in POCKETS:
            if p == "paisa":
                continue
            goal = (st.pocket_goals or {}).get(p)
            bal = round(float(st.pockets.get(p, 0.0)), 2)
            prog = round(min(1.0, bal / goal["target"]), 3) if goal and goal.get("target") else None
            pockets.append({"name": p, "name_bn": POCKET_BN[p], "balance": bal, "goal": goal, "progress": prog})
        return jsonable({"pockets": pockets,
                         "paisa": {"on": st.paisa_on, "paused": st.paisa_paused,
                                   "total": round(st.pockets.get("paisa", 0.0), 2)},
                         "total": round(float(sum(st.pockets.values())), 2),
                         "eid_plan": plan_eid(ctx), "dps": st.dps, "balance": ctx.balance})

    def _now_ts(self, ctx) -> datetime:
        now = datetime.combine(ctx.today, datetime.now().time()).replace(microsecond=0)
        if not ctx.tx.empty:
            last = pd.Timestamp(ctx.tx["ts"].max()).to_pydatetime()
            if now <= last:
                now = last + timedelta(minutes=1)
        return now

    def _sim(self, ctx, typ, amount, direction, category, cp_id, cp_name, cp_type, channel="upay", fee=0.0,
             ts=None, balance=None) -> float:
        start = ctx.balance if balance is None else balance
        bal = round(start + direction * amount - (fee if direction == -1 else 0.0), 2)
        self.store.add_sim_tx(ctx.user_id, {
            "tx_id": f"S-{secrets.token_hex(6)}", "user_id": ctx.user_id, "ts": (ts or self._now_ts(ctx)).isoformat(),
            "type": typ, "amount": round(amount, 2), "direction": direction, "fee": round(fee, 2),
            "balance_after": bal, "counterparty_id": cp_id, "counterparty_name": cp_name,
            "counterparty_type": cp_type, "counterparty_channel": channel, "category": category,
            "area": ctx.user.get("area", "")})
        return bal

    @locked
    def move_pocket(self, uid, pocket, direction, amount):
        if pocket not in POCKETS or (pocket == "paisa" and direction == "in"):
            raise UserError("পকেট সঠিক নয়")
        amount = validate.amount(amount)
        ctx = self.ctx(uid)
        if direction == "in":
            if ctx.balance < amount:
                raise InsufficientFunds("পর্যাপ্ত ব্যালেন্স নেই")
            self._sim(ctx, "pocket_in", amount, -1, "other", f"pocket:{pocket}", POCKET_BN[pocket], "pocket")
            ctx.state.pockets[pocket] = round(ctx.state.pockets.get(pocket, 0.0) + amount, 2)
        else:  # withdrawals are never blocked beyond the pocket balance itself
            if ctx.state.pockets.get(pocket, 0.0) < amount:
                raise InsufficientFunds("পকেটে যথেষ্ট টাকা নেই")
            self._sim(ctx, "pocket_out", amount, 1, "other", f"pocket:{pocket}", POCKET_BN[pocket], "pocket")
            ctx.state.pockets[pocket] = round(ctx.state.pockets[pocket] - amount, 2)
        self.store.save_state(uid, ctx.state)
        return self.savings(uid)

    @locked
    def set_paisa(self, uid, on):
        ctx = self.ctx(uid)
        ctx.state.paisa_on = bool(on)
        if not on:
            ctx.state.paisa_paused = False
        self.store.save_state(uid, ctx.state)
        return self.savings(uid)

    @locked
    def plan_goal(self, uid, target, months, pocket=None):
        ctx = self.ctx(uid)
        g = _plan_goal(ctx, self.models, target, months)
        if pocket:
            if pocket not in POCKETS or pocket == "paisa":
                raise UserError("পকেট সঠিক নয়")
            goals = dict(ctx.state.pocket_goals or {})
            goals[pocket] = {"target": g.target, "months": g.months,
                             "date": (ctx.today + timedelta(days=30 * g.months)).isoformat()}
            ctx.state.pocket_goals = goals
            self.store.save_state(uid, ctx.state)
        return jsonable(g)

    def dps_advice(self, uid, goal_target=None):
        ctx = self.ctx(uid)
        if ctx.insufficient_history:
            return {"status": "not_now", "reason_bn": "আরও কিছু দিনের লেনদেন লাগবে", "safe_monthly": None}
        return jsonable(_dps_advice(ctx, self.models, goal_target))

    @locked
    def dps_open(self, uid, monthly, tenure_months):
        rules = load_rules("dps")
        monthly = validate.amount(monthly)
        try:
            tenure = int(tenure_months)
        except (TypeError, ValueError):
            raise UserError("সময়কাল সঠিক নয়")
        if monthly not in rules["monthly_options"] or tenure not in rules["tenure_months"]:
            raise UserError("জমার পরিমাণ বা সময়কাল তালিকা থেকে বেছে নিন")
        ctx = self.ctx(uid)
        if ctx.state.dps:
            raise UserError("আগে থেকেই একটা DPS চালু আছে")
        sal = [e for e in detect_recurring(ctx.tx, ctx.today) if e.kind == "salary"]
        ctx.state.dps = {"monthly": monthly, "tenure_months": tenure,
                         "day": min(28, sal[0].day_of_month + 1) if sal else 10,
                         "opened": ctx.today.isoformat(), "simulated": True}
        self.store.save_state(uid, ctx.state)
        return jsonable({"ok": True, "dps": ctx.state.dps})

    def emergency(self, uid, amount):
        return jsonable(emergency_options(self.ctx(uid), self.models, amount))

    # --- flows ---------------------------------------------------------------------------------------------
    def category_suggest(self, uid, counterparty_id, counterparty_type, amount):
        ctx = self.ctx(uid)
        try:
            amt = float(amount or 0)
        except (TypeError, ValueError):
            amt = 0.0
        out = suggest_category(ctx, counterparty_id, counterparty_type, amt, self.store.categories(uid))
        return [{"category": c, "category_bn": CATEGORY_BN.get(c, c), "confidence": round(p, 3)} for c, p in out]

    def category_confirm(self, uid, counterparty_id, category):
        self.ctx(uid)
        if category not in CATEGORIES:
            raise UserError("ক্যাটাগরি সঠিক নয়")
        self.store.set_category(uid, counterparty_id, category)
        return {"ok": True}

    def route(self, uid, amount, destination="other_mfs_wallet"):
        ctx = self.ctx(uid)
        amount = validate.amount(amount)
        return jsonable({"routes": _routes(amount, destination), "habits": detect_costly_habits(ctx),
                         "fees_placeholder": True})

    @locked
    def send(self, uid, body: dict):
        amount = validate.amount(body.get("amount"))
        typ = body["type"]
        ctx = self.ctx(uid)
        fee, channel, cp_type, tx_type = 0.0, "upay", "merchant", typ
        dest = body.get("destination") or "other_mfs_wallet"
        if typ == "cash_out":
            fee, cp_type = _routes(amount, "agent_cash")[0].fee, "agent"
        elif typ in ("npsb", "fund_transfer"):
            options = _routes(amount, dest)
            picked = body.get("route")
            if picked:  # the user chose a path on the money map: charge that path, never silently another
                options = [r for r in options if r.nodes == list(picked)]
                if not options:
                    raise UserError("পথ সঠিক নয়")
            fee = options[0].fee
            channel = "bank" if dest == "bank_account" else "other_mfs"
            tx_type, cp_type = "send_money", "person"
        elif typ == "send_money":
            cp_type = "person"
        elif typ in ("bill_pay", "mobile_recharge"):
            cp_type = "biller"
        if ctx.balance < amount + fee:
            raise InsufficientFunds("পর্যাপ্ত ব্যালেন্স নেই")
        cp_id = body.get("counterparty_id") or ("AGENT" if typ == "cash_out" else f"NEW-{typ}")
        cp_name = body.get("counterparty_name") or ("এজেন্ট" if typ == "cash_out" else cp_id)
        category = body.get("category")
        if category:
            if category not in CATEGORIES:
                raise UserError("ক্যাটাগরি সঠিক নয়")
            self.store.set_category(uid, cp_id, category)
        else:
            category = suggest_category(ctx, cp_id, cp_type, amount, self.store.categories(uid))[0][0]
        nudge = None
        if typ == "cash_out":  # at most one contextual nudge per flow
            habits = detect_costly_habits(ctx)
            if habits:
                nudge = {"text_bn": f"বাড়িতে টাকা পাঠাতে চাইলে NPSB দিয়ে পাঠাও — বছরে প্রায় "
                                    f"৳{bn_num(habits[0].annual_saving)} বাঁচবে।",
                         "saving_year": habits[0].annual_saving, "link": "/app/npsb"}
            elif category in ("food_grocery", "shopping"):
                nudge = {"text_bn": f"দোকানে wallet দিয়ে সরাসরি পেমেন্ট করলে ৳{bn_num(fee)} fee লাগবে না।",
                         "saving_year": round(fee * 12), "link": "/app/pay?type=merchant_pay"}
        ts = self._now_ts(ctx)
        bal = self._sim(ctx, tx_type, amount, -1, category, cp_id, cp_name, cp_type, channel, fee, ts=ts)
        new_bal, swept = apply_paisa(ctx.state, bal)
        if swept > 0:
            self._sim(ctx, "pocket_in", swept, -1, "other", "pocket:paisa", POCKET_BN["paisa"], "pocket",
                      ts=ts + timedelta(seconds=30), balance=bal)
        self.store.save_state(uid, ctx.state)
        return {"balance": new_bal, "swept": swept, "fee": fee, "category": category, "nudge": nudge}

    # --- history ------------------------------------------------------------------------------------------
    def transactions(self, uid, limit=50):
        from hishab.llm.tools import _tx_summary
        try:
            limit = int(limit)
        except (TypeError, ValueError):
            raise UserError("সংখ্যা সঠিক নয়")
        if not 1 <= limit <= 200:
            raise UserError("১ থেকে ২০০-এর মধ্যে দিন")
        ctx = self.ctx(uid)
        t = ctx.tx[ctx.tx["type"] != "dps_installment_missed"].sort_values("ts", ascending=False).head(limit)
        items = [{"ts": pd.Timestamp(r.ts).isoformat(), "type": r.type, "name": r.counterparty_name,
                  "amount": float(r.amount), "direction": int(r.direction), "fee": float(r.fee),
                  "category": r.category, "category_bn": CATEGORY_BN.get(r.category, r.category),
                  "balance_after": float(r.balance_after)} for r in t.itertuples(index=False)]
        return {"items": items, "summary": _tx_summary(uid, self, "month")}

    # --- impact -------------------------------------------------------------------------------------------
    def impact(self):
        path = self.settings.artifacts_dir / "impact_snapshot.json"
        return json.loads(path.read_text(encoding="utf-8"))
