import re

with open('web/src/pages/hub/Ask.tsx', 'r', encoding='utf-8') as f:
    code = f.read()

# Add animate-slide-up to user and bot messages
code = code.replace(
    'className="ml-10 rounded-2xl rounded-br-md bg-upay-blue px-3.5 py-2.5 text-white"',
    'className="ml-10 rounded-2xl rounded-br-md bg-upay-blue px-3.5 py-2.5 text-white animate-slide-up"'
)
code = code.replace(
    'className="mr-6 rounded-2xl rounded-bl-md border border-line bg-white px-3.5 py-2.5"',
    'className="mr-6 rounded-2xl rounded-bl-md border border-line bg-white px-3.5 py-2.5 animate-slide-up"'
)

with open('web/src/pages/hub/Ask.tsx', 'w', encoding='utf-8') as f:
    f.write(code)

print("Ask.tsx chat message animations added!")
