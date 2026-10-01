import pytest

from hishab.engine.context import build_ctx
from hishab.engine.route import detect_costly_habits, edge_fee, routes

HAND = {
    "labels_bn": {"upay_wallet": "upay", "x": "X", "y": "Y", "dest": "D"},
    "edges": [
        {"from": "upay_wallet", "to": "x", "fixed": 10, "pct": 0, "min": 0, "max": 100, "minutes": 1},
        {"from": "x", "to": "dest", "fixed": 0, "pct": 0, "min": 0, "max": 0, "minutes": 1},
        {"from": "upay_wallet", "to": "y", "fixed": 5, "pct": 0, "min": 0, "max": 100, "minutes": 9},
        {"from": "y", "to": "dest", "fixed": 1, "pct": 0, "min": 0, "max": 100, "minutes": 9},
        {"from": "upay_wallet", "to": "dest", "fixed": 20, "pct": 0, "min": 0, "max": 100, "minutes": 1},
    ],
}


def test_cheapest_first_on_hand_table():
    r = routes(1000, "dest", HAND)
    assert [x.nodes for x in r] == [["upay_wallet", "y", "dest"], ["upay_wallet", "x", "dest"],
                                    ["upay_wallet", "dest"]]
    assert [x.fee for x in r] == [6.0, 10.0, 20.0]
    assert r[0].label_bn == "upay → Y → D"


def test_edge_fee_clamped():
    e = {"fixed": 0, "pct": 0.5, "min": 5, "max": 50}
    assert edge_fee(e, 100) == 5.0
    assert edge_fee(e, 4000) == 20.0
    assert edge_fee(e, 100000) == 50.0


def test_real_fees_npsb_cheaper_than_cashout_for_other_wallet():
    r = routes(5000, "other_mfs_wallet")
    assert r[0].nodes == ["upay_wallet", "npsb", "other_mfs_wallet"]
    assert r[-1].nodes == ["upay_wallet", "agent_cash", "other_mfs_wallet"]
    assert r[0].fee < r[-1].fee


def test_rina_has_cash_remittance_habit(repo, store, settings):
    habits = detect_costly_habits(build_ctx("U0001", repo, store, settings))
    assert habits and habits[0].annual_saving > 0
    assert habits[0].best_fee < habits[0].current_fee


def test_routes_to_unknown_destination_empty():
    assert routes(1000, "moon") == []


def test_invalid_amount_raises():
    with pytest.raises(ValueError):
        routes(0, "other_mfs_wallet")
