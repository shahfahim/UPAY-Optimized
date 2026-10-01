import { useEffect, useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { getSession } from '../../lib/session'

/** Opening motion modelled on the upay app: yellow → white, mark fades in, a blue ring draws around it. */
export default function Splash() {
  const navigate = useNavigate()
  const [phase, setPhase] = useState<'yellow' | 'mark'>('yellow')
  const next = getSession() ? '/app/home' : '/welcome'

  useEffect(() => {
    const reduce = window.matchMedia?.('(prefers-reduced-motion: reduce)').matches
    if (reduce) {
      navigate(next, { replace: true })
      return
    }
    const a = window.setTimeout(() => setPhase('mark'), 400)
    const b = window.setTimeout(() => navigate(next, { replace: true }), 2200)
    return () => {
      window.clearTimeout(a)
      window.clearTimeout(b)
    }
  }, [navigate, next])

  return (
    <button
      type="button"
      aria-label="Skip"
      onClick={() => navigate(next, { replace: true })}
      className={`flex flex-1 items-center justify-center transition-colors duration-500 ${phase === 'yellow' ? 'bg-upay-yellow' : 'bg-white'}`}
    >
      {phase === 'mark' && (
        <div className="relative flex size-56 items-center justify-center">
          <svg viewBox="0 0 120 120" className="absolute inset-0 size-full" aria-hidden="true">
            <circle cx="60" cy="60" r="54" fill="none" stroke="#0b4ea2" strokeWidth="3" strokeLinecap="round"
              strokeDasharray="340" className="animate-draw" transform="rotate(-90 60 60)" />
          </svg>
          <div className="flex animate-fade-in flex-col items-center leading-none">
            <span className="text-5xl font-bold text-upay-blue">হিসাব</span>
            <span className="mt-2 font-[Inter] text-sm font-semibold tracking-wide text-ink/60">upay prototype</span>
          </div>
        </div>
      )}
    </button>
  )
}
