import re

with open('hishab/llm/fallback.py', 'r', encoding='utf-8') as f:
    code = f.read()

code = code.replace("return _get_memory(uid)", "return _user_memory.setdefault(uid, {})")

with open('hishab/llm/fallback.py', 'w', encoding='utf-8') as f:
    f.write(code)

print("Infinite recursion fixed!")
