import re

with open('web/src/components/AppShell.tsx', 'r', encoding='utf-8') as f:
    code = f.read()

# 1. Modify BalanceButton
old_balance = """className="min-w-[104px] rounded-full bg-gradient-to-b from-upay-yellow to-amber-400 px-3 py-1 text-center text-slate-800 shadow-[0_4px_10px_rgba(255,213,0,0.3)]">"""
new_balance = """className="min-w-[104px] rounded-full bg-[#0b4ea2] px-3 py-1 text-center text-white shadow-sm transition-transform active:scale-95">"""
code = code.replace(old_balance, new_balance)

# 2. Modify MessageStrip tone
old_msg = "const tone = m.priority === 1 ? 'bg-bad text-white' : 'bg-upay-yellow/90 backdrop-blur-md text-slate-800'"
new_msg = "const tone = m.priority === 1 ? 'bg-bad text-white' : 'bg-[#ffd500] text-slate-800'"
code = code.replace(old_msg, new_msg)

old_msg_class = "className={`mt-4 flex w-full items-center gap-2 rounded-xl px-3 py-2.5 text-left text-[13px] font-semibold transition-transform active:scale-95 ${tone}`}"
new_msg_class = "className={`flex w-full items-center gap-2 rounded-xl px-3 py-2.5 text-left text-[13px] font-semibold transition-transform active:scale-95 ${tone}`}"
code = code.replace(old_msg_class, new_msg_class)

# 3. Modify Header component
old_header = """  function Header({ shell }: { shell: Shell | null }) {
    const { L } = useLang()
    return (
      <header className="bg-gradient-to-br from-[#083b7a] via-[#0b4ea2] to-[#083b7a] shadow-[inset_0_1px_1px_rgba(255,255,255,0.2)] px-4 pb-3 pt-3">
        <div className="flex items-center gap-3">
          <div className="flex size-11 items-center justify-center rounded-full bg-white text-base font-bold text-upay-blue ring-2 ring-white/70">
            {shell?.avatar_initials ?? '👤'}
          </div>
          <div className="min-w-0 flex-1">
            <p className="truncate text-[15px] font-bold text-white">{shell?.name ?? ''}</p>
            <p className="font-[Inter] text-xs text-blue-50">{shell?.phone_masked ?? ''}</p>
          </div>
          {shell && <BalanceButton shell={shell} />}
          <Link to="/app/notifications" className="relative p-1 text-white" aria-label={L('নোটিফিকেশন', 'Notifications')}>
            <Icon name="bell" size={22} />
            {shell && shell.unread > 0 && (
              <span className="absolute -right-0.5 -top-0.5 flex size-4 items-center justify-center rounded-full bg-bad text-[10px] font-bold text-white">
                {shell.unread}
              </span>
            )}
          </Link>
          <Link to="/app/more" className="p-1 text-white" aria-label={L('আরও', 'More')}>
            <Icon name="menu" size={22} />
          </Link>
        </div>
        {shell && <MessageStrip shell={shell} />}
      </header>
    )
  }"""

new_header = """  function Header({ shell }: { shell: Shell | null }) {
    const { L } = useLang()
    return (
      <header className="flex flex-col shadow-sm relative z-10">
        <div className="relative px-4 pb-4 pt-4 overflow-hidden bg-[#ffd500]">
          <div className="absolute inset-0 pointer-events-none opacity-[0.07]" style={{
            backgroundImage: `url("data:image/svg+xml,%3Csvg width='60' height='60' viewBox='0 0 60 60' xmlns='http://www.w3.org/2000/svg'%3E%3Ccircle cx='30' cy='30' r='24' fill='none' stroke='%23000000' stroke-width='2'/%3E%3C/svg%3E")`,
            backgroundSize: '40px 40px'
          }}></div>
          <div className="relative flex items-center gap-3">
            <div className="flex size-11 items-center justify-center rounded-full bg-white text-base font-bold text-upay-blue ring-2 ring-white/70 shadow-sm">
              {shell?.avatar_initials ?? '👤'}
            </div>
            <div className="min-w-0 flex-1">
              <p className="truncate text-[15px] font-bold text-slate-900">{shell?.name ?? ''}</p>
              <p className="font-[Inter] text-xs text-slate-700">{shell?.phone_masked ?? ''}</p>
            </div>
            {shell && <BalanceButton shell={shell} />}
            <Link to="/app/notifications" className="relative p-1 text-slate-900" aria-label={L('নোটিফিকেশন', 'Notifications')}>
              <Icon name="bell" size={22} />
              {shell && shell.unread > 0 && (
                <span className="absolute -right-0.5 -top-0.5 flex size-4 items-center justify-center rounded-full bg-bad text-[10px] font-bold text-white shadow-sm">
                  {shell.unread}
                </span>
              )}
            </Link>
            <Link to="/app/more" className="p-1 text-slate-900" aria-label={L('আরও', 'More')}>
              <Icon name="menu" size={22} />
            </Link>
          </div>
        </div>
        
        {/* Bottom Blue Strip */}
        <div className="bg-[#0b4ea2] px-4 pb-3 pt-3">
          {shell && <MessageStrip shell={shell} />}
        </div>
      </header>
    )
  }"""

# Using regex to replace the header block to avoid string matching issues with exact whitespaces
code = re.sub(r'function Header\(\{ shell \}: \{ shell: Shell \| null \}\) \{[\s\S]*?</header>\n  \}', new_header, code)

with open('web/src/components/AppShell.tsx', 'w', encoding='utf-8') as f:
    f.write(code)

print("Header UI updated!")
