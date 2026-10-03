# -*- coding: utf-8 -*-
with open('web/src/components/AppShell.tsx', 'r', encoding='utf-8') as f:
    lines = f.readlines()

for i, line in enumerate(lines):
    if "'/app/hishab'" in line:
        lines[i] = "        {item('/app/hishab', 'spark', L('হিসাব', 'Hishab'), (\n"
        lines[i+1] = "          <>\n"
        lines[i+2] = "            {badge ? (\n"
        lines[i+3] = "              <span className={bsolute right-3 top-1 flex items-center gap-0.5 rounded-full px-1 text-[9px] font-bold text-white }>\n"
        lines[i+4] = "                {badge.days_left !== null ? L(${num(badge.days_left)} দিন, ${badge.days_left}d) : '•'}\n"
        lines[i+5] = "              </span>\n"
        lines[i+6] = "            ) : null}\n"
        lines[i+7] = "            <span className=\"absolute right-1 top-0 text-[10px] font-extrabold text-[#0b4ea2] italic drop-shadow-sm\">AI</span>\n"
        lines[i+8] = "          </>\n"
        lines[i+9] = "        ))}\n"

with open('web/src/components/AppShell.tsx', 'w', encoding='utf-8') as f:
    f.write(''.join(lines))
print("Nav fixed!")
