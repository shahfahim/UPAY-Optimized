import os
import re

def global_replace():
    target_dir = 'web/src'
    replacements = {
        'হিসাব': 'Upay Prototype',
        'Hishab': 'Upay Prototype',
        'hishab': 'upay prototype'
    }
    
    # Files to specifically EXCLUDE from global replace so we don't break code variables/URLs
    exclude_files = ['client.ts', 'session.ts', 'api/'] 
    
    for root, dirs, files in os.walk(target_dir):
        for file in files:
            if not file.endswith(('.tsx', '.ts', '.html')):
                continue
                
            path = os.path.join(root, file)
            # Skip some core config files to prevent breakage
            if any(ex in path.replace('\\', '/') for ex in exclude_files):
                continue
                
            with open(path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            original_content = content
            
            # We want to be careful not to replace 'hishab' inside URLs or variable names.
            # Only replacing in user-facing text or strings.
            # Actually, doing it blindly might break `<Route path="hishab"` or `icon: 'hishab'`.
            # Let's target strictly visible strings.
            
            # 1. Replace inside L('...', '...')
            # Using regex to find L(...) calls and replace inside them
            def l_repl(match):
                inner = match.group(0)
                inner = inner.replace('হিসাব', 'Upay Prototype')
                inner = inner.replace('Hishab', 'Upay Prototype')
                return inner
                
            content = re.sub(r'L\([^\)]+\)', l_repl, content)
            
            # 2. Replace hardcoded text in JSX >...<
            def jsx_repl(match):
                inner = match.group(0)
                inner = inner.replace('হিসাব', 'Upay Prototype')
                inner = inner.replace('Hishab', 'Upay Prototype')
                return inner
                
            content = re.sub(r'>[^<]+<', jsx_repl, content)
            
            if original_content != content:
                with open(path, 'w', encoding='utf-8') as f:
                    f.write(content)
                print(f"Updated branding in {path}")

global_replace()
