"""Label helpers shared by the generator, training, evaluation and replay."""

from __future__ import annotations

from datetime import date, timedelta

import pandas as pd

INCOME_TYPES = {"salary_in", "bonus_in"}


def income_mask(tx: pd.DataFrame) -> pd.Series:
    """Rows that are income (salary, bonus, or money received with category 'income')."""
    return tx["type"].isin(INCOME_TYPES) | ((tx["type"] == "receive_money") & (tx["category"] == "income"))


def income_days(tx_user: pd.DataFrame) -> set[date]:
    rows = tx_user[income_mask(tx_user)]
    return set(pd.to_datetime(rows["ts"]).dt.date)


def daily_balances(tx_user: pd.DataFrame, start: date, end: date) -> pd.Series:
    """End-of-day main-wallet balance for each day in [start, end], carried forward.

    Days before the user's first transaction are NaN.
    """
    idx = pd.date_range(start, end, freq="D").date
    if tx_user.empty:
        return pd.Series(float("nan"), index=idx)
    t = tx_user.sort_values("ts")
    last = t.groupby(pd.to_datetime(t["ts"]).dt.date)["balance_after"].last()
    full_idx = pd.date_range(min(last.index[0], start), end, freq="D").date
    series = last.reindex(full_idx).ffill()
    return series.reindex(idx)


def shortfall_days(tx_user: pd.DataFrame, start: date, end: date, threshold: float = 200.0) -> list[date]:
    """Days in [start, end] whose end-of-day balance is below threshold and that are not income days."""
    bal = daily_balances(tx_user, start, end)
    inc = income_days(tx_user)
    return [d for d, b in bal.items() if pd.notna(b) and b < threshold and d not in inc]


def shortfall_flags(tx_user: pd.DataFrame, start: date, end: date, threshold: float = 200.0) -> pd.Series:
    """Boolean Series over [start, end]: True on shortfall days."""
    days = set(shortfall_days(tx_user, start, end, threshold))
    idx = pd.date_range(start, end, freq="D").date
    return pd.Series([d in days for d in idx], index=idx)


def window_any(flags: pd.Series, t: date, days: int = 14) -> bool:
    """True if any flag is set in (t, t + days]."""
    lo, hi = t + timedelta(days=1), t + timedelta(days=days)
    sub = flags[(flags.index >= lo) & (flags.index <= hi)]
    return bool(sub.any())
