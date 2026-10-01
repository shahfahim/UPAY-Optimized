"""F9 notification triggers (with caps and opt-out) and the I2 header message strip."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import date, timedelta

import pandas as pd

from hishab.engine.text import POCKET_BN, bn_num
from hishab.rules import load_rules


@dataclass
class Notification:
    id: str
    type: str
    created: date
    text_bn: str
    text_en: str
    ai: bool = False
    link: str = "/app/hishab"


@dataclass
class StripMessage:
    priority: int
    text_bn: str
    text_en: str
    link: str


def _as_notif(n) -> Notification:
    if isinstance(n, Notification):
        return n
    created = n["created"] if isinstance(n["created"], date) else date.fromisoformat(str(n["created"]))
    return Notification(n["id"], n["type"], created, n.get("text_bn", ""), n.get("text_en", ""), n.get("ai", False),
                        n.get("link", "/app/hishab"))


def _reengage_hook(ctx, recurring) -> tuple[str, str]:
    eid_bal = float(ctx.state.pockets.get("eid", 0.0))
    goal = (ctx.state.pocket_goals or {}).get("eid", {}).get("target")
    if eid_bal > 0 and goal:
        pct = round(100 * eid_bal / goal)
        left = max(0.0, goal - eid_bal)
        return (f"তোমার ঈদ পকেট {bn_num(pct)}% পূর্ণ — আর ৳{bn_num(left)} বাকি।",
                f"your Eid pocket is {pct}% full — ৳{round(left):,} to go.")
    sal = [e for e in recurring if e.kind == "salary"]
    if sal:
        d = sal[0].next_date
        return (f"বেতন আসার কথা {bn_num(d.day)} তারিখে — এই মাসের পরিকল্পনা দেখো।",
                f"your salary is due on the {d.day} — see this month's plan.")
    return ("তোমার হিসাবে নতুন তথ্য আছে — একবার দেখে যাও।", "there's something new in your Hishab — take a look.")


def evaluate_triggers(ctx, risk, recurring, level, history: list, last_active: date | None) -> list[Notification]:
    rules = load_rules("notifications")
    caps, trig = rules["caps"], rules["triggers"]
    hist = [_as_notif(n) for n in history]
    seen = {n.id for n in hist}
    week_start = ctx.today - timedelta(days=6)
    week = [n for n in hist if n.created >= week_start]
    total, reeng = len(week), len([n for n in week if n.type == "reengage"])
    optout = set(ctx.state.notif_optout or [])
    name = str(ctx.user.get("synthetic_name", "")).split(" ")[0]
    cands: list[Notification] = []

    def add(typ: str, key: str, bn: str, en: str):
        nid = f"{typ}:{key}"
        if typ in optout or nid in seen:
            return
        cands.append(Notification(nid, typ, ctx.today, bn, en, False, trig[typ]["link"]))

    if risk.level == "red":
        days = max(1, (risk.shortfall_date - ctx.today).days) if risk.shortfall_date else 7
        wk = ctx.today.isocalendar()
        add("risk_red", f"{wk[0]}-{wk[1]}", trig["risk_red"]["text_bn"].format(days=bn_num(days)),
            trig["risk_red"]["text_en"].format(days=days))
    for e in recurring:
        dd = (e.next_date - ctx.today).days
        if e.direction < 0 and e.kind in ("bill", "dps") and 0 < dd <= trig["bill_due"]["days"]:
            add("bill_due", f"{e.counterparty_id}:{e.next_date}",
                trig["bill_due"]["text_bn"].format(name=e.counterparty_name, days=bn_num(dd)),
                trig["bill_due"]["text_en"].format(name=e.counterparty_name, days=dd))
    if not ctx.tx.empty:
        today_rows = ctx.tx[pd.to_datetime(ctx.tx["ts"]).dt.date == ctx.today]
        if (today_rows["type"] == "salary_in").any():
            add("salary_plan", str(ctx.today), trig["salary_plan"]["text_bn"], trig["salary_plan"]["text_en"])
    for m in level.milestones:
        if m["reached"]:
            add("level_milestone", str(m["days"]), trig["level_milestone"]["text_bn"].format(badge=m["badge_bn"]),
                trig["level_milestone"]["text_en"].format(badge=f"{m['days']}-day saver"))
    for pocket, goal in (ctx.state.pocket_goals or {}).items():
        target = float(goal.get("target") or 0)
        bal = float(ctx.state.pockets.get(pocket, 0))
        if target > 0 and 0.8 * target <= bal < target:
            add("pocket_80", pocket,
                trig["pocket_80"]["text_bn"].format(pocket_bn=POCKET_BN.get(pocket, pocket),
                                                    pct=bn_num(100 * bal / target), left=bn_num(target - bal)),
                trig["pocket_80"]["text_en"].format(pocket_en=pocket, pct=round(100 * bal / target),
                                                    left=f"{round(target - bal):,}"))
    if last_active is not None:
        idle = (ctx.today - last_active).days
        crossed = [t for t in trig["reengage"]["days"] if idle >= t]
        if crossed:
            t = max(crossed)
            hb, he = _reengage_hook(ctx, recurring)
            add("reengage", f"{t}:{last_active}", trig["reengage"]["text_bn"].format(name=name, hook_bn=hb),
                trig["reengage"]["text_en"].format(name=name, hook_en=he))

    out = []
    for n in cands:
        if total >= caps["total_per_week"]:
            break
        if n.type == "reengage":
            if reeng >= caps["reengage_per_week"]:
                continue
            reeng += 1
        out.append(n)
        total += 1
    return out


def message_strip(ctx, risk, safe_today: float, budget_daily: float, shortcuts: list, lesson, level,
                  next_income: date | None) -> list[StripMessage]:
    msgs: list[StripMessage] = []
    days_left = max(1, (risk.shortfall_date - ctx.today).days) if risk.shortfall_date else None
    to_income = (next_income - ctx.today).days if next_income else None
    if risk.level == "red":
        bn = f"সাবধান: টাকা আর প্রায় {bn_num(days_left or 3)} দিন চলবে"
        en = f"Heads up: money may last about {days_left or 3} more days"
        msgs.append(StripMessage(1, bn, en, "/app/hishab"))
    for s in shortcuts:
        if s.due_in_days:
            msgs.append(StripMessage(2, f"{s.name} {bn_num(s.due_in_days)} দিনের মধ্যে দিতে হবে",
                                     f"{s.name} due in {s.due_in_days} days", "/app/home"))
            break
    if risk.level == "amber":
        bn = f"টাকা আর প্রায় {bn_num(days_left)} দিন চলবে" if days_left else "মাসের শেষে টানাটানির ঝুঁকি আছে"
        en = f"Money may last about {days_left} more days" if days_left else "Some risk of running short this month"
        if to_income:
            bn += f" · বেতন {bn_num(to_income)} দিন পরে"
            en += f" · income in {to_income} days"
        msgs.append(StripMessage(3, bn, en, "/app/hishab"))
    if safe_today > 0:
        msgs.append(StripMessage(4, f"আজ নিরাপদ খরচ ৳{bn_num(safe_today)}", f"Safe to spend today ৳{round(safe_today):,}",
                                 "/app/hishab"))
    elif budget_daily > 0:
        msgs.append(StripMessage(4, f"আজ দিনে ৳{bn_num(budget_daily)}-এর মধ্যে খরচ রাখো",
                                 f"Keep today's spending under ৳{round(budget_daily):,}", "/app/hishab"))
    if level is not None and level.next_level == 1 and level.projection_days:
        msgs.append(StripMessage(5, f"সঞ্চয় লেভেল ১ আর {bn_num(level.projection_days)} দিন দূরে",
                                 f"Savings level 1 is {level.projection_days} days away", "/app/savings/levels"))
    elif lesson is not None:
        msgs.append(StripMessage(5, lesson.title_bn, lesson.title_bn, "/app/hishab/learn"))
    msgs.sort(key=lambda m: m.priority)
    return msgs
