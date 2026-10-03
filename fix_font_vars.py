import re

with open('web/src/index.css', 'r', encoding='utf-8') as f:
    code = f.read()

# Replace --font-sans definition to use system font defaults
code = re.sub(
    r'--font-sans: "Noto Sans Bengali", "Inter", system-ui, sans-serif;',
    r'--font-sans: system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Helvetica Neue", Arial, sans-serif, "Apple Color Emoji", "Segoe UI Emoji", "Segoe UI Symbol";',
    code
)

with open('web/src/index.css', 'w', encoding='utf-8') as f:
    f.write(code)

print("Font variables fully updated!")
