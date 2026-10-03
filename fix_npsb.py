import re

with open('web/src/pages/flows/Npsb.tsx', 'r', encoding='utf-8') as f:
    code = f.read()

old_contacts = """  const contacts = [
    { id: `FAM-${uid}`, name: L('মা (bKash)', 'Mother (bKash)'), sub: L('bKash wallet (demo)', 'bKash wallet (demo)'), destination: 'other_mfs_wallet' },
    { id: 'P-BRO', name: L('ভাই (Nagad)', 'Brother (Nagad)'), sub: L('Nagad wallet (demo)', 'Nagad wallet (demo)'), destination: 'other_mfs_wallet' },
    { id: 'P-FRND', name: L('বন্ধু (Rocket)', 'Friend (Rocket)'), sub: L('Rocket wallet (demo)', 'Rocket wallet (demo)'), destination: 'other_mfs_wallet' },
    { id: 'BANK-OWN', name: L('নিজের ব্যাংক অ্যাকাউন্ট', 'My bank account'), sub: L('ব্যাংক (demo)', 'Bank (demo)'), destination: 'bank_account' },
  ]"""

new_contacts = """  const contacts = [
    { id: 'NPSB-BKASH', name: L('বিকাশ-এ ট্রান্সফার', 'Transfer to bKash'), sub: L('bKash (demo)', 'bKash (demo)'), destination: 'other_mfs_wallet' },
    { id: 'NPSB-NAGAD', name: L('নগদ-এ ট্রান্সফার', 'Transfer to Nagad'), sub: L('Nagad (demo)', 'Nagad (demo)'), destination: 'other_mfs_wallet' },
    { id: 'NPSB-ROCKET', name: L('রকেট-এ ট্রান্সফার', 'Transfer to Rocket'), sub: L('Rocket (demo)', 'Rocket (demo)'), destination: 'other_mfs_wallet' },
    { id: 'NPSB-BANK', name: L('ব্যাংক অ্যাকাউন্টে ট্রান্সফার', 'Transfer to Bank Account'), sub: L('Bank (demo)', 'Bank (demo)'), destination: 'bank_account' },
  ]"""

code = code.replace(old_contacts, new_contacts)

# Wait, there is a risk that `মা` etc. encoding failed to match in replace.
# Let's use regex matching from `const contacts = \[` to `  \]`
regex = re.compile(r"const contacts = \[.*?\]", re.DOTALL)
code = regex.sub(new_contacts.strip(), code)

with open('web/src/pages/flows/Npsb.tsx', 'w', encoding='utf-8') as f:
    f.write(code)

print("NPSB contacts updated to generic banking/MFS options!")
