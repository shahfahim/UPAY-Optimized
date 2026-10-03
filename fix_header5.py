import re

with open('web/src/components/AppShell.tsx', 'r', encoding='utf-8') as f:
    code = f.read()

# Update BalanceButton
old_btn = """<button onClick={() => setOpen((o) => !o)} aria-live="polite"
        className="min-w-[104px] rounded-full bg-[#0b4ea2] px-3 py-1 text-center text-white shadow-sm transition-transform active:scale-95">"""
new_btn = """<button onClick={() => setOpen((o) => !o)} aria-live="polite"
        className="min-w-[104px] rounded-full bg-[#0b4ea2] px-3 py-1 text-center text-white shadow-[0_4px_12px_rgba(11,78,162,0.4)] ring-2 ring-white/30 backdrop-blur-sm transition-transform active:scale-95">"""
code = code.replace(old_btn, new_btn)

# Replace Header
start_marker = "function Header({ shell }: { shell: Shell | null }) {"
end_marker = "  function BottomNav"

start_idx = code.find(start_marker)
end_idx = code.find(end_marker)

if start_idx != -1 and end_idx != -1:
    new_header = """function Header({ shell }: { shell: Shell | null }) {
    const { L } = useLang()
    return (
      <header className="relative overflow-hidden bg-[#ffd500] px-4 pb-5 pt-4 shadow-[0_4px_20px_-5px_rgba(0,0,0,0.2)] z-10">
        
        {/* Abstract Geometric Background - Layer 1 (Wide Deep Blue Slash) */}
        <div className="absolute -top-[120px] -right-[60px] h-[400px] w-[280px] -rotate-[35deg] transform bg-gradient-to-br from-[#083b7a] to-[#0b4ea2] shadow-[-10px_0_30px_rgba(0,0,0,0.3)] opacity-100 z-0 rounded-bl-[40px]"></div>
        
        {/* Abstract Geometric Background - Layer 2 (Lighter Blue Accent Slash) */}
        <div className="absolute -top-[150px] right-[180px] h-[350px] w-[80px] -rotate-[35deg] transform bg-[#1a64c4] shadow-[-5px_0_20px_rgba(0,0,0,0.2)] opacity-95 z-0 rounded-bl-[20px]"></div>

        {/* Abstract Geometric Background - Layer 3 (Small Yellow overlapping slash on blue) */}
        <div className="absolute -top-[60px] -right-[20px] h-[200px] w-[40px] -rotate-[35deg] transform bg-[#ffd500] shadow-[0_0_15px_rgba(0,0,0,0.2)] opacity-90 z-0 rounded-full"></div>

        {/* Subtle Halftone/Dot Pattern Overlay */}
        <div className="absolute inset-0 pointer-events-none mix-blend-overlay opacity-10 z-0" style={{
          backgroundImage: 'radial-gradient(#000 1.5px, transparent 1.5px)',
          backgroundSize: '16px 16px'
        }}></div>
        
        <div className="relative flex items-center justify-between gap-3 z-10">
          
          {/* Left Side: Avatar & Name (Over Yellow BG) */}
          <div className="flex items-center gap-3">
            <div className="flex size-11 shrink-0 items-center justify-center rounded-full bg-white text-[#0b4ea2] ring-[3px] ring-white shadow-md overflow-hidden">
              {shell && (shell as any).profile_pic ? (
                <img src={(shell as any).profile_pic} alt="Profile" className="w-full h-full object-cover" />
              ) : (
                <img src="/upay-logo.png" alt="Upay Logo" className="w-full h-full object-contain p-1.5" />
              )}
            </div>
            <div className="min-w-0 flex-1">
              <p className="truncate text-[16px] font-extrabold text-slate-900 tracking-tight drop-shadow-[0_1px_1px_rgba(255,255,255,0.5)]">{shell?.name ?? ''}</p>
              <p className="font-[Inter] text-[13px] font-bold text-slate-800 drop-shadow-[0_1px_1px_rgba(255,255,255,0.5)]">{shell?.phone_masked ?? ''}</p>
            </div>
          </div>

          {/* Right Side: Balance & Icons (Over Blue Slashes) */}
          <div className="flex items-center gap-2">
            {shell && <BalanceButton shell={shell} />}
            
            <div className="flex items-center gap-1.5 pl-1">
              <Link to="/app/notifications" className="relative flex size-9 items-center justify-center rounded-full bg-white/10 text-white backdrop-blur-md shadow-sm border border-white/20 transition-transform active:scale-95" aria-label={L('নোটিফিকেশন', 'Notifications')}>
                <Icon name="bell" size={20} strokeWidth={2.5} />
                {shell && shell.unread > 0 && (
                  <span className="absolute -right-1 -top-1 flex size-4 items-center justify-center rounded-full bg-rose-500 text-[10px] font-bold text-white shadow-sm ring-2 ring-[#0b4ea2]">
                    {shell.unread}
                  </span>
                )}
              </Link>
              <Link to="/app/more" className="flex size-9 items-center justify-center rounded-full bg-white/10 text-white backdrop-blur-md shadow-sm border border-white/20 transition-transform active:scale-95" aria-label={L('আরও', 'More')}>
                <Icon name="menu" size={20} strokeWidth={2.5} />
              </Link>
            </div>
          </div>
          
        </div>
        
        <div className="relative mt-4 z-10">
          {shell && <MessageStrip shell={shell} />}
        </div>
      </header>
    )
  }

  """
    code = code[:start_idx] + new_header + code[end_idx:]
    with open('web/src/components/AppShell.tsx', 'w', encoding='utf-8') as f:
        f.write(code)
    print("AppShell geometric header successfully upgraded!")
else:
    print(f"Error: start={start_idx}, end={end_idx}")
