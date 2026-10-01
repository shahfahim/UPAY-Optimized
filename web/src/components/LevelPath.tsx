import type { LevelStatus } from '../api/types'
import { useLang } from '../i18n'
import { Icon } from './Icon'

const LEVEL_NAMES: Record<number, [string, string]> = {
  1: ['সঞ্চয়ী', 'Saver'],
  2: ['স্থির', 'Steady'],
  3: ['দক্ষ', 'Skilled'],
}

/** Milestones (5/10/15 days) lead to Level 1 at 30 days, then Levels 2-3. Reached steps are filled. */
export function LevelPath({ status }: { status: LevelStatus }) {
  const { L, num } = useLang()
  const steps = [
    ...status.milestones.map((m) => ({
      key: `m${m.days}`, done: m.reached, big: false,
      label: L(`${num(m.days)} দিন`, `${m.days} days`), sub: m.badge_bn,
    })),
    ...[1, 2, 3].map((lv) => ({
      key: `l${lv}`, done: status.level >= lv, big: true,
      label: L(`লেভেল ${num(lv)}`, `Level ${lv}`),
      sub: lv === 1 ? L('৩০ দিন · DPS-এর জন্য প্রস্তুত', '30 days · DPS-ready') : L(LEVEL_NAMES[lv][0], LEVEL_NAMES[lv][1]),
    })),
  ]
  const current = steps.findIndex((s) => !s.done)
  return (
    <ol className="relative ml-4 border-l-2 border-dashed border-line pl-6">
      {steps.map((s, i) => (
        <li key={s.key} className="relative pb-4 last:pb-0">
          <span
            className={`absolute -left-[37px] flex items-center justify-center rounded-full border-2 ${
              s.big ? 'size-8 -translate-x-[3px]' : 'size-6 translate-y-0.5'
            } ${s.done ? 'border-ok bg-ok text-white' : i === current ? 'border-upay-blue bg-white text-upay-blue' : 'border-line bg-white text-muted'}`}
          >
            {s.done ? <Icon name="check" size={s.big ? 16 : 13} strokeWidth={3} /> : s.big ? <span className="text-xs font-bold">{num(Number(s.key.slice(1)))}</span> : null}
          </span>
          <p className={`font-semibold ${s.big ? 'text-[15px]' : 'text-sm'} ${i === current ? 'text-upay-blue' : ''}`}>{s.label}</p>
          <p className="text-xs text-muted">{s.sub}</p>
        </li>
      ))}
    </ol>
  )
}
