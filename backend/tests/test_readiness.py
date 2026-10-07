from dataclasses import asdict

from hishab.engine.context import build_ctx
from hishab.engine.features import PROTECTED
from hishab.engine.health import indicators
from hishab.engine.readiness import READINESS_INPUTS, readiness
from hishab.rules import contains_forbidden, load_rules


def test_readiness_five_signals_and_disclaimer(repo, store, settings):
    ctx = build_ctx("U0001", repo, store, settings)
    r = readiness(ctx, indicators(ctx))
    assert [s.id for s in r.signals] == ["income_regularity", "emergency_buffer", "on_time_bills",
                                         "shortfall_frequency", "saving_consistency"]
    assert r.disclaimer_bn == load_rules("readiness")["disclaimer_bn"]
    assert all(s.state in ("green", "amber", "red") and s.reason_bn for s in r.signals)
    assert all(s.improve_bn for s in r.signals if s.state != "green")


def test_readiness_no_score_or_loan_language(repo, store, settings):
    for uid in ["U0001", "U0005"]:
        ctx = build_ctx(uid, repo, store, settings)
        d = asdict(readiness(ctx, indicators(ctx)))
        assert "score" not in d and "total" not in d
        text = " ".join([d["disclaimer_bn"]] + [s["reason_bn"] + (s["improve_bn"] or "") for s in d["signals"]])
        body = text.replace(d["disclaimer_bn"], "")
        assert not contains_forbidden(body)


def test_readiness_inputs_exclude_protected():
    assert set(READINESS_INPUTS) & (PROTECTED | {"persona_code"}) == set()


def test_saver_mostly_green(repo, store, settings):
    ctx = build_ctx("U0005", repo, store, settings)
    states = [s.state for s in readiness(ctx, indicators(ctx)).signals]
    assert states.count("green") >= 3
