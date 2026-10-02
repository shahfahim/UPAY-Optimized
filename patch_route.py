"""Patch for transaction routing in Ask.tsx, fallback.py, and normalizer.py"""
import sys, re
sys.stdout.reconfigure(encoding='utf-8')

# ─────────────────────────────────────────────────────────────────────────────
# 1. Update Ask.tsx to render RouteWidget
# ─────────────────────────────────────────────────────────────────────────────
ask_path = 'web/src/pages/hub/Ask.tsx'
with open(ask_path, 'r', encoding='utf-8') as f:
    ask_content = f.read()

# Add import
if 'RouteWidget' not in ask_content:
    ask_content = ask_content.replace(
        "import { isVoiceSupported, listenBn } from '../../lib/voice'",
        "import { isVoiceSupported, listenBn } from '../../lib/voice'\nimport { RouteWidget } from '../../components/RouteWidget'\nimport type { RouteResult } from '../../api/types'"
    )

# Render widget in message loop
old_msg_render = """            {m.answer?.ai && <AiBadge className="mb-1" />}
            <p className="whitespace-pre-line leading-relaxed">{m.text}</p>
            {m.answer && <Sources a={m.answer} />}"""
new_msg_render = """            {m.answer?.ai && <AiBadge className="mb-1" />}
            <p className="whitespace-pre-line leading-relaxed">{m.text}</p>
            {m.answer?.used_tools.map(t => t.name === 'find_route' && t.result ? (
              <RouteWidget key="route" result={t.result as RouteResult} />
            ) : null)}
            {m.answer && <Sources a={m.answer} />}"""

if old_msg_render in ask_content:
    ask_content = ask_content.replace(old_msg_render, new_msg_render)
    print("✅ Ask.tsx patched successfully.")
else:
    print("⚠️ Could not find exact msg render block in Ask.tsx")

with open(ask_path, 'w', encoding='utf-8') as f:
    f.write(ask_content)


# ─────────────────────────────────────────────────────────────────────────────
# 2. Update normalizer.py with new routing phrases
# ─────────────────────────────────────────────────────────────────────────────
nm_path = 'backend/hishab/llm/normalizer.py'
with open(nm_path, 'r', encoding='utf-8') as f:
    nm_content = f.read()

new_phrases = """    # ─── routing queries ──────────────────────────────────────────────────────
    ("nagad", "নগদ"),
    ("bkash", "বিকাশ"),
    ("bkashe", "বিকাশে"),
    ("pathabo", "পাঠাব"),
    ("kivabe pathabo", "কীভাবে পাঠাব"),
    ("kemne pathabo", "কীভাবে পাঠাব"),
    ("npsb theke", "npsb থেকে"),
    ("send money", "সেন্ড মানি"),
"""

if '("nagad", "নগদ")' not in nm_content:
    nm_content = nm_content.replace(
        '    # ─── cashout queries ──────────────────────────────────────────────────────',
        new_phrases + '    # ─── cashout queries ──────────────────────────────────────────────────────'
    )
    with open(nm_path, 'w', encoding='utf-8') as f:
        f.write(nm_content)
    print("✅ normalizer.py patched successfully.")


# ─────────────────────────────────────────────────────────────────────────────
# 3. Update fallback.py with new intent and handler
# ─────────────────────────────────────────────────────────────────────────────
fb_path = 'backend/hishab/llm/fallback.py'
with open(fb_path, 'r', encoding='utf-8') as f:
    fb_lines = f.readlines()

eol = '\r\n' if '\r\n' in fb_lines[0] else '\n'

# Find the intent list
intent_idx = next(i for i, l in enumerate(fb_lines) if '_INTENTS' in l)
# Insert after specific_amount or product_explain
insert_idx = next(i for i, l in enumerate(fb_lines[intent_idx:]) if 'product_explain' in l) + intent_idx

if not any('transaction_route' in l for l in fb_lines):
    new_intent = '    ("transaction_route", r"(কীভাবে|কিভাবে).* (পাঠাব|পাঠাতে|ট্রান্সফার|transfer|সেন্ড|send)|(নগদ|বিকাশ|npsb|ব্যাংক).* (কীভাবে|কিভাবে|পাঠাব)"),' + eol
    fb_lines.insert(insert_idx, new_intent)
    print("✅ Inserted transaction_route intent.")

# Insert handler
handler_idx = next(i for i, l in enumerate(fb_lines) if 'elif intent == "product_explain":' in l)
if not any('elif intent == "transaction_route":' in l for l in fb_lines):
    handler_code = [
        '    # ─── Transaction Route / Send Money ───────────────────────────────────────────────────────────────────────' + eol,
        '    elif intent == "transaction_route":' + eol,
        '        # Try to parse destination' + eol,
        '        dest = "other_mfs_wallet"' + eol,
        '        if "নগদ" in text_l or "বিকাশ" in text_l:' + eol,
        '            dest = "other_mfs_wallet"' + eol,
        '        elif "npsb" in text_l or "ব্যাংক" in text_l:' + eol,
        '            dest = "bank_account"' + eol,
        '' + eol,
        '        # Parse amount (default 500 if not found)' + eol,
        '        amount = 500' + eol,
        '        nums = _numbers(text_l)' + eol,
        '        if nums: amount = nums[0]' + eol,
        '' + eol,
        '        res = tool("find_route", amount=amount, destination=dest)' + eol,
        '        text = "সবচেয়ে ভালো পথ হলো NPSB বা সরাসরি পেমেন্ট। નીચે পুরো হিসাব দেখানো হলো:"' + eol,
        '        return {"text": text, "used_tools": used, "numbers_source": "", "ai": False}' + eol,
        eol
    ]
    fb_lines[handler_idx:handler_idx] = handler_code
    print("✅ Inserted transaction_route handler.")
    with open(fb_path, 'w', encoding='utf-8') as f:
        f.writelines(fb_lines)
