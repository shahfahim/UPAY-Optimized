"""Money moves must not race: parallel requests for one user see each other's balance changes."""

from concurrent.futures import ThreadPoolExecutor


def _parallel(fn, n=12):
    with ThreadPoolExecutor(n) as ex:
        return list(ex.map(lambda _: fn(), range(n)))


def test_parallel_sends_each_reduce_the_balance(client):
    start = client.get("/api/users/U0001/savings").json()["balance"]
    codes = _parallel(lambda: client.post("/api/users/U0001/send", json={
        "type": "send_money", "amount": 10, "counterparty_id": "P1", "category": "other"}).status_code)
    end = client.get("/api/users/U0001/savings").json()["balance"]
    assert round(start - end, 2) == 10 * codes.count(200)
    assert codes.count(200) > 0


def test_parallel_pocket_withdrawals_cannot_exceed_the_pocket(client):
    move = "/api/users/U0001/savings/pockets/family/move"
    assert client.post(move, json={"direction": "in", "amount": 30}).status_code == 200
    start = client.get("/api/users/U0001/savings").json()["balance"]
    codes = _parallel(lambda: client.post(move, json={"direction": "out", "amount": 10}).status_code)
    assert codes.count(200) == 3
    after = client.get("/api/users/U0001/savings").json()
    assert after["balance"] == round(start + 30, 2)
    assert next(p for p in after["pockets"] if p["name"] == "family")["balance"] == 0
