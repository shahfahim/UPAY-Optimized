import pytest


def test_health(client):
    r = client.get("/api/health")
    assert r.status_code == 200 and r.json()["status"] == "ok"


def test_users_list_has_rina(client):
    users = client.get("/api/users").json()
    rina = next(u for u in users if u["user_id"] == "U0001")
    assert rina["phone"] == "01700000001"


def test_login_ok_and_wrong_pin(client):
    ok = client.post("/api/auth/login", json={"mobile": "01700000001", "pin": "123456"})
    assert ok.status_code == 200 and ok.json()["user_id"] == "U0001" and ok.json()["token"]
    bad = client.post("/api/auth/login", json={"mobile": "01700000001", "pin": "000000"})
    assert bad.status_code == 401 and bad.json()["detail"] == "PIN সঠিক নয়"


def test_login_bad_mobile_422(client):
    assert client.post("/api/auth/login", json={"mobile": "12345", "pin": "123456"}).status_code == 422


def test_register_flow_creates_user_with_history(client):
    start = client.post("/api/auth/register/start", json={"mobile": "01811223344"})
    assert start.status_code == 200
    otp = start.json()["otp"]
    assert client.post("/api/auth/register/verify",
                       json={"mobile": "01811223344", "otp": "999999" if otp != "999999" else "111111",
                             "name": "নতুন ইউজার", "pin": "246810"}).status_code == 422
    done = client.post("/api/auth/register/verify",
                       json={"mobile": "01811223344", "otp": otp, "name": "নতুন ইউজার", "pin": "246810"})
    assert done.status_code == 200
    uid, token = done.json()["user_id"], done.json()["token"]
    home = client.get(f"/api/users/{uid}/home", headers={"Authorization": f"Bearer {token}"}).json()
    assert home["insufficient_history"] is False and home["forecast"] is not None
    relog = client.post("/api/auth/login", json={"mobile": "01811223344", "pin": "246810"})
    assert relog.status_code == 200 and relog.json()["user_id"] == uid


def _bearer(token):
    return {"Authorization": f"Bearer {token}"}


@pytest.mark.parametrize("method,path", [
    ("get", "/api/users/U0001/home"), ("get", "/api/users/U0001/shell"), ("get", "/api/users/U0001/savings"),
    ("get", "/api/users/U0001/transactions"), ("post", "/api/users/U0001/send"), ("post", "/api/users/U0001/chat"),
    ("post", "/api/users/U0001/savings/pockets/eid/move"),
])
def test_user_routes_need_a_token(anon, method, path):
    assert getattr(anon, method)(path).status_code == 401
    assert getattr(anon, method)(path, headers=_bearer("not-a-token")).status_code == 401


def test_token_only_opens_its_own_user(anon):
    token = anon.post("/api/auth/login", json={"mobile": "01700000001", "pin": "123456"}).json()["token"]
    assert anon.get("/api/users/U0001/home", headers=_bearer(token)).status_code == 200
    r = anon.get("/api/users/U0002/home", headers=_bearer(token))
    assert r.status_code == 403
    assert anon.post("/api/users/U0002/send", headers=_bearer(token),
                     json={"type": "send_money", "amount": 10}).status_code == 403


def test_public_routes_stay_open(anon):
    assert anon.get("/api/users").status_code == 200
    assert anon.get("/api/health").status_code == 200


def test_demo_reset_keeps_seeded_logins_but_drops_registered_ones(anon):
    seeded = anon.post("/api/auth/login", json={"mobile": "01700000001", "pin": "123456"}).json()["token"]
    otp = anon.post("/api/auth/register/start", json={"mobile": "01811223355"}).json()["otp"]
    new = anon.post("/api/auth/register/verify",
                    json={"mobile": "01811223355", "otp": otp, "name": "নতুন ইউজার", "pin": "246810"}).json()
    assert anon.post("/api/demo/reset", headers=_bearer(seeded)).status_code == 200
    assert anon.get("/api/users/U0001/shell", headers=_bearer(seeded)).status_code == 200
    assert anon.get(f"/api/users/{new['user_id']}/shell", headers=_bearer(new["token"])).status_code == 401


def test_demo_controls_need_a_login(anon):
    assert anon.post("/api/demo/reset").status_code == 401
    assert anon.post("/api/demo/time-travel", json={"days": 7}).status_code == 401
    token = anon.post("/api/auth/login", json={"mobile": "01700000002", "pin": "123456"}).json()["token"]
    assert anon.post("/api/demo/time-travel", json={"days": 7}, headers=_bearer(token)).status_code == 200


def test_registration_is_capped(anon, monkeypatch):
    import hishab.services as services
    monkeypatch.setattr(services, "MAX_REGISTERED_USERS", 1)
    otp = anon.post("/api/auth/register/start", json={"mobile": "01811000001"}).json()["otp"]
    assert anon.post("/api/auth/register/verify", json={"mobile": "01811000001", "otp": otp, "name": "প্রথম",
                                                        "pin": "246810"}).status_code == 200
    r = anon.post("/api/auth/register/start", json={"mobile": "01811000002"})
    assert r.status_code == 422 and "নতুন অ্যাকাউন্ট" in r.json()["detail"]


def test_parallel_verify_registers_once(anon):
    from concurrent.futures import ThreadPoolExecutor
    otp = anon.post("/api/auth/register/start", json={"mobile": "01811000003"}).json()["otp"]
    body = {"mobile": "01811000003", "otp": otp, "name": "দ্বিতীয়", "pin": "246810"}
    with ThreadPoolExecutor(6) as ex:
        codes = list(ex.map(lambda _: anon.post("/api/auth/register/verify", json=body).status_code, range(6)))
    assert codes.count(200) == 1
    assert [u["phone"] for u in anon.get("/api/users").json()].count("01811000003") == 1
