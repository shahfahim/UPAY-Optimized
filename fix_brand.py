import os
import re

def replace_in_file(path, replacements):
    with open(path, 'r', encoding='utf-8') as f:
        content = f.read()
    for old, new in replacements:
        content = content.replace(old, new)
    with open(path, 'w', encoding='utf-8') as f:
        f.write(content)

# 1. Update Logo in UI
replace_in_file('web/src/components/ui.tsx', [
    ('>হিসাব</span>', '>Upay Prototype</span>')
])

# 2. Update Splash
replace_in_file('web/src/pages/auth/Splash.tsx', [
    ('>হিসাব</span>', '>Upay Prototype</span>')
])

# 3. Update HubLayout top title
replace_in_file('web/src/pages/hub/HubLayout.tsx', [
    ("L('হিসাব', 'Hishab')", "L('Upay Prototype', 'Upay Prototype')")
])

# 4. Update AppShell Bottom Nav
replace_in_file('web/src/components/AppShell.tsx', [
    ("L('হিসাব', 'Hishab')", "L('Upay Prototype', 'Upay Prototype')")
])

# 5. Update index.html
replace_in_file('web/index.html', [
    ('<title>হিসাব · upay prototype</title>', '<title>Upay Prototype</title>'),
    ('<title>Hishab</title>', '<title>Upay Prototype</title>')
])

print("Text replacement completed for App Branding.")
