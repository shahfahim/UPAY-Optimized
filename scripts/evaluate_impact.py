"""Part 2 of the evaluation (imported by evaluate.py): E6, E15, E16, E8, E9, impact simulation and fairness."""

from __future__ import annotations

from collections import defaultdict
from datetime import date, timedelta

import numpy as np
import pandas as pd
from sklearn.metrics import average_precision_score

from hishab.data.generator import inactivity_hazard
from hishab.data.labels import income_mask
from hishab.data.splits import TEST_START
from hishab.engine.actions import TRANSFORMS, rank_actions
from hishab.engine.bandit import Bandit
from hishab.engine.category import suggest_category
from hishab.engine.context import ctx_from_history
from hishab.engine.dps import dps_advice
from hishab.engine.eid import last_eid_spend
from hishab.engine.health import indicators, pocket_total_from_history
from hishab.engine.readiness import readiness
from hishab.engine.recurring import detect_recurring
from hishab.engine.replay import month_flows, replay_month
from hishab.engine.risk import RISK_FEATURES, risk_frame
from hishab.engine.shortcuts import PAYMENT_TYPES, recent_payments

MONTHS = [(date(2026, 8, 1), date(2026, 8, 31)), (date(2026, 9, 1), date(2026, 9, 30))]
GROUPS = ["persona", "gender", "area"]


def _users(data) -> dict:
    return {r["user_id"]: r for r in data.users.to_dict("records")}


def _tx_by(data) -> dict:
    return {u: g.sort_values("ts", kind="stable") for u, g in data.transactions.groupby("user_id", sort=False)}


def _active_through(user: dict, d: date) -> bool:
    stop = user.get("inactive_from")
    return stop is None or pd.isna(stop) or stop > d


# --- E6 category ------------------------------------------------------------------------------------

def eval_e6(data, train_ids, test_ids) -> dict:
    users, tx_by = _users(data), _tx_by(data)
    pay_types = ["merchant_pay", "bill_pay", "mobile_recharge", "send_money", "cash_out"]
    train_tx = data.transactions[data.transactions.user_id.isin(set(train_ids))]
    tr = train_tx[(train_tx.direction == -1) & train_tx.type.isin(pay_types)]
    majority = tr.groupby("counterparty_type")["category"].agg(lambda s: s.value_counts().idxmax()).to_dict()
    top1 = top3 = base = n = 0
    for uid in test_ids:
        t = tx_by[uid]
        ctx = ctx_from_history(users[uid], t, TEST_START - timedelta(days=1))
        d = pd.to_datetime(t.ts).dt.date
        test = t[(d >= TEST_START) & (t.direction == -1) & t.type.isin(pay_types)]
        for r in test.itertuples(index=False):
            preds = [c for c, _ in suggest_category(ctx, r.counterparty_id, r.counterparty_type, r.amount, {})]
            top1 += preds[0] == r.category
            top3 += r.category in preds
            base += majority.get(r.counterparty_type, "other") == r.category
            n += 1
    return {"n_payments": n, "top1_accuracy": round(top1 / n, 3), "top3_accuracy": round(top3 / n, 3),
            "baseline_majority_top1": round(base / n, 3)}


# --- E15 recent payments ------------------------------------------------------------------------------

def eval_e15(data, test_ids) -> dict:
    users, tx_by = _users(data), _tx_by(data)
    hits = base_hits = n = 0
    for uid in test_ids:
        t = tx_by[uid]
        d = pd.to_datetime(t.ts).dt.date
        pays = t[t.type.isin(PAYMENT_TYPES) & (t.direction == -1)]
        pd_dates = pd.to_datetime(pays.ts).dt.date
        for k in range(8):
            o = TEST_START + timedelta(days=7 * k)
            nxt = pays[pd_dates > o]
            if nxt.empty or not _active_through(users[uid], o):
                continue
            ctx = ctx_from_history(users[uid], t, o)
            target = nxt.iloc[0].counterparty_id
            shown = [s.counterparty_id for s in recent_payments(ctx, detect_recurring(ctx.tx, o))]
            recency = [s.counterparty_id for s in recent_payments(ctx, [])]
            hits += target in shown
            base_hits += target in recency
            n += 1
    return {"n_obs": n, "hit_rate": round(hits / n, 3), "baseline_recency_hit_rate": round(base_hits / n, 3)}


# --- E16 Smart DPS backtest -----------------------------------------------------------------------------

def _missed_rate(flows: pd.DataFrame, start_balance: float, amount: float, day: int, months) -> tuple[int, int]:
    net = (flows.assign(net=flows.amount - flows.fee).groupby("date")["net"].sum())
    bal, missed, attempts = start_balance, 0, 0
    d = months[0][0]
    while d <= months[-1][1]:
        bal += float(net.get(d, 0.0))
        if d.day == day:
            attempts += 1
            if bal >= amount:
                bal -= amount
            else:
                missed += 1
        d += timedelta(days=1)
    return missed, attempts


def eval_e16(data, models) -> dict:
    users, tx_by = _users(data), _tx_by(data)
    holders = [u for u, r in users.items() if (r.get("dps_monthly") or 0) > 0 and _active_through(r, MONTHS[-1][1])]
    sm = sa = nm = na = not_now = 0
    smart_amounts, naive_amounts = [], []
    for uid in holders:
        t = tx_by[uid]
        ctx = ctx_from_history(users[uid], t, TEST_START - timedelta(days=1))
        if ctx.tx.empty:
            continue
        adv = dps_advice(ctx, models)
        d = pd.to_datetime(t.ts).dt.date
        month_tx = t[(d >= MONTHS[0][0]) & (d <= MONTHS[-1][1])]
        flows = month_flows(month_tx)
        flows = flows[~flows.type.isin(["dps_installment", "dps_installment_missed"])]
        m, a = _missed_rate(flows, ctx.balance, adv.naive_monthly, adv.day or 10, MONTHS)
        nm, na = nm + m, na + a
        naive_amounts.append(adv.naive_monthly)
        if adv.status != "ok":
            not_now += 1
            continue
        m, a = _missed_rate(flows, ctx.balance, adv.safe_monthly, adv.day, MONTHS)
        sm, sa = sm + m, sa + a
        smart_amounts.append(adv.safe_monthly)
    return {"n_dps_holders": len(holders), "smart_missed_rate": round(sm / max(1, sa), 3),
            "naive_10pct_missed_rate": round(nm / max(1, na), 3),
            "smart_avg_monthly": round(float(np.mean(smart_amounts)), 0) if smart_amounts else None,
            "naive_avg_monthly": round(float(np.mean(naive_amounts)), 0) if naive_amounts else None,
            "not_now_share": round(not_now / max(1, len(holders)), 3)}


# --- E8 Eid ---------------------------------------------------------------------------------------------

def eval_e8(data, test_ids) -> dict:
    users, tx_by = _users(data), _tx_by(data)
    prev_eid, eid = date(2026, 3, 20), date(2026, 5, 27)
    preds, actuals = [], []
    for uid in test_ids:
        if not _active_through(users[uid], eid):
            continue
        t = tx_by[uid]
        d = pd.to_datetime(t.ts).dt.date
        preds.append(last_eid_spend(t[d < eid - timedelta(days=30)], prev_eid))
        actuals.append(last_eid_spend(t, eid))
    preds, actuals = np.array(preds), np.array(actuals)
    return {"n_users": int(len(preds)), "mae": round(float(np.mean(np.abs(preds - actuals))), 0),
            "baseline_global_mean_mae": round(float(np.mean(np.abs(actuals.mean() - actuals))), 0),
            "mean_actual_eid_spend": round(float(actuals.mean()), 0)}


# --- E9 bandit replay -----------------------------------------------------------------------------------

def bandit_replay(data, test_ids, items: list[str], days: int = 60, seed: int = 7) -> dict:
    users = _users(data)
    truth = {(r.persona, r.item_id): r.p_accept for r in data.acceptance_truth.itertuples(index=False)}
    personas = [users[u]["persona"] for u in test_ids]
    rng = np.random.default_rng(seed)
    curves = {}
    for policy in ["bandit", "static", "random"]:
        post = defaultdict(lambda: [1.0, 1.0])
        acc_total, shown_total, curve = 0, 0, []
        for day in range(days):
            for persona in personas:
                if policy == "bandit":
                    item = max(items, key=lambda i: rng.beta(*post[(persona, i)]))
                elif policy == "static":
                    item = items[0]
                else:
                    item = items[int(rng.integers(0, len(items)))]
                acc = rng.random() < truth.get((persona, item), 0.2)
                post[(persona, item)][0 if acc else 1] += 1
                acc_total += acc
                shown_total += 1
            curve.append(round(acc_total / shown_total, 4))
        curves[policy] = curve
    curves["day"] = list(range(1, days + 1))
    return curves


# --- impact simulation (spec §11.2) and fairness ----------------------------------------------------------

def _hazard_feats(flows: pd.DataFrame, pockets: float) -> dict:
    out = flows[(flows.amount < 0) & (flows.kind != "internal")]
    total = -float(out.amount.sum()) or 1.0
    cash = -float(out[out.type == "cash_out"].amount.sum())
    return {"depletion_days": 10, "cashout_share": cash / total, "other_wallet_share": 0.0,
            "pocket_total": pockets, "session_trend": 0.0}


def impact(data, models, test_ids, seed: int = 11) -> dict:
    users, tx_by = _users(data), _tx_by(data)
    truth = {(r.persona, r.item_id): r.p_accept for r in data.acceptance_truth.itertuples(index=False)}
    bandit = Bandit.from_dict(models.bandit_priors) if models.bandit_priors else None
    rng = np.random.default_rng(seed)
    rows = []
    survive = {"baseline": [], "with_hishab": []}
    for uid in test_ids:
        u, t = users[uid], tx_by[uid]
        d = pd.to_datetime(t.ts).dt.date
        s_base = s_with = 1.0
        for start, end in MONTHS:
            if not _active_through(u, end):
                break
            ctx = ctx_from_history(u, t, start - timedelta(days=1))
            if ctx.insufficient_history:
                continue
            month_tx = t[(d >= start) & (d <= end)]
            pockets0 = pocket_total_from_history(ctx.tx, ctx.today)
            base = replay_month(month_tx, ctx.balance, pockets0, [], start, end)
            cards = rank_actions(ctx, models, bandit=bandit, k=3, rng=rng)
            accepted = [c for c in cards if rng.random() < truth.get((u["persona"], c.id), 0.2)]
            trs = [TRANSFORMS[c.id](c.params) for c in accepted]
            withh = replay_month(month_tx, ctx.balance, pockets0, trs, start, end)
            flows = month_flows(month_tx)
            flows_with = flows
            for tr in trs:
                flows_with = tr(flows_with.copy(), ctx)
            s_base *= 1 - inactivity_hazard(_hazard_feats(flows, base.end_pockets))
            s_with *= 1 - inactivity_hazard(_hazard_feats(flows_with, withh.end_pockets))
            rows.append({"user_id": uid, "persona": u["persona"], "gender": u["gender"], "area": u["area"],
                         "accepted": len(accepted), **{f"b_{k}": v for k, v in base.__dict__.items()},
                         **{f"w_{k}": v for k, v in withh.__dict__.items()}})
        survive["baseline"].append(s_base)
        survive["with_hishab"].append(s_with)
    df = pd.DataFrame(rows)

    def pair(col, how="mean"):
        b, w = df[f"b_{col}"].dropna(), df[f"w_{col}"].dropna()
        return {"baseline": round(float(b.mean()), 3), "with_hishab": round(float(w.mean()), 3)}

    headline = {
        "emergency_days": pair("emergency_days"),
        "cash_dependency": pair("cash_dependency"),
        "shortfall_free_months": {"baseline": round(float((df.b_shortfall_days == 0).mean()), 3),
                                  "with_hishab": round(float((df.w_shortfall_days == 0).mean()), 3)},
        "shortfall_days_per_user_month": pair("shortfall_days"),
        "fees_per_user_month": pair("fees"),
        "salary_retained_d10": pair("salary_retained_d10"),
    }
    sd_avoided = headline["shortfall_days_per_user_month"]["baseline"] - headline["shortfall_days_per_user_month"]["with_hishab"]
    fees_saved = headline["fees_per_user_month"]["baseline"] - headline["fees_per_user_month"]["with_hishab"]
    per_100k = {"shortfall_days_avoided_per_month": round(sd_avoided * 100_000), "fees_saved_per_month_bdt":
                round(fees_saved * 100_000), "note": "Linear extrapolation of the per-user-month simulation."}
    active = {k: round(float(np.mean(v)), 4) for k, v in survive.items()}
    group_rows = []
    for g in GROUPS:
        for val, sub in df.groupby(g):
            group_rows.append({"group_type": g, "group": str(val), "metric": "shortfall_days_reduction",
                               "value": round(float(sub.b_shortfall_days.mean() - sub.w_shortfall_days.mean()), 3),
                               "n": int(len(sub))})
    return {"headline": headline, "per_100k": per_100k, "active_rate": active, "user_months": int(len(df)),
            "acceptance_mean": round(float(df.accepted.mean()), 2), "group_rows": group_rows}


def fairness(data, models, test_ids, impact_rows: list) -> dict:
    obs = sorted(o for o in data.labels["obs_date"].unique() if o >= TEST_START)
    fr = risk_frame(data, obs, test_ids)
    fr = fr.assign(p=models.risk.predict_proba(fr[RISK_FEATURES]), y=fr.shortfall_14d.astype(int))
    rows = list(impact_rows)
    for g in GROUPS:
        for val, sub in fr.groupby(g):
            if len(sub) < 30 or sub.y.sum() == 0:
                continue
            alert = sub.p >= 0.30
            rec = float((alert & (sub.y == 1)).sum() / sub.y.sum())
            prec = float((alert & (sub.y == 1)).sum() / max(1, alert.sum()))
            rows.append({"group_type": g, "group": str(val), "metric": "recall_at_alert", "value": round(rec, 3),
                         "n": int(len(sub))})
            rows.append({"group_type": g, "group": str(val), "metric": "precision_at_alert", "value": round(prec, 3),
                         "n": int(len(sub))})
    flags = []
    df = pd.DataFrame(rows)
    for (g, m), sub in df[df.n >= 30].groupby(["group_type", "metric"]):
        if m == "shortfall_days_reduction":
            continue
        gap = float(sub.value.max() - sub.value.min())
        if gap > 0.10:
            flags.append({"group_type": g, "metric": m, "gap": round(gap, 3),
                          "note": "Gap above 10 pp: review before any real-world use."})
    return {"rows": rows, "flags": flags}


def readiness_distribution(data, test_ids, as_of: date) -> list:
    users, tx_by = _users(data), _tx_by(data)
    recs = []
    for uid in test_ids:
        u = users[uid]
        if not _active_through(u, as_of):
            continue
        ctx = ctx_from_history(u, tx_by[uid], as_of)
        r = readiness(ctx, indicators(ctx))
        for s in r.signals:
            recs.append({"persona": u["persona"], "gender": u["gender"], "area": u["area"], "signal": s.id,
                         "green": s.state == "green"})
    df = pd.DataFrame(recs)
    out = []
    for g in GROUPS:
        for (val, sig), sub in df.groupby([g, "signal"]):
            out.append({"group_type": g, "group": str(val), "signal": sig, "green_share": round(float(sub.green.mean()), 3),
                        "n": int(len(sub))})
    return out
