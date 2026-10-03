import re

with open('web/src/index.css', 'r', encoding='utf-8') as f:
    code = f.read()

code = code.replace('background-color: #f1f4f9;', 'background-color: #eef1f5;')

with open('web/src/index.css', 'w', encoding='utf-8') as f:
    f.write(code)

print("Made it slightly more gray!")
