"""E17 — emergency money helper: pockets first, then a DPS-backed loan under the BANK's fixed rule.

The AI never approves, denies or sizes a loan. It only checks affordability of the repayments.
"""

from __future__ import annotations

import math
from dataclasses import dataclass, field

import pandas as pd

from hishab.engine import validate
from hishab.engine.eid import plan_eid
from hishab.engine.forecast import band_from_flows, future_flows
from hishab.engine.recurring import _next_on_day, detect_recurring
from hishab.engine.text import POCKET_BN, bn_num
from hishab.rules import load_rules


@dataclass
class EmergencyOption:
    kind: str
    pocket: str | None
    available: float
    tradeoff_bn: str
    affordability_bn: str | None = None


@dataclass
class EmergencyResult:
    amount: float
    options: list = field(default_factory=list)
    note_bn: str = ""


def _affordability(ctx, models, amount: float) -> str:
    rules = load_rules("emergency")
    months = rules["repayment_months"]
    monthly = amount / months
    recurring = detect_recurring(ctx.tx, ctx.today)
    sal = [e for e in recurring if e.kind == "salary"]
    day = min(28, sal[0].day_of_month + 1) if sal else 10
    horizon = 90
    flows = future_flows(ctx, models.forecaster, horizon, recurring)
    base = band_from_flows(ctx, models, flows, horizon=horizon)
    rows, d = [], _next_on_day(ctx.today, day)
    end = ctx.today + pd.Timedelta(days=horizon).to_pytimedelta()
    while d <= end:
        rows.append({"date": d, "amount": -monthly, "category": "other", "type": "loan_repayment", "fee": 0.0,
                     "kind": "action"})
        d = _next_on_day(d, day)
    after = band_from_flows(ctx, models, pd.concat([flows, pd.DataFrame(rows)], ignore_index=True), horizon=horizon)
    threshold = load_rules("guardrails")["shortfall_threshold"]
    gap = threshold - min(after.p50)
    if gap > 0:
        return (f"মাসে প্রায় ৳{bn_num(monthly)} কিস্তি দিলে আগামী ৩ মাসে মাসের শেষে প্রায় "
                f"৳{bn_num(gap)} কম পড়তে পারে।")
    extra = max(0.0, min(base.p50) - min(after.p50))
    return (f"মাসে প্রায় ৳{bn_num(monthly)} কিস্তি দিলেও হিসাবমতো মাসের শেষে টাকা থাকার কথা "
            f"(সর্বনিম্ন ব্যালেন্স প্রায় ৳{bn_num(extra)} কমবে)।")


def emergency_options(ctx, models, amount) -> EmergencyResult:
    amount = validate.amount(amount)
    rules = load_rules("emergency")
    opts: list[EmergencyOption] = []
    pockets = ctx.state.pockets
    if pockets.get("emergency", 0) > 0:
        opts.append(EmergencyOption("emergency_pocket", "emergency", round(pockets["emergency"], 2),
                                    "জরুরি পকেট ঠিক এই সময়ের জন্যই।"))
    eid_weekly = None
    for name in ["eid", "family", "education", "custom", "paisa"]:
        bal = float(pockets.get(name, 0.0))
        if bal <= 0:
            continue
        take = min(bal, amount)
        if name == "eid":
            if eid_weekly is None:
                eid_weekly = plan_eid(ctx).weekly
            weeks = math.ceil(take / eid_weekly) if eid_weekly and eid_weekly > 0 else 1
            trade = f"ঈদ পকেট থেকে নিলে ঈদের লক্ষ্য প্রায় {bn_num(weeks)} সপ্তাহ পিছিয়ে যাবে।"
        else:
            trade = f"{POCKET_BN.get(name, name)} পকেটের লক্ষ্য কিছুটা পিছিয়ে যাবে।"
        opts.append(EmergencyOption("pocket", name, round(bal, 2), trade))
    if ctx.state.dps and ctx.dps_balance > 0:
        cap = round(rules["max_loan_pct_of_dps_balance"] * ctx.dps_balance, 2)
        opts.append(EmergencyOption(
            "dps_loan", None, min(cap, ctx.dps_balance),
            f"তোমার DPS-এ জমা আছে ৳{bn_num(ctx.dps_balance)}। ব্যাংকের নিয়মে এর বিপরীতে সর্বোচ্চ "
            f"৳{bn_num(cap)} পর্যন্ত চাওয়া যায়।",
            _affordability(ctx, models, min(amount, cap))))
    return EmergencyResult(amount=amount, options=opts, note_bn=rules["decision_note_bn"])
