import re

with open('web/src/pages/More.tsx', 'r', encoding='utf-8') as f:
    code = f.read()

new_row = "        {row('bell', 'নোটিফিকেশন সেটিং', 'Notification settings', () => demo(L('নোটিফিকেশন সেটিং', 'Notification settings')))}\n"

code = code.replace(
    "{row('shield', 'পিন পরিবর্তন', 'Change PIN'",
    new_row + "        {row('shield', 'পিন পরিবর্তন', 'Change PIN'"
)

with open('web/src/pages/More.tsx', 'w', encoding='utf-8') as f:
    f.write(code)
print('More.tsx updated')
