"""
patch_group1.py — fixes for cashout & transaction intent handlers + normalizer phrases.

Changes:
  1. fallback.py  :: cashout handler  — guard NPSB savings on non-empty habits with annual_saving>0;
                                        show count prominently first; use conversational tone.
  2. fallback.py  :: transactions     — highlight income vs spend based on query intent;
                                        gracefully handle empty by_category.
  3. normalizer.py :: _PHRASE_MAP     — add cashout/count/period Banglish phrases.
"""

import pathlib, sys

ROOT = pathlib.Path("e:/AI Hackathon DIU-2026")
FALLBACK = ROOT / "backend/hishab/llm/fallback.py"
NORMALIZER = ROOT / "backend/hishab/llm/normalizer.py"

# ─────────────────────────────────────────────────────────────────────────────
# 1.  fallback.py  —  cashout handler
# ─────────────────────────────────────────────────────────────────────────────

OLD_CASHOUT = '''\
    # ── Cash-out & fees ───────────────────────────────────────────────────────
    elif intent == "cashout":
        tx = tool("get_transactions_summary", period="month")
        route = tool("find_route", amount=5000, destination="other_mfs_wallet")
        text = (f"গত ৩০ দিনে {bn_num(tx['cash_out_count'])} বার cash-out ফি দিয়েছ "
                f"প্রায় ৳{bn_num(tx['cash_out_fees'])}। "
                "দোকানে সরাসরি upay দিয়ে পেমেন্ট করলে এই ফি বাঁচে।")
        if route["habits"]:
            text += (f" NPSB দিয়ে পাঠালে বছরে "
                     f"৳{bn_num(route['habits'][0]['annual_saving'])} বাঁচবে।")'''

NEW_CASHOUT = '''\
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
                     f"৳{bn_num(habits[0]['annual_saving'])} বাঁচবে।")'''

# ─────────────────────────────────────────────────────────────────────────────
# 2.  fallback.py  —  transactions handler
# ─────────────────────────────────────────────────────────────────────────────

OLD_TRANSACTIONS = '''\
    # ── Transactions / spending history ───────────────────────────────────────
    elif intent == "transactions":
        tx = tool("get_transactions_summary", period="month")
        top = ", ".join(f"{c['category_bn']}" for c in tx["by_category"][:2])
        net = tx["income_total"] - tx["spend_total"]
        is_avg = re.search(r"average|avg|গড়", text_l)
        if is_avg:
            text = (f"গত মাসে আয় ৳{bn_num(tx['income_total'])}, "
                    f"খরচ ৳{bn_num(tx['spend_total'])}। "
                    f"গড় নিট সঞ্চয় প্রায় ৳{bn_num(max(0.0, net))} — "
                    + (f"বেশি খরচ হয়েছে {top}-এ।" if top else ""))
        else:
            text = (f"গত ৩০ দিনে আয় ৳{bn_num(tx['income_total'])}, "
                    f"খরচ ৳{bn_num(tx['spend_total'])}। "
                    f"বেশি খরচ হয়েছে: {top}।")'''

NEW_TRANSACTIONS = '''\
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
                    + top_line)'''

# ─────────────────────────────────────────────────────────────────────────────
# 3.  normalizer.py  —  new phrases in _PHRASE_MAP  (after the cash-out block)
# ─────────────────────────────────────────────────────────────────────────────

OLD_NORMALIZER_CASHOUT = '''\
    # ─── cash-out ─────────────────────────────────────────────────────────────
    ("cashout",        "ক্যাশ আউট"),
    ("cash out",       "ক্যাশ আউট"),
    ("cash-out",       "ক্যাশ আউট"),
    ("agent theke",    "এজেন্ট থেকে"),
    ("agent fee",      "এজেন্ট ফি"),
    ("fee komabo",     "ফি কমাব"),
    ("fee koto",       "ফি কত"),'''

NEW_NORMALIZER_CASHOUT = '''\
    # ─── cash-out ─────────────────────────────────────────────────────────────
    ("cashout korsi",  "ক্যাশ আউট করেছি"),
    ("cashout korechi","ক্যাশ আউট করেছি"),
    ("last 30dine",    "গত ৩০ দিনে"),
    ("last 30 din",    "গত ৩০ দিন"),
    ("koto bar",       "কতবার"),
    ("ktobar",         "কতবার"),
    ("cashout",        "ক্যাশ আউট"),
    ("cash out",       "ক্যাশ আউট"),
    ("cash-out",       "ক্যাশ আউট"),
    ("agent theke",    "এজেন্ট থেকে"),
    ("agent fee",      "এজেন্ট ফি"),
    ("fee komabo",     "ফি কমাব"),
    ("fee koto",       "ফি কত"),'''

# ─────────────────────────────────────────────────────────────────────────────
# Apply patches
# ─────────────────────────────────────────────────────────────────────────────

def patch(path: pathlib.Path, old: str, new: str, label: str):
    src = path.read_text(encoding="utf-8")
    if old not in src:
        print(f"[ERROR] Could not find target block in {path} — '{label}'")
        sys.exit(1)
    count = src.count(old)
    if count > 1:
        print(f"[WARN]  Found {count} occurrences of '{label}' in {path} — replacing all")
    patched = src.replace(old, new)
    path.write_text(patched, encoding="utf-8")
    print(f"[OK]    Patched '{label}' in {path.name}")

patch(FALLBACK,    OLD_CASHOUT,              NEW_CASHOUT,              "cashout handler")
patch(FALLBACK,    OLD_TRANSACTIONS,          NEW_TRANSACTIONS,         "transactions handler")
patch(NORMALIZER,  OLD_NORMALIZER_CASHOUT,    NEW_NORMALIZER_CASHOUT,   "normalizer cashout phrases")

print("\nAll patches applied.")
