"""Month replay for the impact simulation: re-run a month of actual flows with action transforms applied."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import date, timedelta
from types import SimpleNamespace

import numpy as np
import pandas as pd

from hishab.engine.forecast import FLOW_COLS
from hishab.engine.health import LIVING
from hishab.rules import load_rules

_RECURRING_CATS = {"rent", "family_support", "utilities", "education"}


@dataclass
class MonthOutcome:
    shortfall_days: int
    fees: float
    salary_retained_d10: float | None
    cash_dependency: float
    emergency_days: float
    end_balance: float
    end_pockets: float


def month_flows(tx_month: pd.DataFrame) -> pd.DataFrame:
    """Actual transactions as flows, tagged with the same kinds the action transforms expect."""
    rows = []
    for r in tx_month.itertuples(index=False):
        amt = float(r.amount) * float(r.direction)
        if r.type in ("pocket_in", "pocket_out", "dps_installment", "dps_installment_missed", "cash_in"):
            kind = "internal"
        elif amt > 0:
            kind = "income"
        elif r.category in _RECURRING_CATS or r.type in ("bill_pay",):
            kind = "recurring"
        else:
            kind = "discretionary"
        rows.append({"date": pd.Timestamp(r.ts).date(), "amount": amt, "category": r.category, "type": r.type,
                     "fee": float(r.fee), "kind": kind})
    return pd.DataFrame(rows, columns=FLOW_COLS)


def replay_month(tx_month: pd.DataFrame, start_balance: float, start_pockets: float, transforms: list,
                 start: date, end: date) -> MonthOutcome:
    flows = month_flows(tx_month)
    ctx = SimpleNamespace(today=start - timedelta(days=1))
    for tr in transforms:
        flows = tr(flows.copy(), ctx)
    threshold = load_rules("guardrails")["shortfall_threshold"]
    days = [start + timedelta(days=k) for k in range((end - start).days + 1)]
    f = flows.copy()
    f["net"] = f["amount"] - f["fee"]
    net_by_day = f.groupby("date")["net"].sum()
    pocket_delta = f[f["type"].isin(["pocket_in", "pocket_out"])].groupby("date")["amount"].sum() * -1
    income_days = set(f[(f["kind"] == "income") & (f["category"] == "income")]["date"])
    bal, pockets, shortfalls, balances = start_balance, start_pockets, 0, {}
    for d in days:
        bal += float(net_by_day.get(d, 0.0))
        pockets += float(pocket_delta.get(d, 0.0))
        balances[d] = bal
        if bal < threshold and d not in income_days:
            shortfalls += 1
    sal = f[(f["type"] == "salary_in")]
    retained = None
    if not sal.empty:
        sd = sal["date"].iloc[0]
        d10 = min(end, sd + timedelta(days=10))
        retained = round(max(0.0, balances.get(d10, bal)) / float(sal["amount"].iloc[0]), 3)
    income = float(f.loc[f["kind"] == "income", "amount"].sum())
    cash = -float(f.loc[f["type"] == "cash_out", "amount"].sum())
    living = -float(f.loc[(f["amount"] < 0) & f["category"].isin(LIVING) & (f["kind"] != "internal"), "amount"].sum())
    living_daily = living / max(1, len(days))
    return MonthOutcome(
        shortfall_days=shortfalls, fees=round(float(f["fee"].sum()), 2), salary_retained_d10=retained,
        cash_dependency=round(cash / income, 3) if income > 0 else 0.0,
        emergency_days=round(pockets / living_daily, 1) if living_daily > 0 else 0.0,
        end_balance=round(bal, 2), end_pockets=round(pockets, 2))
