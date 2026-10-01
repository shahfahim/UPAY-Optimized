"""E12 — financial-health indicators (and, from Task 15, habits and the monthly report)."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import date, timedelta

import pandas as pd

from hishab.data.labels import income_mask, shortfall_days
from hishab.rules import load_rules

LIVING = ["food_grocery", "rent", "utilities", "health", "education", "transport", "mobile"]
NON_SPEND = ["pocket_in", "dps_installment", "dps_installment_missed"]


@dataclass
class Indicators:
    emergency_days: float
    cash_dependency: float
    shortfall_free_months: int


def _dates(tx: pd.DataFrame) -> pd.Series:
    return pd.to_datetime(tx["ts"]).dt.date


def living_daily(tx: pd.DataFrame, as_of: date) -> float:
    d = _dates(tx)
    w = tx[(d > as_of - timedelta(days=30)) & (d <= as_of) & (tx["direction"] == -1)
           & tx["category"].isin(LIVING) & ~tx["type"].isin(NON_SPEND)]
    return float(w["amount"].sum()) / 30.0


def pocket_total_from_history(tx: pd.DataFrame, as_of: date) -> float:
    d = _dates(tx)
    t = tx[d <= as_of]
    return float(t.loc[t["type"] == "pocket_in", "amount"].sum() - t.loc[t["type"] == "pocket_out", "amount"].sum())


def indicators(ctx, as_of: date | None = None) -> Indicators:
    as_of = as_of or ctx.today
    tx = ctx.tx[_dates(ctx.tx) <= as_of]
    pockets = float(sum(ctx.state.pockets.values())) if as_of == ctx.today else pocket_total_from_history(tx, as_of)
    daily = living_daily(tx, as_of)
    emergency_days = round(pockets / daily, 1) if daily > 0 else (0.0 if pockets <= 0 else 99.0)
    d = _dates(tx)
    last30 = tx[d > as_of - timedelta(days=30)]
    income30 = float(last30.loc[income_mask(last30), "amount"].sum())
    cash30 = float(last30.loc[last30["type"] == "cash_out", "amount"].sum())
    cash_dep = round(cash30 / income30, 2) if income30 > 0 else 0.0
    threshold = load_rules("guardrails")["shortfall_threshold"]
    free = 0
    for k in range(3):
        lo, hi = as_of - timedelta(days=30 * (k + 1)) + timedelta(days=1), as_of - timedelta(days=30 * k)
        if tx.empty or _dates(tx).min() > lo:
            continue
        if not shortfall_days(tx, lo, hi, threshold):
            free += 1
    return Indicators(emergency_days=min(emergency_days, 99.0), cash_dependency=cash_dep, shortfall_free_months=free)


# --- habits and monthly report (E12) --------------------------------------------------------------------

@dataclass
class HabitInsight:
    id: str
    text_bn: str
    text_en: str
    taka_impact: float


@dataclass
class HealthReport:
    current: Indicators
    previous: Indicators
    trend6: list
    habits: list
    monthly_report: dict


_DAYS_BN = ["সোমবার", "মঙ্গলবার", "বুধবার", "বৃহস্পতিবার", "শুক্রবার", "শনিবার", "রবিবার"]
_DAYS_EN = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
_SPEND_TYPES = ["merchant_pay", "cash_out", "mobile_recharge", "send_money", "bill_pay"]


def _window(tx: pd.DataFrame, today: date, lo: int, hi: int) -> pd.DataFrame:
    d = _dates(tx)
    return tx[(d > today - timedelta(days=hi)) & (d <= today - timedelta(days=lo))]


def mine_habits(ctx, k: int = 5) -> list[HabitInsight]:
    from hishab.engine.features import user_features
    from hishab.engine.text import bn_num, category_bn

    out: list[HabitInsight] = []
    if ctx.tx.empty:
        return out
    f = user_features(ctx)
    last30 = _window(ctx.tx, ctx.today, 0, 30)

    if f["income_amount"] > 0 and f["days_to_income"] > 1 and f["depletion_days"] < 7:
        d = int(f["depletion_days"])
        out.append(HabitInsight("fast_depletion", f"বেতনের {bn_num(d)} দিনের মধ্যেই অর্ধেক টাকা বেরিয়ে যায়",
                                f"Half your salary is gone within {d} days", round(0.5 * f["income_amount"], 0)))

    co = last30[last30["type"] == "cash_out"]
    if len(co) >= 2 and co["fee"].sum() > 0:
        n, fee = len(co), float(co["fee"].sum())
        out.append(HabitInsight("cashout_fees", f"মাসে {bn_num(n)} বার cash-out — fee ৳{bn_num(fee)}",
                                f"{n} cash-outs a month — ৳{round(fee):,} in fees", round(fee, 0)))

    spend60 = _window(ctx.tx, ctx.today, 0, 60)
    spend60 = spend60[(spend60["direction"] == -1) & spend60["type"].isin(_SPEND_TYPES)
                      & ~spend60["category"].isin(["rent", "family_support"])]
    if not spend60.empty:
        by_dow = spend60.groupby(pd.to_datetime(spend60["ts"]).dt.weekday)["amount"].sum()
        avg = float(by_dow.sum()) / 7.0
        top = int(by_dow.idxmax())
        if avg > 0 and by_dow.max() > 1.5 * avg:
            excess = (float(by_dow.max()) - avg) / 2.0  # per month (60-day window)
            out.append(HabitInsight("weekday_spike", f"{_DAYS_BN[top]}ে খরচ বেশি হয়", f"You spend more on {_DAYS_EN[top]}s",
                                    round(excess, 0)))

    spend = ctx.tx[(ctx.tx["direction"] == -1) & ctx.tx["type"].isin(_SPEND_TYPES)]
    best = None
    for cat in ["shopping", "festival", "transport", "mobile", "food_grocery", "other"]:
        def cat_sum(lo: int, hi: int, c: str = cat) -> float:
            w = _window(spend, ctx.today, lo, hi)
            return float(w.loc[w["category"] == c, "amount"].sum())

        cur = cat_sum(0, 30)
        prev = [cat_sum(30 * i, 30 * (i + 1)) for i in (1, 2, 3)]
        mean, sd = float(sum(prev) / 3), float(pd.Series(prev).std(ddof=0))
        if cur > 300 and cur > mean and (sd == 0 or (cur - mean) / sd > 2) and (best is None or cur - mean > best[1]):
            best = (cat, cur - mean)
    if best:
        out.append(HabitInsight("category_spike", f"এই মাসে {category_bn(best[0])} খরচ স্বাভাবিকের চেয়ে বেশি",
                                f"{best[0].replace('_', ' ').capitalize()} spending is above your usual this month",
                                round(best[1], 0)))

    if sum(ctx.state.pockets.values()) <= 0:
        out.append(HabitInsight("no_savings", "এখন কোনো জমানো টাকা নেই — হঠাৎ খরচে চাপ পড়ে",
                                "No savings right now — sudden costs hit hard", 0.0))
    out.sort(key=lambda h: h.taka_impact, reverse=True)
    return out[:k]


def monthly_report(ctx) -> dict:
    from hishab.engine.text import bn_num
    cur = _window(ctx.tx, ctx.today, 0, 30)
    prev = _window(ctx.tx, ctx.today, 30, 60)
    fee_cur = float(cur.loc[cur["type"] == "cash_out", "fee"].sum())
    fee_prev = float(prev.loc[prev["type"] == "cash_out", "fee"].sum())
    saved = max(0.0, fee_prev - fee_cur)
    threshold = load_rules("guardrails")["shortfall_threshold"]
    short = shortfall_days(ctx.tx, ctx.today - timedelta(days=29), ctx.today, threshold) if not ctx.tx.empty else []
    went_well = (f"গত মাসের চেয়ে cash-out fee ৳{bn_num(saved)} কম দিয়েছ।" if saved > 0
                 else ("এই মাসে টাকা কম পড়েনি।" if not short else "নিয়মিত লেনদেন চালিয়ে যাচ্ছ।"))
    change = ("বেতনের দিন কিছু টাকা আলাদা রাখলে মাসের শেষে চাপ কমবে।" if short
              else "পয়সা-সঞ্চয় চালু রাখলে সঞ্চয়ের অভ্যাস তৈরি হবে।")
    return {"went_well_bn": went_well, "change_bn": change, "fees_saved": round(saved, 0),
            "shortfall_avoided": not short}


def health_report(ctx) -> HealthReport:
    trend = [indicators(ctx, ctx.today - timedelta(days=30 * k)) for k in range(5, -1, -1)]
    return HealthReport(current=trend[-1], previous=trend[-2], trend6=trend, habits=mine_habits(ctx),
                        monthly_report=monthly_report(ctx))
