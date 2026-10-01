from hishab.engine.context import build_ctx
from hishab.engine.forecast import forecast
from hishab.engine.recurring import detect_recurring
from hishab.engine.safe_spend import daily_budget, safe_to_spend, safe_to_spend_value


def test_safe_to_spend_formula():
    assert safe_to_spend_value(balance=3000, committed=1000, cushion=500, horizon=10, buffer=200) == 130


def test_safe_to_spend_never_negative():
    assert safe_to_spend_value(balance=0, committed=1000, cushion=500, horizon=10, buffer=200) == 0


def test_safe_to_spend_for_users(repo, store, settings, tiny_models):
    for uid in ["U0001", "U0002", "U0005"]:
        ctx = build_ctx(uid, repo, store, settings)
        v = safe_to_spend(ctx, forecast(ctx, tiny_models), detect_recurring(ctx.tx, ctx.today))
        assert v >= 0


def test_daily_budget_is_break_even_and_at_least_safe(repo, store, settings, tiny_models):
    ctx = build_ctx("U0001", repo, store, settings)
    fc = forecast(ctx, tiny_models)
    rec = detect_recurring(ctx.tx, ctx.today)
    assert daily_budget(ctx, rec) >= safe_to_spend(ctx, fc, rec)
    assert daily_budget(ctx, rec) > 0
