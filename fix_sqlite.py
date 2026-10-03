with open('backend/hishab/store/sqlite.py', 'r', encoding='utf-8') as f:
    code = f.read()

if 'custom_names: dict = field(default_factory=dict)' not in code:
    code = code.replace('pocket_goals: dict = field(default_factory=dict)', 'pocket_goals: dict = field(default_factory=dict)\n    custom_names: dict = field(default_factory=dict)')
    code = code.replace('d["pockets"] = pockets', 'd["pockets"] = pockets\n        d["custom_names"] = d.get("custom_names") or {}')

with open('backend/hishab/store/sqlite.py', 'w', encoding='utf-8') as f:
    f.write(code)

print("Added custom_names to UserState!")
