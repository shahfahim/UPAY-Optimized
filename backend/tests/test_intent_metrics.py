"""The saved intent metrics must come from grouped CV (no typo-variant leakage) and stay above a floor."""
import json
from pathlib import Path

METRICS = Path(__file__).resolve().parents[1] / "artifacts" / "intent_metrics.json"


def test_intent_metrics_are_grouped_and_above_floor():
    m = json.loads(METRICS.read_text(encoding="utf-8"))
    assert "GroupKFold" in m["method"]
    assert m["accuracy"] >= 0.55 and m["macro_f1"] >= 0.45
    assert m["per_class_f1"]["unknown"] >= 0.8
