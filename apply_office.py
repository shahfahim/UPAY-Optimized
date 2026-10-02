import sys
import os

sys.stdout.reconfigure(encoding='utf-8')

# ──────────────────────────────────────────────────────────────────────────────
# 1. QA TEST SCRIPT
# ──────────────────────────────────────────────────────────────────────────────
qa_script = """import sys, os, re
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from backend.hishab.llm.normalizer import normalize
from backend.hishab.llm.fallback import _INTENTS

def detect_intent(message: str) -> str:
    normalized = normalize(message)
    text_l = normalized.lower().strip()
    return next((name for name, pat in _INTENTS if re.search(pat, text_l)), "unknown")

TEST_CASES = [
    ("slm bhai ki khobor kemn acho", "greeting"),
    ("tumi ki ashole manush naki bot ki", "identity"),
    ("humm accha bujhechi dhonnobad", "ack"),
    ("tumi ki ki korte paro sobkichu bolo", "help"),
    ("ekdom andaze kotha bolteso faul bot", "complaint"),
    ("ami ki ashole bhalo korchi naki thik nai", "status"),
    ("amar financial condition ekhon kemon cholche", "status"),
    ("bhai amar ekhon ki kora uchit taka bachate", "advice"),
    ("taka bachate ekhon ki korbo", "advice"),
    ("aaj koto spend korte parbo bolen", "safe_spend"),
    ("ajker safe spend daily limit koto", "safe_spend"),
    ("ami ki ajke 500 taka khoroch korte parbo", "specific_amount"),
    ("2500 taka ki khoroch kora jai", "specific_amount"),
    ("amar wallet a taka ki ache naki nai", "balance"),
    ("mas sheshe ki taka thakbe naki chole jabe", "shortfall"),
    ("amar keno taka kom eibar", "shortfall"),
    ("last week e kothay beshi khoroch hoyeche?", "transactions"),
    ("khawa dawate koto gelo ei mase", "transactions"),
    ("monthly spend er hisab ta den to", "transactions"),
    ("last month vs ei mas kothay khoroch beshi", "compare"),
    ("age cheyey ki amar obostha better naki worse?", "compare"),
    ("ami agami 6 mashe 50,000 taka save korbo kivabe?", "goal"),
    ("jomate chai amar target 20000 mase", "goal"),
    ("notun dps open korbo monthly deposit korbo", "dps"),
    ("amar sanchoy level ba streak koto din", "savings_level"),
    ("amar pocket balance e koto ache ekhon", "pocket"),
    ("agent theke kesh out korle koto fee lagbe", "cashout"),
    ("samne eid er jonno taka jomano dorkar", "eid"),
    ("amar ekhuni taka lagbe hawlat joruri dorkar", "emergency"),
    ("amar next salary ba pay day kobe pabo", "next_income"),
]

passed, failed = 0, 0
print("Running 30 Difficult Edge-Case Intent Tests...")
for i, (msg, expected) in enumerate(TEST_CASES, 1):
    predicted = detect_intent(msg)
    if predicted == expected:
        passed += 1
    else:
        print(f"[{i:02d}] FAIL: '{msg}' | Expected: '{expected}', Got: '{predicted}'")
        failed += 1
print(f"Results: {passed} passed, {failed} failed out of {len(TEST_CASES)}.")
if failed > 0: sys.exit(1)
"""
with open('backend/test_edge_cases.py', 'w', encoding='utf-8') as f:
    f.write(qa_script)


# ──────────────────────────────────────────────────────────────────────────────
# 2. NLP PATCH
# ──────────────────────────────────────────────────────────────────────────────
nlp_phrases = """    # ─── extreme typos (low literacy) ──────────────────────────────────────
    ("csh out", "ক্যাশ আউট"), ("cash ot", "ক্যাশ আউট"), ("kesh out", "ক্যাশ আউট"),
    ("casout", "ক্যাশ আউট"), ("kashout", "ক্যাশ আউট"), ("kyashout", "ক্যাশ আউট"),
    ("cash auot", "ক্যাশ আউট"), ("kes aut", "ক্যাশ আউট"), ("cashut", "ক্যাশ আউট"),
    ("cshut", "ক্যাশ আউট"),
    ("snd money", "সেন্ড মানি"), ("sen money", "সেন্ড মানি"), ("send mony", "সেন্ড মানি"),
    ("snd mny", "সেন্ড মানি"), ("send mani", "সেন্ড মানি"), ("send maney", "সেন্ড মানি"),
    ("sen mani", "সেন্ড মানি"), ("send moni", "সেন্ড মানি"),
    ("balenc", "ব্যালেন্স"), ("balns", "ব্যালেন্স"), ("valoance", "ব্যালেন্স"),
    ("balanc", "ব্যালেন্স"), ("balans", "ব্যালেন্স"), ("valance", "ব্যালেন্স"),
    ("byalans", "ব্যালেন্স"), ("balnce", "ব্যালেন্স"),
    ("hawlat", "হাওলাত"), ("haolat", "হাওলাত"), ("howlat", "হাওলাত"),
    ("holat", "হাওলাত"), ("hulat", "হাওলাত"), ("udar", "উধার"), ("dhar", "ধার"),
    ("ngd", "নগদ"), ("nagd", "নগদ"), ("nogod", "নগদ"), ("nogd", "নগদ"), ("nogot", "নগদ"),
    ("bks", "বিকাশ"), ("bikas", "বিকাশ"), ("bikash", "বিকাশ"), ("bksh", "বিকাশ"), ("vicash", "বিকাশ"),
    ("kivb", "কীভাবে"), ("kibabe", "কীভাবে"), ("kibave", "কীভাবে"), ("kemne", "কীভাবে"), ("kmne", "কীভাবে"),
"""
with open('backend/hishab/llm/normalizer.py', 'r', encoding='utf-8') as f:
    norm = f.read()
if '("csh out"' not in norm:
    norm = norm.replace('    # ─── cashout queries', nlp_phrases + '\n    # ─── cashout queries')
    with open('backend/hishab/llm/normalizer.py', 'w', encoding='utf-8') as f:
        f.write(norm)
    print("✅ Applied NLP Typos to normalizer.py")

# ──────────────────────────────────────────────────────────────────────────────
# 3. BACKEND ARCHITECT PATCH
# ──────────────────────────────────────────────────────────────────────────────
with open('backend/hishab/llm/fallback.py', 'r', encoding='utf-8') as f:
    lines = f.readlines()

for i, line in enumerate(lines):
    if 'tx["income_total"]' in line or 'h["risk_level"]' in line:
        line = line.replace('tx["income_total"]', 'tx.get("income_total", 0)')
        line = line.replace('tx["spend_total"]', 'tx.get("spend_total", 0)')
        line = line.replace('h["risk_level"]', 'h.get("risk_level", "green")')
        line = line.replace('tx["by_category"][0]', 'tx.get("by_category", [{}])[0]')
        line = line.replace('h["top_actions"][0]', 'h.get("top_actions", [""])[0]')
        lines[i] = line

with open('backend/hishab/llm/fallback.py', 'w', encoding='utf-8') as f:
    f.writelines(lines)
print("✅ Applied Safe Getters to fallback.py")
