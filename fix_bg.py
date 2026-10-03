# -*- coding: utf-8 -*-
import glob
import os

for path in glob.glob('web/src/pages/**/*.tsx', recursive=True):
    with open(path, 'r', encoding='utf-8') as f:
        code = f.read()
    
    modified = code.replace('bg-slate-50', 'bg-transparent').replace('bg-surface', 'bg-transparent')
    
    if modified != code:
        with open(path, 'w', encoding='utf-8') as f:
            f.write(modified)
        print(f'Updated {path}')
