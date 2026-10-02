"""
patch_group2.py — Fix 5 intent handlers in hishab/llm/fallback.py:
  1. balance       — show actual h['balance'] instead of useless redirect
  2. safe_spend    — risk-level-aware messaging (green/amber/red)
  3. specific_amount — show remaining safe budget after the requested amount
  4. shortfall     — more specific: exact date/amount, top 2 drivers, 1 tip
  5. status        — include balance + safe_to_spend_today in all risk branches
"""

import sys
import ast
import os

TARGET = os.path.join(
    os.path.dirname(os.path.abspath(__file__)),
    "backend", "hishab", "llm", "fallback.py",
)

with open(TARGET, encoding="utf-8") as fh:
    src = fh.read()

original = src  # keep for diff summary

# ─────────────────────────────────────────────────────────────────────────────
# PATCH 1 — balance handler
# ─────────────────────────────────────────────────────────────────────────────
OLD_BALANCE = (
    "        else:\n"
    "            text = (f\"মূল ব্যালেন্স উপায় অ্যাপের উপরে দেখতে পাবে। \"\n"
    "                    f\"আজ নিরাপদ খরচসীমা ৳{bn_num(h.get('safe_to_spend_today') or 0)}।\")"
)
NEW_BALANCE = (
    "        else:\n"
    "            balance = h.get('balance') or 0\n"
    "            safe = h.get('safe_to_spend_today') or 0\n"
    "            if balance == 0:\n"
    "                text = (\"ব্যালেন্স এখন ০ টাকা — \"\n"
    "                        f\"আজ নিরাপদ খরচসীমা ৳{bn_num(safe)}।\")\n"
    "            else:\n"
    "                text = (f\"আজকের ব্যালেন্স ৳{bn_num(balance)}। \"\n"
    "                        f\"নিরাপদ খরচসীমা ৳{bn_num(safe)}।\")"
)

assert OLD_BALANCE in src, "PATCH 1 target not found — check indentation/string"
src = src.replace(OLD_BALANCE, NEW_BALANCE, 1)
print("✓ PATCH 1 (balance) applied")

# ─────────────────────────────────────────────────────────────────────────────
# PATCH 2 — safe_spend handler (risk-level-aware messaging)
# ─────────────────────────────────────────────────────────────────────────────
OLD_SAFE_SPEND = (
    "    elif intent == \"safe_spend\":\n"
    "        h = tool(\"get_home_summary\")\n"
    "        if h[\"insufficient_history\"]:\n"
    "            text = \"হিসাব দেখাতে আরও কিছু দিনের লেনদেন লাগবে।\"\n"
    "        elif (h.get(\"safe_to_spend_today\") or 0) > 0:\n"
    "            text = (f\"আজকের নিরাপদ খরচসীমা ৳{bn_num(h['safe_to_spend_today'])}। \"\n"
    "                    \"এটা ধরে চললে মাস শেষে চাপ কম হবে।\")\n"
    "        else:\n"
    "            text = \"আজ খরচ যতটা পারো কমাও — মাসের বাজেট একটু টাইট।\""
)
NEW_SAFE_SPEND = (
    "    elif intent == \"safe_spend\":\n"
    "        h = tool(\"get_home_summary\")\n"
    "        if h[\"insufficient_history\"]:\n"
    "            text = \"হিসাব দেখাতে আরও কিছু দিনের লেনদেন লাগবে।\"\n"
    "        else:\n"
    "            safe = h.get(\"safe_to_spend_today\") or 0\n"
    "            risk = h.get(\"risk_level\", \"green\")\n"
    "            if safe <= 0:\n"
    "                text = \"আজ খরচ যতটা পারো কমাও — মাসের বাজেট একটু টাইট।\"\n"
    "            elif risk == \"green\":\n"
    "                text = (f\"আজ ৳{bn_num(safe)} খরচ করতে পারবে — ভালো অবস্থায় আছ!\")\n"
    "            elif risk == \"amber\":\n"
    "                text = (f\"আজ ৳{bn_num(safe)}-এর মধ্যে রাখলে ভালো — \"\n"
    "                        \"মাসের শেষে সামলানো যাবে।\")\n"
    "            else:\n"
    "                text = (f\"আজ ৳{bn_num(safe)}-এর বেশি খরচ করো না — \"\n"
    "                        \"টানাটানির ঝুঁকি আছে।\")"
)

assert OLD_SAFE_SPEND in src, "PATCH 2 target not found — check indentation/string"
src = src.replace(OLD_SAFE_SPEND, NEW_SAFE_SPEND, 1)
print("✓ PATCH 2 (safe_spend) applied")

# ─────────────────────────────────────────────────────────────────────────────
# PATCH 3 — specific_amount handler (show remaining budget after spend)
# ─────────────────────────────────────────────────────────────────────────────
OLD_SPECIFIC = (
    "        if h[\"insufficient_history\"]:\n"
    "            text = \"হিসাব দেখাতে আরও কিছু দিনের লেনদেন লাগবে।\"\n"
    "        elif amount <= safe:\n"
    "            text = (f\"৳{bn_num(amount)} খরচ করা নিরাপদ — আজকের সীমা \"\n"
    "                    f\"৳{bn_num(safe)}, তাই ঠিক আছে।\")\n"
    "        else:\n"
    "            text = (f\"৳{bn_num(amount)} একটু বেশি হতে পারে। \"\n"
    "                    f\"আজকের নিরাপদ সীমা ৳{bn_num(safe)}। \"\n"
    "                    \"একটু কম খরচ করলে মাস শেষে সুবিধা হবে।\")"
)
NEW_SPECIFIC = (
    "        if h[\"insufficient_history\"]:\n"
    "            text = \"হিসাব দেখাতে আরও কিছু দিনের লেনদেন লাগবে।\"\n"
    "        elif amount <= safe:\n"
    "            remaining = safe - amount\n"
    "            text = (f\"হ্যাঁ, ৳{bn_num(amount)} খরচ করতে পারবে। \"\n"
    "                    f\"আজকের বাকি সীমা ৳{bn_num(remaining)}।\")\n"
    "        else:\n"
    "            text = (f\"একটু বেশি হবে — আজ ৳{bn_num(safe)} পর্যন্ত নিরাপদ। \"\n"
    "                    \"একটু কম খরচ করলে মাস শেষে সুবিধা হবে।\")"
)

assert OLD_SPECIFIC in src, "PATCH 3 target not found — check indentation/string"
src = src.replace(OLD_SPECIFIC, NEW_SPECIFIC, 1)
print("✓ PATCH 3 (specific_amount) applied")

# ─────────────────────────────────────────────────────────────────────────────
# PATCH 4 — shortfall handler (more specific: date + amount + drivers + tip)
# ─────────────────────────────────────────────────────────────────────────────
OLD_SHORTFALL = (
    "    elif intent == \"shortfall\":\n"
    "        h = tool(\"get_home_summary\")\n"
    "        if h[\"insufficient_history\"]:\n"
    "            text = \"হিসাব দেখাতে আরও কিছু দিনের লেনদেন লাগবে।\"\n"
    "        elif h[\"risk_level\"] in (\"amber\", \"red\") and h[\"shortfall_date\"]:\n"
    "            drivers = tool(\"get_shortfall_drivers\")[\"drivers\"]\n"
    "            why = \", \".join(d[\"text_bn\"] for d in drivers[:2])\n"
    "            text = (f\"{_day(h['shortfall_date'])} দিকে টানাটানি হতে পারে \"\n"
    "                    f\"(প্রায় ৳{bn_num(h['shortfall_amount'])} শর্ট)। কারণ: {why}।\")\n"
    "            if h[\"top_actions\"]:\n"
    "                text += f\" পরামর্শ: {h['top_actions'][0]}।\"\n"
    "        else:\n"
    "            text = (f\"এই মাসে টানাটানির ঝুঁকি কম — ভালো করছ! \"\n"
    "                    f\"আজ নিরাপদ খরচ প্রায় ৳{bn_num(h.get('safe_to_spend_today') or 0)}।\")"
)
NEW_SHORTFALL = (
    "    elif intent == \"shortfall\":\n"
    "        h = tool(\"get_home_summary\")\n"
    "        if h[\"insufficient_history\"]:\n"
    "            text = \"হিসাব দেখাতে আরও কিছু দিনের লেনদেন লাগবে।\"\n"
    "        elif h[\"risk_level\"] in (\"amber\", \"red\") and h.get(\"shortfall_date\"):\n"
    "            drivers = tool(\"get_shortfall_drivers\")[\"drivers\"]\n"
    "            why = \", \".join(d[\"text_bn\"] for d in drivers[:2])\n"
    "            shortfall_amt = h.get('shortfall_amount') or 0\n"
    "            text = (f\"{_day(h['shortfall_date'])} দিকে টানাটানি হতে পারে \"\n"
    "                    f\"(প্রায় ৳{bn_num(shortfall_amt)} শর্ট)।\")\n"
    "            if why:\n"
    "                text += f\" মূল কারণ: {why}।\"\n"
    "            if h.get(\"top_actions\"):\n"
    "                text += f\" পরামর্শ: {h['top_actions'][0]}।\"\n"
    "            else:\n"
    "                text += \" এখনই খরচ একটু কমালে মাস শেষে সামলানো যাবে।\"\n"
    "        elif h[\"risk_level\"] in (\"amber\", \"red\"):\n"
    "            # risk exists but no shortfall_date yet\n"
    "            drivers = tool(\"get_shortfall_drivers\")[\"drivers\"]\n"
    "            why = \", \".join(d[\"text_bn\"] for d in drivers[:2])\n"
    "            text = (\"মাসের শেষে টানাটানি হতে পারে।\")\n"
    "            if why:\n"
    "                text += f\" কারণ: {why}।\"\n"
    "            if h.get(\"top_actions\"):\n"
    "                text += f\" পরামর্শ: {h['top_actions'][0]}।\"\n"
    "        else:\n"
    "            safe = h.get('safe_to_spend_today') or 0\n"
    "            text = (f\"এই মাসে টানাটানির ঝুঁকি কম — ভালো করছ! \"\n"
    "                    f\"আজ নিরাপদ খরচ প্রায় ৳{bn_num(safe)}।\")"
)

assert OLD_SHORTFALL in src, "PATCH 4 target not found — check indentation/string"
src = src.replace(OLD_SHORTFALL, NEW_SHORTFALL, 1)
print("✓ PATCH 4 (shortfall) applied")

# ─────────────────────────────────────────────────────────────────────────────
# PATCH 5 — status handler (add balance + safe_to_spend to all branches)
# ─────────────────────────────────────────────────────────────────────────────
OLD_STATUS = (
    "    elif intent == \"status\":\n"
    "        h = tool(\"get_home_summary\")\n"
    "        if h[\"insufficient_history\"]:\n"
    "            text = \"হিসাব দেখাতে আরও কিছু দিনের লেনদেন লাগবে।\"\n"
    "        else:\n"
    "            risk = h.get(\"risk_level\", \"green\")\n"
    "            if risk == \"green\":\n"
    "                text = (f\"হ্যাঁ, ভালোই করছ! এই মাসে ঝুঁকি কম। \"\n"
    "                        f\"আজ নিরাপদ খরচসীমা ৳{bn_num(h.get('safe_to_spend_today') or 0)}।\")\n"
    "            elif risk == \"amber\":\n"
    "                text = (\"মোটামুটি চলছে, তবে মাসের শেষে একটু সামলে চলো। \"\n"
    "                        f\"আজ ৳{bn_num(h.get('safe_to_spend_today') or 0)}-এর মধ্যে রাখো।\")\n"
    "            else:\n"
    "                drivers = tool(\"get_shortfall_drivers\")[\"drivers\"]\n"
    "                why = \", \".join(d[\"text_bn\"] for d in drivers[:2])\n"
    "                text = (f\"এই মাসে একটু চাপ আছে — {why}। \"\n"
    "                        \"একটু সামলালেই সামলে নিতে পারবে।\")"
)
NEW_STATUS = (
    "    elif intent == \"status\":\n"
    "        h = tool(\"get_home_summary\")\n"
    "        if h[\"insufficient_history\"]:\n"
    "            text = \"হিসাব দেখাতে আরও কিছু দিনের লেনদেন লাগবে।\"\n"
    "        else:\n"
    "            risk = h.get(\"risk_level\", \"green\")\n"
    "            balance = h.get('balance') or 0\n"
    "            safe = h.get('safe_to_spend_today') or 0\n"
    "            if risk == \"green\":\n"
    "                text = (f\"ভালো করছ! ব্যালেন্স ৳{bn_num(balance)}, \"\n"
    "                        f\"আজ ৳{bn_num(safe)} খরচ করতে পারবে।\")\n"
    "            elif risk == \"amber\":\n"
    "                drivers = tool(\"get_shortfall_drivers\")[\"drivers\"]\n"
    "                why = \", \".join(d[\"text_bn\"] for d in drivers[:2])\n"
    "                text = (f\"মোটামুটি চলছে। ব্যালেন্স ৳{bn_num(balance)}, \"\n"
    "                        f\"তবে {why} কারণে একটু সাবধান।\")\n"
    "            else:\n"
    "                drivers = tool(\"get_shortfall_drivers\")[\"drivers\"]\n"
    "                why = \", \".join(d[\"text_bn\"] for d in drivers[:2])\n"
    "                text = (f\"এই মাসে একটু চাপ আছে। ব্যালেন্স ৳{bn_num(balance)}, \"\n"
    "                        f\"{why} কারণে সাবধান থাকো।\")"
)

assert OLD_STATUS in src, "PATCH 5 target not found — check indentation/string"
src = src.replace(OLD_STATUS, NEW_STATUS, 1)
print("✓ PATCH 5 (status) applied")

# ─────────────────────────────────────────────────────────────────────────────
# WRITE & SYNTAX-CHECK
# ─────────────────────────────────────────────────────────────────────────────
with open(TARGET, "w", encoding="utf-8") as fh:
    fh.write(src)
print(f"\n✓ Written to {TARGET}")

try:
    ast.parse(src)
    print("✓ Syntax check passed (ast.parse OK)")
except SyntaxError as e:
    print(f"✗ SYNTAX ERROR: {e}")
    sys.exit(1)

# Quick diff summary
added = sum(1 for a, b in zip(original.splitlines(), src.splitlines()) if a != b)
print(f"\nSummary: ~{abs(len(src.splitlines()) - len(original.splitlines()))} lines net added, "
      f"{added} lines changed.")
print("All 5 patches applied successfully.")
