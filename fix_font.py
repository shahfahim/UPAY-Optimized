# -*- coding: utf-8 -*-
with open('web/src/index.css', 'r', encoding='utf-8') as f:
    css = f.read()

# Add font import if not present
if 'Noto+Sans+Bengali' not in css:
    css = css.replace('@import "tailwindcss";', "@import \"tailwindcss\";\n@import url('https://fonts.googleapis.com/css2?family=Noto+Sans+Bengali:wght@400;500;600;700;800&family=Inter:wght@400;500;600;700&display=swap');")

# Change font variables
css = css.replace('"Hind Siliguri", "Inter", system-ui, sans-serif', '"Noto Sans Bengali", "Inter", system-ui, sans-serif')
css = css.replace('"Inter", "Hind Siliguri", system-ui, sans-serif', '"Inter", "Noto Sans Bengali", system-ui, sans-serif')

with open('web/src/index.css', 'w', encoding='utf-8') as f:
    f.write(css)
print('Font updated to Noto Sans Bengali')
