"""E12 — financial-health indicators (and, from Task 15, habits and the monthly report)."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import date, timedelta

import pandas as pd

from hishab.data.labels import income_mask, shortfall_days
from hishab.rules import load_rules

LIVING = ["food_grocery", "rent", "utilities", "health", "education", "transport", "mobile"]
NON_SPEND = ["pocket_in", "dps_installment", "dps_installment_missed"]


@dataclass
class Indicators:
    emergency_days: float
    cash_dependency: float
    shortfall_free_months: int


def _dates(tx: pd.DataFrame) -> pd.Series:
    return pd.to_datetime(tx["ts"]).dt.date


def living_daily(tx: pd.DataFrame, as_of: date) -> float:
    d = _dates(tx)
    w = tx[(d > as_of - timedelta(days=30)) & (d <= as_of) & (tx["direction"] == -1)
           & tx["category"].isin(LIVING) & ~tx["type"].isin(NON_SPEND)]
    return float(w["amount"].sum()) / 30.0


def pocket_total_from_history(tx: pd.DataFrame, as_of: date) -> float:
    d = _dates(tx)
    t = tx[d <= as_of]
    return float(t.loc[t["type"] == "pocket_in", "amount"].sum() - t.loc[t["type"] == "pocket_out", "amount"].sum())


def indicators(ctx, as_of: date | None = None) -> Indicators:
    as_of = as_of or ctx.today
    tx = ctx.tx[_dates(ctx.tx) <= as_of]
    pockets = float(sum(ctx.state.pockets.values())) if as_of == ctx.today else pocket_total_from_history(tx, as_of)
    daily = living_daily(tx, as_of)
    emergency_days = round(pockets / daily, 1) if daily > 0 else (0.0 if pockets <= 0 else 99.0)
    d = _dates(tx)
    last30 = tx[d > as_of - timedelta(days=30)]
    income30 = float(last30.loc[income_mask(last30), "amount"].sum())
    cash30 = float(last30.loc[last30["type"] == "cash_out", "amount"].sum())
    cash_dep = round(cash30 / income30, 2) if income30 > 0 else 0.0
    threshold = load_rules("guardrails")["shortfall_threshold"]
    free = 0
    for k in range(3):
        lo, hi = as_of - timedelta(days=30 * (k + 1)) + timedelta(days=1), as_of - timedelta(days=30 * k)
        if tx.empty or _dates(tx).min() > lo:
            continue
        if not shortfall_days(tx, lo, hi, threshold):
            free += 1
    return Indicators(emergency_days=min(emergency_days, 99.0), cash_dependency=cash_dep, shortfall_free_months=free)
