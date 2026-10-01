from datetime import date, timedelta


def test_shell_rina(client):
    r = client.get("/api/users/U0001/shell")
    assert r.status_code == 200
    s = r.json()
    assert s["strip"] and len(s["recent"]) <= 4
    assert s["nav_badge"]["level"] in ("green", "amber", "red")
    assert s["avatar_initials"] and "•" in s["phone_masked"]


def test_home_rina(client):
    h = client.get("/api/users/U0001/home").json()
    assert len(h["actions"]) <= 3
    assert len(h["forecast"]["p50"]) == 30
    assert h["risk"]["level"] in ("amber", "red") and len(h["risk"]["drivers"]) == 3
    assert h["level"]["level"] == 0 and h["health"]["cash_dependency"] > 0


def test_home_unknown_404(client):
    r = client.get("/api/users/U9999/home")
    assert r.status_code == 404


def test_simulate_and_respond(client):
    sim = client.post("/api/users/U0001/actions/simulate", json={"action_id": "save_on_payday"})
    assert sim.status_code == 200 and len(sim.json()["forecast"]["p50"]) == 30
    assert client.post("/api/users/U0001/actions/simulate", json={"action_id": "borrow"}).status_code == 422
    ok = client.post("/api/users/U0001/actions/save_on_payday/respond", json={"accepted": True})
    assert ok.status_code == 200


def test_new_user_endpoints_do_not_crash(client, svc):
    """Review focus 1: a registered user with only ~10 days of history gets friendly empty states, not 500s."""
    from hishab.data.generator import generate_one
    user, tx = generate_one("N0099", "নতুন", seed=5)
    cutoff = date(2026, 9, 18) - timedelta(days=10)
    tx = [t for t in tx if t["ts"].date() > cutoff]
    user["demo_phone"] = "01999999999"
    svc.store.add_user(user, tx)
    for path in ["home", "shell"]:
        r = client.get(f"/api/users/N0099/{path}")
        assert r.status_code == 200, path
        assert r.json()["insufficient_history"] is True


def test_time_travel_caps_and_reset(client):
    """Review focus 4: repeated time-travel respects caps; reset restores the clock and clears notifications."""
    client.get("/api/users/U0001/shell")
    for days in (7, 7, 14, 30):
        assert client.post("/api/demo/time-travel", json={"days": days}).status_code == 200
        client.get("/api/users/U0001/shell")
    notes = client.get("/api/users/U0001/notifications").json()
    by_week: dict = {}
    for n in notes:
        week = date.fromisoformat(n["created"]).isocalendar()[:2]
        by_week.setdefault(week, []).append(n)
    for items in by_week.values():
        assert len(items) <= 3
        assert len([n for n in items if n["type"] == "reengage"]) <= 1
    assert any(n["type"] == "reengage" for n in notes)
    assert client.post("/api/demo/time-travel", json={"days": 5}).status_code == 422
    assert client.post("/api/demo/time-travel", json={"days": 7}).status_code == 422  # 58 + 7 > 60-day cap
    client.post("/api/demo/reset")
    assert client.get("/api/users/U0001/notifications").json() == []
    assert client.get("/api/users/U0001/shell").json()["today"] == "2026-09-18"
