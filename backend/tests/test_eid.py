from datetime import date

from hishab.engine.context import build_ctx
from hishab.engine.eid import next_eid, plan_eid, weekly_amount


def test_eid_weekly_arithmetic():
    assert weekly_amount(7000, 70) == 700
    assert weekly_amount(0, 70) == 0
    assert weekly_amount(1000, 3) == 1000  # less than a week left: all now


def test_next_eid_after_demo_today():
    assert next_eid(date(2026, 9, 18))[:2] == ("Eid-ul-Fitr", date(2027, 3, 10))


def test_rina_eid_plan_positive_need(repo, store, settings):
    p = plan_eid(build_ctx("U0001", repo, store, settings))
    assert p.eid_date == date(2027, 3, 10)
    assert p.days_left == (date(2027, 3, 10) - date(2026, 9, 18)).days
    assert p.last_eid_spend > 0 and p.need > 0 and p.weekly > 0
    assert p.expected_bonus > 0  # garment workers got a bonus before the last Eid
