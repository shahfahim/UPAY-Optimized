from datetime import timedelta

import pytest

from helpers import tx_row, with_extra_tx
from hishab.engine.context import build_ctx
from hishab.engine.emergency import emergency_options
from hishab.rules import contains_forbidden, load_rules


def _with_pockets_and_dps(ctx, dps: bool):
    ctx.state.pockets.update({"emergency": 800.0, "eid": 1500.0})
    if dps:
        ctx.state.dps = {"monthly": 1000, "tenure_months": 24, "day": 8, "opened": "2026-04-01"}
        rows = [tx_row(ctx.today - timedelta(days=30 * k), "dps_installment", 1000, -1, cp="DPS-ISLAMIC")
                for k in range(1, 6)]
        ctx = with_extra_tx(ctx, rows)
    return ctx


def test_emergency_order(repo, store, settings, tiny_models):
    ctx = _with_pockets_and_dps(build_ctx("U0001", repo, store, settings), dps=True)
    kinds = [o.kind for o in emergency_options(ctx, tiny_models, 3000).options]
    assert kinds == ["emergency_pocket", "pocket", "dps_loan"]


def test_no_loan_without_dps(repo, store, settings, tiny_models):
    ctx = _with_pockets_and_dps(build_ctx("U0001", repo, store, settings), dps=False)
    assert "dps_loan" not in [o.kind for o in emergency_options(ctx, tiny_models, 3000).options]


def test_loan_cap_never_exceeds_balance(repo, store, settings, tiny_models):
    ctx = _with_pockets_and_dps(build_ctx("U0001", repo, store, settings), dps=True)
    loan = [o for o in emergency_options(ctx, tiny_models, 100000).options if o.kind == "dps_loan"][0]
    cap = load_rules("emergency")["max_loan_pct_of_dps_balance"]
    assert loan.available == pytest.approx(cap * ctx.dps_balance)
    assert loan.available <= ctx.dps_balance
    assert loan.affordability_bn


def test_eid_pocket_tradeoff_mentions_delay(repo, store, settings, tiny_models):
    ctx = _with_pockets_and_dps(build_ctx("U0001", repo, store, settings), dps=False)
    eid = [o for o in emergency_options(ctx, tiny_models, 3000).options if o.pocket == "eid"][0]
    assert "সপ্তাহ" in eid.tradeoff_bn


def test_emergency_no_forbidden_phrases(repo, store, settings, tiny_models):
    ctx = _with_pockets_and_dps(build_ctx("U0001", repo, store, settings), dps=True)
    res = emergency_options(ctx, tiny_models, 3000)
    text = " ".join([res.note_bn] + [o.tradeoff_bn + (o.affordability_bn or "") for o in res.options])
    assert not contains_forbidden(text)
    assert res.note_bn == load_rules("emergency")["decision_note_bn"]


@pytest.mark.parametrize("amount", [0, -10, 10_000_001])
def test_emergency_amount_validation(repo, store, settings, tiny_models, amount):
    with pytest.raises(ValueError):
        emergency_options(build_ctx("U0001", repo, store, settings), tiny_models, amount)
