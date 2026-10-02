"""Template answers from engine outputs — used when the LLM is off, slow, failing, or unsafe. Never breaks."""

from __future__ import annotations

import re
from datetime import date

from hishab.engine.text import bn_digits, bn_num
from hishab.llm.normalizer import normalize
from hishab.llm.tools import run_tool

_BN_TO_ASCII = str.maketrans("০১২৩৪৫৬৭৮৯", "0123456789")

_INTENTS: list[tuple[str, str]] = [
    # ── high-priority: match before generic words ──
    ("greeting",      r"^hi$|^hello$|^hey$|^হ্যালো$|^হাই$|^সালাম$"
                      r"|আসসালামু আলাইকুম|ওয়ালাইকুম"
                      r"|salam|ki khobor|কী খবর|kemn|kmn|কেমন আছ"),
    ("ack",           r"^ok$|^okay$|^ঠিক আছে$|^thik ache$|^yes$|^ha$"
                      r"|^হুম$|^hm$|^hmm$|^আচ্ছা$|^daw$|^দাও$"
                      r"|thanks|thank you|ধন্যবাদ|dhonnobad"),
    ("identity",      r"tumi ke|who are you|তুমি কে|তোমার নাম|ki nam|bot ki|ai ki"),
    ("help",          r"ki korte paro|কী করতে পারো|ki koro|কী করো"
                      r"|sahajjo|সাহায্য করো|help lagbe|সাহায্য লাগবে|kivabe kaj"),
    ("complaint",     r"faltu|ফালতু|pagol|পাগল|vul|ভুল|andaze|আন্দাজে"
                      r"|kaj hochhe na|কাজ হচ্ছে না|vua|ভুয়া|fau|faul"),
    # ── financial intents ──
    ("safe_spend",    r"নিরাপদ খরচ|safe.?spend|aaj koto|আজ কত|আজকে কত"
                      r"|kharoch korte parbo|খরচ করতে পারব|daily limit|দৈনিক সীমা"),
    ("balance",       r"ব্যালেন্স|balance|belence|balence"
                      r"|taka ache|টাকা আছে|koto taka|কত টাকা|wallet e koto"),
    ("shortfall",     r"কম পড়|শেষে|short|month.?end|টানাটানি|চলবে"
                      r"|taka nei|taka shesh|টাকা নেই|শেষ হয়"
                      r"|kobe shesh|কত দিন চলবে|koto din chalbe"),
    ("cashout",       r"cash.?out|ক্যাশ ?আউট|ক্যাশআউট|agent|এজেন্ট|fee|ফি"
                      r"|agent theke|cash komabo"),
    ("transactions",  r"লেনদেন|transaction|বুঝিয়ে|কোথায় খরচ|history"
                      r"|kharoch kothay|খরচ কোথায়|lenden|income koto|আয় koto|আয় কত"),
    ("goal",          r"জমা|জমাতে|সঞ্চয়|save|saving|goal|লক্ষ্য|target"
                      r"|joma|bachabo|bachaibo|save korbo|jomate parbo"),
    ("dps",           r"dps|ডিপিএস|deposit|মাসিক জমা|kisti|কিস্তি|monthly joma"),
    ("eid",           r"ঈদ|eid|puja|পূজা|festival|bonos|বোনাস|উৎসব"),
    ("emergency",     r"জরুরি|ইমার্জেন্সি|emergency|ঋণ|loan|ধার|dorkar|urgent"),
    ("pocket",        r"pocket|পকেট|amar pocket|আমার পকেট|goal pocket"),
    ("savings_level", r"level|লেভেল|badge|streak|achievement|sanchoy level|সঞ্চয় লেভেল"),
    ("budget",        r"budget|বাজেট|plan|পরিকল্পনা|mas er plan|মাসের পরিকল্পনা"),
    ("notification",  r"notification|নোটিফিকেশন|alert|কেন জানালে|কেন পাঠালে|mane ki"),
]


def _numbers(text: str) -> list[tuple[float, int]]:
    t = text.translate(_BN_TO_ASCII).replace(",", "")
    return [(float(m.group()), m.end()) for m in re.finditer(r"\d+(?:\.\d+)?", t)]


def _parse_goal(text: str) -> tuple[float | None, int]:
    t = text.translate(_BN_TO_ASCII).replace(",", "")
    months = 6
    m = re.search(r"(\d+)\s*(?:মাস|month)", t)
    if m:
        months = int(m.group(1))
    amounts = [n for n, _ in _numbers(text) if n >= 100]
    return (max(amounts) if amounts else None), max(1, min(60, months))


def _day(iso: str | None) -> str:
    """'2026-09-29' -> '২৯ তারিখের'."""
    if not iso:
        return ""
    return f"{bn_digits(date.fromisoformat(iso).day)} তারিখের"


def answer(uid: str, message: str, svc) -> dict:
    # Normalize Banglish → Bangla before intent matching
    normalized = normalize(message)
    text_l = normalized.lower()
    intent = next((name for name, pat in _INTENTS if re.search(pat, text_l)), "unknown")
    used: list[dict] = []
    cache: dict = {}

    def tool(name, **args):
        out = run_tool(name, args, uid, svc, cache)
        used.append({"name": name, "result": out})
        return out

    if intent == "goal":
        target, months = _parse_goal(message)
        if target is None:
            adv = svc.dps_advice(uid)
            used.append({"name": "dps_advice", "result": adv})
            if adv.get("status") == "ok":
                text = f"তোমার বর্তমান আয়-ব্যয় অনুযায়ী, মাসে নিরাপদে প্রায় ৳{bn_num(adv['safe_monthly'])} জমাতে পারবে।"
            else:
                text = adv["reason_bn"]
        else:
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
    elif intent == "identity":
        text = "আমি 'হিসাব', উপায়-এর একটি স্মার্ট আর্থিক সহকারী। আমি তোমার আয়-ব্যয় বিশ্লেষণ করে সঞ্চয় করতে সাহায্য করি।"
    elif intent == "help":
        text = "আমি তোমার প্রতিদিনের নিরাপদ খরচসীমা, মাসের বাজেট, এবং কীভাবে সঞ্চয় করা যায়— এই বিষয়গুলো নিয়ে পরামর্শ দিতে পারি।"
    elif intent == "complaint":
        text = "দুঃখিত! আমি একটি সাধারণ এআই সিস্টেম, তাই মাঝেমধ্যে ভুল হতে পারে। একটু বুঝিয়ে বললে আমি চেষ্টা করব সঠিক উত্তর দেওয়ার।"
    elif intent == "ack":
        text = "ঠিক আছে! আর কোনো সাহায্য লাগলে জানিও।"
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
    elif intent == "notification":
        h = tool("get_home_summary")
        if h["insufficient_history"]:
            text = "হিসাব দেখাতে আরো কিছু দিনের লেনদেন লাগবে।"
        elif h["risk_level"] == "red" and h["shortfall_date"]:
            drivers = tool("get_shortfall_drivers")["drivers"]
            why = ", ".join(d["text_bn"] for d in drivers[:2])
            text = f"এই মাসে একটু সাবধান থাকো — {why} কারণে {_day(h['shortfall_date'])} দিকে টানাটানি হতে পারে।"
        elif h["risk_level"] == "amber":
            text = "মাসের শেষ দিকে একটু পরিকল্পনা করো — এখনই সতর্ক হলে টানাটানি এড়ানো যাবে।"
        else:
            text = "ভালো করছ! তোমার সঞ্চয়ের অগ্রগতি জানাতে notification দিয়েছি।"
    else:
        text = "এই বিষয়ে আমার কিছু জানা নেই — আমি শুধু তোমার আর্থিক হিসাব নিয়ে কাজ করি।"
    return {"text": text, "used_tools": used, "numbers_source": "engine", "ai": False}
