import pytest



@pytest.mark.parametrize("bad", [0, -5, "abc", 10_000_001])
def test_amount_validation(client, bad):
    """Review focus 2: invalid amounts are 422 everywhere, never 500."""
    assert client.post("/api/users/U0001/send", json={"type": "merchant_pay", "amount": bad}).status_code == 422
    assert client.post("/api/users/U0001/emergency/options", json={"amount": bad}).status_code == 422
    assert client.post("/api/users/U0001/goals/plan", json={"target": bad, "months": 6}).status_code == 422
    assert client.post("/api/users/U0005/dps/open", json={"monthly": bad, "tenure_months": 12}).status_code == 422
    assert client.post("/api/users/U0001/route", json={"amount": bad}).status_code == 422


def test_send_more_than_balance_400(client):
    bal = client.get("/api/users/U0001/home").json()["balance"]
    r = client.post("/api/users/U0001/send", json={"type": "merchant_pay", "amount": bal + 1000})
    assert r.status_code == 400 and r.json()["detail"] == "পর্যাপ্ত ব্যালেন্স নেই"


def test_send_applies_paisa_and_category(client):
    client.put("/api/users/U0001/savings/paisa", json={"on": True})
    r = client.post("/api/users/U0001/send", json={"type": "merchant_pay", "amount": 100.35,
                                                   "counterparty_id": "M-001", "category": "food_grocery"}).json()
    assert r["balance"] == int(r["balance"])  # paisa swept from the remaining balance
    assert r["category"] == "food_grocery"
    sugg = client.post("/api/users/U0001/category/suggest", json={"counterparty_id": "M-001",
                                                                 "counterparty_type": "merchant", "amount": 50}).json()
    assert sugg[0]["category"] == "food_grocery"


def test_cashout_nudge_at_most_one(client):
    r = client.post("/api/users/U0001/send", json={"type": "cash_out", "amount": 500}).json()
    assert r["fee"] > 0
    assert r["nudge"] is None or isinstance(r["nudge"], dict)


def test_route_npsb_cheapest(client):
    r = client.post("/api/users/U0001/route", json={"amount": 5000, "destination": "other_mfs_wallet"}).json()
    assert r["routes"][0]["nodes"] == ["upay_wallet", "npsb", "other_mfs_wallet"]
    assert r["habits"] and r["habits"][0]["annual_saving"] > 0


def test_category_confirm_validation(client):
    assert client.post("/api/users/U0001/category/confirm", json={"counterparty_id": "M-001",
                                                                 "category": "spaceships"}).status_code == 422
    assert client.post("/api/users/U0001/category/confirm", json={"counterparty_id": "M-001",
                                                                 "category": "shopping"}).status_code == 200


def test_send_uses_selected_route_fee(client):
    """A route picked on the money map is the one charged — not silently the cheapest."""
    routes = client.post("/api/users/U0001/route", json={"amount": 500, "destination": "other_mfs_wallet"}).json()["routes"]
    via_agent = next(r for r in routes if "agent_cash" in r["nodes"])
    r = client.post("/api/users/U0001/send", json={"type": "npsb", "amount": 500, "destination": "other_mfs_wallet",
                                                   "route": via_agent["nodes"]})
    assert r.status_code == 200 and r.json()["fee"] == via_agent["fee"]
    r = client.post("/api/users/U0001/send", json={"type": "npsb", "amount": 500, "destination": "other_mfs_wallet"})
    assert r.json()["fee"] == routes[0]["fee"]


def test_send_rejects_unknown_route(client):
    r = client.post("/api/users/U0001/send", json={"type": "npsb", "amount": 500, "destination": "other_mfs_wallet",
                                                   "route": ["upay_wallet", "bank_card"]})
    assert r.status_code == 422
