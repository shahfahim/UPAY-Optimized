import re

with open('web/src/components/AppShell.tsx', 'r', encoding='utf-8') as f:
    code = f.read()

old_btn = """function BalanceButton({ shell }: { shell: Shell }) {
    const { L, taka } = useLang()
    const [open, setOpen] = useState(false)
    useEffect(() => {
      if (!open) return
      const t = window.setTimeout(() => setOpen(false), 5000)
      return () => window.clearTimeout(t)
    }, [open])
    return (
      <button onClick={() => setOpen((o) => !o)} aria-live="polite"
        className="min-w-[104px] rounded-full bg-[#ffd500] px-3 py-1.5 text-center text-[#083b7a] font-extrabold shadow-[0_4px_12px_rgba(255,213,0,0.4)] ring-[2px] ring-[#ffd500]/50 transition-transform active:scale-95">
        {open ? (
          <span className="text-[15px] tracking-tight">{taka(shell.balance)}</span>
        ) : (
          <span className="text-sm">{L('ব্যালেন্স', 'Balance')}</span>
        )}
      </button>
    )
  }"""

new_btn = """function BalanceButton({ shell }: { shell: Shell }) {
    const { L, taka } = useLang()
    const [open, setOpen] = useState(false)
    useEffect(() => {
      if (!open) return
      const t = window.setTimeout(() => setOpen(false), 5000)
      return () => window.clearTimeout(t)
    }, [open])
    return (
      <button onClick={() => setOpen((o) => !o)} aria-live="polite"
        className="relative flex h-[34px] min-w-[104px] items-center justify-center overflow-hidden rounded-full bg-[#ffd500] px-3 text-[#083b7a] font-extrabold shadow-[0_4px_12px_rgba(255,213,0,0.4)] ring-[2px] ring-[#ffd500]/50 transition-transform active:scale-95">
        <div className={`absolute flex w-full items-center justify-center transition-all duration-500 ease-[cubic-bezier(0.34,1.56,0.64,1)] ${open ? 'translate-y-0 opacity-100 scale-100' : 'translate-y-6 opacity-0 scale-75'}`}>
          <span className="text-[15.5px] tracking-tight">{taka(shell.balance)}</span>
        </div>
        <div className={`absolute flex w-full items-center justify-center transition-all duration-500 ease-[cubic-bezier(0.34,1.56,0.64,1)] ${open ? '-translate-y-6 opacity-0 scale-75' : 'translate-y-0 opacity-100 scale-100'}`}>
          <span className="text-[13.5px]">{L('ব্যালেন্স', 'Balance')}</span>
        </div>
      </button>
    )
  }"""

if old_btn in code:
    code = code.replace(old_btn, new_btn)
else:
    # Use regex if exact match fails
    pattern = re.compile(r'function BalanceButton.*?<\/button>\n\s*\}', re.DOTALL)
    code = pattern.sub(new_btn, code)

with open('web/src/components/AppShell.tsx', 'w', encoding='utf-8') as f:
    f.write(code)

print("BalanceButton animation added successfully!")
