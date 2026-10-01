from datetime import date, timedelta
from types import SimpleNamespace

import pandas as pd
import pytest

from hishab.engine import forecast as F
from hishab.engine.context import build_ctx


@pytest.fixture(scope="module")
def tiny_models(small_data):
    daily = F.training_daily(small_data, date(2025, 11, 1), date(2026, 8, 31))
    fc = F.Forecaster().fit(daily)
    resid = fc.residuals(daily)
    return SimpleNamespace(forecaster=fc, residuals=resid)


def test_band_shape_and_order(repo, store, settings, tiny_models):
    ctx = build_ctx("U0001", repo, store, settings)
    r = F.forecast(ctx, tiny_models)
    assert len(r.dates) == len(r.p10) == len(r.p50) == len(r.p90) == 30
    assert r.dates[0] == ctx.today + timedelta(days=1)
    assert all(a <= b <= c for a, b, c in zip(r.p10, r.p50, r.p90))


def test_rina_shortfall_predicted_after_today(repo, store, settings, tiny_models):
    ctx = build_ctx("U0001", repo, store, settings)
    r = F.forecast(ctx, tiny_models)
    assert r.shortfall_date is not None
    assert date(2026, 9, 19) <= r.shortfall_date <= date(2026, 10, 6)
    assert r.shortfall_amount > 0


def test_transform_applied(repo, store, settings, tiny_models):
    ctx = build_ctx("U0001", repo, store, settings)
    base = F.forecast(ctx, tiny_models)
    day = ctx.today + timedelta(days=3)

    def add_outflow(flows, _ctx):
        extra = pd.DataFrame([{"date": day, "amount": -2000.0, "category": "other", "type": "test",
                               "fee": 0.0, "kind": "recurring"}])
        return pd.concat([flows, extra], ignore_index=True)

    moved = F.forecast(ctx, tiny_models, transforms=[add_outflow])
    assert base.p50[-1] - moved.p50[-1] == pytest.approx(2000.0, abs=1.0)


def test_to_flows_signs(repo, store, settings):
    ctx = build_ctx("U0001", repo, store, settings)
    flows = F.to_flows(ctx.tx)
    sal = flows[flows.type == "salary_in"]
    co = flows[flows.type == "cash_out"]
    assert (sal.amount > 0).all() and (co.amount < 0).all()


def test_baselines_length(repo, store, settings):
    ctx = build_ctx("U0001", repo, store, settings)
    assert len(F.baseline_last_month(ctx, 30)) == 30
    assert len(F.baseline_trailing_avg(ctx, 30)) == 30
