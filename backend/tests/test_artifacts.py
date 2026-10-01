"""Smoke test: the committed artifacts load and score the demo user on the committed serving data."""

from hishab.config import BACKEND_DIR
from hishab.data.loader import DataRepo
from hishab.engine.context import build_ctx
from hishab.engine.forecast import forecast
from hishab.engine.models import load_from
from hishab.engine.actions import rank_actions
from hishab.engine.risk import score


def test_models_load_and_score_rina(store, settings):
    models = load_from(BACKEND_DIR / "artifacts")
    repo = DataRepo.from_dir(BACKEND_DIR / "data" / "serving")
    ctx = build_ctx("U0001", repo, store, settings)
    fc = forecast(ctx, models)
    r = score(ctx, fc, models)
    assert r.level in ("amber", "red")
    assert fc.shortfall_date is not None


def test_daily_limit_lowers_rina_risk_with_real_models(store, settings):
    models = load_from(BACKEND_DIR / "artifacts")
    repo = DataRepo.from_dir(BACKEND_DIR / "data" / "serving")
    cards = {c.id: c for c in rank_actions(build_ctx("U0001", repo, store, settings), models, k=10)}
    assert cards["daily_limit"].risk_after < cards["daily_limit"].risk_before
