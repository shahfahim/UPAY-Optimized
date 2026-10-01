"""E5 — action optimizer: candidate actions → what-if on future flows → re-scored risk → ranked cards.

Conditions mirror spec §4.2. Copy lives in rules/actions.yaml; guardrails in rules/guardrails.yaml.
"""

from __future__ import annotations

from dataclasses import asdict, dataclass, field
from datetime import date, timedelta
from typing import Callable

import numpy as np
import pandas as pd

from hishab.engine.features import user_features
from hishab.engine.forecast import Transform, band_from_flows, future_flows
from hishab.engine.recurring import RecurringEvent, detect_recurring
from hishab.engine.risk import RiskResult, score
from hishab.engine.text import bn_num, category_bn
from hishab.rules import contains_forbidden, load_rules

COMMITMENT_EFFECT = 0.5  # assumed share of a payday reserve that would otherwise have been spent early


@dataclass
class ActionCard:
    id: str
    title_bn: str
    title_en: str
    why_bn: str
    why_en: str
    params: dict = field(default_factory=dict)
    risk_before: float = 0.0
    risk_after: float = 0.0
    fees_saved: float = 0.0
    score: float = 0.0


def _catalog() -> dict:
    return {a["id"]: a for a in load_rules("actions")["actions"]}


def _edge(frm: str, to: str) -> dict:
    return next(e for e in load_rules("fees")["edges"] if e["from"] == frm and e["to"] == to)


def _fee(frm: str, to: str, amount: float) -> float:
    e = _edge(frm, to)
    return round(min(max(e["fixed"] + e["pct"] / 100.0 * amount, e["min"]), e["max"]), 2)


def _row(d: date, amount: float, category: str, typ: str) -> dict:
    return {"date": d, "amount": round(amount, 2), "category": category, "type": typ, "fee": 0.0, "kind": "action"}


def _add(flows: pd.DataFrame, rows: list[dict]) -> pd.DataFrame:
    return pd.concat([flows, pd.DataFrame(rows)], ignore_index=True) if rows else flows


def _next_15th(d: date) -> date:
    if d.day < 15:
        return d.replace(day=15)
    nm = (d.replace(day=28) + timedelta(days=4)).replace(day=15)
    return nm


# --- transforms -------------------------------------------------------------------------------------

def _t_save_on_payday(p: dict) -> Transform:
    amount, payday = float(p["amount"]), date.fromisoformat(p["payday"])

    def tr(flows: pd.DataFrame, ctx) -> pd.DataFrame:
        release = payday + timedelta(days=15)
        disc = (flows["kind"] == "discretionary") & (flows["amount"] < 0) & \
               (flows["date"] >= payday) & (flows["date"] < release)
        total = -float(flows.loc[disc, "amount"].sum())
        if total > 0:
            factor = max(0.0, 1 - COMMITMENT_EFFECT * amount / total)
            flows.loc[disc, "amount"] = flows.loc[disc, "amount"] * factor
        return _add(flows, [_row(payday, -amount, "other", "pocket_in"), _row(release, amount, "other", "pocket_out")])
    return tr


def _t_split_remittance(p: dict) -> Transform:
    d = date.fromisoformat(p["date"])

    def tr(flows: pd.DataFrame, ctx) -> pd.DataFrame:
        m = (flows["kind"] == "recurring") & (flows["category"] == "family_support") & (flows["date"] == d)
        if not m.any():
            return flows
        half = flows.loc[m, "amount"].sum() / 2.0
        fee_half = flows.loc[m, "fee"].sum() / 2.0
        flows.loc[m, "amount"] = flows.loc[m, "amount"] / 2.0
        flows.loc[m, "fee"] = flows.loc[m, "fee"] / 2.0
        r = _row(_next_15th(d), half, "family_support", "send_money")
        r["fee"] = fee_half
        r["kind"] = "recurring"
        return _add(flows, [r])
    return tr


def _t_digital_pay(p: dict) -> Transform:
    share = float(p.get("saving_share", 0.0))

    def tr(flows: pd.DataFrame, ctx) -> pd.DataFrame:
        m = (flows["kind"] == "discretionary") & (flows["amount"] < 0)
        flows.loc[m, "amount"] = flows.loc[m, "amount"] * (1 - share)
        return flows
    return tr


def _t_cheaper_route(p: dict) -> Transform:
    def tr(flows: pd.DataFrame, ctx) -> pd.DataFrame:
        m = (flows["kind"] == "recurring") & (flows["category"] == "family_support") & (flows["type"] == "cash_out")
        for i in flows.index[m]:
            flows.at[i, "fee"] = _fee("upay_wallet", "npsb", -float(flows.at[i, "amount"]))
            flows.at[i, "type"] = "send_money"
        return flows
    return tr


def _t_identity(p: dict) -> Transform:
    return lambda flows, ctx: flows


def _t_trim(p: dict) -> Transform:
    cat = p["category"]

    def tr(flows: pd.DataFrame, ctx) -> pd.DataFrame:
        m = (flows["kind"] == "discretionary") & (flows["category"] == cat) & (flows["amount"] < 0)
        flows.loc[m, "amount"] = flows.loc[m, "amount"] * 0.9
        return flows
    return tr


def _t_dps(p: dict) -> Transform:
    amount, day = float(p["amount"]), int(p["day"])

    def tr(flows: pd.DataFrame, ctx) -> pd.DataFrame:
        from hishab.engine.recurring import _next_on_day
        rows, d = [], _next_on_day(ctx.today, day)
        end = ctx.today + timedelta(days=int(p.get("horizon", 30)))
        while d <= end:
            rows.append(_row(d, -amount, "other", "dps_installment"))
            d = _next_on_day(d, day)
        return _add(flows, rows)
    return tr


def _t_daily_limit(p: dict) -> Transform:
    limit, until = float(p["amount"]), date.fromisoformat(p["until"])

    def tr(flows: pd.DataFrame, ctx) -> pd.DataFrame:
        m = (flows["kind"] == "discretionary") & (flows["amount"] < 0) & (flows["date"] < until)
        day_tot = -flows.loc[m].groupby("date")["amount"].sum()
        for d, tot in day_tot.items():
            if tot > limit > 0:
                dm = m & (flows["date"] == d)
                flows.loc[dm, "amount"] = flows.loc[dm, "amount"] * (limit / tot)
        return flows
    return tr


def _t_eid(p: dict) -> Transform:
    weekly = float(p["amount"])

    def tr(flows: pd.DataFrame, ctx) -> pd.DataFrame:
        rows = [_row(ctx.today + timedelta(days=k), -weekly, "festival", "pocket_in") for k in range(7, 31, 7)]
        return _add(flows, rows)
    return tr


TRANSFORMS: dict[str, Callable[[dict], Transform]] = {
    "save_on_payday": _t_save_on_payday,
    "split_remittance": _t_split_remittance,
    "digital_pay_instead_of_cashout": _t_digital_pay,
    "cheaper_route": _t_cheaper_route,
    "pause_paisa_saving": _t_identity,
    "trim_discretionary": _t_trim,
    "dps_ready": _t_dps,
    "eid_weekly_saving": _t_eid,
    "daily_limit": _t_daily_limit,
}


# --- candidates -------------------------------------------------------------------------------------

def _window(tx: pd.DataFrame, today: date, lo_days: int, hi_days: int) -> pd.DataFrame:
    ts = pd.to_datetime(tx["ts"]).dt.date
    return tx[(ts > today - timedelta(days=hi_days)) & (ts <= today - timedelta(days=lo_days))]


def cash_remittance_saving(recurring: list[RecurringEvent]) -> tuple[float, RecurringEvent | None]:
    """Monthly fee saved by sending a cash-out remittance through NPSB instead."""
    for e in recurring:
        if e.kind == "remittance" and e.tx_type == "cash_out":
            saving = _fee("upay_wallet", "agent_cash", e.amount) - _fee("upay_wallet", "npsb", e.amount)
            if saving > 0:
                return round(saving, 2), e
    return 0.0, None


def candidate_actions(ctx, feats: dict, risk: RiskResult, recurring: list[RecurringEvent], fc,
                      extras: dict | None = None) -> list[tuple[str, dict]]:
    extras = extras or {}
    out: list[tuple[str, dict]] = []
    salary = [e for e in recurring if e.kind == "salary"]
    remit = [e for e in recurring if e.kind == "remittance"]
    risk_hi = risk.level in ("amber", "red")

    if salary and (risk_hi or feats.get("shortfall_days_90d", 0) > 0):
        s = salary[0]
        x = min(0.10 * s.amount, fc.shortfall_amount) if fc.shortfall_amount > 0 else 0.05 * s.amount
        out.append(("save_on_payday", {"amount": float(max(100, round(x, -2))), "payday": s.next_date.isoformat()}))

    base_income = salary[0].amount if salary else feats.get("income_amount", 0.0)
    for r in remit:
        if base_income > 0 and r.amount >= 0.25 * base_income:
            out.append(("split_remittance", {"date": r.next_date.isoformat(), "amount": r.amount}))
            break

    last30 = _window(ctx.tx, ctx.today, 0, 30)
    co = last30[(last30["type"] == "cash_out") & (last30["category"] != "family_support")]
    disc_out = float(last30[(last30["direction"] == -1) & last30["type"].isin(
        ["merchant_pay", "cash_out", "mobile_recharge"]) & (last30["category"] != "family_support")]
        [["amount", "fee"]].sum().sum())
    if len(co) >= 3 and disc_out > 0:
        fee = round(float(co["fee"].sum()), 0)
        if fee > 0:
            out.append(("digital_pay_instead_of_cashout", {"fee": fee, "monthly_saving": fee,
                                                           "saving_share": fee / disc_out}))

    saving, ev = cash_remittance_saving(recurring)
    if ev is not None:
        out.append(("cheaper_route", {"monthly_saving": saving, "fee": round(saving * 12, 0),
                                      "date": ev.next_date.isoformat()}))

    if ctx.state.paisa_on and risk_hi:
        out.append(("pause_paisa_saving", {}))

    trimmable = set(load_rules("guardrails")["trimmable"])
    spend = ctx.tx[(ctx.tx["direction"] == -1) & ctx.tx["type"].isin(["merchant_pay", "cash_out", "mobile_recharge"])]
    best = None
    def cat_sum(lo: int, hi: int, cat: str) -> float:
        w = _window(spend, ctx.today, lo, hi)
        return float(w.loc[w["category"] == cat, "amount"].sum())

    for cat in sorted(trimmable):
        cur = cat_sum(0, 30, cat)
        prev = [cat_sum(30 * k, 30 * (k + 1), cat) for k in (1, 2, 3)]
        med = float(np.median(prev))
        if cur >= 300 and med > 0 and cur > 1.2 * med and (best is None or cur - med > best[1]):
            best = (cat, cur - med, cur)
    if best:
        out.append(("trim_discretionary", {"category": best[0], "amount": float(round(0.1 * best[2], -1))}))

    if risk_hi:
        from hishab.engine.recurring import next_income
        from hishab.engine.safe_spend import daily_budget
        limit = daily_budget(ctx, recurring)
        nxt = next_income(recurring, ctx.today) or ctx.today + timedelta(days=7)
        f = fc.flows
        disc = f[(f["kind"] == "discretionary") & (f["amount"] < 0) & (f["date"] < nxt)]
        avg = -float(disc.groupby("date")["amount"].sum().mean()) if not disc.empty else 0.0
        if limit >= 50 and avg > 0 and limit < 0.95 * avg:
            out.append(("daily_limit", {"amount": float(round(limit, -1)), "until": nxt.isoformat()}))

    dps = extras.get("dps")
    if dps is not None and getattr(dps, "status", None) == "ok" and risk.level == "green" and not ctx.state.dps:
        out.append(("dps_ready", {"amount": float(dps.safe_monthly), "day": int(dps.day)}))
    eid = extras.get("eid")
    if eid is not None and eid.days_left <= 120 and eid.need > 0:
        out.append(("eid_weekly_saving", {"amount": float(eid.weekly), "days": int(eid.days_left)}))
    return out


# --- cards ------------------------------------------------------------------------------------------

def _fill(template: str, params: dict, lang: str) -> str:
    num = bn_num if lang == "bn" else (lambda v: f"{round(v):,}")
    vals = {}
    for k in ("amount", "fee", "days"):
        if k in params:
            vals[k] = num(params[k])
    if "category" in params:
        vals["category_bn"] = category_bn(params["category"])
        vals["category_en"] = params["category"].replace("_", " ")
    try:
        return template.format(**vals)
    except KeyError:
        return template


def make_card(action_id: str, params: dict, risk_before: float, risk_after: float, fees_saved: float,
              score_: float) -> ActionCard:
    a = _catalog()[action_id]
    return ActionCard(id=action_id, title_bn=_fill(a["title_bn"], params, "bn"),
                      title_en=_fill(a["title_en"], params, "en"), why_bn=_fill(a["why_bn"], params, "bn"),
                      why_en=_fill(a["why_en"], params, "en"), params=params,
                      risk_before=round(risk_before, 4), risk_after=round(risk_after, 4),
                      fees_saved=round(fees_saved, 0), score=round(score_, 3))


def violates_guardrails(card: ActionCard) -> bool:
    text = " ".join([card.title_bn, card.title_en, card.why_bn, card.why_en])
    if contains_forbidden(text):
        return True
    if card.id == "trim_discretionary" and card.params.get("category") not in set(load_rules("guardrails")["trimmable"]):
        return True
    return False


def _evaluate(ctx, models, flows, fc, risk, action_id, params):
    fc2 = band_from_flows(ctx, models, flows, [TRANSFORMS[action_id](params)])
    r2 = score(ctx, fc2, models, base_fc=fc)
    return fc2, r2


def rank_actions(ctx, models, bandit=None, k: int | None = None, extras: dict | None = None,
                 responses: list | None = None, rng=None) -> list[ActionCard]:
    k = k or load_rules("guardrails")["max_action_cards"]
    rng = rng or np.random.default_rng()
    recurring = detect_recurring(ctx.tx, ctx.today)
    flows = future_flows(ctx, models.forecaster, 30, recurring)
    fc = band_from_flows(ctx, models, flows)
    risk = score(ctx, fc, models)
    feats = user_features(ctx)
    cards = []
    for action_id, params in candidate_actions(ctx, feats, risk, recurring, fc, extras):
        fc2, r2 = _evaluate(ctx, models, flows, fc, risk, action_id, params)
        fees = float(params.get("monthly_saving", 0.0))
        benefit = (max(0.0, risk.prob - r2.prob) * 1000 + fees
                   + 0.1 * max(0.0, min(fc2.p50) - min(fc.p50)) + 1.0)
        p_acc = bandit.sample(ctx.persona, action_id, responses or [], rng) if bandit is not None else 0.5
        card = make_card(action_id, params, risk.prob, r2.prob, fees, benefit * p_acc)
        if not violates_guardrails(card):
            cards.append(card)
    cards.sort(key=lambda c: c.score, reverse=True)
    return cards[:k]


def simulate_action(ctx, models, action_id: str, extras: dict | None = None):
    if action_id not in TRANSFORMS:
        raise ValueError("অজানা পরামর্শ")
    recurring = detect_recurring(ctx.tx, ctx.today)
    flows = future_flows(ctx, models.forecaster, 30, recurring)
    fc = band_from_flows(ctx, models, flows)
    risk = score(ctx, fc, models)
    cands = dict(candidate_actions(ctx, user_features(ctx), risk, recurring, fc, extras))
    if action_id not in cands:
        raise ValueError("এই পরামর্শ এখন প্রযোজ্য নয়")
    return _evaluate(ctx, models, flows, fc, risk, action_id, cands[action_id])


def card_dict(card: ActionCard) -> dict:
    return asdict(card)
