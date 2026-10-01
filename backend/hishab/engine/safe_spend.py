"""E11 — safe-to-spend today (spec §5.2)."""

from __future__ import annotations

from datetime import timedelta

from hishab.engine.recurring import RecurringEvent, next_income
from hishab.rules import load_rules


def safe_to_spend_value(balance: float, committed: float, cushion: float, horizon: int, buffer: float) -> float:
    return max(0.0, (balance - committed - cushion - buffer) / max(1, horizon))


def _horizon_and_committed(ctx, recurring: list[RecurringEvent], max_horizon: int = 30) -> tuple[int, float]:
    nxt = next_income(recurring, ctx.today)
    horizon = (nxt - ctx.today).days if nxt else 7
    horizon = max(1, min(horizon, max_horizon))
    end = ctx.today + timedelta(days=horizon)
    committed = sum(e.amount for e in recurring if e.direction < 0 and ctx.today < e.next_date < end)
    return horizon, float(committed)


def safe_to_spend(ctx, fc, recurring: list[RecurringEvent]) -> float:
    """Spec §5.2: conservative daily amount, keeping an uncertainty cushion (P50 − P10 at the horizon)."""
    buffer = float(load_rules("guardrails")["essential_buffer"])
    horizon, committed = _horizon_and_committed(ctx, recurring, len(fc.p50))
    cushion = max(0.0, fc.p50[horizon - 1] - fc.p10[horizon - 1])
    return round(safe_to_spend_value(ctx.balance, committed, cushion, horizon, buffer), 0)


def daily_budget(ctx, recurring: list[RecurringEvent]) -> float:
    """Break-even daily amount until the next income (no uncertainty cushion). Shown when safe_to_spend is 0."""
    buffer = float(load_rules("guardrails")["essential_buffer"])
    horizon, committed = _horizon_and_committed(ctx, recurring)
    return round(safe_to_spend_value(ctx.balance, committed, 0.0, horizon, buffer), 0)
