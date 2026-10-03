# -*- coding: utf-8 -*-
with open('web/src/pages/hub/Overview.tsx', 'r', encoding='utf-8') as f:
    code = f.read()

code = code.replace(
    'className="bg-upay-blue px-4 pt-6 pb-12 rounded-b-3xl"',
    'className="bg-upay-blue px-4 pt-6 pb-12 rounded-b-3xl animate-fade-in"'
)

with open('web/src/pages/hub/Overview.tsx', 'w', encoding='utf-8') as f:
    f.write(code)
