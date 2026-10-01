import pytest

from hishab.engine.actions import (TRANSFORMS, candidate_actions, rank_actions, simulate_action,
                                   violates_guardrails)
from hishab.engine.context import build_ctx
from hishab.engine.features import user_features
from hishab.engine.forecast import forecast
from hishab.engine.recurring import detect_recurring
from hishab.engine.risk import score
from hishab.rules import contains_forbidden, load_rules

ESSENTIALS = set(load_rules("guardrails")["essentials"])


def test_all_catalog_ids_have_transforms():
    ids = [a["id"] for a in load_rules("actions")["actions"]]
    assert set(ids) == set(TRANSFORMS)


def test_rank_returns_at_most_3(repo, store, settings, tiny_models):
    for uid in ["U0001", "U0002", "U0003", "U0004", "U0005"]:
        cards = rank_actions(build_ctx(uid, repo, store, settings), tiny_models)
        assert len(cards) <= 3


def test_no_essential_reduction(repo, store, settings, tiny_models):
    for uid in ["U0001", "U0002", "U0003", "U0004"]:
        for c in rank_actions(build_ctx(uid, repo, store, settings), tiny_models, k=10):
            if c.id == "trim_discretionary":
                assert c.params["category"] not in ESSENTIALS
            assert not violates_guardrails(c)


def test_pause_paisa_appears_when_risk_high(repo, store, settings, tiny_models):
    ctx = build_ctx("U0001", repo, store, settings)
    ctx.state.paisa_on = True
    fc = forecast(ctx, tiny_models)
    risk = score(ctx, fc, tiny_models)
    assert risk.level in ("amber", "red")
    ids = [i for i, _ in candidate_actions(ctx, user_features(ctx), risk, detect_recurring(ctx.tx, ctx.today), fc)]
    assert "pause_paisa_saving" in ids


def test_simulate_trim_reduces_or_keeps_risk(repo, store, settings, tiny_models):
    ctx = build_ctx("U0001", repo, store, settings)
    fc_after, r_after = simulate_action(ctx, tiny_models, "save_on_payday")
    base = score(ctx, forecast(ctx, tiny_models), tiny_models)
    assert r_after.prob <= base.prob + 1e-9


def test_unknown_action_rejected(repo, store, settings, tiny_models):
    with pytest.raises(ValueError):
        simulate_action(build_ctx("U0001", repo, store, settings), tiny_models, "borrow_money")


def test_no_forbidden_phrases_in_cards(repo, store, settings, tiny_models):
    for uid in ["U0001", "U0002", "U0003", "U0004", "U0005"]:
        for c in rank_actions(build_ctx(uid, repo, store, settings), tiny_models, k=10):
            assert not contains_forbidden(" ".join([c.title_bn, c.title_en, c.why_bn, c.why_en]))


def test_daily_limit_offered_and_improves_forecast(repo, store, settings, tiny_models):
    ctx = build_ctx("U0001", repo, store, settings)
    cards = {c.id: c for c in rank_actions(ctx, tiny_models, k=10)}
    assert "daily_limit" in cards
    assert cards["daily_limit"].risk_after <= cards["daily_limit"].risk_before
    fc_after, _ = simulate_action(ctx, tiny_models, "daily_limit")
    assert min(fc_after.p50[:14]) > min(forecast(ctx, tiny_models).p50[:14])


def test_bandit_preferences_change_ranking(repo, store, settings, tiny_models):
    import numpy as np

    from hishab.engine.bandit import Bandit
    ctx = build_ctx("U0001", repo, store, settings)
    ids = [c.id for c in rank_actions(ctx, tiny_models, k=10)]
    assert "save_on_payday" in ids
    loves = Bandit({("garment_worker", i): ((1000.0, 1.0) if i == "save_on_payday" else (1.0, 1000.0))
                    for i in ids})
    top = rank_actions(ctx, tiny_models, bandit=loves, k=1, rng=np.random.default_rng(0))
    assert top[0].id == "save_on_payday"
