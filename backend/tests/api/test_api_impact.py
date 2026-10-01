def test_impact_serves_snapshot(client):
    r = client.get("/api/impact")
    assert r.status_code == 200
    body = r.json()
    assert "headline" in body and "fairness" in body and "models" in body
