from datetime import date

from hishab.config import get_settings


def test_defaults(monkeypatch):
    monkeypatch.delenv("DEMO_TODAY", raising=False)
    monkeypatch.delenv("ANTHROPIC_API_KEY", raising=False)
    monkeypatch.delenv("LLM_ENABLED", raising=False)
    get_settings.cache_clear()
    s = get_settings()
    assert s.demo_today == date(2026, 9, 18)
    assert s.seed == 42
    assert s.llm_model == "claude-opus-5-5"
    assert s.llm_enabled is False


def test_env_override(monkeypatch):
    monkeypatch.setenv("DEMO_TODAY", "2026-09-20")
    get_settings.cache_clear()
    assert get_settings().demo_today == date(2026, 9, 20)
    get_settings.cache_clear()


def test_llm_auto_enabled_with_key(monkeypatch):
    monkeypatch.setenv("ANTHROPIC_API_KEY", "test-key")
    monkeypatch.delenv("LLM_ENABLED", raising=False)
    get_settings.cache_clear()
    assert get_settings().llm_enabled is True
    get_settings.cache_clear()
