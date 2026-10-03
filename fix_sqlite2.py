import re

with open('backend/hishab/store/sqlite.py', 'r', encoding='utf-8') as f:
    code = f.read()

old_json = """        pockets = {p: 0.0 for p in POCKETS}
        pockets.update(d.get("pockets") or {})
        d["pockets"] = pockets"""
new_json = """        d["pockets"] = d.get("pockets") or {}"""

code = code.replace(old_json, new_json)

with open('backend/hishab/store/sqlite.py', 'w', encoding='utf-8') as f:
    f.write(code)

print("Fixed from_json to allow persistent deletion!")
