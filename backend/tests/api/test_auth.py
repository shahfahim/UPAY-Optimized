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
    uid = done.json()["user_id"]
    home = client.get(f"/api/users/{uid}/home").json()
    assert home["insufficient_history"] is False and home["forecast"] is not None
    relog = client.post("/api/auth/login", json={"mobile": "01811223344", "pin": "246810"})
    assert relog.status_code == 200 and relog.json()["user_id"] == uid
