from datetime import date, timedelta

import pandas as pd
import pytest

from hishab.data.generator import generate, inactivity_hazard
from hishab.data.labels import shortfall_days


@pytest.fixture(scope="module")
def data():
    return generate(n_users=40, seed=1)


def test_reproducible():
    a = generate(n_users=8, seed=3)
    b = generate(n_users=8, seed=3)
    pd.testing.assert_frame_equal(a.transactions, b.transactions)


def test_no_negative_balance(data):
    assert (data.transactions.balance_after >= 0).all()


def test_persona_mix(data):
    assert set(data.users.persona) == {"garment_worker", "daily_wage", "shop_owner", "student"}


def test_rina_exists(data):
    rina = data.users.set_index("user_id").loc["U0001"]
    assert rina.persona == "garment_worker" and rina.area == "Gazipur"
    tx = data.transactions
    sal = tx[(tx.user_id == "U0001") & (tx.type == "salary_in")]
    days = pd.to_datetime(sal.ts).dt.day
    assert len(sal) >= 10 and days.between(5, 9).all()


def test_rina_heads_to_shortfall(data):
    rina_tx = data.transactions[data.transactions.user_id == "U0001"]
    assert shortfall_days(rina_tx, date(2026, 9, 19), date(2026, 9, 30))


def test_label_prevalence(data):
    assert 0.05 <= data.labels.shortfall_14d.mean() <= 0.45


def test_eid_spike(data):
    """Garment workers spend clearly more in the 14 days before Eid than in the same days a month earlier."""
    tx = data.transactions
    garment = data.users[data.users.persona == "garment_worker"].user_id
    out = tx[tx.user_id.isin(garment) & (tx.direction == -1) & (tx.category != "rent")]
    d = pd.to_datetime(out.ts).dt.date
    eid = date(2026, 3, 20)
    pre = out[(d >= eid - timedelta(days=14)) & (d < eid)].amount.sum()
    normal = out[(d >= date(2026, 2, 6)) & (d < date(2026, 2, 20))].amount.sum()
    assert pre > 1.5 * normal


def test_dps_holders():
    big = generate(n_users=200, seed=2)
    share = (big.users.dps_monthly > 0).mean()
    assert 0.03 <= share <= 0.20
    assert (big.transactions.type == "dps_installment_missed").any()


def test_inactivity_hazard_monotonic_in_cashout_share():
    base = dict(depletion_days=10, cashout_share=0.2, other_wallet_share=0.1, pocket_total=0, session_trend=0)
    hi = dict(base, cashout_share=0.8)
    assert 0 < inactivity_hazard(base) < inactivity_hazard(hi) < 1


def test_timestamps_follow_balance_chain(data):
    """Rows sorted by time must reproduce the balance chain (ts never goes backwards per user)."""
    for _, t in data.transactions.groupby("user_id"):
        assert t["ts"].is_monotonic_increasing
