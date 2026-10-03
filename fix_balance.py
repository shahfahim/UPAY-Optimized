import re

with open('web/src/components/AppShell.tsx', 'r', encoding='utf-8') as f:
    code = f.read()

# Replace the block
old_block = """          {bal ? (
          <span className="block leading-tight">
            <span className="block text-[15px] font-bold">{taka(shell.balance)}</span>
            <span className="block text-[10px] opacity-90">
              {shell.safe_today > 0
                ? L(`আজ নিরাপদ খরচ ${taka(shell.safe_today)}`, `Safe today ${taka(shell.safe_today)}`)
                : L(`সাবধানে খরচ করুন`, `Spend carefully`)}
            </span>
          </span>
        ) : ("""

# Since powershell messes up Bengali text matching, I will use a regex based on english text and structure.

import re

with open('web/src/components/AppShell.tsx', 'r', encoding='utf-8') as f:
    code = f.read()

pattern = re.compile(r'\{bal \? \(\s*<span className="block leading-tight">\s*<span className="block text-\[15px\] font-bold">\{taka\(shell\.balance\)\}<\/span>\s*<span className="block text-\[10px\] opacity-90">.*?<\/span>\s*<\/span>\s*\) : \(', re.DOTALL)

replacement = """{bal ? (
          <span className="text-[15px] font-bold">{taka(shell.balance)}</span>
        ) : ("""

new_code = pattern.sub(replacement, code)

with open('web/src/components/AppShell.tsx', 'w', encoding='utf-8') as f:
    f.write(new_code)

print("Updated AppShell.tsx!")
