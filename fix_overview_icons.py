# -*- coding: utf-8 -*-
with open('web/src/pages/hub/Overview.tsx', 'r', encoding='utf-8') as f:
    code = f.read()

# Fix button 1
code = code.replace(
    'className="flex flex-col items-center justify-center bg-white rounded-xl p-3 shadow-sm border border-slate-100"',
    'className="flex flex-col items-center justify-center bg-white rounded-[20px] p-4 shadow-[0_8px_20px_-4px_rgba(0,0,0,0.05)] border border-slate-100/50 hover:shadow-[0_8px_25px_-4px_rgba(11,78,162,0.15)] transition-all duration-300 active:scale-95"'
)
code = code.replace(
    'className="h-10 w-10 rounded-full bg-blue-50 flex items-center justify-center mb-2"',
    'className="h-12 w-12 rounded-[14px] bg-blue-50 flex items-center justify-center mb-3"'
)

# Fix button 2
code = code.replace(
    'className="h-10 w-10 rounded-full bg-green-50 flex items-center justify-center mb-2"',
    'className="h-12 w-12 rounded-[14px] bg-green-50 flex items-center justify-center mb-3"'
)

# Fix button 3
code = code.replace(
    'className="h-10 w-10 rounded-full bg-yellow-100 flex items-center justify-center mb-2"',
    'className="h-12 w-12 rounded-[14px] bg-[#ffd500] bg-opacity-20 flex items-center justify-center mb-3"'
)

with open('web/src/pages/hub/Overview.tsx', 'w', encoding='utf-8') as f:
    f.write(code)
print('Overview buttons updated')
