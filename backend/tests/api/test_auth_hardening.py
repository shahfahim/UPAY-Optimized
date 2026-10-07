"""Sessions expire and can be revoked; PINs are salted scrypt; logins lock out; OTPs expire and run out."""

import pytest

from hishab.passwords import hash_pin, verify_pin
from hishab.store.sqlite import SESSION_IDLE_S, SESSION_TTL_S, Store


class Clock:
    def __init__(self):
        self.t = 1_000_000.0

    def __call__(self):
        return self.t


@pytest.fixture
def clocked(tmp_path):
    c = Clock()
    return Store(tmp_path / "s.db", clock=c), c


def _h(t):
    return {"Authorization": f"Bearer {t}"}


def test_tokens_are_hashed_at_rest(clocked):
    store, _ = clocked
    tok = store.create_session("U0001")
    rows = store._exec("SELECT token_hash FROM auth_sessions")
    assert rows and tok not in rows[0][0]


def test_idle_and_absolute_expiry(clocked):
    store, c = clocked
    tok = store.create_session("U0001")
    c.t += SESSION_IDLE_S - 5
    assert store.session_user(tok) == "U0001"           # activity keeps it alive
    c.t += SESSION_IDLE_S + 1
    assert store.session_user(tok) is None              # idle too long
    tok2 = store.create_session("U0001")
    for _ in range(int(SESSION_TTL_S // (SESSION_IDLE_S - 60)) + 1):
        c.t += SESSION_IDLE_S - 60
        store.session_user(tok2)
    assert store.session_user(tok2) is None             # absolute lifetime reached


def test_logout_and_logout_all(anon):
    login = {"mobile": "01700000001", "pin": "123456"}
    a = anon.post("/api/auth/login", json=login).json()["token"]
    b = anon.post("/api/auth/login", json=login).json()["token"]
    assert anon.post("/api/auth/logout", headers=_h(a)).status_code == 200
    assert anon.get("/api/users/U0001/home", headers=_h(a)).status_code == 401
    assert anon.get("/api/users/U0001/shell", headers=_h(b)).status_code == 200
    c = anon.post("/api/auth/login", json=login).json()["token"]
    assert anon.post("/api/auth/logout-all", headers=_h(c)).json()["revoked"] >= 2
    assert anon.get("/api/users/U0001/shell", headers=_h(b)).status_code == 401


def test_lockout_after_five_wrong_pins(anon):
    bad = {"mobile": "01700000002", "pin": "000000"}
    for _ in range(5):
        assert anon.post("/api/auth/login", json=bad).status_code == 401
    r = anon.post("/api/auth/login", json={"mobile": "01700000002", "pin": "123456"})
    assert r.status_code == 429  # even the right PIN waits out the lockout


def test_pin_hash_is_salted_scrypt_and_peppered():
    a, b = hash_pin("246810", "p1"), hash_pin("246810", "p1")
    assert a != b and a.startswith("scrypt$")
    assert verify_pin(a, "246810", "p1") and not verify_pin(a, "246811", "p1")
    assert not verify_pin(a, "246810", "other-pepper")


def test_legacy_hash_upgrades_on_login(anon, svc):
    import hashlib
    otp = anon.post("/api/auth/register/start", json={"mobile": "01811229999"}).json()["otp"]
    uid = anon.post("/api/auth/register/verify", json={"mobile": "01811229999", "otp": otp, "name": "পুরনো",
                                                         "pin": "246810"}).json()["user_id"]
    legacy = hashlib.sha256(b"hishab-demo:246810").hexdigest()
    svc.store.add_user({**svc.store.extra_user(uid), "pin_hash": legacy}, [])
    assert anon.post("/api/auth/login", json={"mobile": "01811229999", "pin": "246810"}).status_code == 200
    assert svc.store.extra_user(uid)["pin_hash"].startswith("scrypt$")


def test_otp_runs_out_after_three_wrong_tries(anon):
    otp = anon.post("/api/auth/register/start", json={"mobile": "01811228888"}).json()["otp"]
    body = {"mobile": "01811228888", "name": "নতুন", "pin": "246810"}
    wrong = "000000" if otp != "000000" else "111111"
    for _ in range(3):
        assert anon.post("/api/auth/register/verify", json={**body, "otp": wrong}).status_code == 422
    assert anon.post("/api/auth/register/verify", json={**body, "otp": otp}).status_code == 422


def test_otp_expires(anon, svc):
    otp = anon.post("/api/auth/register/start", json={"mobile": "01811227777"}).json()["otp"]
    svc.store.clock = lambda: 10**12
    r = anon.post("/api/auth/register/verify", json={"mobile": "01811227777", "otp": otp, "name": "নতুন",
                                                      "pin": "246810"})
    assert r.status_code == 422


def test_otp_not_stored_in_plain_text(anon, svc):
    otp = anon.post("/api/auth/register/start", json={"mobile": "01811226666"}).json()["otp"]
    assert otp not in (svc.store.get_meta("otp:01811226666") or "")
