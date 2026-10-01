def test_chat_fallback_route(client):
    r = client.post("/api/users/U0001/chat", json={"message": "মাসের শেষে টাকা কম পড়ে কেন?"})
    assert r.status_code == 200
    body = r.json()
    assert body["text"] and body["ai"] is False and body["numbers_source"] == "engine"


def test_chat_too_long_422(client):
    assert client.post("/api/users/U0001/chat", json={"message": "x" * 501}).status_code == 422


def test_chat_rate_limit_429(client):
    codes = [client.post("/api/users/U0003/chat", json={"message": "হিসাব"}).status_code for _ in range(11)]
    assert codes[:10] == [200] * 10 and codes[10] == 429
