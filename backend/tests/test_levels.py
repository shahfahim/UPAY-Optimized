from datetime import date, timedelta

import pytest

from helpers import hand_ctx, saving_days, tx_row
from hishab.engine.health import Indicators
from hishab.engine.levels import compute_level, saving_streak

TODAY = date(2026, 9, 18)
NO_HEALTH = Indicators(emergency_days=0, cash_dependency=0.5, shortfall_free_months=0)
GOOD_HEALTH = Indicators(emergency_days=20, cash_dependency=0.2, shortfall_free_months=3)


@pytest.mark.parametrize("days,level,reached", [(4, 0, []), (5, 0, [5]), (15, 0, [5, 10, 15]),
                                                (30, 1, [5, 10, 15])])
def test_level_milestones_5_10_15_30(days, level, reached):
    ctx = hand_ctx(saving_days(TODAY, days), TODAY)
    st = compute_level(ctx, NO_HEALTH)
    assert saving_streak(ctx) == days
    assert st.level == level
    assert [m["days"] for m in st.milestones if m["reached"]] == reached
    assert st.dps_ready is (level >= 1)


def test_streak_allows_three_missed_days():
    rows = [r for k, r in enumerate(saving_days(TODAY, 20)) if k not in (3, 7, 11)]
    assert saving_streak(hand_ctx(rows, TODAY)) == 20


def test_streak_breaks_after_too_many_misses():
    rows = [r for k, r in enumerate(saving_days(TODAY, 20)) if k not in (3, 4, 5, 6)]
    assert saving_streak(hand_ctx(rows, TODAY)) == 3


def test_level2_needs_health():
    ctx = hand_ctx(saving_days(TODAY, 40), TODAY)
    assert compute_level(ctx, GOOD_HEALTH).level == 2
    assert compute_level(ctx, NO_HEALTH).level == 1


def test_level3_needs_on_time_installments():
    rows = saving_days(TODAY, 40) + [tx_row(TODAY - timedelta(days=30 * k + 1), "dps_installment", 1000, -1)
                                     for k in range(3)]
    assert compute_level(hand_ctx(rows, TODAY), GOOD_HEALTH).level == 3


def test_projection_and_progress():
    st = compute_level(hand_ctx(saving_days(TODAY, 18), TODAY), NO_HEALTH)
    assert st.projection_days == 12 and st.next_level == 1
    assert 0 < st.progress < 1
