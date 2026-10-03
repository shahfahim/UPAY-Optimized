# -*- coding: utf-8 -*-
with open('web/src/components/AppShell.tsx', 'r', encoding='utf-8') as f:
    code = f.read()

import re
code = re.sub(
    r'className=\{ bsolute right-3 top-1 flex items-center gap-0\.5 rounded-full px-1 text-\[9px\] font-bold text-white \}',
    'className={bsolute right-3 top-1 flex items-center gap-0.5 rounded-full px-1 text-[9px] font-bold text-white }',
    code
)
code = re.sub(
    r'\{badge\.days_left \!\=\= null \? L\(\$\{num\(badge\.days_left\)\} দিন, \$\{badge\.days_left\}d\) \: \'•\'\}',
    '{badge.days_left !== null ? L(${num(badge.days_left)} দিন, ${badge.days_left}d) : \'•\'}',
    code
)

with open('web/src/components/AppShell.tsx', 'w', encoding='utf-8') as f:
    f.write(code)
print('Fixed!')
