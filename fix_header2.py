import re

with open('web/src/components/AppShell.tsx', 'r', encoding='utf-8') as f:
    code = f.read()

# Replace Header
header_pattern = re.compile(r'function Header\(\{ shell \}: \{ shell: Shell \| null \}\) \{.*?</header>\n  \}', re.DOTALL)
new_header = """function Header({ shell }: { shell: Shell | null }) {
    const { L } = useLang()
    return (
      <header className="relative overflow-hidden bg-[#ffd500] px-4 pb-4 pt-4 shadow-sm z-10">
        {/* Geometric Background Layer (Upay Pattern) */}
        <div className="absolute inset-0 pointer-events-none opacity-[0.06]" style={{
          backgroundImage: `repeating-linear-gradient(45deg, #000 0, #000 1px, transparent 1px, transparent 24px), repeating-linear-gradient(-45deg, #000 0, #000 1px, transparent 1px, transparent 24px), radial-gradient(circle at 20% 50%, #000 0%, transparent 15%), radial-gradient(circle at 80% 50%, #000 0%, transparent 15%)`
        }}></div>
        
        <div className="relative flex items-center gap-3">
          <div className="flex size-11 items-center justify-center rounded-full bg-white text-base font-bold text-[#0b4ea2] ring-2 ring-white/70 shadow-sm">
            {shell?.avatar_initials ?? '👤'}
          </div>
          <div className="min-w-0 flex-1">
            <p className="truncate text-[15px] font-bold text-slate-900">{shell?.name ?? ''}</p>
            <p className="font-[Inter] text-xs text-slate-700">{shell?.phone_masked ?? ''}</p>
          </div>
          {shell && <BalanceButton shell={shell} />}
          <Link to="/app/notifications" className="relative p-1 text-slate-900" aria-label={L('নোটিফিকেশন', 'Notifications')}>
            <Icon name="bell" size={24} strokeWidth={2} />
            {shell && shell.unread > 0 && (
              <span className="absolute -right-0.5 -top-0.5 flex size-4 items-center justify-center rounded-full bg-bad text-[10px] font-bold text-white shadow-sm ring-1 ring-white">
                {shell.unread}
              </span>
            )}
          </Link>
          <Link to="/app/more" className="p-1 text-slate-900" aria-label={L('আরও', 'More')}>
            <Icon name="menu" size={26} strokeWidth={2} />
          </Link>
        </div>
        
        <div className="relative mt-4">
          {shell && <MessageStrip shell={shell} />}
        </div>
      </header>
    )
  }"""

code = header_pattern.sub(new_header, code)

# Replace MessageStrip tone
code = code.replace("const tone = m.priority === 1 ? 'bg-bad text-white' : 'bg-[#ffd500] text-slate-800'", 
                    "const tone = m.priority === 1 ? 'bg-bad text-white' : 'bg-[#fff8cc] text-slate-900'")
code = code.replace("const tone = m.priority === 1 ? 'bg-bad text-white' : 'bg-upay-yellow/90 backdrop-blur-md text-slate-800'",
                    "const tone = m.priority === 1 ? 'bg-bad text-white' : 'bg-[#fff8cc] text-slate-900'")

with open('web/src/components/AppShell.tsx', 'w', encoding='utf-8') as f:
    f.write(code)

print("Header replacement via regex complete.")
