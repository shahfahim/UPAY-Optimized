"""Template answers — used when the LLM is off, slow, failing, or unsafe. Never breaks.

Edge-case coverage:
  • 25 intent categories (greeting, ack, identity, help, complaint, status, advice,
    safe_spend, specific_amount, balance, shortfall, cashout, transactions, compare,
    goal, dps, eid, emergency, pocket, savings_level, budget, notification,
    next_income, product_explain, off_topic)
  • Banglish normalizer pre-pass
  • Typo-resilient patterns
  • Handles: frustration, silence, numbers-only, "ki korbo", average savings,
    "ami ki bhalo korchi", "last month vs", category-specific spend, etc.
"""

from __future__ import annotations

import re
from datetime import date

from hishab.engine.text import bn_digits, bn_num
from hishab.llm.normalizer import normalize
from hishab.llm.tools import run_tool

_BN_TO_ASCII = str.maketrans("০১২৩৪৫৬৭৮৯", "0123456789")

# ─────────────────────────────────────────────────────────────────────────────
# INTENT TABLE  (first match wins — order matters)
# ─────────────────────────────────────────────────────────────────────────────
_INTENTS: list[tuple[str, str]] = [

    # ── 1. Greetings ──────────────────────────────────────────────────────────
    ("greeting",
     r"^hi$|^hello$|^hey$|^হ্যালো$|^হাই$|^সালাম$|^yo$|^sup$"
     r"|আসসালামু আলাইকুম|ওয়ালাইকুম"
     r"|salam|ki khobor|কী খবর|kemn|kmn|কেমন আছ"
     r"|good morning|good night|good evening|shubho|শুভ সকাল|শুভ রাত"),

    # ── 2. Short acknowledgment / filler ─────────────────────────────────────
    ("ack",
     r"^ok$|^okay$|^ঠিক আছে$|^thik ache$|^yes$|^ha$|^ji$|^জি$"
     r"|^হুম$|^hm$|^hmm$|^আচ্ছা$|^daw$|^দাও$|^accha$|^acha$|^\.$|^…$"
     r"|thanks|thank you|ধন্যবাদ|dhonnobad|jajakallah|শুকরিয়া"
     r"|got it|understood|bujhechi|বুঝেছি|noted|পেয়েছি"),

    # ── 3. Identity ───────────────────────────────────────────────────────────
    ("identity",
     r"tumi ke|who are you|তুমি কে|তোমার নাম|ki nam|bot ki|ai ki"
     r"|hishab ki|হিসাব কী|তুমি কি মানুষ|are you human|are you a bot"
     r"|kon company|upay er ai|কে তৈরি করেছে"),

    # ── 4. Help / capability ─────────────────────────────────────────────────
    ("help",
     r"ki korte paro|কী করতে পারো|ki koro|কী করো"
     r"|sahajjo|সাহায্য করো|help lagbe|সাহায্য লাগবে|kivabe kaj"
     r"|^help$|^সাহায্য$|^ki$|ki bojhao|how do you work"
     r"|feature|কী কী পারো|sob ki paro|sobkichu"),

    # ── 5. Complaint / frustration ───────────────────────────────────────────
    ("complaint",
     r"faltu|ফালতু|pagol|পাগল|vul|ভুল|andaze|আন্দাজে"
     r"|kaj hochhe na|কাজ হচ্ছে না|vua|ভুয়া|fau|faul|bekar|বেকার"
     r"|\?\?\?|\!\!\!|kaje ashe na|কাজে আসে না|nosto|নষ্ট"
     r"|bokar|বোকার|chagol|matha kharap|মাথা খারাপ"
     r"|wrong answer|vul ans|ভুল উত্তর|nonsense"),

    # ── 6. Status / "am I doing well?" ───────────────────────────────────────
    ("status",
     r"ami ki bhalo|আমি কি ভালো|amar obostha|আমার অবস্থা"
     r"|financial condition|hisab thik|হিসাব ঠিক|ami ki save korte parchhi"
     r"|আমার প্রগতি|আমার আর্থিক অবস্থা|kemon cholche|কেমন চলছে"
     r"|am i doing (well|ok|good)|how am i doing|amar ki khobor"),

    # ── 7. Advice / "ki korbo?" ───────────────────────────────────────────────
    ("advice",
     r"ki korbo|কী করব|ki korle|কী করলে|ki kora uchit|কী করা উচিত"
     r"|porামর্শ|পরামর্শ|tips?|suggestion|ki korbo ekhon"
     r"|what should i do|what to do|help me|help koro|ekhon ki|এখন কী"
     r"|taka bachate|টাকা বাঁচাতে|kharoch komabe kivabe|খরচ কমাব কীভাবে"),

    # ── 8. Safe spend (today's limit) ────────────────────────────────────────
    ("safe_spend",
     r"নিরাপদ খরচ|safe.?spend|aaj koto|আজ কত|আজকে কত"
     r"|kharoch korte parbo|খরচ করতে পারব|daily limit|দৈনিক সীমা"
     r"|aaj ki kharoch|আজ কি খরচ|today.*spend|spend.*today"
     r"|koto taka kharoch kora jai|কত টাকা খরচ করা যাই"
     r"|aaj er limit|আজকের সীমা"),

    # ── 9. Amount-specific safe-spend check ("can I spend 500?") ─────────────
    ("specific_amount",
     r"\d[\d,]*\s*(?:\u099f\u09be\u0995\u09be|taka|\u09f3)\s*(?:\u0996\u09b0\u099a|kharoch|spend|\u0995\u09bf\u09a8\u09a4\u09c7|\u0995\u09bf\u09a8\u09ac|\u09a8\u09c7\u09ac|\u09a6\u09bf\u09a4\u09c7)"
     r"|(?:\u0996\u09b0\u099a|kharoch|spend|\u0995\u09bf\u09a8\u09a4\u09c7)\s*\d[\d,]*"
     r"|\d[\d,]*\s*(?:\u099f\u09be\u0995\u09be|taka)\s*(?:\u0996\u09b0\u099a|kharoch|spend|\u0995\u09b0\u09a4\u09c7)\s*(?:\u09aa\u09be\u09b0\u09bf|\u09aa\u09be\u09b0\u09ac|pari|parbo|jai)"),

    # ── 10. Balance ───────────────────────────────────────────────────────────
    ("balance",
     r"ব্যালেন্স|balance|belence|balence|bal koto"
     r"|taka ache|টাকা আছে|koto taka|কত টাকা|wallet e koto"
     r"|wallet.*koto|account.*koto|taka ki ache|টাকা কি আছে"
     r"|what.*balance|how much.*wallet|wallet.*money"),

    # ── 11. Shortfall / risk ─────────────────────────────────────────────────
    ("shortfall",
     r"কম পড়|শেষে|short|month.?end|টানাটানি|চলবে"
     r"|taka nei|taka shesh|টাকা নেই|শেষ হয়|টাকা শেষ"
     r"|kobe shesh|কত দিন চলবে|koto din chalbe"
     r"|taka thakbe|টাকা থাকবে|run out|mas shesh"
     r"|keno taka kom|কেন টাকা কম|taka kome jacche|টাকা কমে যাচ্ছে"
     r"|will i have money|month end"),

    # ── 24. Product explanation ("what is X?") ───────────────────────────────
    ("product_explain",
     r"(?:dps|pocket|npsb|upay|hishab|cash.?out|cashout)\s*(?:ki|keno|mane|কী|কেন|মানে)"
     r"|what is (?:dps|pocket|npsb|upay|hishab|cashout)"
     r"|কীভাবে কাজ করে|kivabe kaj kore"),

    # ── 12. Cash-out & fees ───────────────────────────────────────────────────
    ("cashout",
     r"cash.?out(?!\s*(?:ki|ki|mane|\u0995\u09c0))|ক্যাশ ?আউট|ক্যাশআউট|agent|এজেন্ট|fee|ফি"
     r"|agent theke|cash komabo"
     r"|taka tule|টাকা তুলে|agent fee|cash withdrawal"
     r"|koto fee|ফি কত|charge koto|কত চার্জ"),

    # ── 13. Transactions / spending history ───────────────────────────────────
    ("transactions",
     r"লেনদেন|transaction|বুঝিয়ে|কোথায় খরচ|history"
     r"|kharoch kothay|খরচ কোথায়|lenden|income koto|আয় koto|আয় কত"
     r"|average savings|average joma|average koto|গড় সঞ্চয়|গড় জমা|গড় কত"
     r"|koto kharoch|কত খরচ|kharoch er hisab|খরচের হিসাব"
     r"|spending.*month|monthly.*spend|show.*transaction|ei mase koto"
     r"|food.*koto|khawa.*koto|transport.*koto|যাতায়াত.*কত"
     r"|kothay beshi|কোথায় বেশি|kotha theke|last week|last month.*kharoch"
     r"|income.*mase|আয়.*মাসে|koto.*income|how much.*spend|how much.*earn"),

    # ── 14. Comparison (this vs last) ────────────────────────────────────────
    ("compare",
     r"compare|তুলনা|age.*ekhon|আগে.*এখন|last month.*vs|ei mas.*age"
     r"|beshi.*hoyeche|কমেছে.*বেড়েছে|age cheyey|আগের চেয়ে"
     r"|previous month|last month.*cheyey|better.*worse"),

    # ── 15. Savings goal ─────────────────────────────────────────────────────
    ("goal",
     r"জমাতে চাই|সঞ্চয় করতে চাই|সঞ্চয় করব|বাঁচাব|save korbo"
     r"|jomate parbo|jomate পারব|jomate chai|জমাতে পারব"
     r"|goal|লক্ষ্য|target|bachabo|bachaibo"
     r"|(?:\d[\d,]*).*(?:joma|save|সঞ্চয়|জমা|month|mase)"
     r"|(?:joma|সঞ্চয়|জমা).*(?:\d[\d,]*|mase|month)"
     r"|koto save|কত সঞ্চয়|ki vabe save|কীভাবে জমাব"),


    # ── 16. DPS ───────────────────────────────────────────────────────────────
    ("dps",
     r"dps|ডিপিএস|deposit scheme|মাসিক জমা|monthly জমা|kisti|কিস্তি|monthly joma"
     r"|dps ki|ডিপিএস কী|dps korbo|dps open|dps account"
     r"|recurring deposit|monthly deposit|dps thik ache"),

    # ── 17. Festival / Eid ───────────────────────────────────────────────────
    ("eid",
     r"ঈদ|eid|puja|পূজা|festival|bonos|বোনাস|উৎসব"
     r"|eid er jonno|পূজার জন্য|holiday.*taka|taka jomano.*eid"),

    # ── 18. Emergency / urgent money ─────────────────────────────────────────
    ("emergency",
     r"জরুরি|ইমার্জেন্সি|emergency|ঋণ|loan|ধার|dorkar|urgent"
     r"|help.*taka|taka lagbe|টাকা লাগবে|ekhuni taka|এখনই টাকা"
     r"|dharon|borrow|udhar|উধার|joruri taka"),

    # ── 19. Pocket ────────────────────────────────────────────────────────────
    ("pocket",
     r"pocket|পকেট|amar pocket|আমার পকেট|goal pocket"
     r"|pocket e koto|পকেটে কত|pocket balance|pocket theke"),

    # ── 20. Savings level / streak / badge ───────────────────────────────────
    ("savings_level",
     r"level|লেভেল|badge|streak|achievement|sanchoy level|সঞ্চয় লেভেল"
     r"|streak koto|level up|koto din streak|আমার level|amar level"
     r"|level dekhao|badge dekhao|accomplishment"),

    # ── 21. Budget overview ───────────────────────────────────────────────────
    ("budget",
     r"budget|বাজেট|mas er plan|মাসের পরিকল্পনা"
     r"|monthly plan|plan koro|পরিকল্পনা করো"),

    # ── 22. Notification explanation ─────────────────────────────────────────
    ("notification",
     r"notification|নোটিফিকেশন|alert|কেন জানালে|কেন পাঠালে"
     r"|mane ki|এই মেসেজ কেন|keno message|কেন নোটিফিকেশন"
     r"|push.*keno|alert.*keno|কেন সতর্কতা"),

    # ── 23. Next income / payday ─────────────────────────────────────────────
    ("next_income",
     r"kobe taka ashbe|কবে টাকা আসবে|next income|পরের আয়"
     r"|payday|payment.*kobe|kobe pabo|কবে পাব"
     r"|income.*kobe|salary.*kobe|আয়.*কবে"),

]


# ─────────────────────────────────────────────────────────────────────────────
# HELPERS
# ─────────────────────────────────────────────────────────────────────────────

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
    """'2026-09-29' → '২৯ তারিখের'."""
    if not iso:
        return ""
    return f"{bn_digits(date.fromisoformat(iso).day)} তারিখের"


def _risk_label(risk: str) -> str:
    return {"green": "কম ঝুঁকি — ভালো করছ!", "amber": "মাঝারি ঝুঁকি", "red": "বেশি ঝুঁকি"}.get(risk, risk)


# ─────────────────────────────────────────────────────────────────────────────
# MAIN ANSWER FUNCTION
# ─────────────────────────────────────────────────────────────────────────────

def answer(uid: str, message: str, svc) -> dict:  # noqa: C901 (intentionally long)
    # ── Pre-process: Banglish normalizer ─────────────────────────────────────
    normalized = normalize(message)
    text_l = normalized.lower().strip()

    # ── Detect intent ─────────────────────────────────────────────────────────
    intent = next((name for name, pat in _INTENTS if re.search(pat, text_l)), "unknown")

    used: list[dict] = []
    cache: dict = {}

    def tool(name, **args):
        out = run_tool(name, args, uid, svc, cache)
        used.append({"name": name, "result": out})
        return out

    # ─────────────────────────────────────────────────────────────────────────
    # INTENT HANDLERS
    # ─────────────────────────────────────────────────────────────────────────

    # ── Greeting ──────────────────────────────────────────────────────────────
    if intent == "greeting":
        text = "হ্যালো! আমি উপায় 'হিসাব'। তোমার বাজেট বা জমানো নিয়ে কোনো সাহায্য লাগবে?"

    # ── Acknowledgment ────────────────────────────────────────────────────────
    elif intent == "ack":
        text = "ঠিক আছে! আর কোনো সাহায্য লাগলে জানিও।"

    # ── Identity ──────────────────────────────────────────────────────────────
    elif intent == "identity":
        text = ("আমি 'হিসাব', উপায়-এর স্মার্ট আর্থিক সহকারী। "
                "আমি তোমার আয়-ব্যয় বিশ্লেষণ করে সঞ্চয় করতে সাহায্য করি — "
                "কোনো API key ছাড়াই কাজ করি।")

    # ── Help ──────────────────────────────────────────────────────────────────
    elif intent == "help":
        text = ("আমি যা করতে পারি: আজকের নিরাপদ খরচসীমা, আয়-ব্যয় হিসাব, "
                "সঞ্চয় পরিকল্পনা, DPS পরামর্শ, cash-out ফি কমানো, "
                "ঈদ/উৎসবের বাজেট। কী জানতে চাও?")

    # ── Complaint / frustration ───────────────────────────────────────────────
    elif intent == "complaint":
        text = ("দুঃখিত! আমি একটি সাধারণ এআই সিস্টেম — মাঝেমধ্যে বুঝতে ভুল হয়। "
                "কোন উত্তরটা ঠিক মনে হয়নি বলো, আবার চেষ্টা করব।")

    # ── Status ("ami ki bhalo korchi?") ──────────────────────────────────────
    elif intent == "status":
        h = tool("get_home_summary")
        if h["insufficient_history"]:
            text = "হিসাব দেখাতে আরও কিছু দিনের লেনদেন লাগবে।"
        else:
            risk = h.get("risk_level", "green")
            bal  = h.get("balance") or 0
            safe = h.get("safe_to_spend_today") or 0
            if risk == "green":
                text = f"ভালো করছ! ব্যালেন্স ৳{bn_num(bal)}, আজ ৳{bn_num(safe)} খরচ করতে পারবে।"
            elif risk == "amber":
                text = (f"মোটামুটি চলছে। ব্যালেন্স ৳{bn_num(bal)}, তবে মাসের শেষে একটু সামলে চলো। "
                        f"আজ ৳{bn_num(safe)}-এর মধ্যে রাখো।")
            else:
                drivers = tool("get_shortfall_drivers")["drivers"]
                why = ", ".join(d["text_bn"] for d in drivers[:2])
                text = (f"এই মাসে চাপ আছে। ব্যালেন্স ৳{bn_num(bal)}, "
                        f"তবে {why} কারণে সাবধান থাকো।")

    # ── Advice ("ki korbo?") ──────────────────────────────────────────────────
    elif intent == "advice":
        h  = tool("get_home_summary")
        tx = tool("get_transactions_summary", period="month")
        top_cat = tx["by_category"][0]["category_bn"] if tx.get("by_category") else None
        if h["insufficient_history"]:
            text = "হিসাব দেখাতে আরও কিছু দিনের লেনদেন লাগবে।"
        elif h["risk_level"] == "green":
            adv = svc.dps_advice(uid)
            used.append({"name": "dps_advice", "result": adv})
            if adv.get("status") == "ok":
                text = (f"ভালো অবস্থায় আছ! "
                        f"মাসে ৳{bn_num(adv['safe_monthly'])} DPS-এ দিলে বছরে ৳{bn_num(int(adv['safe_monthly']*12))} জমবে।")

            else:
                text = "ভালো অবস্থায় আছ! cash-out কমিয়ে সরাসরি পেমেন্ট করো।"
        else:
            drivers = tool("get_shortfall_drivers")["drivers"]
            actions = h.get("top_actions", [])
            text = ("এখন সবচেয়ে ভালো হবে: "
                    + (f"{actions[0]}।" if actions else
                       f"{', '.join(d['text_bn'] for d in drivers[:2])} কমাও।"))

    # ── Safe spend today ──────────────────────────────────────────────────────
    elif intent == "safe_spend":
        h = tool("get_home_summary")
        if h["insufficient_history"]:
            text = "হিসাব দেখাতে আরও কিছু দিনের লেনদেন লাগবে।"
            safe = h.get("safe_to_spend_today") or 0
            risk = h.get("risk_level", "green")
            if safe <= 0:
                text = "আজ খরচ যতটা পারো কমাও — মাসের বাজেট একটু টাইট।"
            elif risk == "green":
                text = f"আজ ৳{bn_num(safe)} পর্যন্ত নিরাপদে খরচ করতে পারবে — ভালো অবস্থায় আছ!"
            elif risk == "amber":
                text = f"আজ ৳{bn_num(safe)}-এর মধ্যে রাখলে ভালো — মাসের শেষে সামলানো যাবে।"
            else:
                text = f"আজ ৳{bn_num(safe)}-এর বেশি খরচ করো না — টানাটানির ঝুঁকি আছে।"
    elif intent == "specific_amount":
        h = tool("get_home_summary")
        nums = [n for n, _ in _numbers(message) if n >= 10]
        amount = nums[0] if nums else 0
        safe = h.get("safe_to_spend_today") or 0
        if h["insufficient_history"]:
            text = "হিসাব দেখাতে আরও কিছু দিনের লেনদেন লাগবে।"
        elif amount <= safe:
            remaining = safe - amount
            text = (f"হ্যাঁ, ৳{bn_num(amount)} খরচ করতে পারবে। "
                    f"খরচের পর আজের বাকি সীমা ৳{bn_num(remaining)}।")
        else:
            text = (f"৳{bn_num(amount)} একটু বেশি হতে পারে। "
                    f"আজকের নিরাপদ সীমা ৳{bn_num(safe)}। "
                    "একটু কম খরচ করলে মাস শেষে সুবিধা হবে।")

    # ── Balance ───────────────────────────────────────────────────────────────
    elif intent == "balance":
        h = tool("get_home_summary")
        if h["insufficient_history"]:
            text = "হিসাব দেখাতে আরও কিছু দিনের লেনদেন লাগবে।"
        else:
            bal  = h.get("balance") or 0
            safe = h.get("safe_to_spend_today") or 0
            text = (f"তোমার উপায় ব্যালেন্স ৳{bn_num(bal)}। "
                    f"আজ নিরাপদ খরচসীমা ৳{bn_num(safe)}।")

    # ── Shortfall / risk ──────────────────────────────────────────────────────
    elif intent == "shortfall":
        h = tool("get_home_summary")
        if h["insufficient_history"]:
            text = "হিসাব দেখাতে আরও কিছু দিনের লেনদেন লাগবে।"
        elif h["risk_level"] in ("amber", "red") and h["shortfall_date"]:
            drivers = tool("get_shortfall_drivers")["drivers"]
            why = ", ".join(d["text_bn"] for d in drivers[:2])
            text = (f"{_day(h['shortfall_date'])} দিকে টানাটানি হতে পারে "
                    f"(প্রায় ৳{bn_num(h['shortfall_amount'])} শর্ট)। কারণ: {why}।")
            if h["top_actions"]:
                text += f" পরামর্শ: {h['top_actions'][0]}।"
        else:
            text = (f"এই মাসে টানাটানির ঝুঁকি কম — ভালো করছ! "
                    f"আজ নিরাপদ খরচ প্রায় ৳{bn_num(h.get('safe_to_spend_today') or 0)}।")

    # ── Cash-out & fees ───────────────────────────────────────────────────────
    elif intent == "cashout":
        tx = tool("get_transactions_summary", period="month")
        route = tool("find_route", amount=5000, destination="other_mfs_wallet")
        # Lead with count (answers "কতবার"), then fee total
        count = tx.get("cash_out_count", 0)
        fees  = tx.get("cash_out_fees", 0)
        text = (f"গত ৩০ দিনে {bn_num(count)} বার ক্যাশ আউট করেছ, "
                f"ফি গেছে মোট ৳{bn_num(fees)}। "
                "এজেন্টে না গিয়ে সরাসরি upay দিয়ে পেমেন্ট করলে এই ফি বাঁচত।")
        # Only show NPSB saving when habits data is present AND saving > 0
        habits = route.get("habits", [])
        if habits and habits[0].get("annual_saving", 0) > 0:
            text += (f" NPSB দিয়ে পাঠালে বছরে "
                     f"৳{bn_num(habits[0]['annual_saving'])} বাঁচবে।")

    # ── Transactions / spending history ───────────────────────────────────────
    elif intent == "transactions":
        tx = tool("get_transactions_summary", period="month")
        cats = tx.get("by_category", [])
        top = ", ".join(c["category_bn"] for c in cats[:2])
        net = tx["income_total"] - tx["spend_total"]
        is_avg    = re.search(r"average|avg|গড়", text_l)
        wants_inc = re.search(r"income koto|aay koto|আয় কত|আয়.*কত|income.*কত", text_l)
        wants_exp = re.search(r"kharoch koto|খরচ কত|koto kharoch|কত খরচ", text_l)
        top_line  = (f"সবচেয়ে বেশি গেছে: {top}।" if top else "")
        if is_avg:
            text = (f"গত মাসে আয় ৳{bn_num(tx['income_total'])}, "
                    f"খরচ ৳{bn_num(tx['spend_total'])}। "
                    f"গড় নিট সঞ্চয় প্রায় ৳{bn_num(max(0.0, net))}। "
                    + top_line)
        elif wants_inc:
            text = (f"গত ৩০ দিনে তোমার আয় হয়েছে ৳{bn_num(tx['income_total'])}। "
                    f"এই সময়ে খরচ হয়েছে ৳{bn_num(tx['spend_total'])}। "
                    + top_line)
        elif wants_exp:
            text = (f"গত ৩০ দিনে মোট খরচ হয়েছে ৳{bn_num(tx['spend_total'])}। "
                    f"আয় ছিল ৳{bn_num(tx['income_total'])}। "
                    + top_line)
        else:
            text = (f"গত ৩০ দিনে আয় ৳{bn_num(tx['income_total'])}, "
                    f"খরচ ৳{bn_num(tx['spend_total'])}। "
                    + top_line)

    # ── Comparison (this vs last month) ──────────────────────────────────────
    elif intent == "compare":
        tx = tool("get_transactions_summary", period="month")
        top = ", ".join(f"{c['category_bn']}" for c in tx["by_category"][:2])
        text = (f"এই মাসে আয় ৳{bn_num(tx['income_total'])}, "
                f"খরচ ৳{bn_num(tx['spend_total'])}। "
                f"বেশি খরচ হয়েছে {top}-এ। "
                "মাস-ওয়ারি তুলনা হিসাব ট্যাবে বিস্তারিত দেখতে পাবে।")

    # ── Savings goal ──────────────────────────────────────────────────────────
    elif intent == "goal":
        target, months = _parse_goal(message)
        if target is None:
            adv = svc.dps_advice(uid)
            used.append({"name": "dps_advice", "result": adv})
            tx_g = tool("get_transactions_summary", period="month")
            net_g = max(0.0, tx_g["income_total"] - tx_g["spend_total"])
            if adv.get("status") == "ok":
                text = (f"গত মাসে ৳{bn_num(net_g)} বাঁচানো হয়েছে। চেষ্টা করলে মাসে "
                        f"৳{bn_num(adv['safe_monthly'])} জমাতে পারবে। "
                        "ছোট লক্ষ্য দিয়ে শুরু করো।")
            else:
                text = adv["reason_bn"]
        else:
            g = tool("plan_goal", target=target, months=months)
            if g.get("insufficient_history"):
                text = "লক্ষ্যের হিসাব করতে আরও কিছু দিনের লেনদেন লাগবে।"
            else:
                text = (f"৳{bn_num(target)} জমাতে {bn_num(months)} মাসে "
                        f"মাসে ৳{bn_num(g['monthly'])} লাগবে। ")
                if g["feasibility"] < 0.05:
                    text += ("লক্ষ্যটা এখন একটু কঠিন — "
                             "সময় বাড়ালে বা পরিমাণ কমালে সহজ হবে।")
                else:
                    text += f"পারার সম্ভাবনা {bn_num(round(100 * g['feasibility']))}%।"
                    if g["feasibility"] < 0.5:
                        text += " সময় বাড়ালে আরও সহজ হবে।"

    # ── DPS ───────────────────────────────────────────────────────────────────
    elif intent == "dps":
        adv = svc.dps_advice(uid)
        used.append({"name": "dps_advice", "result": adv})
        if adv.get("status") == "ok":
            text = (f"মাসে ৳{bn_num(adv['safe_monthly'])} DPS-এ দিলে বছরে ৳{bn_num(int(adv['safe_monthly']*12))} জমবে। "
                    + adv["reason_bn"])
        else:
            text = adv["reason_bn"]

    # ── Festival / Eid ────────────────────────────────────────────────────────
    elif intent == "eid":
        e = tool("plan_eid")
        text = (f"{e['eid_name_bn']} আর {bn_num(e['days_left'])} দিন পরে। "
                f"গত ঈদে খরচ হয়েছিল ৳{bn_num(e['last_eid_spend'])}।")
        text += (f" সপ্তাহে ৳{bn_num(e['weekly'])} করে রাখলে চাপ কমবে।"
                 if e["weekly"] > 0 else " জমানো টাকাতেই ঈদের খরচ চলার কথা।")

    # ── Emergency ─────────────────────────────────────────────────────────────
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
            text = ("কোনো পকেটে জমানো টাকা নেই এখন। "
                    "মাসে অল্প করে জরুরি পকেটে রাখলে পরে কাজে লাগবে।")

    # ── Pocket ────────────────────────────────────────────────────────────────
    elif intent == "pocket":
        h = tool("get_home_summary")
        text = "পকেটগুলো দেখতে হিসাব ট্যাব → সঞ্চয় → আমার পকেট-এ যাও।"
        if not h["insufficient_history"] and h.get("safe_to_spend_today"):
            text += f" আজ নিরাপদ খরচসীমা ৳{bn_num(h['safe_to_spend_today'])}।"

    # ── Savings level / streak ────────────────────────────────────────────────
    elif intent == "savings_level":
        h = tool("get_home_summary")
        text = "সঞ্চয় লেভেল দেখতে হিসাব ট্যাব → সঞ্চয় → লেভেল পেজে যাও।"
        if not h["insufficient_history"]:
            text += f" এই মাসে: {_risk_label(h.get('risk_level', 'green'))}।"

    # ── Budget overview ───────────────────────────────────────────────────────
    elif intent == "budget":
        tx = tool("get_transactions_summary", period="month")
        diff = tx["income_total"] - tx["spend_total"]
        text = (f"এই মাসে আয় ৳{bn_num(tx['income_total'])}, "
                f"খরচ ৳{bn_num(tx['spend_total'])}। ")
        text += (f"এখন পর্যন্ত ৳{bn_num(diff)} সাশ্রয় — চালিয়ে যাও!"
                 if diff > 0 else "খরচ একটু বেশি হয়েছে — বাকি মাসে সামলে চলো।")

    # ── Notification explanation ──────────────────────────────────────────────
    elif intent == "notification":
        h = tool("get_home_summary")
        if h["insufficient_history"]:
            text = "হিসাব দেখাতে আরও কিছু দিনের লেনদেন লাগবে।"
        elif h["risk_level"] == "red" and h["shortfall_date"]:
            drivers = tool("get_shortfall_drivers")["drivers"]
            why = ", ".join(d["text_bn"] for d in drivers[:2])
            text = (f"এই মাসে একটু সাবধান থাকো — "
                    f"{why} কারণে {_day(h['shortfall_date'])} দিকে টানাটানি হতে পারে।")
        elif h["risk_level"] == "amber":
            text = ("মাসের শেষ দিকে একটু পরিকল্পনা করো — "
                    "এখনই সতর্ক হলে টানাটানি এড়ানো যাবে।")
        else:
            text = "ভালো করছ! তোমার সঞ্চয়ের অগ্রগতি জানাতে notification দিয়েছি।"

    # ── Next income / payday ─────────────────────────────────────────────────
    elif intent == "next_income":
        h = tool("get_home_summary")
        nid = h.get("next_income_date")
        if nid:
            text = f"হিসাব অনুযায়ী পরের আয় আসতে পারে {_day(nid)} দিকে।"
        else:
            text = ("পরের আয়ের সঠিক তারিখ এখনো বোঝা যাচ্ছে না — "
                    "আরও কিছু লেনদেন হলে ধারণা দিতে পারব।")

    # ── Product explanation ("DPS কী?", "pocket কী?") ───────────────────────
    elif intent == "product_explain":
        if re.search(r"dps|ডিপিএস", text_l):
            text = ("DPS (Deposit Pension Scheme) হলো মাসিক নির্দিষ্ট পরিমাণ জমা রাখার স্কিম। "
                    "উপায় অ্যাপে সঞ্চয় → DPS-এ গিয়ে শুরু করতে পারো।")
        elif re.search(r"pocket|পকেট", text_l):
            text = ("পকেট হলো ভার্চুয়াল সঞ্চয় বাক্স — ঈদ, চিকিৎসা, লক্ষ্য ইত্যাদির জন্য আলাদা রাখা যায়। "
                    "হিসাব ট্যাব → আমার পকেট-এ দেখো।")
        elif re.search(r"npsb", text_l):
            text = ("NPSB হলো ব্যাংক-টু-ব্যাংক তাৎক্ষণিক পেমেন্ট সিস্টেম। "
                    "Cash-out-এর চেয়ে অনেক কম ফিতে টাকা পাঠানো যায়।")
        elif re.search(r"cash.?out|cashout", text_l):
            text = ("Cash-out মানে এজেন্ট বা ATM থেকে নগদ টাকা তোলা। "
                    "প্রতিবার ১.৮৫% ফি লাগে — সরাসরি পেমেন্টে এই ফি বাঁচে।")
        else:
            text = ("উপায় হলো বাংলাদেশের একটি MFS (Mobile Financial Service) প্ল্যাটফর্ম। "
                    "'হিসাব' হলো উপায়-এর AI আর্থিক সহকারী।")

    # ── Unknown / off-topic ──────────────────────────────────────────────────
    else:
        text = ("এই বিষয়ে আমার কিছু জানা নেই — "
                "আমি শুধু তোমার আর্থিক হিসাব নিয়ে কাজ করি।")

    return {"text": text, "used_tools": used, "numbers_source": "engine", "ai": False}
