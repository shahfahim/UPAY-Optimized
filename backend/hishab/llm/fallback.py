"""Template answers from engine outputs — used when the LLM is off, slow, failing, or unsafe. Never breaks."""

from __future__ import annotations

import re
from datetime import date

from hishab.engine.text import bn_digits, bn_num
from hishab.llm.tools import run_tool

_BN_TO_ASCII = str.maketrans("০১২৩৪৫৬৭৮৯", "0123456789")

_INTENTS = [
    # --- existing intents (expanded with Banglish) ---
    ("emergency",     r"জরুরি|ইমার্জেন্সি|emergency|ঋণ|loan|ধার|dorkar|urgent|help lagbe"),
    ("dps",           r"dps|ডিপিএস|deposit|মাসিক জমা"),
    ("eid",           r"ঈদ|eid|festival|bonos|বোনাস"),
    ("goal",          r"জমা|জমাতে|সঞ্চয়|save|saving|goal|লক্ষ্য|target|joma|bachabo|bachaibo"),
    ("cashout",       r"cash.?out|ক্যাশ ?আউট|ক্যাশআউট|agent|এজেন্ট|fee|ফি"),
    ("transactions",  r"লেনদেন|transaction|বুঝিয়ে|খরচ কোথায়|কোথায় খরচ|history|hisab|হিসাব দেখা|kharoch"),
    ("shortfall",     r"কম পড়|শেষে|short|month.?end|টানাটানি|চলবে|taka nei|taka shesh|টাকা নেই|শেষ হয়"),
    # --- new intents ---
    ("safe_spend",    r"নিরাপদ খরচ|safe.?spend|aaj koto|আজ কত|আজকে কত|kharoch korte parbo|খরচ করতে পারব"),
    ("balance",       r"balance|belence|balence|ব্যালেন্স|taka ache|টাকা আছে|koto taka|কত টাকা|wallet e koto"),
    ("budget",        r"budget|বাজেট|plan|পরিকল্পনা|mas er plan|মাসের পরিকল্পনা|income|আয়"),
    ("savings_level", r"level|লেভেল|dps.?ready|sanchoy level|সঞ্চয় লেভেল|badge|streak"),
    ("pocket",        r"pocket|পকেট|amar pocket|আমার পকেট|joma ache|জমা আছে|goal pocket"),
    ("greeting",      r"^hi$|^hello$|^hey$|^হ্যালো$|^হাই$|^সালাম$|salam|ki khobor|kemn|kmn|কেমন"),
]


def _numbers(text: str) -> list[tuple[float, int]]:
    t = text.translate(_BN_TO_ASCII).replace(",", "")
    return [(float(m.group()), m.end()) for m in re.finditer(r"\d+(?:\.\d+)?", t)]


def _parse_goal(text: str) -> tuple[float, int]:
    t = text.translate(_BN_TO_ASCII).replace(",", "")
    months = 6
    m = re.search(r"(\d+)\s*(?:মাস|month)", t)
    if m:
        months = int(m.group(1))
    amounts = [n for n, _ in _numbers(text) if n >= 100]
    return (max(amounts) if amounts else 30000.0), max(1, min(60, months))


def _day(iso: str | None) -> str:
    """'2026-09-29' -> '২৯ তারিখের'."""
    if not iso:
        return ""
    return f"{bn_digits(date.fromisoformat(iso).day)} তারিখের"


def answer(uid: str, message: str, svc) -> dict:
    text_l = message.lower()
    intent = next((name for name, pat in _INTENTS if re.search(pat, text_l)), "unknown")
    used: list[dict] = []
    cache: dict = {}

    def tool(name, **args):
        out = run_tool(name, args, uid, svc, cache)
        used.append({"name": name, "result": out})
        return out

    if intent == "goal":
        target, months = _parse_goal(message)
        g = tool("plan_goal", target=target, months=months)
        if g.get("insufficient_history"):
            text = "লক্ষ্যের হিসাব করতে আরও কিছু দিনের লেনদেন লাগবে।"
        else:
            text = f"৳{bn_num(target)} {bn_num(months)} মাসে জমাতে মাসে ৳{bn_num(g['monthly'])} লাগবে। "
            if g["feasibility"] < 0.05:
                text += ("লক্ষ্যটা বর্তমানে একটু কঠিন। আগে ছোট লক্ষ্য দিয়ে শুরু করো — সময় বাড়ালে বা জমার পরিমাণ কমালে সহজ হবে।")
            else:
                text += f"তোমার আয়-খরচ অনুযায়ী এটা পারার সম্ভাবনা {bn_num(100 * g['feasibility'])}%।"
                if g["feasibility"] < 0.5:
                    text += " সময় বাড়ালে বা লক্ষ্য কমালে আরও সহজ হবে।"
    elif intent == "cashout":
        tx = tool("get_transactions_summary", period="month")
        route = tool("find_route", amount=5000, destination="other_mfs_wallet")
        text = (f"গত ৩০ দিনে {bn_num(tx['cash_out_count'])} বার cash-out ফি দিয়েছ প্রায় "
                f"৳{bn_num(tx['cash_out_fees'])}। দোকানে সরাসরি পেমেন্ট করলে ফি বাঁচে।")
        if route["habits"]:
            text += f" বাড়িতে NPSB দিয়ে টাকা পাঠালে বছরে ৳{bn_num(route['habits'][0]['annual_saving'])} বাঁচবে।"
    elif intent == "transactions":
        tx = tool("get_transactions_summary", period="month")
        top = ", ".join(f"{c['category_bn']}" for c in tx["by_category"][:2])
        text = (f"গত ৩০ দিনে আয় ৳{bn_num(tx['income_total'])}, খরচ ৳{bn_num(tx['spend_total'])}। "
                f"বেশি খরচ হয়েছে: {top}।")
    elif intent == "emergency":
        amounts = [n for n, _ in _numbers(message) if n >= 100]
        e = tool("emergency_options", amount=max(amounts) if amounts else 2000)
        if e["options"]:
            parts = []
            for o in e["options"]:
                if o["kind"] == "dps_loan":
                    parts.append(f"DPS ঋণ (৳{bn_num(o['available'])})")
                else:
                    parts.append(f"{o['pocket']} পকেট (৳{bn_num(o['available'])})")
            text = "জরুরি টাকার জন্য দেখতে পারো: " + ", ".join(parts) + "।"
            if any(o["kind"] == "dps_loan" for o in e["options"]):
                text += f" {e['note_bn']}"
        else:
            text = "কোনো পকেটে জমানো টাকা নেই। মাসে অল্প করে জরুরি পকেটে রাখলে পরে কাজে লাগবে।"
    elif intent == "dps":
        adv = svc.dps_advice(uid)
        used.append({"name": "dps_advice", "result": adv})
        text = adv["reason_bn"]
        if adv.get("status") == "ok":
            text = f"তোমার নিরাপদ মাসিক জমা প্রায় ৳{bn_num(adv['safe_monthly'])}। " + text
    elif intent == "eid":
        e = tool("plan_eid")
        text = f"{e['eid_name_bn']} আর {bn_num(e['days_left'])} দিন পরে। গত ঈদে খরচ হয়েছিল ৳{bn_num(e['last_eid_spend'])}।"
        text += (f" সপ্তাহে ৳{bn_num(e['weekly'])} করে রাখলে চাপ কমবে।" if e["weekly"] > 0
                 else " জমানো টাকাতেই ঈদের খরচ চলার কথা।")
    elif intent == "safe_spend":
        h = tool("get_home_summary")
        if h["insufficient_history"]:
            text = "হিসাব দেখাতে আরও কিছু দিনের লেনদেন লাগবে।"
        elif (h.get("safe_to_spend_today") or 0) > 0:
            text = f"আজকের নিরাপদ খরচসীমা ৳{bn_num(h['safe_to_spend_today'])}। এটা ধরে চললে মাস শেষে চাপ কম হবে।"
        else:
            text = "আজ খরচ যতটা পারো কমাও — মাসের বাজেট একটু টাইট আছে।"
    elif intent == "balance":
        h = tool("get_home_summary")
        if h["insufficient_history"]:
            text = "হিসাব দেখাতে আরও কিছু দিনের লেনদেন লাগবে।"
        else:
            text = f"মূল ব্যালেন্স উপায় অ্যাপের উপরে দেখতে পাবে। আজ তোমার নিরাপদ খরচসীমা ৳{bn_num(h.get('safe_to_spend_today') or 0)}।"
    elif intent == "budget":
        tx = tool("get_transactions_summary", period="month")
        text = f"এই মাসে আয় ৳{bn_num(tx['income_total'])}, খরচ ৳{bn_num(tx['spend_total'])}। "
        diff = tx['income_total'] - tx['spend_total']
        if diff > 0:
            text += f"এখন পর্যন্ত ৳{bn_num(diff)} সাশ্রয় হয়েছে — চালিয়ে যাও!"
        else:
            text += "খরচ একটু বেশি হয়েছে — বাকি মাসে একটু সামলে চলো।"
    elif intent == "savings_level":
        h = tool("get_home_summary")
        text = "সঞ্চয় লেভেল দেখতে হিসাব ট্যাব → সঞ্চয় → লেভেল পেজে যাও।"
        if not h["insufficient_history"]:
            text += f" এই মাসে ঝুঁকির মাত্রা: {h.get('risk_level', 'green')}।"
    elif intent == "pocket":
        h = tool("get_home_summary")
        text = "পকেটগুলো দেখতে হিসাব ট্যাব → সঞ্চয় → আমার পকেট-এ যাও।"
        if not h["insufficient_history"] and h.get("safe_to_spend_today"):
            text += f" আজ নিরাপদ খরচসীমা ৳{bn_num(h['safe_to_spend_today'])}।"
    elif intent == "greeting":
        text = "হ্যালো! আমি উপায় 'হিসাব'। তোমার বাজেট বা জমানো নিয়ে কোনো সাহায্য লাগবে?"
    elif intent == "shortfall":
        h = tool("get_home_summary")
        if h["insufficient_history"]:
            text = "হিসাব দেখাতে আরও কিছু দিনের লেনদেন লাগবে।"
        elif h["risk_level"] in ("amber", "red") and h["shortfall_date"]:
            drivers = tool("get_shortfall_drivers")["drivers"]
            why = ", ".join(d["text_bn"] for d in drivers[:2])
            text = f"{_day(h['shortfall_date'])} দিকে টানাটানি হতে পারে (প্রায় ৳{bn_num(h['shortfall_amount'])} শর্ট)। কারণ: {why}।"
            if h["top_actions"]:
                text += f" পরামর্শ: {h['top_actions'][0]}।"
        else:
            text = f"এই মাসে টানাটানির ঝুঁকি কম। আজ নিরাপদ খরচ প্রায় ৳{bn_num(h['safe_to_spend_today'] or 0)}।"
    else:
        text = "আমি উপায় 'হিসাব'। আমি শুধু লেনদেন, সঞ্চয় আর বাজেট নিয়ে সাহায্য করতে পারি। একটু বুঝিয়ে বলবে?"
    return {"text": text, "used_tools": used, "numbers_source": "engine", "ai": False}
