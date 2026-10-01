import { useLang } from '../i18n'
import { toBnDigits } from '../lib/format'

/** Six-dot PIN entry with a large on-screen keypad (no device keyboard needed). */
export function PinPad({ value, onChange, length = 6 }: { value: string; onChange: (v: string) => void; length?: number }) {
  const { lang, L } = useLang()
  const press = (d: string) => value.length < length && onChange(value + d)
  const keys = ['1', '2', '3', '4', '5', '6', '7', '8', '9']
  return (
    <div>
      <div className="mb-4 flex justify-center gap-3" aria-label={L('PIN', 'PIN')}>
        {Array.from({ length }, (_, i) => (
          <span key={i} className={`size-3.5 rounded-full ${i < value.length ? 'bg-upay-blue' : 'bg-line'}`} />
        ))}
      </div>
      <div className="grid grid-cols-3 gap-2">
        {keys.map((k) => (
          <button key={k} type="button" onClick={() => press(k)}
            className="h-14 rounded-xl bg-surface text-xl font-semibold active:bg-line">
            {lang === 'bn' ? toBnDigits(k) : k}
          </button>
        ))}
        <span />
        <button type="button" onClick={() => press('0')} className="h-14 rounded-xl bg-surface text-xl font-semibold active:bg-line">
          {lang === 'bn' ? '০' : '0'}
        </button>
        <button type="button" onClick={() => onChange(value.slice(0, -1))} aria-label={L('মুছুন', 'Delete')}
          className="h-14 rounded-xl text-lg text-muted active:bg-surface">
          ⌫
        </button>
      </div>
    </div>
  )
}
