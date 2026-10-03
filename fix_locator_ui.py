import re

with open('web/src/pages/hub/AgentLocator.tsx', 'r', encoding='utf-8') as f:
    code = f.read()

# 1. Increase bottom padding to prevent overlap with bottom nav
code = code.replace('<div className="min-h-screen bg-slate-50 pb-20 animate-fade-in">', '<div className="min-h-screen bg-slate-50 pb-36 animate-fade-in">')

# 2. Replace ErrorNote with a subtle blue info note
old_error_render = """        {geoError && (
          <ErrorNote message={geoError} />
        )}"""

new_error_render = """        {geoError && (
          <div className="bg-blue-50/50 text-blue-600 border border-blue-100 p-3 rounded-xl text-sm mb-4 text-center">
            {geoError}
          </div>
        )}"""

code = code.replace(old_error_render, new_error_render)

# 3. Update the text to be more polite for the demo
old_text = "Location blocked (HTTP). Showing default (Dhaka)."
new_text = "Demo Mode: Showing default location (Dhaka)."
code = code.replace(old_text, new_text)
code = code.replace('লোকেশন ব্লক করা হয়েছে (HTTP)। ডিফল্ট লোকেশন (ঢাকা) দেখানো হচ্ছে।', 'ডেমো মোড: ডিফল্ট লোকেশন (ঢাকা) দেখানো হচ্ছে।')

with open('web/src/pages/hub/AgentLocator.tsx', 'w', encoding='utf-8') as f:
    f.write(code)

print("Fixed UI issues!")
