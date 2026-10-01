"""Test helpers to build small hand-made contexts."""

from __future__ import annotations

from dataclasses import replace
from datetime import date, datetime, timedelta

import pandas as pd

from hishab.engine.context import UserCtx
from hishab.store.sqlite import UserState


def tx_row(d: date, typ: str, amount: float, direction: int, category: str = "other", cp: str = "X",
           fee: float = 0.0, balance_after: float = 1000.0, channel: str = "upay", cp_type: str = "merchant") -> dict:
    return {"tx_id": f"H{d}{typ}{amount}", "user_id": "H1", "ts": datetime(d.year, d.month, d.day, 12),
            "type": typ, "amount": float(amount), "direction": direction, "fee": fee,
            "balance_after": balance_after, "counterparty_id": cp, "counterparty_name": cp,
            "counterparty_type": cp_type, "counterparty_channel": channel, "category": category, "area": "Gazipur"}


def hand_ctx(rows: list[dict], today: date, balance: float = 1000.0, state: UserState | None = None,
             persona: str = "garment_worker") -> UserCtx:
    tx = pd.DataFrame(rows)
    tx["ts"] = pd.to_datetime(tx["ts"])
    user = {"user_id": "H1", "persona": persona, "synthetic_name": "Test", "tenure_days": 400}
    return UserCtx(user=user, tx=tx.sort_values("ts").reset_index(drop=True), today=today, balance=balance,
                   state=state or UserState())


def with_extra_tx(ctx: UserCtx, rows: list[dict]) -> UserCtx:
    extra = pd.DataFrame(rows)
    extra["ts"] = pd.to_datetime(extra["ts"])
    tx = pd.concat([ctx.tx, extra], ignore_index=True).sort_values("ts").reset_index(drop=True)
    return replace(ctx, tx=tx)


def saving_days(today: date, n: int, pocket: str = "emergency", amount: float = 20.0) -> list[dict]:
    return [tx_row(today - timedelta(days=k), "pocket_in", amount, -1, cp=f"pocket:{pocket}", cp_type="pocket")
            for k in range(n)]
