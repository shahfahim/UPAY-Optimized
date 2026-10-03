import { useEffect, type ButtonHTMLAttributes, type ReactNode } from 'react'
import { useLang } from '../i18n'

export function AiBadge({ className = '' }: { className?: string }) {
  return (
    <span
      aria-label="AI"
      className={`inline-flex shrink-0 items-center rounded-md bg-upay-blue px-1.5 py-[1px] font-[Inter] text-[11px] font-bold leading-4 tracking-wide text-white ${className}`}
    >
      AI
    </span>
  )
}

export function PrototypeRibbon() {
  return (
    <div className="bg-ink px-3 py-1 text-center text-[11px] leading-4 text-white/90">
      Prototype — upay-এর অফিসিয়াল app নয় · synthetic data
    </div>
  )
}

export function TextMark({ size = 'md' }: { size?: 'md' | 'lg' }) {
  const big = size === 'lg'
  return (
    <div className="flex flex-col items-center leading-none">
      <span className={`font-bold text-upay-blue ${big ? 'text-5xl' : 'text-2xl'}`}>Upay Prototype</span>
      <span className={`mt-1 font-[Inter] font-semibold tracking-wide text-ink/60 ${big ? 'text-sm' : 'text-[10px]'}`}>
        upay prototype
      </span>
    </div>
  )
}

type BtnProps = ButtonHTMLAttributes<HTMLButtonElement> & { variant?: 'blue' | 'yellow' | 'ghost' | 'outline'; full?: boolean }

export function Button({ variant = 'blue', full, className = '', ...rest }: BtnProps) {
  const styles = {
    blue: 'bg-upay-blue text-white hover:bg-upay-blue-dark',
    yellow: 'bg-upay-yellow text-ink hover:bg-upay-yellow-dark',
    ghost: 'bg-transparent text-upay-blue hover:bg-upay-blue/5',
    outline: 'border border-line bg-white text-ink hover:bg-surface',
  }[variant]
  return (
    <button
      {...rest}
      className={`inline-flex min-h-11 items-center justify-center gap-2 rounded-xl px-4 text-[15px] font-semibold transition active:scale-[0.98] disabled:opacity-50 ${styles} ${full ? 'w-full' : ''} ${className}`}
    />
  )
}

export function Spinner({ label }: { label?: string }) {
  return (
    <div className="flex items-center justify-center gap-2 py-8 text-sm text-muted" role="status">
      <span className="size-5 animate-spin rounded-full border-2 border-upay-blue border-t-transparent" />
      {label}
    </div>
  )
}

export function ErrorNote({ message, onRetry }: { message: string; onRetry?: () => void }) {
  const { L } = useLang()
  return (
    <div className="m-4 rounded-xl bg-bad-bg p-3 text-sm text-bad" role="alert">
      {message}
      {onRetry && (
        <button className="ml-2 font-semibold underline" onClick={onRetry}>
          {L('আবার চেষ্টা করুন', 'Retry')}
        </button>
      )}
    </div>
  )
}

export function Sheet({ open, onClose, title, children }: { open: boolean; onClose: () => void; title?: string; children: ReactNode }) {
  useEffect(() => {
    if (!open) return
    const onKey = (e: KeyboardEvent) => e.key === 'Escape' && onClose()
    window.addEventListener('keydown', onKey)
    return () => window.removeEventListener('keydown', onKey)
  }, [open, onClose])
  if (!open) return null
  return (
    <div className="fixed inset-0 z-50 flex items-end justify-center bg-black/40 animate-backdrop" onClick={onClose}>
      <div
        role="dialog"
        aria-modal="true"
        className="max-h-[85dvh] w-full max-w-[430px] animate-rise overflow-y-auto rounded-t-3xl bg-white p-5 pb-8"
        onClick={(e) => e.stopPropagation()}
      >
        <div className="mx-auto mb-3 h-1.5 w-10 rounded-full bg-line" />
        {title && <h2 className="mb-3 text-lg font-semibold">{title}</h2>}
        {children}
      </div>
    </div>
  )
}

const RISK_STYLES = {
  green: 'bg-ok-bg text-ok',
  amber: 'bg-warn-bg text-warn',
  red: 'bg-bad-bg text-bad',
} as const

export function riskClasses(level: 'green' | 'amber' | 'red' | null | undefined): string {
  return RISK_STYLES[level ?? 'green']
}

export function Card({ children, className = '' }: { children: ReactNode; className?: string }) {
  return <div className={`rounded-2xl border border-line bg-white p-4 ${className}`}>{children}</div>
}

export function SectionTitle({ children, right }: { children: ReactNode; right?: ReactNode }) {
  return (
    <div className="mb-2 mt-5 flex items-center justify-between px-4">
      <h2 className="text-[15px] font-semibold text-upay-blue">{children}</h2>
      {right}
    </div>
  )
}

export function ProgressBar({ value, tone = 'blue' }: { value: number; tone?: 'blue' | 'ok' | 'warn' | 'bad' }) {
  const color = { blue: 'bg-upay-blue', ok: 'bg-ok', warn: 'bg-warn', bad: 'bg-bad' }[tone]
  return (
    <div className="h-2 w-full overflow-hidden rounded-full bg-surface">
      <div className={`h-full rounded-full ${color}`} style={{ width: `${Math.max(0, Math.min(100, value * 100))}%` }} />
    </div>
  )
}
