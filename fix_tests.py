import sys

with open('backend/hishab/llm/fallback.py', 'r', encoding='utf-8') as f:
    text = f.read()

text = text.replace('r"কে তুমি|ke tumi|tomar nam ki|robot|ai"', 'r"কে তুমি|ke tumi|tomar nam ki|robot|bot|ai"')
text = text.replace('r"obostha kemon|অবস্থা কেমন"', 'r"obostha kemon|অবস্থা কেমন|bhalo korchi naki|bhalo korsi naki"')
text = text.replace('r"(খরচ|khoroch).* (করতে পারবো|korte parbo|korte parba)"', 'r"(খরচ|khoroch).* (করতে|korte)"')
text = text.replace('r"koyta taka ache|কত টাকা আছে|balance|ব্যালেন্স|koto ache|tk ache"', 'r"koyta taka ache|কত টাকা আছে|balance|ব্যালেন্স|koto ache|tk ache|wallet"')
text = text.replace('r"taka pabo|টাকা পাবো|shortfall|টানাটানি|tanatani"', 'r"taka pabo|টাকা পাবো|shortfall|টানাটানি|tanatani|taka kom"')
text = text.replace('r"kothay khoroch|kothay koto|kothai koto"', 'r"kothay khoroch|kothay koto|kothai koto|koto gelo"')
text = text.replace('r"compare|toulona|তুলনা|better"', 'r"compare|toulona|তুলনা|better|better naki"')

# Fix intent order (pocket should come before balance)
import re
text = re.sub(r'(\s*\("balance".*?\n)', r'', text)
pocket_idx = text.find('("pocket",')
if pocket_idx != -1:
    text = text[:pocket_idx] + '("balance", r"koyta taka ache|কত টাকা আছে|balance|ব্যালেন্স|koto ache|tk ache|wallet"),\n    ' + text[pocket_idx:]

with open('backend/hishab/llm/fallback.py', 'w', encoding='utf-8') as f:
    f.write(text)
print("Regex patched.")
