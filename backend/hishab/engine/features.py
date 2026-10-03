"""Shared feature set (spec §4.1), computed per user at an as-of date.

The same code path builds training rows (from raw synthetic data) and live features (from a UserCtx),
so training and serving cannot drift apart.
"""

from __future__ import annotations

from datetime import date, timedelta

import numpy as np
import pandas as pd

from hishab.rules import load_rules

PROTECTED = {"persona", "gender", "area", "age_band"}
CATEGORIES = ["food_grocery", "rent", "family_support", "transport", "mobile", "health", "education",
              "utilities", "shopping", "festival", "other"]
PERSONA_CODES = {"garment_worker": 0, "daily_wage": 1, "shop_owner": 2, "student": 3}
NON_SPEND_TYPES = {"pocket_in", "dps_installment", "dps_installment_missed"}

FEATURE_KEYS = [
    "balance", "days_since_income", "days_to_income", "income_amount", "income_regularity",
    "out_7d", "out_30d", "cashout_share_30d", "depletion_days", "cashout_3d_after_income_share",
    "remittance_share", "other_wallet_share", "pocket_total", "days_to_eid", "month_end", "dom", "dow",
    "shortfall_days_90d", "min_balance_30d", "tenure_days", "persona_code", "recent_income_days",
] + [f"out_30d_{c}" for c in CATEGORIES]

_EPOCH = date(2000, 1, 1)


def _d(x: date) -> int:
    return (x - _EPOCH).days


def _eid_days() -> list[int]:
    out = []
    for e in load_rules("eid_dates")["eids"]:
        d = e["date"] if isinstance(e["date"], date) else date.fromisoformat(str(e["date"]))
        out.append(_d(d))
    return sorted(out)


class UserArrays:
    """Numpy view of one user's transactions, sorted by time, for fast as-of slicing."""

    def __init__(self, tx_user: pd.DataFrame):
        t = tx_user.sort_values("ts", kind="stable")
        ts = pd.to_datetime(t["ts"])
        self.day = ((ts - pd.Timestamp(_EPOCH)).dt.days).to_numpy(dtype=np.int64)
        self.dom = ts.dt.day.to_numpy()
        self.amount = t["amount"].to_numpy(dtype=float)
        self.dirn = t["direction"].to_numpy(dtype=np.int64)
        self.bal = t["balance_after"].to_numpy(dtype=float)
        self.type = t["type"].to_numpy(dtype=object)
        self.cat = t["category"].to_numpy(dtype=object)
        self.chan = t["counterparty_channel"].to_numpy(dtype=object)
        self.cp = t["counterparty_id"].astype(str).to_numpy(dtype=object)
        self.is_income = (np.isin(self.type, ["salary_in", "bonus_in"])
                          | ((self.type == "receive_money") & (self.cat == "income")))
        self.is_regular_income = (self.type == "salary_in") | (
            (self.type == "receive_money") & (self.cat == "income") & np.char.startswith(self.cp.astype(str), "FAM-"))
        self.is_spend = (self.dirn == -1) & ~np.isin(self.type, list(NON_SPEND_TYPES))
        self.pocket_delta = np.where(self.type == "pocket_in", self.amount,
                                     np.where(self.type == "pocket_out", -self.amount, 0.0))


def _end_balances(a: UserArrays, start_day: int, end_day: int) -> np.ndarray:
    """End-of-day balances for days start_day..end_day (inclusive); NaN before the first transaction."""
    days = np.arange(start_day, end_day + 1)
    idx = np.searchsorted(a.day, days, side="right") - 1
    out = np.where(idx >= 0, a.bal[np.clip(idx, 0, None)], np.nan)
    return out


def features_at(a: UserArrays, user: dict, as_of: date, pocket_total: float | None = None,
                threshold: float = 200.0) -> dict[str, float]:
    t = _d(as_of)
    end = int(np.searchsorted(a.day, t, side="right"))
    day, amt, dirn = a.day[:end], a.amount[:end], a.dirn[:end]
    f: dict[str, float] = {}
    f["balance"] = float(a.bal[end - 1]) if end else 0.0

    w30 = day > t - 30
    w7 = day > t - 7
    spend = a.is_spend[:end]
    out30 = amt[w30 & spend]
    f["out_7d"] = float(amt[w7 & spend].sum())
    f["out_30d"] = float(out30.sum())
    cats = a.cat[:end]
    for c in CATEGORIES:
        f[f"out_30d_{c}"] = float(amt[w30 & spend & (cats == c)].sum())
    typ = a.type[:end]
    cash30 = float(amt[w30 & (typ == "cash_out")].sum())
    f["cashout_share_30d"] = cash30 / f["out_30d"] if f["out_30d"] > 0 else 0.0
    other30 = float(amt[w30 & spend & (a.chan[:end] == "other_mfs")].sum())
    f["other_wallet_share"] = other30 / f["out_30d"] if f["out_30d"] > 0 else 0.0

    inc = a.is_income[:end]
    inc30 = float(amt[w30 & inc].sum())
    f["remittance_share"] = float(amt[w30 & spend & (cats == "family_support")].sum()) / max(inc30, 1.0)
    w90 = day > t - 90
    f["income_amount"] = float(amt[w90 & inc].sum()) / 3.0
    # income regularity: 1 - CV of six 30-day income buckets
    buckets = [float(amt[(day > t - 30 * (k + 1)) & (day <= t - 30 * k) & inc].sum()) for k in range(6)]
    mean_b = float(np.mean(buckets))
    f["income_regularity"] = float(np.clip(1 - (np.std(buckets) / mean_b if mean_b > 0 else 1.0), 0.0, 1.0))

    # pay cycle
    inc_days = day[inc]
    f["days_since_income"] = float(t - inc_days[-1]) if len(inc_days) else 60.0
    reg = a.is_regular_income[:end] & (day > t - 183)
    reg_idx = np.flatnonzero(reg)
    recent_income_days = int(np.unique(day[inc & w30]).size)
    f["recent_income_days"] = float(recent_income_days)
    if len(reg_idx) >= 2:
        payday = int(np.median(a.dom[:end][reg_idx]))
        nxt = _next_payday(as_of, payday)
        f["days_to_income"] = float((nxt - as_of).days)
        last_i = reg_idx[-1]
        inc_bal = a.bal[last_i]
        after = np.flatnonzero((np.arange(end) > last_i) & (a.bal[:end] < 0.5 * inc_bal))
        f["depletion_days"] = float(day[after[0]] - day[last_i]) if len(after) else float(min(30, t - day[last_i]))
        win = (day >= day[last_i]) & (day <= day[last_i] + 3) & (typ == "cash_out")
        f["cashout_3d_after_income_share"] = float(amt[win].sum()) / max(a.amount[last_i], 1.0)
    else:
        f["days_to_income"] = float("nan") if recent_income_days >= 8 else 30.0
        f["depletion_days"] = 30.0
        f["cashout_3d_after_income_share"] = 0.0

    f["pocket_total"] = float(a.pocket_delta[:end].sum()) if pocket_total is None else float(pocket_total)
    eids = [e for e in _eid_days() if e > t]
    f["days_to_eid"] = float(eids[0] - t) if eids else 365.0
    f["month_end"] = 1.0 if as_of.day >= 25 else 0.0
    f["dom"] = float(as_of.day)
    f["dow"] = float(as_of.weekday())

    bal90 = _end_balances(a, t - 89, t)
    inc_set = set(inc_days.tolist())
    days90 = np.arange(t - 89, t + 1)
    sf = (~np.isnan(bal90)) & (bal90 < threshold) & ~np.isin(days90, list(inc_set))
    f["shortfall_days_90d"] = float(sf.sum())
    bal30 = bal90[-30:]
    f["min_balance_30d"] = float(np.nanmin(bal30)) if np.any(~np.isnan(bal30)) else 0.0
    f["tenure_days"] = float(user.get("tenure_days", 0) or 0)
    f["persona_code"] = float(PERSONA_CODES.get(user.get("persona", ""), 0))
    return {k: float(v) for k, v in f.items()}


def _next_payday(as_of: date, dom: int) -> date:
    from hishab.engine.recurring import _next_on_day
    return _next_on_day(as_of, dom)


def user_features(ctx) -> dict[str, float]:
    threshold = load_rules("guardrails")["shortfall_threshold"]
    pockets = float(sum(ctx.state.pockets.values()))
    if ctx.tx.empty:
        return {k: 0.0 for k in FEATURE_KEYS}
    return features_at(UserArrays(ctx.tx), ctx.user, ctx.today, pocket_total=pockets, threshold=threshold)


def training_frame(data, obs_dates: list[date]) -> pd.DataFrame:
    """One row per (user, obs_date) with FEATURE_KEYS + labels, from raw synthetic data."""
    threshold = load_rules("guardrails")["shortfall_threshold"]
    obs_set = set(obs_dates)
    labels = data.labels[data.labels["obs_date"].isin(obs_set)]
    users = {r["user_id"]: r for r in data.users.to_dict("records")}
    rows = []
    tx_by_user = {uid: g for uid, g in data.transactions.groupby("user_id", sort=False)}
    for uid, lab in labels.groupby("user_id", sort=False):
        a = UserArrays(tx_by_user[uid])
        for r in lab.itertuples(index=False):
            f = features_at(a, users[uid], r.obs_date, threshold=threshold)
            f.update(user_id=uid, obs_date=r.obs_date, shortfall_14d=bool(r.shortfall_14d),
                     persona=users[uid]["persona"], gender=users[uid]["gender"], area=users[uid]["area"])
            rows.append(f)
    return pd.DataFrame(rows)
