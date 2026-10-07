from hishab.engine.agents import nearby_agents


def test_agents_need_own_token(anon, client):
    url = "/api/users/U0001/agents/nearby?lat=23.81&lng=90.41"
    assert anon.get(url).status_code == 401
    token = client.post("/api/auth/login", json={"mobile": "01700000001", "pin": "123456"}).json()["token"]
    assert anon.get(url.replace("U0001", "U0002"), headers={"Authorization": f"Bearer {token}"}).status_code == 403


def test_agents_are_deterministic_demo_rows(client):
    url = "/api/users/U0001/agents/nearby?lat=23.81&lng=90.41"
    a, b = client.get(url).json(), client.get(url).json()
    assert a == b and a and all(x["is_demo"] for x in a)
    assert [x["distance_m"] for x in a] == sorted(x["distance_m"] for x in a)
    assert "ai_liquidity_score" not in a[0]


def test_agents_reject_bad_coordinates(client):
    assert client.get("/api/users/U0001/agents/nearby?lat=123&lng=90").status_code == 422


def test_engine_distances_match_offsets():
    rows = nearby_agents(23.81, 90.41)
    assert rows[0]["name"] == "Rahim Store" and 100 < rows[0]["distance_m"] < 140
