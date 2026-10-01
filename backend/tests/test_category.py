from datetime import date, timedelta

from helpers import hand_ctx, tx_row
from hishab.engine.category import suggest_category

TODAY = date(2026, 9, 18)


def _ctx():
    rows = [tx_row(TODAY - timedelta(days=k), "merchant_pay", 300, -1, category="food_grocery", cp="M-001")
            for k in range(1, 8)]
    rows += [tx_row(TODAY - timedelta(days=9), "merchant_pay", 900, -1, category="shopping", cp="M-001")]
    return hand_ctx(rows, TODAY)


def test_confirmed_label_wins():
    out = suggest_category(_ctx(), "M-001", "merchant", 300, {"M-001": "health"})
    assert out[0][0] == "health" and out[0][1] >= 0.9


def test_history_used_when_no_label():
    out = suggest_category(_ctx(), "M-001", "merchant", 300, {})
    assert out[0][0] == "food_grocery"
    assert "shopping" in [c for c, _ in out]


def test_rules_for_unknown_counterparty():
    assert suggest_category(_ctx(), "BILL-recharge", "biller", 100, {})[0][0] == "mobile"
    assert suggest_category(_ctx(), "NEW-P", "person", 5000, {})[0][0] == "family_support"


def test_top3_unique_and_bounded():
    for args in [("M-001", "merchant", 300), ("X", "agent", 2000), ("BILL-electric", "biller", 600)]:
        out = suggest_category(_ctx(), *args, {})
        cats = [c for c, _ in out]
        assert len(cats) == 3 and len(set(cats)) == 3
        assert sum(p for _, p in out) <= 1.0 + 1e-9
