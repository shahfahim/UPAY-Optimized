import json

with open('web/src/pages/Home.tsx', 'r', encoding='utf-8') as f:
    lines = f.readlines()

out = []
in_tiles = False
tiles_lines = []

for line in lines:
    if line.startswith('const TILES: Tile[] = ['):
        in_tiles = True
        out.append(line)
        continue
    if in_tiles:
        if line.strip() == ']':
            in_tiles = False
            
            # Now process tiles_lines
            # We want to replace Add Money at index 4 with Smart DPS
            # And append Add Money at the end.
            
            # Find Add money
            add_money_line = ""
            add_idx = -1
            for i, l in enumerate(tiles_lines):
                if "icon: 'add'" in l:
                    add_money_line = l
                    add_idx = i
                    break
            
            if add_idx != -1:
                tiles_lines.pop(add_idx)
                
                # Insert Smart DPS at the same index
                smart_dps = "  { icon: 'shield', bn: 'Smart DPS', en: 'Smart DPS', to: '/app/savings/dps', hishab: true },\n"
                tiles_lines.insert(add_idx, smart_dps)
                
                # Add "Add Money" to the end (which will be index 12)
                tiles_lines.append(add_money_line)
            
            out.extend(tiles_lines)
            out.append(line)
        else:
            tiles_lines.append(line)
    else:
        out.append(line)

with open('web/src/pages/Home.tsx', 'w', encoding='utf-8') as f:
    f.writelines(out)

print("TILES updated!")
