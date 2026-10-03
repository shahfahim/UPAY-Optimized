import re

path = 'web/src/pages/hub/Ask.tsx'
with open(path, 'r', encoding='utf-8') as f:
    code = f.read()

# 1. Update intro box (make it smaller)
old_intro = r'<div className="rounded-3xl bg-white p-5 shadow-sm border border-slate-100">\s*<p className="flex items-center gap-2 font-semibold"><AiBadge />\{L\(\`\$\{shell\?\.name\.split\(\' \'\)\[0\] \?\? \'\'\},.*?</p>\s*</div>'

new_intro = """<div className="rounded-2xl bg-white p-3.5 shadow-sm border border-slate-100 flex flex-col gap-1 mx-2">
            <p className="flex items-center gap-1.5 text-[15px] font-semibold text-slate-800"><AiBadge />{L(`${shell?.name.split(' ')[0] ?? ''}, টাকা নিয়ে যা খুশি জিজ্ঞেস করুন`, 'Ask anything about your money')}</p>
            <p className="text-[13px] text-slate-500 leading-snug">{L('বাংলায় লিখে বা বলে জিজ্ঞেস করতে পারেন। উত্তর আপনার নিজের লেনদেনের হিসাব থেকে।', 'Type or speak in Bangla. Answers come from your own transactions.')}</p>
          </div>"""

# Ensure exact regex match is not failing due to encoding. Let's use broader regex if needed.
# Since L(...) contains bangla, doing a generic replace is safer.
intro_pattern = r'\{msgs\.length === 0 && \(\s*<div className="rounded-3xl bg-white p-5.*?\)\}'
intro_replacement = """{msgs.length === 0 && (
          <div className="rounded-2xl bg-white p-3.5 shadow-[0_2px_10px_-3px_rgba(0,0,0,0.05)] border border-slate-100 flex flex-col gap-1 mx-1 mt-2">
            <p className="flex items-center gap-1.5 text-[15px] font-semibold text-slate-800"><AiBadge />{L(`${shell?.name.split(' ')[0] ?? ''}, টাকা নিয়ে যা খুশি জিজ্ঞেস করুন`, 'Ask anything about your money')}</p>
            <p className="text-[12px] text-slate-500 leading-snug">{L('বাংলায় লিখে বা বলে জিজ্ঞেস করতে পারেন। উত্তর আপনার নিজের লেনদেনের হিসাব থেকে।', 'Type or speak in Bangla. Answers come from your own transactions.')}</p>
          </div>
        )}"""

code = re.sub(intro_pattern, intro_replacement, code, flags=re.DOTALL)

# 2. Update background color
code = code.replace('bg-slate-50/70', 'bg-gradient-to-b from-blue-50/40 via-slate-50/30 to-blue-50/50')

# 3. Update scroll logic
old_scroll = "useEffect(() => { end.current?.scrollIntoView({ behavior: 'smooth', block: 'end' }) }, [msgs, busy])"
new_scroll = """useEffect(() => { 
    if (end.current) {
      setTimeout(() => {
        end.current?.scrollIntoView({ behavior: 'smooth', block: 'end' })
      }, 100)
    }
  }, [msgs, busy])"""
code = code.replace(old_scroll, new_scroll)

with open(path, 'w', encoding='utf-8') as f:
    f.write(code)

print("Updated Ask.tsx with styling and scroll fixes.")
