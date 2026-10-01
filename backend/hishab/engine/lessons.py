"""E13 — personalised micro-lessons: triggered by the user's own behaviour and filled with their numbers."""

from __future__ import annotations

import re
from dataclasses import dataclass
from datetime import timedelta

import numpy as np
import pandas as pd

from hishab.engine.health import Indicators, mine_habits
from hishab.engine.text import bn_num, category_bn
from hishab.rules import load_rules


@dataclass
class Lesson:
    id: str
    title_bn: str
    body_bn: str
    action_id: str | None


_CMP = re.compile(r"^\s*(\w+)\s*(<=|>=|<|>)\s*([\d.]+)\s*$")


def _signals(ctx, feats: dict, health: Indicators) -> dict:
    """Values used by triggers and placeholders."""
    from hishab.engine.eid import plan_eid
    from hishab.engine.route import detect_costly_habits

    d = pd.to_datetime(ctx.tx["ts"]).dt.date if not ctx.tx.empty else pd.Series(dtype=object)
    last30 = ctx.tx[d > ctx.today - timedelta(days=30)] if not ctx.tx.empty else ctx.tx
    fees = float(last30.loc[last30["type"] == "cash_out", "fee"].sum()) if not ctx.tx.empty else 0.0
    eid = plan_eid(ctx)
    habits = detect_costly_habits(ctx) if not ctx.tx.empty else []
    spikes = [h for h in mine_habits(ctx) if h.id == "category_spike"]
    top_cat = "shopping"
    if spikes:
        top_cat = next((c for c in ["shopping", "festival", "transport", "mobile", "food_grocery", "other"]
                        if category_bn(c) in spikes[0].text_bn), "shopping")
    return {
        "cash_dependency": health.cash_dependency,
        "emergency_days": health.emergency_days,
        "eid_days_left": eid.days_left,
        "costly_remittance": bool(habits),
        "overspend_category": bool(spikes),
        "paisa_off": not ctx.state.paisa_on,
        # placeholders
        "cashout_fees_month": bn_num(fees),
        "cashout_fees_year": bn_num(fees * 12),
        "emergency_days_bn": bn_num(health.emergency_days),
        "eid_days_left_bn": bn_num(eid.days_left),
        "eid_weekly": bn_num(eid.weekly),
        "npsb_saving": bn_num(habits[0].annual_saving if habits else 0),
        "top_category_bn": category_bn(top_cat),
    }


def _triggered(trigger: str, sig: dict) -> bool:
    m = _CMP.match(trigger)
    if m:
        name, op, val = m.group(1), m.group(2), float(m.group(3))
        x = float(sig.get(name, 0))
        return {"<": x < val, "<=": x <= val, ">": x > val, ">=": x >= val}[op]
    return bool(sig.get(trigger.strip(), False))


def _render(text: str, sig: dict) -> str:
    vals = {k: v for k, v in sig.items() if isinstance(v, str)}
    vals["emergency_days"] = sig["emergency_days_bn"]
    vals["eid_days_left"] = sig["eid_days_left_bn"]
    return text.format(**vals)


def eligible_lessons(ctx, feats: dict, health: Indicators) -> list[str]:
    sig = _signals(ctx, feats, health)
    return [l["id"] for l in load_rules("lessons")["lessons"] if _triggered(l["trigger"], sig)]


def rank_lessons(ctx, feats: dict, health: Indicators, bandit=None, responses: list | None = None,
                 rng=None) -> list[Lesson]:
    sig = _signals(ctx, feats, health)
    rng = rng or np.random.default_rng()
    scored = []
    for l in load_rules("lessons")["lessons"]:
        if not _triggered(l["trigger"], sig):
            continue
        p = bandit.sample(ctx.persona, l["id"], responses or [], rng) if bandit is not None else 0.5
        scored.append((p, Lesson(l["id"], _render(l["title_bn"], sig), _render(l["body_bn"], sig), l.get("action_id"))))
    scored.sort(key=lambda x: x[0], reverse=True)
    return [x[1] for x in scored]
