"""E8 — Eid planner: estimate next Eid's extra need from last Eid, minus expected bonus and Eid pocket."""

from __future__ import annotations

import math
from dataclasses import dataclass
from datetime import date, timedelta

import numpy as np
import pandas as pd

from hishab.rules import load_rules


@dataclass
class EidPlan:
    eid_name: str
    eid_name_bn: str
    eid_date: date
    days_left: int
    last_eid_spend: float
    expected_bonus: float
    need: float
    weekly: float
    pocket_balance: float


def _eids() -> list[tuple[str, str, date]]:
    out = []
    for e in load_rules("eid_dates")["eids"]:
        d = e["date"] if isinstance(e["date"], date) else date.fromisoformat(str(e["date"]))
        out.append((e["name"], e["name_bn"], d))
    return sorted(out, key=lambda x: x[2])


def next_eid(today: date) -> tuple[str, date, str]:
    for name, name_bn, d in _eids():
        if d > today:
            return name, d, name_bn
    name, name_bn, d = _eids()[-1]
    return name, d, name_bn


def previous_eid(today: date) -> date | None:
    past = [d for _, _, d in _eids() if d <= today]
    return past[-1] if past else None


def weekly_amount(need: float, days_left: int) -> float:
    if need <= 0:
        return 0.0
    weeks = max(1, days_left // 7)
    return float(math.ceil(need / weeks))


def _spend(tx: pd.DataFrame, lo: date, hi: date) -> pd.DataFrame:
    d = pd.to_datetime(tx["ts"]).dt.date
    return tx[(d >= lo) & (d < hi) & (tx["direction"] == -1) & ~tx["type"].isin(["pocket_in", "dps_installment"])]


def last_eid_spend(tx: pd.DataFrame, eid: date) -> float:
    """Festival spending in the 30 days before Eid + uplift of other spending over a normal 30 days."""
    win = _spend(tx, eid - timedelta(days=30), eid)
    festival = float(win.loc[win["category"] == "festival", "amount"].sum())
    other = float(win.loc[win["category"] != "festival", "amount"].sum())
    normals = []
    for k in range(2, 6):  # comparable 30-day windows well before the Eid window
        w = _spend(tx, eid - timedelta(days=30 * (k + 1)), eid - timedelta(days=30 * k))
        if not w.empty:
            normals.append(float(w.loc[w["category"] != "festival", "amount"].sum()))
    normal = float(np.median(normals)) if normals else other
    return round(festival + max(0.0, other - normal), 0)


def plan_eid(ctx) -> EidPlan:
    name, eid_date, name_bn = next_eid(ctx.today)
    prev = previous_eid(ctx.today)
    spend = last_eid_spend(ctx.tx, prev) if prev else 0.0
    bonus_rows = ctx.tx[ctx.tx["type"] == "bonus_in"]
    expected_bonus = float(bonus_rows["amount"].iloc[-1]) if not bonus_rows.empty else 0.0
    pocket = float(ctx.state.pockets.get("eid", 0.0))
    need = max(0.0, spend - expected_bonus - pocket)
    days_left = (eid_date - ctx.today).days
    return EidPlan(eid_name=name, eid_name_bn=name_bn, eid_date=eid_date, days_left=days_left,
                   last_eid_spend=spend, expected_bonus=expected_bonus, need=round(need, 0),
                   weekly=weekly_amount(need, days_left), pocket_balance=pocket)
