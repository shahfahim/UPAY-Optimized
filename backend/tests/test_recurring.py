from datetime import date

from hishab.engine.context import build_ctx
from hishab.engine.recurring import detect_recurring, next_income


def _events(repo, store, settings, uid):
    ctx = build_ctx(uid, repo, store, settings)
    return ctx, detect_recurring(ctx.tx, ctx.today)


def test_rina_salary_detected(repo, store, settings):
    _, ev = _events(repo, store, settings, "U0001")
    sal = [e for e in ev if e.kind == "salary"]
    assert len(sal) == 1
    assert 6 <= sal[0].day_of_month <= 8
    assert abs(sal[0].amount - 12500) / 12500 <= 0.05
    assert sal[0].direction == 1


def test_rent_detected(repo, store, settings):
    _, ev = _events(repo, store, settings, "U0001")
    rent = [e for e in ev if e.kind == "rent"]
    # due on the 5th, but deferred to payday (7th) when the balance is short
    assert rent and 5 <= rent[0].day_of_month <= 7 and rent[0].direction == -1


def test_remittance_detected_for_rina(repo, store, settings):
    _, ev = _events(repo, store, settings, "U0001")
    assert any(e.kind == "remittance" for e in ev)


def test_next_income_after_as_of(repo, store, settings):
    ctx, ev = _events(repo, store, settings, "U0001")
    nxt = next_income(ev, ctx.today)
    assert nxt is not None and nxt > ctx.today
    assert nxt == date(2026, 10, nxt.day) and 6 <= nxt.day <= 8


def test_irregular_earner_has_no_monthly_salary(repo, store, settings):
    _, ev = _events(repo, store, settings, "U0002")
    assert not [e for e in ev if e.kind == "salary"]
