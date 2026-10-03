# -*- coding: utf-8 -*-
with open('web/src/pages/hub/Overview.tsx', 'r', encoding='utf-8') as f:
    code = f.read()

# Add animation to the BarChart card
code = code.replace(
    'className="px-4 -mt-6"',
    'className="px-4 -mt-6 animate-slide-up" style={{ animationDelay: "100ms" }}'
)

# Add animation to the buttons grid
code = code.replace(
    'className="px-4 mt-4 grid grid-cols-3 gap-3"',
    'className="px-4 mt-4 grid grid-cols-3 gap-3 animate-slide-up" style={{ animationDelay: "200ms" }}'
)

# Add animation to the lesson card
code = code.replace(
    'className="px-4 mt-4"',
    'className="px-4 mt-4 animate-slide-up" style={{ animationDelay: "300ms" }}'
)

with open('web/src/pages/hub/Overview.tsx', 'w', encoding='utf-8') as f:
    f.write(code)
print('Overview animations added')
