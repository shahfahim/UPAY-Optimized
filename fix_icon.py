# -*- coding: utf-8 -*-
with open('web/src/components/Icon.tsx', 'r', encoding='utf-8') as f:
    code = f.read()

code = code.replace('strokeWidth = 1.8', 'strokeWidth = 2')

with open('web/src/components/Icon.tsx', 'w', encoding='utf-8') as f:
    f.write(code)
print('Icon.tsx updated')
