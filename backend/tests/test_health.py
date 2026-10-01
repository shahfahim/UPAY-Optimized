from datetime import date, timedelta

from helpers import hand_ctx, tx_row
from hishab.engine.context import build_ctx
from hishab.engine.health import health_report, indicators, mine_habits
from hishab.store.sqlite import UserState

TODAY = date(2026, 9, 18)


def test_indicators_hand_fixture():
    rows = [tx_row(TODAY - timedelta(days=k), "merchant_pay", 100, -1, category="food_grocery") for k in range(30)]
    rows += [tx_row(TODAY - timedelta(days=5), "salary_in", 10000, 1, category="income", cp="EMP"),
             tx_row(TODAY - timedelta(days=3), "cash_out", 6000, -1, category="family_support", cp="AGENT")]
    st = UserState()
    st.pockets["emergency"] = 1500.0
    ind = indicators(hand_ctx(rows, TODAY, state=st))
    assert ind.emergency_days == 15.0
    assert ind.cash_dependency == 0.6


def test_habits_sorted_and_bounded(repo, store, settings):
    for uid in ["U0001", "U0002", "U0003", "U0004", "U0005"]:
        h = mine_habits(build_ctx(uid, repo, store, settings))
        assert len(h) <= 5
        assert [x.taka_impact for x in h] == sorted([x.taka_impact for x in h], reverse=True)
        assert all(x.text_bn and x.text_en for x in h)


def test_rina_cash_habit_found(repo, store, settings):
    ids = [h.id for h in mine_habits(build_ctx("U0001", repo, store, settings))]
    assert "cashout_fees" in ids


def test_health_report_shape(repo, store, settings):
    r = health_report(build_ctx("U0001", repo, store, settings))
    assert len(r.trend6) == 6
    assert {"went_well_bn", "change_bn", "fees_saved", "shortfall_avoided"} <= set(r.monthly_report)
