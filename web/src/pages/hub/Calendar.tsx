import { useState } from 'react'
import { api } from '../../api/client'
import type { CalendarDay } from '../../api/types'
import { useShell } from '../../components/AppShell'
import { ErrorNote, Sheet, Spinner } from '../../components/ui'
import { useLang } from '../../i18n'
import { useApi } from '../../lib/useApi'

const WEEK_BN = ['সোম', 'মঙ্গল', 'বুধ', 'বৃহঃ', 'শুক্র', 'শনি', 'রবি']
const WEEK_EN = ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun']

function shift(month: string, by: number): string {
  const [y, m] = month.split('-').map(Number)
  const d = new Date(y, m - 1 + by, 1)
  return `${d.getFullYear()}-${String(d.getMonth() + 1).padStart(2, '0')}`
}

export default function Calendar() {
  const { L, lang, taka, num, date } = useLang()
  const { uid, shell } = useShell()
  const [month, setMonth] = useState(() => (shell?.today ?? '2026-09-18').slice(0, 7))
  const { data, error, loading, reload } = useApi(() => api.calendar(uid, month), [uid, month])
  const [pick, setPick] = useState<CalendarDay | null>(null)

  const maxOut = data ? Math.max(1, ...data.days.filter((d) => !d.predicted).map((d) => d.out_total)) : 1
  const offset = data ? (new Date(`${data.days[0].date}T00:00:00`).getDay() + 6) % 7 : 0
  const cellTone = (d: CalendarDay) => {
    if (d.predicted) {
      return d.risk === 'red' ? 'bg-bad-bg text-bad' : d.risk === 'amber' ? 'bg-warn-bg text-warn' : d.risk === 'green' ? 'bg-ok-bg text-ok' : 'bg-white text-muted'
    }
    const a = d.out_total / maxOut
    return a > 0.6 ? 'bg-upay-blue/35' : a > 0.3 ? 'bg-upay-blue/20' : a > 0 ? 'bg-upay-blue/8' : 'bg-white'
  }
  const monthLabel = new Date(`${month}-01T00:00:00`).toLocaleDateString(lang === 'bn' ? 'bn-BD' : 'en-GB', { month: 'long', year: 'numeric' })

  return (
    <div className="space-y-3 px-3 pb-6">
      <div className="flex items-center justify-between rounded-xl bg-white px-2 py-2">
        <button onClick={() => setMonth(shift(month, -1))} className="px-3 text-xl" aria-label={L('আগের মাস', 'Previous month')}>‹</button>
        <span className="font-semibold">{monthLabel}</span>
        <button onClick={() => setMonth(shift(month, 1))} className="px-3 text-xl" aria-label={L('পরের মাস', 'Next month')}>›</button>
      </div>
      {loading && <Spinner />}
      {error && <ErrorNote message={error} onRetry={reload} />}
      {data && (
        <div className="rounded-2xl bg-white p-2">
          <div className="grid grid-cols-7 gap-1 text-center text-[11px] text-muted">
            {(lang === 'bn' ? WEEK_BN : WEEK_EN).map((w) => <span key={w}>{w}</span>)}
          </div>
          <div className="mt-1 grid grid-cols-7 gap-1">
            {Array.from({ length: offset }, (_, k) => <span key={`e${k}`} />)}
            {data.days.map((d) => (
              <button key={d.date} onClick={() => setPick(d)}
                className={`relative flex aspect-square flex-col items-center justify-center rounded-lg text-sm ${cellTone(d)} ${d.date === data.today ? 'ring-2 ring-upay-yellow' : ''} ${d.predicted ? 'border border-dashed border-line' : ''}`}>
                <span className="font-semibold">{num(Number(d.date.slice(8)))}</span>
                {d.events.length > 0 && <span className="absolute bottom-1 size-1.5 rounded-full bg-upay-yellow-dark" />}
              </button>
            ))}
          </div>
          <div className="mt-3 flex flex-wrap gap-3 px-1 text-[11px] text-muted">
            <span><span className="mr-1 inline-block size-3 rounded bg-upay-blue/30 align-middle" />{L('খরচ (অতীত)', 'Spending (past)')}</span>
            <span><span className="mr-1 inline-block size-3 rounded bg-bad-bg align-middle" />{L('ঝুঁকি (পূর্বাভাস)', 'Risk (forecast)')}</span>
            <span><span className="mr-1 inline-block size-1.5 rounded-full bg-upay-yellow-dark align-middle" />{L('ভাড়া/বিল', 'Rent/bills')}</span>
          </div>
        </div>
      )}
      <Sheet open={pick !== null} onClose={() => setPick(null)} title={pick ? date(pick.date) : ''}>
        {pick && (
          <div className="space-y-2 text-sm">
            <p className="text-muted">{pick.predicted ? L('পূর্বাভাস (AI)', 'Forecast (AI)') : L('যা হয়েছে', 'What happened')}</p>
            <p>{L('আয়', 'In')}: <b>{taka(pick.in_total)}</b> · {L('খরচ', 'Out')}: <b>{taka(pick.out_total)}</b></p>
            {pick.events.length > 0 && <p>{pick.events.join(' · ')}</p>}
            {pick.risk && pick.risk !== 'green' && (
              <p className={pick.risk === 'red' ? 'text-bad' : 'text-warn'}>
                {pick.risk === 'red' ? L('এই দিনে ব্যালেন্স ৳২০০-এর নিচে থাকার কথা', 'Balance expected below ৳200') : L('এই দিনে টাকা কম পড়ার ঝুঁকি আছে', 'Some risk of running short')}
              </p>
            )}
          </div>
        )}
      </Sheet>
    </div>
  )
}
