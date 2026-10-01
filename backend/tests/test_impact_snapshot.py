import json

from hishab.config import BACKEND_DIR

KEYS = ["headline", "per_100k", "active_rate", "models", "bandit_curve", "lesson_curve", "fairness",
        "readiness_distribution", "assumptions_note"]
HEADLINE = ["emergency_days", "cash_dependency", "shortfall_free_months", "shortfall_days_per_user_month",
            "fees_per_user_month", "salary_retained_d10"]


def test_snapshot_schema():
    snap = json.loads((BACKEND_DIR / "artifacts" / "impact_snapshot.json").read_text(encoding="utf-8"))
    for k in KEYS:
        assert k in snap, k
    for k in HEADLINE:
        assert {"baseline", "with_hishab"} <= set(snap["headline"][k]), k
    assert {"baseline", "with_hishab"} <= set(snap["active_rate"])
    assert {"day", "bandit", "static", "random"} <= set(snap["bandit_curve"])
    assert {"rows", "flags"} <= set(snap["fairness"])
