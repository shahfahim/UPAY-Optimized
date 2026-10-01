from datetime import date, timedelta

from helpers import hand_ctx, tx_row
from hishab.engine.context import build_ctx
from hishab.engine.features import user_features
from hishab.engine.health import Indicators, indicators
from hishab.engine.lessons import eligible_lessons, rank_lessons
from hishab.rules import contains_forbidden

TODAY = date(2026, 9, 18)


def test_lesson_trigger_only_when_condition():
    rows = [tx_row(TODAY - timedelta(days=k), "merchant_pay", 100, -1, category="food_grocery") for k in range(30)]
    rows.append(tx_row(TODAY - timedelta(days=5), "salary_in", 10000, 1, category="income", cp="EMP"))
    ctx = hand_ctx(rows, TODAY)
    low_cash = Indicators(emergency_days=20, cash_dependency=0.1, shortfall_free_months=3)
    assert "cashout_cost" not in eligible_lessons(ctx, user_features(ctx), low_cash)
    high_cash = Indicators(emergency_days=20, cash_dependency=0.5, shortfall_free_months=3)
    assert "cashout_cost" in eligible_lessons(ctx, user_features(ctx), high_cash)


def test_lesson_placeholders_filled(repo, store, settings):
    for uid in ["U0001", "U0002", "U0003", "U0004", "U0005"]:
        ctx = build_ctx(uid, repo, store, settings)
        for lesson in rank_lessons(ctx, user_features(ctx), indicators(ctx), bandit=None):
            assert "{" not in lesson.body_bn and "{" not in lesson.title_bn
            assert not contains_forbidden(lesson.body_bn)


def test_rina_gets_cashout_lesson_with_her_numbers(repo, store, settings):
    ctx = build_ctx("U0001", repo, store, settings)
    lessons = {l.id: l for l in rank_lessons(ctx, user_features(ctx), indicators(ctx), bandit=None)}
    assert "cashout_cost" in lessons and "৳" in lessons["cashout_cost"].body_bn
