import re

path = 'web/src/pages/hub/Ask.tsx'
with open(path, 'r', encoding='utf-8') as f:
    code = f.read()

# 1. Update Intro Box
old_intro_exact = """        {msgs.length === 0 && (
          <div className="rounded-3xl bg-white p-5 shadow-sm border border-slate-100">
            <p className="flex items-center gap-2 font-semibold"><AiBadge />{L(`${shell?.name.split(' ')[0] ?? ''}, টাকা নিয়ে যা খুশি জিজ্ঞেস করুন`, 'Ask anything about your money')}</p>
            <p className="mt-1 text-sm text-muted">{L('বাংলায় লিখে বা বলে জিজ্ঞেস করতে পারেন। উত্তর আপনার নিজের লেনদেনের হিসাব থেকে।', 'Type or speak in Bangla. Answers come from your own transactions.')}</p>
          </div>
        )}"""

new_intro_exact = """        {msgs.length === 0 && (
          <div className="rounded-2xl bg-white p-3.5 shadow-sm border border-slate-100/60 flex flex-col gap-1 mx-1 mt-1">
            <p className="flex items-center gap-1.5 text-[15px] font-semibold text-slate-800"><AiBadge />{L(`${shell?.name.split(' ')[0] ?? ''}, টাকা নিয়ে যা খুশি জিজ্ঞেস করুন`, 'Ask anything about your money')}</p>
            <p className="text-[12.5px] text-slate-500 leading-snug">{L('বাংলায় লিখে বা বলে জিজ্ঞেস করতে পারেন। উত্তর আপনার নিজের লেনদেনের হিসাব থেকে।', 'Type or speak in Bangla. Answers come from your own transactions.')}</p>
          </div>
        )}"""

code = code.replace(old_intro_exact, new_intro_exact)

# 2. Update background color
code = code.replace('bg-slate-50/70', 'bg-gradient-to-br from-blue-50/50 via-slate-50 to-indigo-50/30')

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

print("Updates applied safely.")
