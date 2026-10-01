"""Read-only tools the chat model may call. Every tool is scoped to the session user on the server side."""

from __future__ import annotations

from datetime import timedelta

import pandas as pd

from hishab.engine.text import CATEGORY_BN


def _schema(props: dict | None = None, required: list | None = None) -> dict:
    return {"type": "object", "properties": props or {}, "required": required or [], "additionalProperties": False}


_NUM = {"type": "number", "description": "Amount in taka"}

TOOLS: list[dict] = [
    {"name": "get_home_summary", "description": "Balance, shortfall risk, predicted shortfall date and amount, "
     "safe-to-spend today, next income date and the top suggested actions.", "input_schema": _schema()},
    {"name": "get_shortfall_drivers", "description": "The top reasons (in Bangla and English) behind the shortfall risk.",
     "input_schema": _schema()},
    {"name": "list_actions", "description": "Ranked suggested actions with their expected effect on risk and fees.",
     "input_schema": _schema()},
    {"name": "simulate_action", "description": "What-if: the forecast and risk if the user follows one suggested action.",
     "input_schema": _schema({"action_id": {"type": "string", "description": "id from list_actions"}}, ["action_id"])},
    {"name": "plan_goal", "description": "Feasibility of saving a target amount in a number of months.",
     "input_schema": _schema({"target": _NUM, "months": {"type": "integer", "description": "1 to 60"}},
                             ["target", "months"])},
    {"name": "plan_eid", "description": "Next Eid, last Eid's extra spending, expected bonus and a weekly saving plan.",
     "input_schema": _schema()},
    {"name": "get_budget_status", "description": "Budget vs spending per category for a period.",
     "input_schema": _schema({"period": {"type": "string", "enum": ["day", "week", "month"]}}, ["period"])},
    {"name": "find_route", "description": "Cheapest ways to send money (fees are demo assumptions) and costly habits.",
     "input_schema": _schema({"amount": _NUM, "destination": {"type": "string", "enum": [
         "other_mfs_wallet", "bank_account", "upay_wallet", "merchant", "agent_cash"]}}, ["amount", "destination"])},
    {"name": "get_transactions_summary", "description": "Income, spending by category and cash-out fees for a period.",
     "input_schema": _schema({"period": {"type": "string", "enum": ["week", "month"]}}, ["period"])},
    {"name": "get_health", "description": "Financial health indicators (emergency days, cash dependency, "
     "shortfall-free months) and detected habits.", "input_schema": _schema()},
    {"name": "get_readiness", "description": "Educational consistency signals with a disclaimer. Not a credit score.",
     "input_schema": _schema()},
    {"name": "get_lessons", "description": "Short personalised money lessons for this user.", "input_schema": _schema()},
    {"name": "get_levels", "description": "Savings level, streak and progress to the next level.",
     "input_schema": _schema()},
    {"name": "emergency_options", "description": "Ways to get emergency money in a safe order (own pockets first; "
     "a DPS-backed bank loan only under the bank's rule).", "input_schema": _schema({"amount": _NUM}, ["amount"])},
]
for _t in TOOLS:
    _t["strict"] = True

TOOL_NAMES = [t["name"] for t in TOOLS]


def _home(uid, svc, cache) -> dict:
    if "home" not in cache:
        cache["home"] = svc.home(uid)
    return cache["home"]


def _tx_summary(uid, svc, period: str) -> dict:
    ctx = svc.ctx(uid)
    days = 7 if period == "week" else 30
    d = pd.to_datetime(ctx.tx["ts"]).dt.date
    t = ctx.tx[d > ctx.today - timedelta(days=days)]
    internal = ["pocket_in", "pocket_out", "dps_installment", "dps_installment_missed", "cash_in"]
    spend = t[(t.direction == -1) & ~t.type.isin(internal)]
    by_cat = spend.groupby("category")["amount"].sum().sort_values(ascending=False)
    income = t[(t.direction == 1) & (t.category == "income")]["amount"].sum()
    co = t[t.type == "cash_out"]
    return {"user_id": uid, "period_days": days, "income_total": round(float(income)),
            "spend_total": round(float(spend["amount"].sum())),
            "by_category": [{"category": c, "category_bn": CATEGORY_BN.get(c, c), "amount": round(float(v))}
                            for c, v in by_cat.items()],
            "cash_out_count": int(len(co)), "cash_out_fees": round(float(co["fee"].sum()))}


def run_tool(name: str, args: dict, uid: str, svc, cache: dict | None = None) -> dict:
    """Execute a tool for the session user. Any `user_id` the model passes is ignored."""
    cache = {} if cache is None else cache
    args = dict(args or {})
    args.pop("user_id", None)
    if name == "get_home_summary":
        h = _home(uid, svc, cache)
        risk, fc = h.get("risk") or {}, h.get("forecast") or {}
        return {"user_id": uid, "today": h["today"], "balance": h["balance"],
                "insufficient_history": h["insufficient_history"], "risk_level": risk.get("level"),
                "risk_probability": risk.get("prob"), "shortfall_date": fc.get("shortfall_date"),
                "shortfall_amount": fc.get("shortfall_amount"), "safe_to_spend_today": h.get("safe_today"),
                "daily_budget_until_income": h.get("daily_budget"), "next_income": h.get("next_income"),
                "top_actions": [a["title_bn"] for a in h.get("actions", [])]}
    if name == "get_shortfall_drivers":
        risk = _home(uid, svc, cache).get("risk") or {}
        return {"user_id": uid, "risk_level": risk.get("level"), "drivers": risk.get("drivers", [])}
    if name == "list_actions":
        return {"user_id": uid, "actions": [{k: a[k] for k in ("id", "title_bn", "why_bn", "risk_before", "risk_after",
                                                               "fees_saved")} for a in _home(uid, svc, cache)["actions"]]}
    if name == "simulate_action":
        s = svc.simulate(uid, str(args.get("action_id", "")))
        return {"user_id": uid, "action_id": s["action_id"], "shortfall_date": s["forecast"]["shortfall_date"],
                "shortfall_amount": s["forecast"]["shortfall_amount"], "risk_after": s["risk"]}
    if name == "plan_goal":
        return {"user_id": uid, **svc.plan_goal(uid, args.get("target"), args.get("months"))}
    if name == "plan_eid":
        return {"user_id": uid, **svc.savings(uid)["eid_plan"]}
    if name == "get_budget_status":
        return {"user_id": uid, **svc.budget(uid, str(args.get("period", "month")))}
    if name == "find_route":
        return {"user_id": uid, **svc.route(uid, args.get("amount"), str(args.get("destination", "other_mfs_wallet")))}
    if name == "get_transactions_summary":
        return _tx_summary(uid, svc, str(args.get("period", "month")))
    if name == "get_health":
        h = svc.health(uid)
        return {"user_id": uid, "current": h.get("current"), "previous": h.get("previous"),
                "habits": [x["text_bn"] for x in h.get("habits", [])], "monthly_report": h.get("monthly_report")}
    if name == "get_readiness":
        return {"user_id": uid, **svc.readiness(uid)}
    if name == "get_lessons":
        return {"user_id": uid, "lessons": svc.lessons(uid)[:3]}
    if name == "get_levels":
        return {"user_id": uid, **svc.levels(uid)}
    if name == "emergency_options":
        return {"user_id": uid, **svc.emergency(uid, args.get("amount"))}
    raise ValueError(f"unknown tool: {name}")
