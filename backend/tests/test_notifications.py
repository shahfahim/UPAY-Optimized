from dataclasses import replace
from datetime import date, timedelta

from hishab.engine.context import build_ctx
from hishab.engine.levels import LevelStatus
from hishab.engine.notifications import Notification, evaluate_triggers, message_strip
from hishab.engine.recurring import detect_recurring
from hishab.engine.risk import RiskResult
from hishab.engine.shortcuts import Shortcut
from hishab.rules import contains_forbidden

GREEN = RiskResult(prob=0.1, level="green")
RED = RiskResult(prob=0.8, level="red", shortfall_date=date(2026, 9, 24), shortfall_amount=1800)
LV0 = LevelStatus(level=0, name_bn="শুরু", streak_days=0,
                  milestones=[{"days": 5, "reached": False, "badge_bn": "৫ দিনের সঞ্চয়"}])


def _ctx(repo, store, settings, uid="U0001"):
    return build_ctx(uid, repo, store, settings)


def test_reengage_7_14_30(repo, store, settings):
    ctx = _ctx(repo, store, settings)
    rec = detect_recurring(ctx.tx, ctx.today)
    for days in (7, 14, 30):
        new = evaluate_triggers(ctx, GREEN, rec, LV0, [], last_active=ctx.today - timedelta(days=days))
        re = [n for n in new if n.type == "reengage"]
        assert len(re) == 1 and str(days) in re[0].id
    assert not [n for n in evaluate_triggers(ctx, GREEN, rec, LV0, [], last_active=ctx.today - timedelta(days=3))
                if n.type == "reengage"]


def test_caps_hold(repo, store, settings):
    ctx = _ctx(repo, store, settings)
    rec = detect_recurring(ctx.tx, ctx.today)
    history: list[Notification] = []
    for day in range(5):  # five trigger rounds within one week
        c = replace(ctx, today=ctx.today + timedelta(days=day))
        history += evaluate_triggers(c, RED, rec, LV0, history, last_active=c.today - timedelta(days=30))
    week = [n for n in history if n.created > ctx.today + timedelta(days=4) - timedelta(days=7)]
    assert len(week) <= 3
    assert len([n for n in week if n.type == "reengage"]) <= 1


def test_no_duplicate_notifications(repo, store, settings):
    ctx = _ctx(repo, store, settings)
    rec = detect_recurring(ctx.tx, ctx.today)
    first = evaluate_triggers(ctx, RED, rec, LV0, [], last_active=None)
    again = evaluate_triggers(ctx, RED, rec, LV0, first, last_active=None)
    assert not ({n.id for n in first} & {n.id for n in again})


def test_optout_respected(repo, store, settings):
    ctx = _ctx(repo, store, settings)
    ctx.state.notif_optout = ["reengage", "risk_red"]
    new = evaluate_triggers(ctx, RED, detect_recurring(ctx.tx, ctx.today), LV0, [],
                            last_active=ctx.today - timedelta(days=30))
    assert not [n for n in new if n.type in ("reengage", "risk_red")]


def _strip(ctx, risk):
    bill = Shortcut("BILL-electric", "বিদ্যুৎ বিল", "bill_pay", "utilities", 600.0, due_in_days=3)
    return message_strip(ctx, risk, safe_today=210, budget_daily=120, shortcuts=[bill], lesson=None, level=LV0,
                         next_income=date(2026, 10, 7))


def test_strip_priority_order(repo, store, settings):
    s = _strip(_ctx(repo, store, settings), RED)
    assert [m.priority for m in s] == sorted(m.priority for m in s)
    assert s[0].priority == 1 and s[1].priority == 2


def test_strip_risk_message_has_no_taka_amount(repo, store, settings):
    ctx = _ctx(repo, store, settings)
    for risk in (RED, replace(RED, level="amber", prob=0.45)):
        for m in _strip(ctx, risk):
            if m.priority in (1, 3):
                assert "৳" not in m.text_bn


def test_no_forbidden_phrases(repo, store, settings):
    ctx = _ctx(repo, store, settings)
    new = evaluate_triggers(ctx, RED, detect_recurring(ctx.tx, ctx.today), LV0, [],
                            last_active=ctx.today - timedelta(days=14))
    for n in new:
        assert not contains_forbidden(n.text_bn + n.text_en)
    for m in _strip(ctx, RED):
        assert not contains_forbidden(m.text_bn)
