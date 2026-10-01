from datetime import date

from hishab.store.sqlite import UserState


def test_store_roundtrip_state(store):
    st = UserState()
    st.pockets["emergency"] = 1500.0
    st.paisa_on = True
    st.dps = {"monthly": 1000, "tenure_months": 24, "day": 8, "opened": "2026-09-01"}
    st.last_active = date(2026, 9, 10)
    store.save_state("U0001", st)
    back = store.get_state("U0001")
    assert back.pockets["emergency"] == 1500.0
    assert back.paisa_on is True
    assert back.dps["monthly"] == 1000
    assert back.last_active == date(2026, 9, 10)


def test_get_state_uses_default_factory_once(store):
    calls = []

    def factory():
        calls.append(1)
        s = UserState()
        s.pockets["emergency"] = 99.0
        return s

    assert store.get_state("U0009", factory).pockets["emergency"] == 99.0
    assert store.get_state("U0009", factory).pockets["emergency"] == 99.0
    assert len(calls) == 1


def test_store_reset_clears_everything(store):
    store.set_clock_offset(14)
    store.add_notification("U0001", {"id": "n1", "type": "reengage", "created": "2026-09-20"})
    store.add_sim_tx("U0001", {"amount": 10})
    store.record_response("U0001", "action", "save_on_payday", True)
    store.reset()
    assert store.clock_offset() == 0
    assert store.notifications("U0001") == []
    assert store.sim_tx("U0001") == []
    assert store.responses("U0001", "action") == []


def test_session_token_maps_to_user(store):
    token = store.create_session("U0001")
    assert store.session_user(token) == "U0001"
    assert store.session_user("nope") is None


def test_responses_and_categories(store):
    store.record_response("U0001", "lesson", "cashout_cost", False)
    assert store.responses("U0001", "lesson") == [("cashout_cost", False)]
    store.set_category("U0001", "M-001", "food_grocery")
    store.set_category("U0001", "M-001", "shopping")
    assert store.categories("U0001") == {"M-001": "shopping"}
