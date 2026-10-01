from hishab.engine.context import build_ctx
from hishab.engine.features import PROTECTED
from hishab.engine.forecast import forecast
from hishab.engine.risk import RISK_FEATURES, risk_features, rule_baseline, score
from hishab.rules import risk_level


def _score(uid, repo, store, settings, models):
    ctx = build_ctx(uid, repo, store, settings)
    fc = forecast(ctx, models)
    return ctx, fc, score(ctx, fc, models)


def test_prob_in_unit_interval(repo, store, settings, tiny_models):
    for uid in ["U0001", "U0002", "U0003", "U0004", "U0005"]:
        _, _, r = _score(uid, repo, store, settings, tiny_models)
        assert 0.0 <= r.prob <= 1.0


def test_level_matches_thresholds(repo, store, settings, tiny_models):
    _, _, r = _score("U0001", repo, store, settings, tiny_models)
    assert r.level == risk_level(r.prob)


def test_drivers_have_bangla_text(repo, store, settings, tiny_models):
    _, _, r = _score("U0001", repo, store, settings, tiny_models)
    assert len(r.drivers) == 3
    assert all(d.text_bn and d.text_en for d in r.drivers)


def test_rina_is_amber_or_red(repo, store, settings, tiny_models):
    _, _, r = _score("U0001", repo, store, settings, tiny_models)
    assert r.level in ("amber", "red")


def test_saver_is_green(repo, store, settings, tiny_models):
    _, _, r = _score("U0005", repo, store, settings, tiny_models)
    assert r.level == "green"


def test_protected_not_in_risk_features(repo, store, settings, tiny_models):
    assert not (set(RISK_FEATURES) & (PROTECTED | {"persona_code"}))
    ctx = build_ctx("U0001", repo, store, settings)
    feats = risk_features(ctx, forecast(ctx, tiny_models))
    assert set(feats) == set(RISK_FEATURES)


def test_rule_baseline_binary(repo, store, settings, tiny_models):
    ctx = build_ctx("U0001", repo, store, settings)
    assert rule_baseline(risk_features(ctx, forecast(ctx, tiny_models))) in (0.0, 1.0)
