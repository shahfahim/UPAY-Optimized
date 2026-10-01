"""Paisa saving (spec §5.3): sweep the balance's fractional part into the paisa pocket."""

from __future__ import annotations

from decimal import ROUND_DOWN, Decimal

from hishab.store.sqlite import UserState


def paisa_sweep(balance: float) -> tuple[float, float]:
    """Returns (new_balance, swept). 6240.35 -> (6240.00, 0.35). Never adds a charge."""
    b = Decimal(str(round(balance, 2)))
    whole = b.to_integral_value(rounding=ROUND_DOWN)
    swept = b - whole
    return float(whole), float(swept)


def apply_paisa(state: UserState, balance: float) -> tuple[float, float]:
    """Sweep after a transaction unless paisa saving is off or paused. Updates state.pockets['paisa']."""
    if not state.paisa_on or state.paisa_paused:
        return balance, 0.0
    new_balance, swept = paisa_sweep(balance)
    if swept > 0:
        state.pockets["paisa"] = round(state.pockets.get("paisa", 0.0) + swept, 2)
    return new_balance, swept


def update_paisa_pause(state: UserState, risk_level: str, income_today: bool) -> None:
    """Pause at amber/red risk; resume when income arrives."""
    if not state.paisa_on:
        return
    if income_today:
        state.paisa_paused = False
    elif risk_level in ("amber", "red"):
        state.paisa_paused = True
