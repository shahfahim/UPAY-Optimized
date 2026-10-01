from hishab.engine.savings import apply_paisa, paisa_sweep, update_paisa_pause
from hishab.store.sqlite import UserState


def test_paisa_sweep():
    assert paisa_sweep(6240.35) == (6240.00, 0.35)
    assert paisa_sweep(100.00) == (100.00, 0.0)
    assert paisa_sweep(0.99) == (0.0, 0.99)


def test_apply_paisa_respects_toggle_and_pause():
    st = UserState()
    assert apply_paisa(st, 6240.35) == (6240.35, 0.0)  # off
    st.paisa_on = True
    assert apply_paisa(st, 6240.35) == (6240.00, 0.35)
    assert st.pockets["paisa"] == 0.35
    st.paisa_paused = True
    assert apply_paisa(st, 10.5) == (10.5, 0.0)


def test_pause_on_risk_and_resume_on_income():
    st = UserState()
    st.paisa_on = True
    update_paisa_pause(st, "amber", income_today=False)
    assert st.paisa_paused is True
    update_paisa_pause(st, "amber", income_today=True)
    assert st.paisa_paused is False
    update_paisa_pause(st, "green", income_today=False)
    assert st.paisa_paused is False
