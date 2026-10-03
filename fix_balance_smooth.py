import re

path_shell = 'web/src/components/AppShell.tsx'
with open(path_shell, 'r', encoding='utf-8') as f:
    code = f.read()

pattern = r"function BalanceButton\(\{ shell \}: \{ shell: Shell \}\) \{.*?(?=function Header\(\{ shell \}: \{ shell: Shell \| null \}\) \{)"

new_btn = """function BalanceButton({ shell }: { shell: Shell }) {
  const { L, taka } = useLang()
  const [animating, setAnimating] = useState(false)
  const [revealed, setRevealed] = useState(false)

  const handleClick = () => {
    if (animating || revealed) return
    setAnimating(true)
    
    // Exactly at half the animation (400ms), when the coin is completely scaled to 0
    // We swap the text so the user never sees it change abruptly.
    setTimeout(() => setRevealed(true), 400)

    // Reset back to idle state after 4 seconds
    setTimeout(() => {
      setAnimating(false)
      setRevealed(false)
    }, 4000)
  }

  return (
    <button
      onClick={handleClick}
      aria-live="polite"
      className={`relative flex h-9 items-center justify-center rounded-full bg-[#ffd500] text-[#083b7a] font-extrabold shadow-[0_4px_12px_rgba(255,213,0,0.4)] ring-[2px] ring-[#ffd500]/50 active:scale-95 ${
        animating ? 'animate-coin-hole px-3' : 'min-w-[104px] px-3'
      }`}
    >
      <span
        className={`whitespace-nowrap transition-opacity duration-150 ${
          animating && !revealed ? 'opacity-0' : 'opacity-100'
        }`}
      >
        {revealed ? (
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


path_css = 'web/src/index.css'
with open(path_css, 'r', encoding='utf-8') as f:
    css = f.read()

# Add the new keyframes if not exists
if 'animate-coin-hole' not in css:
    css_addition = """
@keyframes coin-flip-hole {
  0% { width: 104px; transform: scale(1) rotateY(0deg); opacity: 1; }
  49% { width: 36px; transform: scale(0) rotateY(360deg); opacity: 0; }
  50% { width: 36px; transform: scale(0) rotateY(360deg); opacity: 0; }
  100% { width: 110px; transform: scale(1) rotateY(720deg); opacity: 1; }
}
.animate-coin-hole {
  animation: coin-flip-hole 0.8s cubic-bezier(0.34, 1.56, 0.64, 1) forwards;
}
"""
    with open(path_css, 'a', encoding='utf-8') as f:
        f.write(css_addition)

print("Smoothed inline BalanceButton applied.")
