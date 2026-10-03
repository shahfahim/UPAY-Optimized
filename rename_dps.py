import re

files_to_update = {
    'web/src/pages/hub/HubLayout.tsx': [
        (r"bn: 'Smart DPS', en: 'Smart DPS'", r"bn: 'সঞ্চয়', en: 'Savings'")
    ],
    'web/src/pages/Home.tsx': [
        (r"bn: 'Smart DPS', en: 'Smart DPS'", r"bn: 'সঞ্চয়', en: 'Savings'")
    ],
    'web/src/pages/savings/SavingsHome.tsx': [
        (r"bn: 'Smart DPS', en: 'Smart DPS'", r"bn: 'সঞ্চয়', en: 'Savings'")
    ],
    'web/src/pages/savings/Dps.tsx': [
        (r'bn="Smart DPS" en="Smart DPS"', r'bn="সঞ্চয় (DPS)" en="Savings (DPS)"')
    ]
}

for filepath, replacements in files_to_update.items():
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
        
        for old_str, new_str in replacements:
            content = re.sub(old_str, new_str, content)
            
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(content)
        print(f"Updated {filepath}")
    except Exception as e:
        print(f"Failed {filepath}: {e}")
