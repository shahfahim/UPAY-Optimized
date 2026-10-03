import re

with open('web/src/components/AppShell.tsx', 'r', encoding='utf-8') as f:
    code = f.read()

pattern = re.compile(r'\{open \? \(\s*<span className="block leading-tight">\s*<span className="block text-\[15px\] font-bold">\{taka\(shell\.balance\)\}<\/span>\s*<span className="block text-\[10px\] opacity-90">.*?<\/span>\s*<\/span>\s*\) : \(', re.DOTALL)

replacement = """{open ? (
        <span className="text-[15px] font-bold">{taka(shell.balance)}</span>
      ) : ("""

new_code = pattern.sub(replacement, code)

with open('web/src/components/AppShell.tsx', 'w', encoding='utf-8') as f:
    f.write(new_code)

print("Updated AppShell.tsx properly!")
