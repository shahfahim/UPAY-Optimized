import re

path_shell = 'web/src/components/AppShell.tsx'
with open(path_shell, 'r', encoding='utf-8') as f:
    code = f.read()

# We need to find the entire BalanceButton component and replace it.
# It starts with "function BalanceButton({ shell }: { shell: Shell }) {"
# and ends right before "function Header({ shell }: { shell: Shell | null }) {"

pattern = r"function BalanceButton\(\{ shell \}: \{ shell: Shell \}\) \{.*?(?=function Header\(\{ shell \}: \{ shell: Shell \| null \}\) \{)"

new_btn = """function BalanceButton({ shell }: { shell: Shell }) {
  const { L, taka } = useLang()
  const [step, setStep] = useState<'idle' | 'spin-in' | 'hole' | 'spin-out' | 'open'>('idle')

  useEffect(() => {
    if (step === 'spin-in') {
      const t = setTimeout(() => setStep('hole'), 300)
      return () => clearTimeout(t)
    }
    if (step === 'hole') {
      const t = setTimeout(() => setStep('spin-out'), 200)
      return () => clearTimeout(t)
    }
    if (step === 'spin-out') {
      const t = setTimeout(() => setStep('open'), 300)
      return () => clearTimeout(t)
    }
    if (step === 'open') {
      const t = setTimeout(() => setStep('idle'), 4000)
      return () => clearTimeout(t)
    }
  }, [step])

  return (
    <button
      onClick={() => step === 'idle' && setStep('spin-in')}
      aria-live="polite"
      className={`relative flex h-9 items-center justify-center rounded-full bg-[#ffd500] text-[#083b7a] font-extrabold shadow-[0_4px_12px_rgba(255,213,0,0.4)] ring-[2px] ring-[#ffd500]/50 transition-all duration-300 ease-in-out ${
        (step === 'spin-in' || step === 'hole' || step === 'spin-out') ? 'w-9 px-0' : 'min-w-[104px] px-3'
      } ${step === 'spin-in' ? 'rotate-180 scale-50 opacity-50' : ''} ${
        step === 'hole' ? 'scale-0 opacity-0' : ''
      } ${step === 'spin-out' ? 'rotate-[360deg] scale-100 opacity-100' : ''}`}
    >
      <span
        className={`whitespace-nowrap transition-opacity duration-200 ${
          (step === 'spin-in' || step === 'hole' || step === 'spin-out') ? 'opacity-0' : 'opacity-100'
        }`}
      >
        {step === 'open' ? (
          <span className="text-[15px] tracking-tight">{taka(shell.balance)}</span>
        ) : (
          <span className="text-sm">{L('ব্যালেন্স', 'Balance')}</span>
        )}
      </span>
    </button>
  )
}

"""

new_code = re.sub(pattern, new_btn, code, flags=re.DOTALL)

with open(path_shell, 'w', encoding='utf-8') as f:
    f.write(new_code)

print("Minimal inline BalanceButton applied.")
