from datetime import date, timedelta

from helpers import hand_ctx, tx_row
from hishab.engine.recurring import detect_recurring
from hishab.engine.shortcuts import recent_payments

TODAY = date(2026, 9, 18)


def _ctx():
    rows = []
    for m in range(1, 5):  # electricity bill on the 21st of each past month -> due in 3 days
        d = date(2026, 9 - m, 21)
        rows.append(tx_row(d, "bill_pay", 600, -1, category="utilities", cp="BILL-electric", cp_type="biller"))
    for k, cp in enumerate(["M-001", "M-002", "M-003", "M-004", "M-001", "M-005"]):
        rows.append(tx_row(TODAY - timedelta(days=k + 1), "merchant_pay", 200 + k, -1, category="food_grocery", cp=cp))
    rows.append(tx_row(TODAY - timedelta(days=2), "salary_in", 12000, 1, category="income", cp="EMP"))
    return hand_ctx(rows, TODAY)


def test_due_soon_bill_first():
    ctx = _ctx()
    out = recent_payments(ctx, detect_recurring(ctx.tx, ctx.today))
    assert out[0].counterparty_id == "BILL-electric" and out[0].due_in_days == 3


def test_recent_returns_at_most_4_distinct():
    ctx = _ctx()
    out = recent_payments(ctx, detect_recurring(ctx.tx, ctx.today))
    ids = [s.counterparty_id for s in out]
    assert len(ids) == 4 and len(set(ids)) == 4
    assert "EMP" not in ids  # income is never a payment shortcut
    assert ids[1:] == ["M-001", "M-002", "M-003"]
