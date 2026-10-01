def test_health_route(client):
    h = client.get("/api/users/U0001/health").json()
    assert len(h["trend6"]) == 6 and h["habits"] and "went_well_bn" in h["monthly_report"]


def test_lessons_and_respond(client):
    lessons = client.get("/api/users/U0001/lessons").json()
    assert lessons and "{" not in lessons[0]["body_bn"]
    r = client.post(f"/api/users/U0001/lessons/{lessons[0]['id']}/respond", json={"accepted": False})
    assert r.status_code == 200


def test_readiness_route(client):
    r = client.get("/api/users/U0001/readiness").json()
    assert len(r["signals"]) == 5 and r["disclaimer_bn"]
    assert "score" not in r


def test_levels_route(client):
    lv = client.get("/api/users/U0005/levels").json()
    assert lv["level"] >= 1 and lv["dps_ready"] is True


def test_calendar_route(client):
    cal = client.get("/api/users/U0001/calendar", params={"month": "2026-09"}).json()
    days = {d["date"]: d for d in cal["days"]}
    assert len(days) == 30
    assert days["2026-09-07"]["predicted"] is False and days["2026-09-07"]["in_total"] > 0
    assert days["2026-09-25"]["predicted"] is True and days["2026-09-25"]["risk"] in ("green", "amber", "red")
    assert client.get("/api/users/U0001/calendar", params={"month": "2026-13"}).status_code == 422


def test_budget_auto_and_manual(client):
    auto = client.get("/api/users/U0001/budget", params={"period": "month"}).json()
    assert auto["mode"] == "auto" and auto["items"] and auto["reason_bn"]
    assert client.put("/api/users/U0001/budget", json={"mode": "manual", "manual": {"food_grocery": 3000}}).status_code == 200
    man = client.get("/api/users/U0001/budget", params={"period": "week"}).json()
    food = next(i for i in man["items"] if i["category"] == "food_grocery")
    assert man["mode"] == "manual" and food["budget"] == 700
    assert client.put("/api/users/U0001/budget", json={"mode": "manual", "manual": {"food_grocery": -5}}).status_code == 422
    assert client.get("/api/users/U0001/budget", params={"period": "year"}).status_code == 422


def test_transactions_route(client):
    r = client.get("/api/users/U0001/transactions", params={"limit": 20}).json()
    assert len(r["items"]) == 20
    first = r["items"][0]
    assert {"ts", "type", "name", "amount", "direction", "fee", "category", "category_bn"} <= set(first)
    assert r["items"][0]["ts"] >= r["items"][-1]["ts"]  # newest first
    assert r["summary"]["by_category"] and r["summary"]["income_total"] > 0
    assert client.get("/api/users/U0001/transactions", params={"limit": 0}).status_code == 422
