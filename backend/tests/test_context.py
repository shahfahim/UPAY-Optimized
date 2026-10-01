from datetime import date

import pandas as pd
import pytest

from hishab.engine.context import UserNotFound, build_ctx


def test_build_ctx_rina(repo, store, settings):
    ctx = build_ctx("U0001", repo, store, settings)
    assert ctx.today == date(2026, 9, 18)
    assert ctx.balance > 0
    assert (pd.to_datetime(ctx.tx.ts).dt.date <= ctx.today).all()
    assert ctx.insufficient_history is False


def test_build_ctx_unknown_raises(repo, store, settings):
    with pytest.raises(UserNotFound):
        build_ctx("U9999", repo, store, settings)


def test_clock_offset_moves_today(repo, store, settings):
    store.set_clock_offset(7)
    assert build_ctx("U0001", repo, store, settings).today == date(2026, 9, 25)


def test_sim_tx_changes_balance(repo, store, settings):
    before = build_ctx("U0001", repo, store, settings)
    row = {"ts": "2026-09-18T20:00:00", "type": "merchant_pay", "amount": 100.0, "direction": -1, "fee": 0.0,
           "balance_after": round(before.balance - 100.0, 2), "counterparty_id": "M-001",
           "counterparty_name": "মুদি দোকান", "counterparty_type": "merchant", "counterparty_channel": "upay",
           "category": "food_grocery", "area": "Gazipur"}
    store.add_sim_tx("U0001", row)
    after = build_ctx("U0001", repo, store, settings)
    assert after.balance == pytest.approx(before.balance - 100.0)


def test_state_seeded_from_history(repo, store, settings):
    ctx = build_ctx("U0005", repo, store, settings)  # the saver
    assert ctx.state.pockets["emergency"] > 0
