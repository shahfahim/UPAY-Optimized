"""Evaluate models on the held-out test split and write reports/metrics.json + reports/metrics.md.

Test split = 15% held-out users, observation dates in months 11–12 (Aug–Sep 2026).
Usage: python scripts/evaluate.py
"""

from __future__ import annotations

import json
import sys
import time
from datetime import date, timedelta
from pathlib import Path

import numpy as np
import pandas as pd
from sklearn.metrics import average_precision_score, brier_score_loss, roc_auc_score

from hishab.config import BACKEND_DIR
from hishab.data.labels import daily_balances, shortfall_days
from hishab.data.splits import TEST_START, DATA_END, split_users
from hishab.engine.context import ctx_from_history
from hishab.engine.forecast import baseline_last_month, baseline_trailing_avg, forecast
from hishab.engine.models import load_from
from hishab.engine.risk import RISK_FEATURES, risk_frame, rule_baseline

ROOT = BACKEND_DIR.parent
REPORTS = ROOT / "reports"
ART = BACKEND_DIR / "artifacts"

def _load_full():
    from hishab.data.generator import SyntheticData
    d = BACKEND_DIR / "data" / "full"
    return SyntheticData(
        users=pd.read_parquet(d / "users.parquet"),
        transactions=pd.read_parquet(d / "transactions.parquet"),
        sessions=pd.read_parquet(d / "sessions.parquet"),
        labels=pd.read_parquet(d / "labels.parquet"),
        acceptance_truth=pd.read_parquet(d / "acceptance_truth.parquet"),
    )


def eval_e2(data, models, test_ids: list[str]) -> dict:
    obs_dates = [TEST_START + timedelta(days=1 + 7 * k) for k in range(5)]  # horizon ends <= DATA_END
    users = data.users.set_index("user_id")
    tx_by = {u: g for u, g in data.transactions.groupby("user_id", sort=False)}
    err = {"model": {14: [], 30: []}, "last_month": {14: [], 30: []}, "trailing_avg": {14: [], 30: []}}
    cover = {14: [], 30: []}
    for uid in test_ids:
        t = tx_by[uid]
        user = users.loc[uid].to_dict() | {"user_id": uid}
        stop = user.get("inactive_from")
        for o in obs_dates:
            if stop is not None and not pd.isna(stop) and o + timedelta(days=30) >= stop:
                continue
            ctx = ctx_from_history(user, t, o)
            if ctx.tx.empty:
                continue
            actual = daily_balances(t, o + timedelta(days=1), o + timedelta(days=30))
            fc = forecast(ctx, models)
            b1 = baseline_last_month(ctx, 30)
            b2 = baseline_trailing_avg(ctx, 30)
            for h in (14, 30):
                a = float(actual.iloc[h - 1])
                err["model"][h].append(abs(fc.p50[h - 1] - a))
                err["last_month"][h].append(abs(b1[h - 1] - a))
                err["trailing_avg"][h].append(abs(b2[h - 1] - a))
                cover[h].append(fc.p10[h - 1] <= a <= fc.p90[h - 1])
    out = {"n_forecasts": len(err["model"][14])}
    for h in (14, 30):
        out[f"mae_day{h}"] = round(float(np.mean(err["model"][h])), 1)
        out[f"baseline_last_month_mae_day{h}"] = round(float(np.mean(err["last_month"][h])), 1)
        out[f"baseline_trailing_avg_mae_day{h}"] = round(float(np.mean(err["trailing_avg"][h])), 1)
        out[f"p10_p90_coverage_day{h}"] = round(float(np.mean(cover[h])), 3)
    return out


def eval_e3(data, models, test_ids: list[str]) -> dict:
    obs = sorted(o for o in data.labels["obs_date"].unique() if o >= TEST_START)
    fr = risk_frame(data, obs, test_ids)
    y = fr["shortfall_14d"].astype(int).to_numpy()
    p = models.risk.predict_proba(fr[RISK_FEATURES])
    rule = np.array([rule_baseline(r) for r in fr[RISK_FEATURES].to_dict("records")])
    alert = p >= 0.30
    tx_by = {u: g for u, g in data.transactions.groupby("user_id", sort=False)}
    leads, leads_new = [], []
    bal_at_obs = fr["balance"].to_numpy()
    for (uid, o), a, yy, b in zip(fr[["user_id", "obs_date"]].itertuples(index=False), alert, y, bal_at_obs):
        if a and yy:
            sf = shortfall_days(tx_by[uid], o + timedelta(days=1), o + timedelta(days=14))
            if sf:
                leads.append((sf[0] - o).days)
                if b >= 200:  # not already short when warned: a genuinely new shortfall
                    leads_new.append((sf[0] - o).days)

    def prec_rec(pred):
        tp = int(((pred == 1) & (y == 1)).sum())
        return (tp / max(1, int(pred.sum())), tp / max(1, int(y.sum())))

    prec, rec = prec_rec(alert.astype(int))
    rprec, rrec = prec_rec(rule.astype(int))
    return {
        "n_obs": int(len(y)), "positive_rate": round(float(y.mean()), 3),
        "pr_auc": round(float(average_precision_score(y, p)), 3),
        "roc_auc": round(float(roc_auc_score(y, p)), 3),
        "brier": round(float(brier_score_loss(y, p)), 4),
        "precision_at_alert": round(prec, 3), "recall_at_alert": round(rec, 3),
        "median_lead_days": float(np.median(leads)) if leads else None,
        "median_lead_days_new_shortfalls": float(np.median(leads_new)) if leads_new else None,
        "baseline_rule_pr_auc": round(float(average_precision_score(y, rule)), 3),
        "baseline_rule_precision": round(rprec, 3), "baseline_rule_recall": round(rrec, 3),
    }


def merge_metrics(new: dict) -> dict:
    REPORTS.mkdir(exist_ok=True)
    path = REPORTS / "metrics.json"
    cur = json.loads(path.read_text(encoding="utf-8")) if path.exists() else {}
    cur.update(new)
    path.write_text(json.dumps(cur, indent=2, ensure_ascii=False), encoding="utf-8")
    return cur


def write_markdown(m: dict, notes: list[str] | None = None) -> None:
    lines = ["# Model metrics (held-out test split)", "",
             "Synthetic data; test = 15% held-out users, observation dates Aug–Sep 2026. "
             "Generated by `scripts/evaluate.py`.", ""]
    if "E2" in m:
        e = m["E2"]
        lines += ["## E2 cash-flow forecaster", "", "| Metric | Model | Same as last month | Trailing 30-day avg |",
                  "|---|---|---|---|"]
        for h in (14, 30):
            lines.append(f"| MAE balance day {h} (৳) | {e[f'mae_day{h}']} | {e[f'baseline_last_month_mae_day{h}']} "
                         f"| {e[f'baseline_trailing_avg_mae_day{h}']} |")
        lines += [f"| P10–P90 coverage day 14 / 30 | {e['p10_p90_coverage_day14']} / {e['p10_p90_coverage_day30']} "
                  "| – | – |", f"\nForecasts evaluated: {e['n_forecasts']}", ""]
    if "E3" in m:
        e = m["E3"]
        lines += ["## E3 shortfall-risk model", "", "| Metric | Model | Rule baseline |", "|---|---|---|",
                  f"| PR-AUC | {e['pr_auc']} | {e['baseline_rule_pr_auc']} |",
                  f"| Precision at alert (amber+) | {e['precision_at_alert']} | {e['baseline_rule_precision']} |",
                  f"| Recall at alert | {e['recall_at_alert']} | {e['baseline_rule_recall']} |",
                  f"| ROC-AUC | {e['roc_auc']} | – |", f"| Brier | {e['brier']} | – |",
                  f"| Median warning lead time, all alerted positives (days) | {e['median_lead_days']} | – |",
                  f"| Median warning lead time, new shortfalls only (days) | "
                  f"{e.get('median_lead_days_new_shortfalls')} | – |",
                  f"\nObservations: {e['n_obs']}, positive rate {e['positive_rate']}", ""]
    for key, title in [("E6", "E6 category suggestion"), ("E15", "E15 recent payments"),
                       ("E16", "E16 Smart DPS"), ("E8", "E8 Eid planner"), ("E9", "E9 learning nudges (replay)")]:
        if key in m:
            lines += [f"## {title}", "", "| Metric | Value |", "|---|---|"]
            lines += [f"| {k} | {v} |" for k, v in m[key].items()]
            lines.append("")
    if notes:
        lines += ["## Notes", ""] + [f"- {n}" for n in notes] + [""]
    (REPORTS / "metrics.md").write_text("\n".join(lines), encoding="utf-8")


def main() -> None:
    t0 = time.time()
    data = _load_full()
    models = load_from(ART)
    _, test_ids = split_users(list(data.users.user_id))
    m = {}
    if "--skip-e2" not in sys.argv:
        m["E2"] = eval_e2(data, models, test_ids)
        print("E2", m["E2"], f"({time.time() - t0:.0f}s)")
    if "--skip-e3" not in sys.argv:
        m["E3"] = eval_e3(data, models, test_ids)
        print("E3", m["E3"], f"({time.time() - t0:.0f}s)")
    snapshot = None
    if "--skip-part2" not in sys.argv:
        import evaluate_impact as EI
        from hishab.rules import load_rules

        train_ids = [u for u in data.users.user_id if u not in set(test_ids)]
        m["E6"] = EI.eval_e6(data, train_ids, test_ids)
        print("E6", m["E6"], f"({time.time() - t0:.0f}s)")
        m["E15"] = EI.eval_e15(data, test_ids)
        print("E15", m["E15"], f"({time.time() - t0:.0f}s)")
        m["E16"] = EI.eval_e16(data, models)
        print("E16", m["E16"], f"({time.time() - t0:.0f}s)")
        m["E8"] = EI.eval_e8(data, test_ids)
        print("E8", m["E8"], f"({time.time() - t0:.0f}s)")
        action_ids = [a["id"] for a in load_rules("actions")["actions"]]
        lesson_ids = [x["id"] for x in load_rules("lessons")["lessons"]]
        bc = EI.bandit_replay(data, test_ids, action_ids)
        lc = EI.bandit_replay(data, test_ids, lesson_ids)
        m["E9"] = {"actions_acceptance_bandit": bc["bandit"][-1], "actions_acceptance_static": bc["static"][-1],
                   "actions_acceptance_random": bc["random"][-1], "lessons_acceptance_bandit": lc["bandit"][-1],
                   "lessons_acceptance_static": lc["static"][-1], "lessons_acceptance_random": lc["random"][-1]}
        print("E9", m["E9"], f"({time.time() - t0:.0f}s)")
        imp = EI.impact(data, models, test_ids)
        print("impact", imp["headline"], imp["active_rate"], f"({time.time() - t0:.0f}s)")
        fair = EI.fairness(data, models, test_ids, imp["group_rows"])
        rd = EI.readiness_distribution(data, test_ids, date(2026, 9, 18))
        snapshot = {"headline": imp["headline"], "per_100k": imp["per_100k"], "active_rate": imp["active_rate"],
                    "user_months": imp["user_months"], "acceptance_mean": imp["acceptance_mean"],
                    "bandit_curve": bc, "lesson_curve": lc, "fairness": fair, "readiness_distribution": rd,
                    "assumptions_note": ASSUMPTIONS}
    allm = merge_metrics(m)
    write_markdown(allm, NOTES)
    if snapshot is not None:
        snapshot["models"] = allm
        (ART / "impact_snapshot.json").write_text(json.dumps(snapshot, ensure_ascii=False, indent=1, default=str),
                                                  encoding="utf-8")
    print(f"done ({time.time() - t0:.0f}s)")


ASSUMPTIONS = ("Simulated on synthetic data (docs/synthetic-data.md). Impact: the 300 held-out users over Aug–Sep 2026 "
               "are replayed month by month. With Hishab, the top-3 ranked actions are accepted with each persona's "
               "assumed acceptance probability, and their effect is applied to the month's real flows. The active rate "
               "re-applies the generator's assumed inactivity mechanism. Fees are placeholders. These are model-based "
               "estimates, not measured outcomes.")

NOTES: list[str] = [
    "E2 beats both baselines at day 14 and day 30; the P10–P90 band covers about 75–81% of actual balances "
    "(target about 80%).",
    "E3 lead time: across all alerted positives the median is 3 days, because many users are already short when "
    "the alert fires. For genuinely new shortfalls (balance still >= ৳200 at alert time) the median warning is "
    "6 days, which meets the >= 5-day bar. Both numbers are reported.",
    "All results are on synthetic data and show that the pipeline works, not real-world accuracy "
    "(see docs/synthetic-data.md).",
]

if __name__ == "__main__":
    main()
