import re

with open('web/src/pages/flows/Npsb.tsx', 'r', encoding='utf-8') as f:
    code = f.read()

new_contacts = '''const contacts = [
    { id: FAM-, name: L('মা (bKash)', 'Mother (bKash)'), sub: L('bKash wallet (demo)', 'bKash wallet (demo)'), destination: 'other_mfs_wallet' },
    { id: 'P-BRO', name: L('ভাই (Nagad)', 'Brother (Nagad)'), sub: L('Nagad wallet (demo)', 'Nagad wallet (demo)'), destination: 'other_mfs_wallet' },
    { id: 'P-FRND', name: L('বন্ধু (Rocket)', 'Friend (Rocket)'), sub: L('Rocket wallet (demo)', 'Rocket wallet (demo)'), destination: 'other_mfs_wallet' },
    { id: 'BANK-OWN', name: L('নিজের ব্যাংক অ্যাকাউন্ট', 'My bank account'), sub: L('ব্যাংক (demo)', 'Bank (demo)'), destination: 'bank_account' },
  ]'''

code = re.sub(r'const contacts = \[.*?\]', new_contacts, code, flags=re.DOTALL)

with open('web/src/pages/flows/Npsb.tsx', 'w', encoding='utf-8') as f:
    f.write(code)
print('Npsb updated')
