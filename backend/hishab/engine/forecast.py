"""E2 — cash-flow forecaster with an uncertainty band.

Future flows = recurring events (E1) + LightGBM-predicted daily discretionary outflow (and irregular inflow).
The band comes from bootstrapping the model's daily residuals over 200 paths.

Training and serving build model features through the same day-by-day `_DayState`, so they match.
"""

from __future__ import annotations

import json
from collections import deque
from dataclasses import dataclass
from datetime import date, timedelta
from pathlib import Path
from typing import Callable, Sequence

import lightgbm as lgb
import numpy as np
import pandas as pd

from hishab.engine.features import PERSONA_CODES
from hishab.engine.recurring import RecurringEvent, detect_recurring
from hishab.rules import load_rules

DISC_TYPES = {"merchant_pay", "cash_out", "mobile_recharge", "send_money"}
NON_DISC_CATEGORIES = {"rent", "family_support"}
FC_FEATURES = ["dom", "dow", "month_end", "days_to_eid", "persona_code", "is_regular", "days_since_income",
               "days_to_payday", "trail7", "trail30", "trail_in30", "bal_prev"]
FLOW_COLS = ["date", "amount", "category", "type", "fee", "kind"]

Transform = Callable[[pd.DataFrame, object], pd.DataFrame]


def _eid_dates() -> list[date]:
    out = []
    for e in load_rules("eid_dates")["eids"]:
        out.append(e["date"] if isinstance(e["date"], date) else date.fromisoformat(str(e["date"])))
    return sorted(out)


def _is_regular_income(row_type: str, category: str, cp: str) -> bool:
    return row_type == "salary_in" or (row_type == "receive_money" and category == "income" and cp.startswith("FAM-"))


def _is_income(row_type: str, category: str) -> bool:
    return row_type in ("salary_in", "bonus_in") or (row_type == "receive_money" and category == "income")


class _DayState:
    """Rolling per-user state used to build one feature row per day."""

    def __init__(self, persona: str, eids: list[date]):
        self.out_hist: deque = deque(maxlen=30)
        self.in_hist: deque = deque(maxlen=30)
        self.bal = 0.0
        self.last_income: date | None = None
        self.reg_doms: deque = deque(maxlen=6)
        self.persona_code = float(PERSONA_CODES.get(persona, 0))
        self.eids = eids

    @property
    def payday(self) -> int | None:
        return int(np.median(self.reg_doms)) if len(self.reg_doms) >= 2 else None

    def row(self, d: date) -> dict:
        nxt = [e for e in self.eids if e > d]
        payday = self.payday
        if payday is not None:
            from hishab.engine.recurring import _next_on_day
            to_pay = (_next_on_day(d - timedelta(days=1), payday) - d).days
        else:
            to_pay = 0
        o = list(self.out_hist)
        i = list(self.in_hist)
        return {
            "dom": float(d.day), "dow": float(d.weekday()), "month_end": 1.0 if d.day >= 25 else 0.0,
            "days_to_eid": float((nxt[0] - d).days) if nxt else 365.0,
            "persona_code": self.persona_code, "is_regular": 1.0 if payday is not None else 0.0,
            "days_since_income": float((d - self.last_income).days) if self.last_income else 60.0,
            "days_to_payday": float(to_pay),
            "trail7": float(np.mean(o[-7:])) if o else 0.0,
            "trail30": float(np.mean(o)) if o else 0.0,
            "trail_in30": float(np.mean(i)) if i else 0.0,
            "bal_prev": float(self.bal),
        }

    def advance(self, d: date, out: float, inn: float, bal: float, income_today: bool, regular_dom: int | None):
        self.out_hist.append(out)
        self.in_hist.append(inn)
        self.bal = bal
        if income_today:
            self.last_income = d
        if regular_dom is not None:
            self.reg_doms.append(regular_dom)


def _daily_actuals(tx_user: pd.DataFrame) -> dict[date, dict]:
    """Per calendar day: discretionary out (incl. fees), irregular in, end balance, income flags."""
    t = tx_user.sort_values("ts", kind="stable")
    out: dict[date, dict] = {}
    for r in t.itertuples(index=False):
        d = r.ts.date()
        rec = out.setdefault(d, {"out": 0.0, "in": 0.0, "bal": 0.0, "income": False, "reg_dom": None})
        cp = str(r.counterparty_id)
        if r.direction == -1 and r.type in DISC_TYPES and r.category not in NON_DISC_CATEGORIES:
            rec["out"] += float(r.amount) + float(r.fee)
        if _is_income(r.type, r.category):
            rec["income"] = True
            if _is_regular_income(r.type, r.category, cp):
                rec["reg_dom"] = d.day
            else:
                rec["in"] += float(r.amount)
        rec["bal"] = float(r.balance_after)
    return out


def _walk(tx_user: pd.DataFrame, persona: str, until: date, emit_from: date | None = None):
    """Replay history day by day. Yields (day, feature_row, actual) for days >= emit_from; returns final state."""
    eids = _eid_dates()
    st = _DayState(persona, eids)
    acts = _daily_actuals(tx_user)
    rows = []
    if not acts:
        return st, rows
    d = min(acts)
    while d <= until:
        a = acts.get(d)
        if emit_from is not None and d >= emit_from:
            rows.append((d, st.row(d), a))
        if a is None:
            st.advance(d, 0.0, 0.0, st.bal, False, None)
        else:
            st.advance(d, a["out"], a["in"], a["bal"], a["income"], a["reg_dom"])
        d += timedelta(days=1)
    return st, rows


def training_daily(data, start: date, end: date, user_ids: Sequence[str] | None = None) -> pd.DataFrame:
    users = data.users.set_index("user_id")
    rows = []
    for uid, t in data.transactions.groupby("user_id", sort=False):
        if user_ids is not None and uid not in user_ids:
            continue
        persona = users.loc[uid, "persona"]
        _, emitted = _walk(t, persona, end, emit_from=start)
        for d, feat, a in emitted:
            feat = dict(feat)
            feat.update(user_id=uid, date=d, persona=persona,
                        disc_out=a["out"] if a else 0.0, disc_in=a["in"] if a else 0.0)
            rows.append(feat)
    return pd.DataFrame(rows)


_PARAMS = dict(objective="regression", learning_rate=0.05, num_leaves=31, min_data_in_leaf=50,
               feature_fraction=0.9, bagging_fraction=0.9, bagging_freq=1, verbose=-1, seed=42)


class Forecaster:
    def __init__(self, out_model: lgb.Booster | None = None, in_model: lgb.Booster | None = None):
        self.out_model = out_model
        self.in_model = in_model

    def fit(self, daily: pd.DataFrame, rounds: int = 300) -> "Forecaster":
        X = daily[FC_FEATURES]
        self.out_model = lgb.train(_PARAMS, lgb.Dataset(X, daily["disc_out"]), num_boost_round=rounds)
        self.in_model = lgb.train(_PARAMS, lgb.Dataset(X, daily["disc_in"]), num_boost_round=rounds)
        return self

    def predict_rows(self, rows: pd.DataFrame) -> tuple[np.ndarray, np.ndarray]:
        X = rows[FC_FEATURES]
        return (np.clip(self.out_model.predict(X), 0, None), np.clip(self.in_model.predict(X), 0, None))

    def residuals(self, daily: pd.DataFrame, max_per_persona: int = 3000) -> dict[str, list[float]]:
        pred_out, _ = self.predict_rows(daily)
        res = daily.assign(r=daily["disc_out"].to_numpy() - pred_out)
        out = {}
        rng = np.random.default_rng(0)
        for persona, g in res.groupby("persona"):
            vals = g["r"].to_numpy()
            if len(vals) > max_per_persona:
                vals = rng.choice(vals, size=max_per_persona, replace=False)
            out[str(persona)] = [round(float(v), 2) for v in vals]
        return out

    def save(self, directory: Path) -> None:
        directory = Path(directory)
        directory.mkdir(parents=True, exist_ok=True)
        self.out_model.save_model(str(directory / "forecaster_out.txt"))
        self.in_model.save_model(str(directory / "forecaster_in.txt"))

    @classmethod
    def load(cls, directory: Path) -> "Forecaster":
        directory = Path(directory)
        return cls(lgb.Booster(model_file=str(directory / "forecaster_out.txt")),
                   lgb.Booster(model_file=str(directory / "forecaster_in.txt")))


def save_residuals(res: dict, path: Path) -> None:
    Path(path).write_text(json.dumps(res), encoding="utf-8")


def load_residuals(path: Path) -> dict:
    return json.loads(Path(path).read_text(encoding="utf-8"))


# --- flows ---------------------------------------------------------------------------------------------

def to_flows(tx: pd.DataFrame) -> pd.DataFrame:
    if tx.empty:
        return pd.DataFrame(columns=FLOW_COLS)
    return pd.DataFrame({
        "date": pd.to_datetime(tx["ts"]).dt.date,
        "amount": tx["amount"].astype(float) * tx["direction"].astype(float),
        "category": tx["category"],
        "type": tx["type"],
        "fee": tx["fee"].astype(float),
        "kind": "actual",
    })


def _cashout_fee(amount: float) -> float:
    edge = next(e for e in load_rules("fees")["edges"] if e["from"] == "upay_wallet" and e["to"] == "agent_cash")
    fee = edge["fixed"] + edge["pct"] / 100.0 * amount
    return round(min(max(fee, edge["min"]), edge["max"]), 2)


def recurring_flows(events: list[RecurringEvent], today: date, horizon: int) -> list[dict]:
    from hishab.engine.recurring import _next_on_day
    rows = []
    end = today + timedelta(days=horizon)
    for e in events:
        d = _next_on_day(today, e.day_of_month)
        while d <= end:
            fee = _cashout_fee(e.amount) if e.tx_type == "cash_out" else 0.0
            rows.append({"date": d, "amount": e.direction * e.amount, "category": e.category,
                         "type": e.tx_type or e.kind, "fee": fee, "kind": "recurring"})
            d = _next_on_day(d, e.day_of_month)
    return rows


def _category_shares(tx: pd.DataFrame, today: date) -> dict[str, float]:
    lo = pd.Timestamp(today - timedelta(days=60))
    t = tx[(pd.to_datetime(tx["ts"]) > lo) & (tx["direction"] == -1) & tx["type"].isin(DISC_TYPES)
           & ~tx["category"].isin(NON_DISC_CATEGORIES)]
    total = float(t["amount"].sum())
    if total <= 0:
        return {"food_grocery": 1.0}
    s = t.groupby("category")["amount"].sum() / total
    return {str(k): float(v) for k, v in s.items() if v > 0}


def future_flows(ctx, fc: Forecaster, horizon: int = 30, events: list[RecurringEvent] | None = None) -> pd.DataFrame:
    today = ctx.today
    events = detect_recurring(ctx.tx, today) if events is None else events
    rec = recurring_flows(events, today, horizon)
    rec_by_day: dict[date, list[dict]] = {}
    for r in rec:
        rec_by_day.setdefault(r["date"], []).append(r)
    st, _ = _walk(ctx.tx, ctx.persona, today)
    st.bal = float(ctx.balance)
    shares = _category_shares(ctx.tx, today)
    rows = list(rec)
    for k in range(1, horizon + 1):
        d = today + timedelta(days=k)
        feat = pd.DataFrame([st.row(d)])
        p_out, p_in = fc.predict_rows(feat)
        out, inn = float(p_out[0]), float(p_in[0])
        for cat, share in shares.items():
            if out * share > 0:
                rows.append({"date": d, "amount": -round(out * share, 2), "category": cat, "type": "discretionary",
                             "fee": 0.0, "kind": "discretionary"})
        if inn > 1.0:
            rows.append({"date": d, "amount": round(inn, 2), "category": "income", "type": "receive_money",
                         "fee": 0.0, "kind": "discretionary"})
        day_rec = rec_by_day.get(d, [])
        net_rec = sum(r["amount"] - r["fee"] for r in day_rec)
        income_today = any(r["amount"] > 0 for r in day_rec) or inn > 1.0
        reg_dom = d.day if any(r["amount"] > 0 and r["category"] == "income" for r in day_rec) else None
        st.advance(d, out, inn, st.bal + net_rec + inn - out, income_today, reg_dom)
    df = pd.DataFrame(rows, columns=FLOW_COLS)
    return df


# --- band ----------------------------------------------------------------------------------------------

@dataclass
class ForecastResult:
    dates: list[date]
    p10: list[float]
    p50: list[float]
    p90: list[float]
    flows: pd.DataFrame
    shortfall_date: date | None
    shortfall_amount: float


def balance_band(balance: float, flows: pd.DataFrame, residuals: dict, persona: str, today: date,
                 horizon: int = 30, n_paths: int = 200, seed: int = 0, threshold: float = 200.0) -> ForecastResult:
    dates = [today + timedelta(days=k) for k in range(1, horizon + 1)]
    net = np.zeros(horizon)
    disc = np.zeros(horizon)
    if not flows.empty:
        f = flows.copy()
        f["net"] = f["amount"].astype(float) - f["fee"].astype(float)
        by_day = f.groupby("date")["net"].sum()
        disc_by_day = f[(f["kind"] == "discretionary") & (f["amount"] < 0)].groupby("date")["amount"].sum()
        for i, d in enumerate(dates):
            net[i] = float(by_day.get(d, 0.0))
            disc[i] = -float(disc_by_day.get(d, 0.0))
    res = np.asarray(residuals.get(persona) or next(iter(residuals.values()), [0.0]), dtype=float)
    rng = np.random.default_rng(seed)
    noise = rng.choice(res, size=(n_paths, horizon)) if len(res) else np.zeros((n_paths, horizon))
    noise = np.maximum(noise, -disc)  # a day's discretionary outflow cannot go negative
    paths = balance + np.cumsum(net - noise, axis=1)
    p10, p50, p90 = np.percentile(paths, [10, 50, 90], axis=0)
    below = np.flatnonzero(p50 < threshold)
    sf_date = dates[int(below[0])] if len(below) else None
    sf_amount = round(max(0.0, threshold - float(p50.min())), 0) if len(below) else 0.0
    return ForecastResult(dates=dates, p10=[round(float(x), 2) for x in p10], p50=[round(float(x), 2) for x in p50],
                          p90=[round(float(x), 2) for x in p90], flows=flows, shortfall_date=sf_date,
                          shortfall_amount=float(sf_amount))


def forecast(ctx, models, transforms: Sequence[Transform] = (), horizon: int = 30,
             events: list[RecurringEvent] | None = None) -> ForecastResult:
    threshold = load_rules("guardrails")["shortfall_threshold"]
    flows = future_flows(ctx, models.forecaster, horizon, events)
    for tr in transforms:
        flows = tr(flows, ctx)
    return balance_band(ctx.balance, flows, models.residuals, ctx.persona, ctx.today, horizon,
                        threshold=threshold)


# --- baselines -----------------------------------------------------------------------------------------

def _actual_net_by_day(tx: pd.DataFrame) -> pd.Series:
    f = to_flows(tx)
    if f.empty:
        return pd.Series(dtype=float)
    f["net"] = f["amount"] - f["fee"]
    return f.groupby("date")["net"].sum()


def baseline_last_month(ctx, horizon: int = 30) -> list[float]:
    net = _actual_net_by_day(ctx.tx)
    bal, out = ctx.balance, []
    for k in range(1, horizon + 1):
        d = ctx.today + timedelta(days=k) - timedelta(days=30)
        bal += float(net.get(d, 0.0))
        out.append(round(bal, 2))
    return out


def baseline_trailing_avg(ctx, horizon: int = 30) -> list[float]:
    net = _actual_net_by_day(ctx.tx)
    window = [ctx.today - timedelta(days=k) for k in range(30)]
    avg = float(sum(net.get(d, 0.0) for d in window)) / 30.0
    return [round(ctx.balance + avg * k, 2) for k in range(1, horizon + 1)]
