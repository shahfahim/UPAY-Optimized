"""UserCtx: everything the engine needs to know about one user at the demo's "today"."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import date, timedelta

import pandas as pd

from hishab.config import Settings
from hishab.data.loader import DataRepo
from hishab.store.sqlite import Store, UserState


class UserNotFound(KeyError):
    pass


@dataclass
class UserCtx:
    user: dict
    tx: pd.DataFrame
    today: date
    balance: float
    state: UserState

    @property
    def user_id(self) -> str:
        return self.user["user_id"]

    @property
    def persona(self) -> str:
        return self.user.get("persona", "garment_worker")

    @property
    def insufficient_history(self) -> bool:
        if self.tx.empty:
            return True
        first = self.tx["ts"].min().date()
        return (self.today - first).days < 30

    @property
    def dps_balance(self) -> float:
        paid = self.tx[self.tx["type"] == "dps_installment"]["amount"].sum()
        return float(paid)


def _pocket_from_history(tx: pd.DataFrame, name: str) -> float:
    rows = tx[tx["counterparty_id"] == f"pocket:{name}"]
    inn = rows[rows["type"] == "pocket_in"]["amount"].sum()
    out = rows[rows["type"] == "pocket_out"]["amount"].sum()
    return round(float(inn - out), 2)


def _default_state(user: dict, tx: pd.DataFrame) -> UserState:
    st = UserState()
    st.pockets["emergency"] = max(0.0, _pocket_from_history(tx, "emergency"))
    st.paisa_on = bool(user.get("paisa_saving_default", False))
    monthly = int(user.get("dps_monthly") or 0)
    if monthly > 0:
        paid = int((tx["type"] == "dps_installment").sum())
        first = tx[tx["type"].isin(["dps_installment", "dps_installment_missed"])]
        opened = first["ts"].min().date().isoformat() if not first.empty else None
        st.dps = {"monthly": monthly, "tenure_months": 24, "day": int(first["ts"].min().day) if not first.empty else 10,
                  "opened": opened, "paid_installments": paid}
    return st


def _frame(rows: list[dict], like: pd.DataFrame) -> pd.DataFrame:
    if not rows:
        return like.iloc[0:0].copy()
    df = pd.DataFrame(rows)
    df["ts"] = pd.to_datetime(df["ts"])
    for c in like.columns:
        if c not in df.columns:
            df[c] = None
    return df[like.columns]


def build_ctx(user_id: str, repo: DataRepo, store: Store, settings: Settings) -> UserCtx:
    today = settings.demo_today + timedelta(days=store.clock_offset())
    user = repo.user(user_id)
    if user is not None:
        hist = repo.history(user_id, today)
    else:
        user = store.extra_user(user_id)
        if user is None:
            raise UserNotFound(user_id)
        hist = _frame(store.extra_tx(user_id), repo.tx)
        hist = hist[hist["ts"].dt.date <= today]
    sim = _frame(store.sim_tx(user_id), repo.tx)
    parts = [p for p in (hist, sim) if not p.empty]
    tx = pd.concat(parts, ignore_index=True) if parts else repo.tx.iloc[0:0].copy()
    tx = tx.sort_values("ts", kind="stable").reset_index(drop=True)
    balance = float(tx["balance_after"].iloc[-1]) if not tx.empty else 0.0
    base_hist = hist
    state = store.get_state(user_id, lambda: _default_state(user, base_hist))
    return UserCtx(user=user, tx=tx, today=today, balance=round(balance, 2), state=state)


def ctx_from_history(user: dict, tx_user: pd.DataFrame, as_of: date) -> UserCtx:
    """Build a UserCtx straight from raw synthetic data (used by evaluation and replay, no store)."""
    tx = tx_user[pd.to_datetime(tx_user["ts"]).dt.date <= as_of].sort_values("ts", kind="stable")
    tx = tx.reset_index(drop=True)
    balance = float(tx["balance_after"].iloc[-1]) if not tx.empty else 0.0
    return UserCtx(user=user, tx=tx, today=as_of, balance=round(balance, 2), state=_default_state(user, tx))
