with open('web/src/components/AppShell.tsx', 'r', encoding='utf-8') as f:
    code = f.read()

start_marker = "function Header({ shell }: { shell: Shell | null }) {"
end_marker = "function BottomNav"

start_idx = code.find(start_marker)
end_idx = code.find(end_marker)

if start_idx != -1 and end_idx != -1:
    new_header = """function Header({ shell }: { shell: Shell | null }) {
    const { L } = useLang()
    return (
      <header className="relative overflow-hidden bg-[#ffd500] px-4 pb-4 pt-4 shadow-sm z-10">
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
  }

  """
    code = code[:start_idx] + new_header + code[end_idx:]
    with open('web/src/components/AppShell.tsx', 'w', encoding='utf-8') as f:
        f.write(code)
    print("Force replaced using exact index slicing!")
else:
    print(f"Error: start={start_idx}, end={end_idx}")
