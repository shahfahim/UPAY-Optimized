"""Hybrid chat routing: regex intents first, the trained intent classifier only when regex finds nothing."""

import sys

import pytest

from hishab import ml_engine
from hishab.llm import fallback
from hishab.llm.fallback import answer
from hishab.rules import contains_forbidden
from hishab.services import Hishab

UNKNOWN = "এই বিষয়ে আমার কিছু জানা নেই"
needs_model = pytest.mark.skipif(not ml_engine._classifier_instance.is_trained,
                                 reason="intent model not trained yet")


@pytest.fixture
def svc(repo, store, tiny_models, settings):
    return Hishab(repo, store, tiny_models, settings)


@pytest.fixture
def fake_ml(monkeypatch):
    """Replace the classifier with a scripted prediction."""
    def _set(intent, confidence):
        monkeypatch.setattr(fallback, "_ml_predictor",
                            lambda text: {"intent": intent, "confidence": confidence, "extracted_entities": {}})
    return _set


def _tools(r):
    return [u["name"] for u in r["used_tools"]]


# ── (a) regex misses, ML catches ─────────────────────────────────────────────
@needs_model
@pytest.mark.parametrize("q,tool", [
    ("maa ke tk pathabo kishe", "find_route"),
    ("porer masher tour er jnno kivabe tk save krbo", "dps_advice"),
    ("tour er jnno tk jomabo", "dps_advice"),
])
def test_real_model_rescues_regex_misses(svc, q, tool):
    r = answer("U0001", q, svc)
    assert UNKNOWN not in r["text"]
    assert tool in _tools(r)
    assert not contains_forbidden(r["text"])


@pytest.mark.parametrize("ml_intent,tool", [
    ("goal", "dps_advice"), ("savings", "dps_advice"), ("send_money", "find_route"),
    ("route_planner", "find_route"), ("cashout", "get_transactions_summary"),
    ("balance", "get_home_summary"), ("status", "get_home_summary"), ("health", "get_home_summary"),
    ("advice", "get_home_summary"), ("emergency", "emergency_options"),
])
def test_every_ml_intent_maps_to_a_real_handler(svc, fake_ml, ml_intent, tool):
    fake_ml(ml_intent, 0.95)
    r = answer("U0001", "qqq zzz", svc)
    assert UNKNOWN not in r["text"] and tool in _tools(r)
    assert not contains_forbidden(r["text"])


def test_regex_stays_primary_over_ml(svc, fake_ml):
    fake_ml("emergency", 0.99)
    r = answer("U0001", "৬ মাসে ৳৩০,০০০ জমাতে পারব?", svc)
    assert _tools(r)[0] == "plan_goal"


def test_ml_never_routes_to_budget(svc, fake_ml):
    fake_ml("budget", 0.99)
    r = answer("U0001", "qqq zzz", svc)
    assert UNKNOWN in r["text"] and r["used_tools"] == []
    assert "budget" not in fallback._ML_TO_INTENT.values()


def test_ml_loan_requests_are_never_approved(svc, fake_ml):
    fake_ml("emergency", 0.95)
    r = answer("U0001", "amake 5000 tk diye dao please", svc)
    assert not contains_forbidden(r["text"])
    assert "অনুমোদ" not in r["text"]  # never "approved"


# ── (b) low confidence keeps the polite fallback ─────────────────────────────
@needs_model
@pytest.mark.parametrize("q", ["asdkjh qwe zzz", "xyzzy", "blorp flim"])
def test_real_model_gibberish_gets_polite_fallback(svc, q):
    r = answer("U0001", q, svc)
    assert UNKNOWN in r["text"] and r["used_tools"] == []


def test_below_threshold_keeps_polite_fallback(svc, fake_ml):
    fake_ml("goal", fallback._ML_THRESHOLD - 0.01)
    r = answer("U0001", "qqq zzz", svc)
    assert UNKNOWN in r["text"] and r["used_tools"] == []


# ── (c) chat survives without the ML engine ──────────────────────────────────
def test_chat_works_when_ml_engine_cannot_import(svc, monkeypatch):
    monkeypatch.setitem(sys.modules, "hishab.ml_engine", None)  # import now raises
    monkeypatch.setattr(fallback, "_ml_predictor", None)        # force a fresh load attempt
    r = answer("U0001", "tour er jnno tk jomabo", svc)
    assert UNKNOWN in r["text"]
    assert answer("U0001", "৬ মাসে ৳৩০,০০০ জমাতে পারব?", svc)["used_tools"][0]["name"] == "plan_goal"


def test_chat_works_when_prediction_raises(svc, monkeypatch):
    def boom(text):
        raise RuntimeError("model broken")
    monkeypatch.setattr(fallback, "_ml_predictor", boom)
    r = answer("U0001", "qqq zzz", svc)
    assert UNKNOWN in r["text"]


# ── regression: safe-spend handler used to crash with UnboundLocalError ──────
def test_safe_spend_answers_without_crashing(svc):
    r = answer("U0001", "aaj koto kharoch korte parbo", svc)
    assert r["text"] and "get_home_summary" in _tools(r)
