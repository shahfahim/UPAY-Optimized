"""E16 — savings levels (spec F4). Levels are advice and in-app unlocks only; they never gate upay products."""

from __future__ import annotations

import math
from dataclasses import dataclass, field
from datetime import timedelta

import pandas as pd

from hishab.engine.health import Indicators, living_daily
from hishab.rules import load_rules


@dataclass
class LevelStatus:
    level: int
    name_bn: str
    streak_days: int
    milestones: list = field(default_factory=list)
    next_level: int | None = None
    progress: float = 0.0
    projection_days: int | None = None
    dps_ready: bool = False
    unlocks_bn: list = field(default_factory=list)
    note_bn: str = ""


def _dates(tx: pd.DataFrame) -> pd.Series:
    return pd.to_datetime(tx["ts"]).dt.date


def _emptied_days(tx: pd.DataFrame) -> set:
    t = tx[tx["type"].isin(["pocket_in", "pocket_out"])].sort_values("ts")
    bal, out = 0.0, set()
    for r in t.itertuples(index=False):
        bal += r.amount if r.type == "pocket_in" else -r.amount
        if r.type == "pocket_out" and bal <= 0.01:
            out.add(pd.Timestamp(r.ts).date())
    return out


def saving_streak(ctx) -> int:
    """Calendar days from the start of the current saving run to today (up to `allowed_missed_days` gaps)."""
    if ctx.tx.empty:
        return 0
    allowed = load_rules("levels")["allowed_missed_days"]
    d = _dates(ctx.tx)
    saved = set(d[ctx.tx["type"] == "pocket_in"])
    emptied = _emptied_days(ctx.tx)
    first = min(d)
    day, missed, span = ctx.today, 0, 0
    while day >= first:
        if day in emptied:
            break
        if day in saved:
            span = (ctx.today - day).days + 1
        else:
            missed += 1
            if missed > allowed:
                break
        day -= timedelta(days=1)
    return span


def _on_time_installments(ctx) -> int:
    d = _dates(ctx.tx)
    recent_missed = ctx.tx[(ctx.tx["type"] == "dps_installment_missed") & (d > ctx.today - timedelta(days=90))]
    if not recent_missed.empty:
        return 0
    return int(((ctx.tx["type"] == "dps_installment") & (d > ctx.today - timedelta(days=120))).sum())


def compute_level(ctx, ind: Indicators) -> LevelStatus:
    r = load_rules("levels")
    streak = saving_streak(ctx)
    ontime = _on_time_installments(ctx)
    level = 0
    if streak >= r["level1_days"]:
        level = 1
    if level >= 1 and ind.shortfall_free_months >= r["level2"]["shortfall_free_months"] \
            and ind.emergency_days >= r["level2"]["emergency_days"]:
        level = 2
    if level >= 2 and ontime >= r["level3"]["on_time_installments"]:
        level = 3
    milestones = [{"days": m, "reached": streak >= m, "badge_bn": r["milestone_badges_bn"][m]} for m in r["milestones"]]

    projection = None
    if level == 0:
        progress = streak / r["level1_days"]
        projection = r["level1_days"] - streak
    elif level == 1:
        need_m, need_e = r["level2"]["shortfall_free_months"], r["level2"]["emergency_days"]
        progress = (min(1.0, ind.shortfall_free_months / need_m) + min(1.0, ind.emergency_days / need_e)) / 2
        days_months = 30 * max(0, need_m - ind.shortfall_free_months)
        d = _dates(ctx.tx)
        rate = float(ctx.tx.loc[(ctx.tx["type"] == "pocket_in") & (d > ctx.today - timedelta(days=30)),
                                "amount"].sum()) / 30.0
        deficit = max(0.0, need_e - ind.emergency_days) * living_daily(ctx.tx, ctx.today)
        days_emerg = math.ceil(deficit / rate) if rate > 0 else None
        projection = max(days_months, days_emerg) if days_emerg is not None else None
    elif level == 2:
        need = r["level3"]["on_time_installments"]
        progress = min(1.0, ontime / need)
        projection = 30 * max(0, need - ontime)
    else:
        progress = 1.0
    info = next(x for x in r["levels"] if x["level"] == level)
    return LevelStatus(level=level, name_bn=info["name_bn"], streak_days=streak, milestones=milestones,
                       next_level=level + 1 if level < 3 else None, progress=round(progress, 3),
                       projection_days=projection, dps_ready=level >= 1, unlocks_bn=list(info["unlocks_bn"]),
                       note_bn=r["note_bn"])
