import re

with open('web/src/pages/Account.tsx', 'r', encoding='utf-8') as f:
    code = f.read()

# 1. Update wallet colors
old_wallets = """  const wallets = data && [
    { bn: 'প্রাইমারি', en: 'Primary', v: data.balance, c: 'bg-gradient-to-br from-blue-50/80 to-blue-100/80', ic: 'text-blue-600', i: 'wallet' },
    { bn: 'সঞ্চয় পকেট', en: 'Savings pockets', v: data.total, c: 'bg-gradient-to-br from-emerald-50/80 to-emerald-100/80', ic: 'text-emerald-600', i: 'pig', to: '/app/savings' },
    { bn: 'ডিপিএস (মাসিক)', en: 'DPS (monthly)', v: data.dps?.monthly ?? 0, c: 'bg-gradient-to-br from-violet-50/80 to-violet-100/80', ic: 'text-violet-600', i: 'calendar', to: '/app/savings/dps' },
    { bn: 'পয়সা-সঞ্চয়', en: 'Paisa saving', v: data.paisa.total, c: 'bg-gradient-to-br from-amber-50/80 to-amber-100/80', ic: 'text-amber-600', i: 'chart', to: '/app/savings', paisa: true },
  ]"""

new_wallets = """  const wallets = data && [
    { bn: 'প্রাইমারি', en: 'Primary', v: data.balance, c: 'bg-gradient-to-br from-blue-100 to-blue-200', ic: 'text-blue-700', i: 'wallet' },
    { bn: 'সঞ্চয় পকেট', en: 'Savings pockets', v: data.total, c: 'bg-gradient-to-br from-emerald-100 to-emerald-200', ic: 'text-emerald-700', i: 'pig', to: '/app/savings' },
    { bn: 'ডিপিএস (মাসিক)', en: 'DPS (monthly)', v: data.dps?.monthly ?? 0, c: 'bg-gradient-to-br from-violet-100 to-violet-200', ic: 'text-violet-700', i: 'calendar', to: '/app/savings/dps' },
    { bn: 'পয়সা-সঞ্চয়', en: 'Paisa saving', v: data.paisa.total, c: 'bg-gradient-to-br from-amber-100 to-amber-200', ic: 'text-amber-700', i: 'chart', to: '/app/savings', paisa: true },
  ]"""

code = code.replace(old_wallets, new_wallets)

# 2. Remove the profile card
profile_pattern = re.compile(r'\{\/\* Profile Card \*\/\}.*?<\/div>\s*<\/div>\s*<\/div>', re.DOTALL)
code = profile_pattern.sub('', code)

with open('web/src/pages/Account.tsx', 'w', encoding='utf-8') as f:
    f.write(code)

print("Account.tsx updated: Deeper card colors + removed duplicate profile block.")
