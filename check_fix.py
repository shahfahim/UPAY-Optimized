import re
with open('backend/hishab/llm/fallback.py', 'r', encoding='utf-8') as f:
    code = f.read()

match = re.search(r'সবচেয়ে ভালো পথ হলো NPSB বা সরাসরি পেমেন্ট।.*', code)
if match:
    # Print it out as unicode escapes so we don't get encoding errors in the terminal
    print(match.group(0).encode('utf-8'))
