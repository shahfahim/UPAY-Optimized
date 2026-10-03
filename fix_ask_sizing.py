import re

path = 'web/src/pages/hub/Ask.tsx'
with open(path, 'r', encoding='utf-8') as f:
    code = f.read()

# 1. Background color
# replace <div className="flex min-h-[60dvh] flex-col px-4 pb-6 bg-gradient-to-br from-blue-50/50 via-slate-50 to-indigo-50/30">
code = re.sub(
    r'<div className="flex min-h-\[60dvh\] flex-col px-4 pb-6 [^"]+">',
    '<div className="flex min-h-[60dvh] flex-col px-4 pb-6 bg-slate-100/80">',
    code
)

# 2. Intro Box
old_intro = r'<div className="rounded-3xl bg-white p-5 shadow-sm border border-slate-100">\s*<p className="flex items-center gap-2 font-semibold"><AiBadge />\{L\(\`\$\{shell\?\.name\.split\(\' \'\)\[0\] \?\? \'\'\},(.*?)\</p>\s*</div>'
new_intro = r"""<div className="rounded-2xl bg-white p-3 shadow-sm border border-slate-100 flex flex-col gap-1 mx-1 mt-1">
            <p className="flex items-center gap-1.5 text-[14px] font-semibold text-slate-800"><AiBadge />{L(`${shell?.name.split(' ')[0] ?? ''},\1</p>
          </div>"""
code = re.sub(old_intro, new_intro, code, flags=re.DOTALL)

# 3. User Bubble
code = code.replace(
    'className="ml-auto max-w-[85%] rounded-3xl rounded-tr-sm bg-upay-blue px-4 py-3 text-white shadow-md shadow-upay-blue/20 animate-slide-up"',
    'className="ml-auto max-w-[85%] rounded-2xl rounded-tr-sm bg-upay-blue px-3.5 py-2 text-[14px] text-white shadow-md shadow-upay-blue/20 animate-slide-up"'
)

# 4. Bot Bubble
code = code.replace(
    'className="mr-auto max-w-[85%] rounded-3xl rounded-tl-sm border border-slate-100 bg-white px-4 py-3 text-slate-800 shadow-sm animate-slide-up"',
    'className="mr-auto max-w-[85%] rounded-2xl rounded-tl-sm border border-slate-100 bg-white px-3.5 py-2.5 text-[14px] text-slate-800 shadow-sm animate-slide-up"'
)

# 5. Busy Bubble
code = code.replace(
    'className="mr-auto max-w-[85%] flex items-center gap-2 rounded-3xl rounded-tl-sm border border-slate-100 bg-white px-4 py-3 text-sm text-muted shadow-sm"',
    'className="mr-auto max-w-[85%] flex items-center gap-2 rounded-2xl rounded-tl-sm border border-slate-100 bg-white px-3.5 py-2.5 text-[13px] text-muted shadow-sm"'
)

# 6. Suggestions
code = code.replace(
    'className="shrink-0 rounded-full border border-upay-blue/30 bg-white px-3 py-1.5 text-sm text-upay-blue disabled:opacity-50"',
    'className="shrink-0 rounded-full border border-upay-blue/30 bg-white px-3 py-1.5 text-[12.5px] text-upay-blue disabled:opacity-50"'
)

# 7. Form Wrapper
code = code.replace(
    'className="sticky bottom-2 z-10 mt-3 flex items-end gap-2 rounded-3xl bg-white/70 backdrop-blur-lg border border-white/50 p-2 shadow-[0_8px_30px_rgb(0,0,0,0.04)]"',
    'className="sticky bottom-2 z-10 mt-3 flex items-end gap-2 rounded-3xl bg-white/70 backdrop-blur-lg border border-white/50 p-1.5 shadow-[0_4px_20px_rgb(0,0,0,0.04)]"'
)

# 8. Textarea wrapper
code = code.replace(
    'className="flex-1 rounded-2xl bg-white/50 px-4 py-2 focus-within:bg-white focus-within:ring-1 focus-within:ring-upay-blue/50 transition-all border border-transparent"',
    'className="flex-1 rounded-2xl bg-white/60 px-3.5 py-1.5 focus-within:bg-white focus-within:ring-1 focus-within:ring-upay-blue/50 transition-all border border-transparent"'
)

# 9. Textarea itself
code = code.replace(
    'className="max-h-28 min-h-9 w-full resize-none bg-transparent py-1.5 outline-none"',
    'className="max-h-28 min-h-9 w-full resize-none bg-transparent py-1 outline-none text-[14px]"'
)

# 10. Voice/Send buttons
code = code.replace(
    'className={`flex size-11 shrink-0 items-center justify-center rounded-full ${listening ? \'animate-pulse bg-bad text-white\' : \'bg-upay-yellow text-upay-blue\'}`}',
    'className={`flex size-10 shrink-0 items-center justify-center rounded-full ${listening ? \'animate-pulse bg-bad text-white\' : \'bg-upay-yellow text-upay-blue\'}`}'
)
code = code.replace(
    'className="flex size-11 shrink-0 items-center justify-center rounded-full bg-upay-blue text-white disabled:opacity-50"',
    'className="flex size-10 shrink-0 items-center justify-center rounded-full bg-upay-blue text-white disabled:opacity-50"'
)
code = code.replace(
    'className="flex size-11 shrink-0 cursor-help items-center justify-center rounded-full bg-transparent text-muted"',
    'className="flex size-10 shrink-0 cursor-help items-center justify-center rounded-full bg-transparent text-muted"'
)
code = code.replace('<Icon name="mic" size={20} />', '<Icon name="mic" size={18} />')
code = code.replace('<Icon name="send" size={18} />', '<Icon name="send" size={16} />')

with open(path, 'w', encoding='utf-8') as f:
    f.write(code)

print("Applied massive shrinkage and distinct background color.")
