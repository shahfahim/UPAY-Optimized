"""Input validation shared by engine entry points (errors are Bangla, shown to the user)."""

from __future__ import annotations

import math

from hishab.errors import UserError
from hishab.rules import load_rules


def amount(value) -> float:
    try:
        v = float(value)
    except (TypeError, ValueError):
        raise UserError("টাকার পরিমাণ সঠিক নয়")
    if not math.isfinite(v) or v <= 0 or v > load_rules("guardrails")["max_amount"]:
        raise UserError("টাকার পরিমাণ সঠিক নয়")
    return round(v, 2)
