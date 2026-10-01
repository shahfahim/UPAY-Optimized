import pytest

from hishab.engine.context import build_ctx
from hishab.engine.goals import plan_goal


@pytest.mark.parametrize("target,months", [(0, 6), (-5, 6), (30000, 0), (30000, 61)])
def test_goal_validation(repo, store, settings, tiny_models, target, months):
    with pytest.raises(ValueError):
        plan_goal(build_ctx("U0001", repo, store, settings), tiny_models, target, months)


def test_goal_feasibility_monotonic(repo, store, settings, tiny_models):
    ctx = build_ctx("U0005", repo, store, settings)
    small = plan_goal(ctx, tiny_models, 5000, 6)
    big = plan_goal(ctx, tiny_models, 200000, 6)
    assert 0.0 <= big.feasibility <= small.feasibility <= 1.0
    assert small.monthly == 834  # ceil(5000 / 6)


def test_goal_plan_fields(repo, store, settings, tiny_models):
    p = plan_goal(build_ctx("U0001", repo, store, settings), tiny_models, 30000, 6)
    assert p.target == 30000 and p.months == 6 and p.monthly == 5000
    assert isinstance(p.enabling_actions, list)
