import sys, os, re
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
