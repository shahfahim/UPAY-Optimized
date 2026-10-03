import re

with open('web/src/pages/hub/HubLayout.tsx', 'r', encoding='utf-8') as f:
    code = f.read()

old_tabs = """  const tabs = [
    { to: '/app/hishab/ask', bn: 'জিজ্ঞেস', en: 'Ask' },
    { to: '/app/hishab', end: true, bn: 'ওভারভিউ', en: 'Overview' },
    { to: '/app/hishab/learn', bn: 'শেখো', en: 'Learn' },
    { to: '/app/savings', bn: 'Smart DPS', en: 'Smart DPS' },
  ]"""

new_tabs = """  const tabs = [
    { to: '/app/hishab', end: true, bn: 'জিজ্ঞেস', en: 'Ask' },
    { to: '/app/hishab/overview', bn: 'ওভারভিউ', en: 'Overview' },
    { to: '/app/hishab/learn', bn: 'শেখো', en: 'Learn' },
    { to: '/app/savings', bn: 'Smart DPS', en: 'Smart DPS' },
  ]"""

code = code.replace(old_tabs, new_tabs)

with open('web/src/pages/hub/HubLayout.tsx', 'w', encoding='utf-8') as f:
    f.write(code)

print("HubLayout.tsx tabs updated!")
