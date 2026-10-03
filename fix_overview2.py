import re

with open('web/src/pages/hub/Overview.tsx', 'r', encoding='utf-8') as f:
    code = f.read()

# Fix Card (BarChart)
code = re.sub(
    r'className="bg-white shadow-sm border border-slate-100"',
    r'className="bg-white shadow-[0_8px_30px_rgb(0,0,0,0.06)] border-none rounded-2xl"',
    code
)

# Fix Grid Buttons
code = re.sub(
    r'shadow-\[0_8px_20px_-4px_rgba\(0,0,0,0\.05\)\] border border-slate-100/50',
    r'shadow-[0_8px_30px_rgb(0,0,0,0.06)] border-none',
    code
)

# Fix Lesson Card
code = re.sub(
    r'className="border-slate-200 shadow-sm bg-white"',
    r'className="border-none bg-white shadow-[0_8px_30px_rgb(0,0,0,0.06)] rounded-2xl"',
    code
)

with open('web/src/pages/hub/Overview.tsx', 'w', encoding='utf-8') as f:
    f.write(code)

print("Overview card shadows fixed properly!")
