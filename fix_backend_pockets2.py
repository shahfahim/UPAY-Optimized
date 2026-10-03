import re

with open('backend/hishab/services_hub.py', 'r', encoding='utf-8') as f:
    code = f.read()

# Fix second restriction in move_pocket
old_move2 = 'if pocket not in POCKETS or pocket == "paisa":'
new_move2 = 'if pocket == "paisa":'
code = code.replace(old_move2, new_move2)

with open('backend/hishab/services_hub.py', 'w', encoding='utf-8') as f:
    f.write(code)

print("Updated backend move_pocket fully!")
