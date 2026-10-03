import re

with open('web/src/index.css', 'r', encoding='utf-8') as f:
    code = f.read()

old_css = """  background-color: #e2e8f0;
  background-image: 
    linear-gradient(rgba(11, 78, 162, 0.06) 1px, transparent 1px),
    linear-gradient(90deg, rgba(11, 78, 162, 0.06) 1px, transparent 1px);
  background-size: 24px 24px;"""

new_css = """  background-color: #f4f7fb;
  background-image: 
    repeating-linear-gradient(120deg, rgba(11, 78, 162, 0.04) 0px, rgba(11, 78, 162, 0.04) 1px, transparent 1px, transparent 30px),
    repeating-linear-gradient(60deg, rgba(11, 78, 162, 0.04) 0px, rgba(11, 78, 162, 0.04) 1px, transparent 1px, transparent 30px),
    repeating-linear-gradient(0deg, rgba(11, 78, 162, 0.03) 0px, rgba(11, 78, 162, 0.03) 1px, transparent 1px, transparent 15px);"""

code = code.replace(old_css, new_css)

with open('web/src/index.css', 'w', encoding='utf-8') as f:
    f.write(code)

print("Financial Geometry Applied!")
