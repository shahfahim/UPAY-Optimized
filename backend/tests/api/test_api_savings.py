import pytest


def test_savings_overview(client):
    s = client.get("/api/users/U0005/savings").json()
    names = [p["name"] for p in s["pockets"]]
    assert names[:2] == ["emergency", "eid"] and s["pockets"][0]["balance"] > 0
    assert {"on", "paused", "total"} <= set(s["paisa"]) and s["eid_plan"]["days_left"] > 0


def test_pocket_move_and_withdraw_always_allowed(client):
    before = client.get("/api/users/U0001/home").json()["balance"]
    assert client.post("/api/users/U0001/savings/pockets/eid/move", json={"direction": "in", "amount": 500}).status_code == 200
    s = client.get("/api/users/U0001/savings").json()
    assert next(p for p in s["pockets"] if p["name"] == "eid")["balance"] == 500
    assert client.get("/api/users/U0001/home").json()["balance"] == pytest.approx(before - 500)
    assert client.post("/api/users/U0001/savings/pockets/eid/move", json={"direction": "out", "amount": 200}).status_code == 200
    over = client.post("/api/users/U0001/savings/pockets/eid/move", json={"direction": "out", "amount": 999})
    assert over.status_code == 400
    assert client.post("/api/users/U0001/savings/pockets/moon/move", json={"direction": "in", "amount": 1}).status_code == 422


def test_paisa_toggle_and_goal(client):
    assert client.put("/api/users/U0001/savings/paisa", json={"on": True}).json()["paisa"]["on"] is True
    g = client.post("/api/users/U0001/goals/plan", json={"target": 30000, "months": 6, "pocket": "education"}).json()
    assert g["monthly"] == 5000 and 0 <= g["feasibility"] <= 1
    s = client.get("/api/users/U0001/savings").json()
    assert next(p for p in s["pockets"] if p["name"] == "education")["goal"]["target"] == 30000


def test_dps_advice_not_now_for_rina(client):
    adv = client.post("/api/users/U0001/dps/advice", json={}).json()
    assert adv["status"] == "not_now"


def test_dps_open(client):
    bad = client.post("/api/users/U0005/dps/open", json={"monthly": 777, "tenure_months": 12})
    assert bad.status_code == 422
    ok = client.post("/api/users/U0005/dps/open", json={"monthly": 1000, "tenure_months": 12})
    assert ok.status_code == 200 and ok.json()["dps"]["monthly"] == 1000
    assert client.post("/api/users/U0005/dps/open", json={"monthly": 1000, "tenure_months": 12}).status_code == 422


def test_emergency_route(client):
    client.post("/api/users/U0001/savings/pockets/emergency/move", json={"direction": "in", "amount": 300})
    r = client.post("/api/users/U0001/emergency/options", json={"amount": 2000}).json()
    assert r["options"][0]["kind"] == "emergency_pocket" and r["note_bn"]
