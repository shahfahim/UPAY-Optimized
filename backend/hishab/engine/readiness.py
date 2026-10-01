"""E14 — responsible credit-readiness signals: transparent, educational, never a score or a decision.

Inputs never include persona, gender, area or age.
"""

from __future__ import annotations

import math
from dataclasses import dataclass, field
from datetime import timedelta

import pandas as pd

from hishab.engine.health import Indicators, living_daily
from hishab.engine.recurring import detect_recurring
from hishab.engine.text import bn_num
from hishab.rules import load_rules

READINESS_INPUTS = ["income_cv", "emergency_days", "on_time_share", "shortfall_months_3", "saving_months_3"]


@dataclass
class Signal:
    id: str
    name_bn: str
    state: str
    reason_bn: str
    improve_bn: str | None = None


@dataclass
class Readiness:
    signals: list = field(default_factory=list)
    disclaimer_bn: str = ""


def _metrics(ctx, health: Indicators) -> dict[str, float]:
    tx = ctx.tx
    d = pd.to_datetime(tx["ts"]).dt.date if not tx.empty else pd.Series(dtype=object)
    from hishab.data.labels import income_mask
    buckets = []
    for k in range(6):
        w = tx[(d > ctx.today - timedelta(days=30 * (k + 1))) & (d <= ctx.today - timedelta(days=30 * k))]
        buckets.append(float(w.loc[income_mask(w), "amount"].sum()) if not w.empty else 0.0)
    mean = sum(buckets) / 6
    cv = (pd.Series(buckets).std(ddof=0) / mean) if mean > 0 else 1.0

    # on-time recurring bills/recharges/DPS over the last 3 months
    ev = [e for e in detect_recurring(tx, ctx.today) if e.kind in ("bill", "dps") or e.tx_type == "mobile_recharge"]
    hits = total = 0
    for e in ev:
        for k in range(3):
            month_end = ctx.today - timedelta(days=30 * k)
            rows = tx[(tx["counterparty_id"] == e.counterparty_id) & (d > month_end - timedelta(days=30))
                      & (d <= month_end) & (tx["type"] != "dps_installment_missed")]
            total += 1
            hits += int(any(abs(pd.Timestamp(t).day - e.day_of_month) <= 3 for t in rows["ts"]))
    missed = int(((tx["type"] == "dps_installment_missed") & (d > ctx.today - timedelta(days=90))).sum()) \
        if not tx.empty else 0
    total += missed
    on_time = hits / total if total else 1.0

    saving_months = 0
    for k in range(3):
        w = tx[(d > ctx.today - timedelta(days=30 * (k + 1))) & (d <= ctx.today - timedelta(days=30 * k))]
        net = float(w.loc[w["type"] == "pocket_in", "amount"].sum() - w.loc[w["type"] == "pocket_out", "amount"].sum())
        saving_months += int(net > 0)
    return {"income_cv": float(cv), "emergency_days": float(health.emergency_days), "on_time_share": float(on_time),
            "shortfall_months_3": float(3 - health.shortfall_free_months), "saving_months_3": float(saving_months)}


def _state(value: float, sig: dict) -> str:
    if sig["higher_is_better"]:
        return "green" if value >= sig["green"] else ("amber" if value >= sig["amber"] else "red")
    return "green" if value <= sig["green"] else ("amber" if value <= sig["amber"] else "red")


def readiness(ctx, health: Indicators, models=None) -> Readiness:
    rules = load_rules("readiness")
    m = _metrics(ctx, health)
    out = []
    for sig in rules["signals"]:
        v = m[sig["metric"]]
        state = _state(v, sig)
        reason = sig["reason_bn"].format(value=bn_num(v), value_pct=bn_num(100 * v))
        improve = None
        if state != "green":
            if sig["id"] == "emergency_buffer":
                deficit = max(0.0, sig["green"] - v) * living_daily(ctx.tx, ctx.today)
                months = max(1, math.ceil(deficit / 500.0))
                improve = sig["improve_bn"].format(monthly=bn_num(500), months=bn_num(months))
            else:
                improve = sig["improve_bn"]
        out.append(Signal(sig["id"], sig["name_bn"], state, reason, improve))
    return Readiness(signals=out, disclaimer_bn=rules["disclaimer_bn"])
