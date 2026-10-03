import re

with open('web/src/components/AppShell.tsx', 'r', encoding='utf-8') as f:
    code = f.read()

# We want to remove the badge rendering block inside the extra parameter of item('/app/hishab'
# Current block:
"""
            {badge ? (
              <span className={`absolute right-3 top-1 flex items-center gap-0.5 rounded-full px-1 text-[9px] font-bold text-white ${dot}`}>
                {badge.days_left !== null ? L(`${num(badge.days_left)} দিন`, `${badge.days_left}d`) : '•'}
              </span>
            ) : null}
"""

# Regex to safely remove it
code = re.sub(r'\{badge \? \(\s*<span.*?</span>\s*\) : null\}', '', code, flags=re.DOTALL)

with open('web/src/components/AppShell.tsx', 'w', encoding='utf-8') as f:
    f.write(code)

print("Green badge removed!")
