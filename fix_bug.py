import re

with open('backend/hishab/services_hub.py', 'r', encoding='utf-8') as f:
    code = f.read()

old_str = '"name_bn": POCKET_BN.get(p, p.title())'
new_str = '"name_bn": getattr(st, "custom_names", {}).get(p, POCKET_BN.get(p, p.title()))'

code = code.replace(old_str, new_str)

with open('backend/hishab/services_hub.py', 'w', encoding='utf-8') as f:
    f.write(code)

print("Fixed the name_bn resolving issue in services_hub.py!")
