import re

with open('backend/hishab/services_hub.py', 'r', encoding='utf-8') as f:
    code = f.read()

# 1. Fix savings() iteration
old_iter = """        pockets = []
        for p in POCKETS:
            if p == "paisa":
                continue"""
new_iter = """        pockets = []
        # Dynamic pockets
        for p in list(st.pockets.keys()):
            if p == "paisa" or p == "custom":
                continue"""
code = code.replace(old_iter, new_iter)

# 2. Fix name mapping in savings()
code = code.replace('POCKET_BN[p]', 'POCKET_BN.get(p, p.title())')

# 3. Fix move_pocket restrictions
old_move = 'if pocket not in POCKETS or (pocket == "paisa" and direction == "in"):'
new_move = 'if (pocket == "paisa" and direction == "in"):'
code = code.replace(old_move, new_move)

with open('backend/hishab/services_hub.py', 'w', encoding='utf-8') as f:
    f.write(code)

print("Updated backend to support dynamic pockets!")
