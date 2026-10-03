import re

with open('web/src/pages/History.tsx', 'r', encoding='utf-8') as f:
    code = f.read()

# Replace the specific transaction amount rendering
old_amount = """<p className={`text-sm font-bold ${inflow ? 'text-ok' : ''}`}>{inflow ? '+' : '−'}{taka(t.amount, { paisa: t.amount % 1 !== 0 })}</p>"""
new_amount = """<p className={`text-[15px] font-extrabold tracking-tight ${inflow ? 'text-emerald-600' : 'text-rose-600'}`}>{inflow ? '+' : '-'}{taka(t.amount, { paisa: t.amount % 1 !== 0 })}</p>"""

if old_amount in code:
    code = code.replace(old_amount, new_amount)
else:
    # If using regex because of whitespace
    code = re.sub(r'<p className=\{`text-sm font-bold \$\{inflow \? \'text-ok\' : \'\'\}`\}>\{inflow \? \'\+\' : \'−\'\}\{taka\(t\.amount, \{ paisa: t\.amount % 1 !== 0 \}\)\}<\/p>', new_amount, code)

with open('web/src/pages/History.tsx', 'w', encoding='utf-8') as f:
    f.write(code)

print("History.tsx updated to show red and green colors.")
