"""Security hardening: demo-only routes, CORS allowlist, headers, PII redaction, OTP echo."""
from dataclasses import replace

import pytest
from fastapi.testclient import TestClient

from hishab.api.main import create_app
from hishab.security import PII_Stripper


@pytest.fixture
def prod(svc):
    """The same service with demo mode off."""
    svc.settings = replace(svc.settings, demo_mode=False)
    return TestClient(create_app(svc=svc))


def _token(c):
    return c.post("/api/auth/login", json={"mobile": "01700000001", "pin": "123456"}).json()["token"]


def test_demo_routes_hidden_when_demo_mode_off(prod):
    h = {"Authorization": f"Bearer {_token(prod)}"}
    assert prod.get("/api/users").status_code == 404
    assert prod.post("/api/demo/reset", headers=h).status_code == 404
    assert prod.post("/api/demo/time-travel", json={"days": 7}, headers=h).status_code == 404


def test_otp_not_echoed_when_demo_mode_off(prod):
    r = prod.post("/api/auth/register/start", json={"mobile": "01811223355"}).json()
    assert "otp" not in r and r["sent"] is True


def test_user_list_never_includes_registered_numbers(client):
    otp = client.post("/api/auth/register/start", json={"mobile": "01811223366"}).json()["otp"]
    client.post("/api/auth/register/verify", json={"mobile": "01811223366", "otp": otp, "name": "নতুন", "pin": "246810"})
    assert "01811223366" not in [u["phone"] for u in client.get("/api/users").json()]


def test_cors_only_allows_listed_origins(anon):
    ok = anon.options("/api/health", headers={"Origin": "http://localhost:5173", "Access-Control-Request-Method": "GET"})
    assert ok.headers.get("access-control-allow-origin") == "http://localhost:5173"
    bad = anon.options("/api/health", headers={"Origin": "https://evil.example", "Access-Control-Request-Method": "GET"})
    assert "access-control-allow-origin" not in bad.headers


def test_security_headers(anon):
    h = anon.get("/api/health").headers
    assert h["x-content-type-options"] == "nosniff" and h["x-frame-options"] == "DENY"
    assert "frame-ancestors 'none'" in h["content-security-policy"]


def test_predict_needs_session_and_hides_errors(anon, monkeypatch):
    assert anon.post("/api/upay/ai/predict", json={"query": "balance koto"}).status_code == 401
    import hishab.ml_engine as ml

    def boom(_):
        raise RuntimeError("secret internal detail")
    monkeypatch.setattr(ml, "predict_intent", boom)
    r = anon.post("/api/upay/ai/predict", json={"query": "x"}, headers={"Authorization": f"Bearer {_token(anon)}"})
    assert r.status_code == 500 and "secret" not in r.text


@pytest.mark.parametrize("text,expected", [
    ("tour er jnno 5000 tk jomabo 01712345678", "tour er jnno 5000 tk jomabo [PHONE_REDACTED]"),
    ("+8801812345678 e pathao", "[PHONE_REDACTED] e pathao"),
    ("amar pin 123456", "amar pin [PIN_REDACTED]"),
    ("OTP: 4321 ache", "OTP: [PIN_REDACTED] ache"),
    ("পিন ১২৩৪৫৬ দিলাম", "পিন [PIN_REDACTED] দিলাম"),
    ("2000 taka pathabo", "2000 taka pathabo"),
])
def test_pii_stripper(text, expected):
    assert PII_Stripper(text) == expected
