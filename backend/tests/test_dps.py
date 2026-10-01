from hishab.engine.context import build_ctx
from hishab.engine.dps import dps_advice, installment_risk
from hishab.engine.forecast import forecast
from hishab.engine.recurring import detect_recurring
from hishab.engine.risk import score
from hishab.rules import contains_forbidden, load_rules


def test_dps_not_now_when_amber(repo, store, settings, tiny_models):
    ctx = build_ctx("U0001", repo, store, settings)
    assert score(ctx, forecast(ctx, tiny_models), tiny_models).level in ("amber", "red")
    adv = dps_advice(ctx, tiny_models)
    assert adv.status == "not_now" and adv.safe_monthly is None and adv.reason_bn


def test_dps_ok_for_green_saver(repo, store, settings, tiny_models):
    adv = dps_advice(build_ctx("U0005", repo, store, settings), tiny_models)
    assert adv.status == "ok"
    assert adv.safe_monthly in load_rules("dps")["monthly_options"]
    assert adv.maturity_estimate == adv.safe_monthly * adv.tenure_months


def test_dps_never_exceeds_safe_limit(repo, store, settings, tiny_models):
    ctx = build_ctx("U0005", repo, store, settings)
    adv = dps_advice(ctx, tiny_models)
    assert installment_risk(ctx, tiny_models, adv.safe_monthly, adv.day) < 0.30


def test_dps_day_after_salary(repo, store, settings, tiny_models):
    ctx = build_ctx("U0005", repo, store, settings)
    sal = [e for e in detect_recurring(ctx.tx, ctx.today) if e.kind == "salary"][0]
    assert dps_advice(ctx, tiny_models).day == sal.day_of_month + 1


def test_levels_never_block_dps(repo, store, settings, tiny_models):
    """A green-risk user with no saving streak (level 0) is not refused because of level."""
    ctx = build_ctx("U0003", repo, store, settings)
    assert score(ctx, forecast(ctx, tiny_models), tiny_models).level == "green"
    adv = dps_advice(ctx, tiny_models)
    assert "লেভেল" not in adv.reason_bn


def test_dps_tenure_from_goal(repo, store, settings, tiny_models):
    adv = dps_advice(build_ctx("U0005", repo, store, settings), tiny_models, goal_target=24000)
    assert adv.tenure_months * adv.safe_monthly >= 24000 or adv.tenure_months == 60


def test_no_pressure_language(repo, store, settings, tiny_models):
    for uid in ["U0001", "U0005"]:
        assert not contains_forbidden(dps_advice(build_ctx(uid, repo, store, settings), tiny_models).reason_bn)


def test_installment_capped_at_quarter_of_income(repo, store, settings, tiny_models):
    ctx = build_ctx("U0005", repo, store, settings)
    sal = [e for e in detect_recurring(ctx.tx, ctx.today) if e.kind == "salary"][0]
    assert dps_advice(ctx, tiny_models).safe_monthly <= 0.25 * sal.amount


def test_reason_mentions_salary_only_for_salaried(repo, store, settings, tiny_models):
    adv = dps_advice(build_ctx("U0003", repo, store, settings), tiny_models)  # shop owner, no salary
    if adv.status == "ok":
        assert "বেতন" not in adv.reason_bn
