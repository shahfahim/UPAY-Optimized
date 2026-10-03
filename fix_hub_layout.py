import re

with open('web/src/pages/hub/HubLayout.tsx', 'r', encoding='utf-8') as f:
    code = f.read()

# Fix the sticky nav mixing with content on scroll
# It is currently: className="no-scrollbar sticky top-0 z-30 mt-2 flex gap-1 overflow-x-auto bg-transparent px-3 pb-2"
bad_nav_class = 'className="no-scrollbar sticky top-0 z-30 mt-2 flex gap-1 overflow-x-auto bg-transparent px-3 pb-2"'
good_nav_class = 'className="no-scrollbar sticky top-0 z-30 mt-2 flex gap-1 overflow-x-auto bg-white/85 backdrop-blur-xl px-3 pb-2 pt-2 border-b border-slate-200/50 shadow-sm transition-all"'

code = code.replace(bad_nav_class, good_nav_class)

with open('web/src/pages/hub/HubLayout.tsx', 'w', encoding='utf-8') as f:
    f.write(code)

print("HubLayout sticky nav fixed!")
