import re

with open('backend/hishab/llm/fallback.py', 'r', encoding='utf-8') as f:
    code = f.read()

# Add is_english helper
helper = """def _is_en(text: str) -> bool:
    en = len(re.findall(r'[a-zA-Z]', text))
    bn = len(re.findall(r'[\u0980-\u09FF]', text))
    return en > bn and en > 0

def _translate_bn_to_en(text: str) -> str:
    # Convert numbers
    bn_digits = "০১২৩৪৫৬৭৮৯"
    en_digits = "0123456789"
    for bd, ed in zip(bn_digits, en_digits):
        text = text.replace(bd, ed)
    
    # Dictionary of common phrases
    mapping = {
        "আপনার বর্তমান ব্যালেন্স": "Your current balance is",
        "বর্তমান ব্যালেন্স": "current balance",
        "টাকা": "Tk",
        "৳": "Tk ",
        "নিরাপদে খরচ করতে পারবেন": "can safely spend",
        "আপনার নিরাপদে খরচ করার লিমিট": "Your safe spending limit is",
        "আজ আর": "Today",
        "খরচ না করাই ভালো": "it is better not to spend",
        "খরচ করতে পারবেন": "can spend",
        "ক্যাশ আউট": "Cash-out",
        "ক্যাশ-আউট": "Cash-out",
        "চার্জ": "charge",
        "কাটবে": "will be deducted",
        "ডিপিএস": "DPS",
        "সেভিংস": "savings",
        "মোট": "Total",
        "জমা": "saved",
        "লক্ষ্য": "goal",
        "মাসে": "month",
        "আজকের জন্য": "for today",
        "আপনার অবস্থা": "Your status",
        "ভালো": "Good",
        "খারাপ": "Bad",
        "সাবধান": "Warning",
        "বাকি": "remaining",
        "অ্যাকাউন্ট": "account",
        "পর্যাপ্ত ব্যালেন্স নেই": "Insufficient balance",
        "দুঃখিত": "Sorry",
        "আমি বুঝতে পারিনি": "I couldn't understand",
        "আবার বলুন": "Please say that again",
        "সাহায্য": "Help",
        "পরামর্শ": "Advice",
        "ট্রানজেকশন": "transaction",
        "হিসাব": "calculation",
        "কিভাবে": "How",
        "কেন": "Why",
        "কোথায়": "Where",
        "থেকে": "from",
        "এজেন্ট": "Agent",
        "ফি": "fee",
        "বাঁচবে": "will be saved",
        "নোট:": "Note:",
        "কম পড়েছে": "fell short",
        "বেশি": "more",
        "কম": "less",
        "আছে": "is available",
        "নেই": "is not available",
        "করতে পারবেন": "you can do",
        "করলে": "if done",
        "গেলে": "if gone",
        "হবে": "will be",
        "হয়েছে": "has been",
        "ধন্যবাদ": "Thank you",
        "হ্যালো": "Hello",
        "সালাম": "Greetings",
        "ওয়ালাইকুম আসসালাম": "Walaikum Assalam",
        "কি খবর": "What's up",
        "আমি হিসাব এআই": "I am Hishab AI",
        "আপনার স্মার্ট অ্যাসিস্ট্যান্ট": "your smart assistant",
        "কীভাবে সাহায্য করতে পারি?": "How can I help you?",
        "এই বিষয়টি এখন আমার কাছে নেই।": "I don't have information on this right now.",
        "তোমার আয়-খরচের হিসাব জানতে চাইলে বলো।": "Ask me if you want to know about your income and expenses.",
        "আজ আপনার নিরাপদ খরচ": "Today your safe spend is"
    }
    
    # Sort keys by length descending to prevent partial replacements
    for k in sorted(mapping.keys(), key=len, reverse=True):
        text = text.replace(k, mapping[k])
        
    return text

"""

if "def _is_en" not in code:
    code = code.replace("def _ml_intent(text: str) -> str | None:", helper + "def _ml_intent(text: str) -> str | None:")

# Inject translation before returning in answer()
old_return = """    if not text:
        text = " 3 ?ssݨ , +rݨ   ؅"+ ?    <r__"    <  ?_ -_ ?r__" __ "

    return {"text": text, "used_tools": used, "numbers_source": "", "ai": False}"""

new_return = """    if not text:
        text = "দুঃখিত, আমি বুঝতে পারিনি। আবার বলুন।"

    if _is_en(message):
        text = _translate_bn_to_en(text)

    return {"text": text, "used_tools": used, "numbers_source": "", "ai": False}"""

# Fix encoding issues in old_return regex matching by using a simpler replace
if "return {\"text\": text, \"used_tools\": used, \"numbers_source\": \"\", \"ai\": False}" in code:
    code = re.sub(
        r'    if not text:\n        text = "[^"]+"\n\n    return \{"text": text, "used_tools": used, "numbers_source": "", "ai": False\}',
        new_return,
        code
    )

with open('backend/hishab/llm/fallback.py', 'w', encoding='utf-8') as f:
    f.write(code)

print("Updated fallback.py with English translation support!")
