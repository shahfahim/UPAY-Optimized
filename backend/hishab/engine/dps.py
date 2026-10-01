"""E16 — Smart DPS: the largest safe monthly installment, the installment day, tenure and maturity estimate."""

from __future__ import annotations

from dataclasses import dataclass, field

import pandas as pd

from hishab.engine.features import user_features
from hishab.engine.forecast import band_from_flows, future_flows
from hishab.engine.recurring import _next_on_day, detect_recurring
from hishab.engine.risk import PROJ_FEATURES, risk_features, score
from hishab.engine.text import bn_digits
from hishab.rules import load_rules


@dataclass
class DpsAdvice:
    status: str
    safe_monthly: float | None
    day: int | None
    tenure_months: int | None
    maturity_estimate: float | None
    reason_bn: str
    options: list = field(default_factory=list)
    naive_monthly: float = 0.0


def _installment_day(recurring) -> int:
    sal = [e for e in recurring if e.kind == "salary"]
    return min(28, sal[0].day_of_month + 1) if sal else 10


def _risk_with(ctx, models, flows, base, monthly: float, day: int, horizon: int) -> float:
    rows = []
    d = _next_on_day(ctx.today, day)
    end = ctx.today + pd.Timedelta(days=horizon).to_pytimedelta()
    while d <= end:
        rows.append({"date": d, "amount": -monthly, "category": "other", "type": "dps_installment", "fee": 0.0,
                     "kind": "action"})
        d = _next_on_day(d, day)
    with_dps = band_from_flows(ctx, models, pd.concat([flows, pd.DataFrame(rows)], ignore_index=True),
                               horizon=horizon)
    feats = risk_features(ctx, band_from_flows(ctx, models, flows, horizon=30))
    delta = min(with_dps.p50) - min(base.p50)  # installments over the whole check period shift the projection
    for k in PROJ_FEATURES:
        feats[k] += delta
    return float(models.risk.predict_proba(pd.DataFrame([feats]))[0])


def installment_risk(ctx, models, monthly: float, day: int) -> float:
    horizon = 30 * load_rules("dps")["check_months"]
    recurring = detect_recurring(ctx.tx, ctx.today)
    flows = future_flows(ctx, models.forecaster, horizon, recurring)
    base = band_from_flows(ctx, models, flows, horizon=horizon)
    return _risk_with(ctx, models, flows, base, monthly, day, horizon)


def dps_advice(ctx, models, goal_target: float | None = None) -> DpsAdvice:
    rules = load_rules("dps")
    opts = sorted(rules["monthly_options"])
    tenures = sorted(rules["tenure_months"])
    recurring = detect_recurring(ctx.tx, ctx.today)
    day = _installment_day(recurring)
    sal = [e for e in recurring if e.kind == "salary"]
    income = sal[0].amount if sal else user_features(ctx).get("income_amount", 0.0)
    naive = float(min(opts, key=lambda o: abs(o - rules["naive_fraction"] * income))) if income > 0 else float(opts[0])

    if income > 0:  # prudential cap on top of the risk check
        capped = [o for o in opts if o <= rules["max_income_fraction"] * income]
        opts = capped or opts[:1]

    horizon = 30 * rules["check_months"]
    flows = future_flows(ctx, models.forecaster, horizon, recurring)
    base30 = band_from_flows(ctx, models, flows, horizon=30)
    if score(ctx, base30, models).level != "green":
        return DpsAdvice("not_now", None, day, None, None,
                         "এখন মাসের শেষে টানাটানির ঝুঁকি আছে, তাই নতুন কিস্তি শুরু না করাই ভালো। "
                         "ঝুঁকি কমলে আবার দেখো।", opts, naive)
    base = band_from_flows(ctx, models, flows, horizon=horizon)
    lo, hi, best = 0, len(opts) - 1, None
    while lo <= hi:  # risk grows with the installment, so binary search for the largest safe option
        mid = (lo + hi) // 2
        if _risk_with(ctx, models, flows, base, opts[mid], day, horizon) < load_rules("guardrails")["risk_levels"]["amber"]:
            best, lo = mid, mid + 1
        else:
            hi = mid - 1
    if best is None:
        return DpsAdvice("not_now", None, day, None, None,
                         "এখন কিস্তির জন্য নিরাপদ জায়গা নেই — আগে জরুরি পকেটে কিছু জমাও।", opts, naive)
    safe = float(opts[best])
    if goal_target:
        tenure = next((t for t in tenures if safe * t >= goal_target), tenures[-1])
    else:
        tenure = 12
    day_note = f"{bn_digits(day)} তারিখ — বেতনের পরের দিন" if sal else f"{bn_digits(day)} তারিখ"
    return DpsAdvice("ok", safe, day, tenure, safe * tenure,
                     f"এর বেশি দিলে মাসের শেষে টাকা কম পড়ার সম্ভাবনা বাড়বে। কিস্তির দিন রাখো {day_note}।",
                     opts, naive)
