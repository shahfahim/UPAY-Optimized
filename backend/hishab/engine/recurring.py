"""E1 — recurring-event detector (salary, rent, remittance, bills, DPS)."""

from __future__ import annotations

import calendar
from dataclasses import dataclass
from datetime import date, timedelta

import numpy as np
import pandas as pd

LOOKBACK_DAYS = 183
MIN_MONTHS = 3
MAX_DAY_SPREAD = 3
MAX_CV = 0.25
MAX_PER_MONTH = 2.0

# Transactions that can be recurring, and how each group key maps to a kind.
_CANDIDATE_TYPES = {"salary_in", "receive_money", "send_money", "cash_out", "bill_pay", "dps_installment"}


@dataclass
class RecurringEvent:
    kind: str
    counterparty_id: str
    category: str
    direction: int
    day_of_month: int
    amount: float
    confidence: float
    next_date: date
    counterparty_name: str = ""


def _kind(typ: str, category: str) -> str:
    if typ == "salary_in" or (typ == "receive_money" and category == "income"):
        return "salary"
    if category == "rent":
        return "rent"
    if category == "family_support":
        return "remittance"
    if typ == "dps_installment":
        return "dps"
    if typ == "bill_pay":
        return "bill"
    return "other"


def _next_on_day(as_of: date, dom: int) -> date:
    y, m = as_of.year, as_of.month
    for _ in range(3):
        last = calendar.monthrange(y, m)[1]
        d = date(y, m, min(dom, last))
        if d > as_of:
            return d
        m += 1
        if m == 13:
            y, m = y + 1, 1
    return as_of + timedelta(days=30)


def detect_recurring(tx: pd.DataFrame, as_of: date) -> list[RecurringEvent]:
    if tx.empty:
        return []
    ts = pd.to_datetime(tx["ts"])
    lo = pd.Timestamp(as_of - timedelta(days=LOOKBACK_DAYS))
    hi = pd.Timestamp(as_of) + pd.Timedelta(days=1)
    t = tx[(ts >= lo) & (ts < hi) & tx["type"].isin(_CANDIDATE_TYPES)].copy()
    if t.empty:
        return []
    t["ts"] = pd.to_datetime(t["ts"])
    # cash-outs all go to "AGENT": only the remittance ones (category family_support) are a recurring stream
    t = t[(t["type"] != "cash_out") | (t["category"] == "family_support")]
    t["month"] = t["ts"].dt.to_period("M")
    t["dom"] = t["ts"].dt.day
    events: list[RecurringEvent] = []
    n_months_window = max(1, round(LOOKBACK_DAYS / 30.4))
    for (typ, cp, cat), g in t.groupby(["type", "counterparty_id", "category"], sort=False):
        n_months = g["month"].nunique()
        if n_months < MIN_MONTHS or len(g) / n_months > MAX_PER_MONTH:
            continue  # too few months, or a daily/weekly stream rather than a monthly one
        med = float(np.median(g["dom"]))
        # one occurrence per month: the one whose day is closest to the median day
        g = g.assign(dist=(g["dom"] - med).abs()).sort_values(["month", "dist"]).drop_duplicates("month")
        within = (g["dist"] <= MAX_DAY_SPREAD).mean()
        if within < 0.75:
            continue
        amounts = g["amount"].to_numpy(dtype=float)
        cv = float(np.std(amounts) / np.mean(amounts)) if np.mean(amounts) > 0 else 1.0
        if cv > MAX_CV:
            continue
        dom = int(round(float(np.median(g["dom"]))))
        kind = _kind(typ, cat)
        direction = 1 if kind == "salary" else -1
        conf = float(min(1.0, len(g) / n_months_window) * (1 - cv))
        events.append(RecurringEvent(
            kind=kind, counterparty_id=str(cp), category=str(cat), direction=direction, day_of_month=dom,
            amount=round(float(np.median(amounts)), 2), confidence=round(conf, 3),
            next_date=_next_on_day(as_of, dom), counterparty_name=str(g["counterparty_name"].iloc[-1]),
        ))
    events.sort(key=lambda e: (e.next_date, -e.amount))
    return events


def next_income(events: list[RecurringEvent], as_of: date) -> date | None:
    dates = [e.next_date for e in events if e.kind == "salary" and e.next_date > as_of]
    return min(dates) if dates else None
