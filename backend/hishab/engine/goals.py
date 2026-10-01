"""E8 — goal planner: feasibility of saving `target` in `months` from bootstrapped monthly surpluses."""

from __future__ import annotations

import math
from dataclasses import dataclass, field
from datetime import timedelta

import numpy as np
import pandas as pd

from hishab.engine.forecast import forecast
from hishab.rules import load_rules

INTERNAL_TYPES = {"pocket_in", "pocket_out", "dps_installment", "dps_installment_missed"}


@dataclass
class GoalPlan:
    target: float
    months: int
    monthly: float
    feasibility: float
    enabling_actions: list[str] = field(default_factory=list)
    insufficient_history: bool = False


def validate_goal(target, months) -> tuple[float, int]:
    max_amount = load_rules("guardrails")["max_amount"]
    try:
        target, months = float(target), int(months)
    except (TypeError, ValueError):
        raise ValueError("লক্ষ্যের পরিমাণ বা মাস সঠিক নয়")
    if not (0 < target <= max_amount):
        raise ValueError("লক্ষ্যের পরিমাণ সঠিক নয়")
    if not (1 <= months <= 60):
        raise ValueError("মাস ১ থেকে ৬০-এর মধ্যে হতে হবে")
    return target, months


def monthly_surpluses(ctx, n: int = 6) -> list[float]:
    """Net external money flow (income − spending, excluding internal pocket/DPS moves) per 30-day window."""
    t = ctx.tx[~ctx.tx["type"].isin(INTERNAL_TYPES)]
    d = pd.to_datetime(t["ts"]).dt.date
    net = t["direction"].astype(float) * t["amount"].astype(float) - t["fee"].astype(float)
    out = []
    for k in range(n):
        lo, hi = ctx.today - timedelta(days=30 * (k + 1)), ctx.today - timedelta(days=30 * k)
        m = (d > lo) & (d <= hi)
        if m.any():
            out.append(float(net[m].sum()))
    return out


def plan_goal(ctx, models, target, months, with_actions: bool = True) -> GoalPlan:
    target, months = validate_goal(target, months)
    monthly = float(math.ceil(target / months))
    samples = np.array(monthly_surpluses(ctx), dtype=float)
    if samples.size == 0 or ctx.insufficient_history:
        return GoalPlan(target, months, monthly, 0.0, [], True)
    fc = forecast(ctx, models)
    e2_net = fc.p50[-1] - ctx.balance
    samples = samples + 0.5 * (e2_net - samples.mean())  # lean the history towards the current forecast
    rng = np.random.default_rng(0)
    sums = rng.choice(samples, size=(1000, months)).sum(axis=1)
    feas = float((sums >= target).mean())
    enabling = []
    if with_actions:
        from hishab.engine.actions import rank_actions
        enabling = [c.id for c in rank_actions(ctx, models, k=3) if c.fees_saved > 0 or c.risk_after < c.risk_before]
    return GoalPlan(target, months, monthly, round(feas, 3), enabling, False)
