import os
import re

def fix_bad_replaces():
    target_dir = 'web/src'
    
    for root, dirs, files in os.walk(target_dir):
        for file in files:
            if not file.endswith(('.tsx', '.ts')):
                continue
                
            path = os.path.join(root, file)
            with open(path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Revert everything blindly first!
            content = content.replace('Upay Prototype', 'হিসাব')
            content = content.replace('upay prototype', 'hishab')
            # Fix the english versions (mostly in L(bn, en))
            content = content.replace("L('হিসাব', 'হিসাব')", "L('হিসাব', 'Hishab')")
            content = content.replace("L('হিসাব', 'hishab')", "L('হিসাব', 'Hishab')")
            
            with open(path, 'w', encoding='utf-8') as f:
                f.write(content)

fix_bad_replaces()
print("Reverted all.")
