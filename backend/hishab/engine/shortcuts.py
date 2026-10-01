"""E15 — recent payments row (I4): last distinct payees/billers, with recurring bills due soon first."""

from __future__ import annotations

from dataclasses import dataclass

from hishab.engine.recurring import RecurringEvent

PAYMENT_TYPES = ["merchant_pay", "bill_pay", "mobile_recharge", "send_money"]
DUE_SOON_DAYS = 5


@dataclass
class Shortcut:
    counterparty_id: str
    name: str
    type: str
    category: str
    last_amount: float
    due_in_days: int | None = None


def recent_payments(ctx, recurring: list[RecurringEvent], k: int = 4) -> list[Shortcut]:
    if ctx.tx.empty:
        return []
    pays = ctx.tx[ctx.tx["type"].isin(PAYMENT_TYPES) & (ctx.tx["direction"] == -1)].sort_values("ts", ascending=False)
    pays = pays.drop_duplicates("counterparty_id")
    due = {}
    for e in recurring:
        days = (e.next_date - ctx.today).days
        if e.direction < 0 and 0 < days <= DUE_SOON_DAYS:
            due[e.counterparty_id] = days
    rows = [Shortcut(str(r.counterparty_id), str(r.counterparty_name), str(r.type), str(r.category),
                     float(r.amount), due.get(str(r.counterparty_id))) for r in pays.itertuples(index=False)]
    rows.sort(key=lambda s: (s.due_in_days is None, s.due_in_days or 0))  # due soon first, then most recent
    return rows[:k]
