import { useState } from 'react'
import { api } from '../../api/client'
import type { ActionCard, Forecast, Home } from '../../api/types'
import { useShell } from '../../components/AppShell'
import { ForecastChart } from '../../components/ForecastChart'
import { Icon } from '../../components/Icon'
import { AiBadge, Button, Card, ErrorNote, riskClasses, Spinner } from '../../components/ui'
import { useLang } from '../../i18n'
import { bnPossessive } from '../../lib/format'
import { useApi } from '../../lib/useApi'
import { InsufficientHistory } from '../common'

function likelihood(prob: number, L: (bn: string, en: string) => string): string {
  if (prob >= 0.6) return L('খুব সম্ভাবনা আছে', 'very likely')
  if (prob >= 0.3) return L('বেশ সম্ভাবনা আছে', 'quite likely')
  return L('সম্ভাবনা কম', 'unlikely')
}

function RiskCard({ home }: { home: Home }) {
  const { L, taka, date, num } = useLang()
  const [why, setWhy] = useState(false)
  const r = home.risk!
  const fc = home.forecast!
  const headline = fc.shortfall_date
    ? L(`${bnPossessive(date(fc.shortfall_date))} দিকে প্রায় ${taka(fc.shortfall_amount)} কম পড়তে পারে`,
      `You may run short by about ${taka(fc.shortfall_amount)} around ${date(fc.shortfall_date)}`)
    : L('সামনের ৩০ দিনে টাকা কম পড়ার সম্ভাবনা কম', 'Low chance of running short in the next 30 days')
  return (
    <div className={`rounded-2xl p-4 ${riskClasses(r.level)}`}>
      <p className="text-[16px] font-bold leading-snug">{headline}</p>
      <p className="mt-1 text-sm">{likelihood(r.prob, L)} · {num(Math.round(r.prob * 100))}%</p>
      <button onClick={() => setWhy((w) => !w)} className="mt-2 text-sm font-semibold underline" aria-expanded={why}>
        {L('কেন?', 'Why?')}
      </button>
      {why && (
        <ul className="mt-2 space-y-1.5 rounded-xl bg-white/70 p-3 text-sm text-ink">
          {r.drivers.map((d) => (
            <li key={d.feature} className="flex gap-2"><AiBadge /><span>{L(d.text_bn, d.text_en)}</span></li>
          ))}
        </ul>
      )}
    </div>
  )
}

function ActionItem({ card, active, onPreview, onRespond }: {
  card: ActionCard; active: boolean; onPreview: () => void; onRespond: (ok: boolean) => void
}) {
  const { L, taka, num } = useLang()
  const pct = (x: number) => num(Math.round(x * 100))
  return (
    <Card className={active ? 'border-ok ring-1 ring-ok' : ''}>
      <div className="flex items-start gap-2"><AiBadge className="mt-0.5" /><p className="font-semibold leading-snug">{L(card.title_bn, card.title_en)}</p></div>
      <p className="mt-1 text-sm text-ink/70">{L(card.why_bn, card.why_en)}</p>
      <div className="mt-2 flex flex-wrap gap-2 text-xs font-semibold">
        {card.risk_after < card.risk_before - 0.005 && (
          <span className="rounded-full bg-ok-bg px-2 py-0.5 text-ok">{L(`ঝুঁকি ${pct(card.risk_before)}% → ${pct(card.risk_after)}%`, `Risk ${pct(card.risk_before)}% → ${pct(card.risk_after)}%`)}</span>
        )}
        {card.fees_saved > 0 && (
          <span className="rounded-full bg-ok-bg px-2 py-0.5 text-ok">{L(`মাসে ${taka(card.fees_saved)} বাঁচবে`, `Saves ${taka(card.fees_saved)}/month`)}</span>
        )}
      </div>
      <div className="mt-3 grid grid-cols-3 gap-2">
        <Button variant="outline" className="!min-h-9 !px-2 text-[13px]" onClick={onPreview}>{active ? L('লুকাও', 'Hide') : L('কী হবে দেখো', 'Preview')}</Button>
        <Button className="!min-h-9 !px-2 text-[13px]" onClick={() => onRespond(true)}>{L('রাজি', 'Accept')}</Button>
        <Button variant="ghost" className="!min-h-9 !px-2 text-[13px]" onClick={() => onRespond(false)}>{L('বাদ', 'Dismiss')}</Button>
      </div>
    </Card>
  )
}

/** Hub home: the core loop — predict (risk + forecast), explain (কেন?), act (what-if actions). */
export default function Forecast() {
  const { L, taka } = useLang()
  const { uid } = useShell()
  const { data: home, error, loading, reload, setData } = useApi(() => api.home(uid), [uid])
  const [whatIf, setWhatIf] = useState<{ id: string; fc: Forecast } | null>(null)
  const [toast, setToast] = useState('')

  if (loading && !home) return <Spinner label={L('হিসাব করা হচ্ছে…', 'Working it out…')} />
  if (error) return <ErrorNote message={error} onRetry={reload} />
  if (!home) return null
  if (home.insufficient_history || !home.forecast || !home.risk) return <InsufficientHistory />

  const preview = async (id: string) => {
    if (whatIf?.id === id) return setWhatIf(null)
    try {
      const s = await api.simulate(uid, id)
      setWhatIf({ id, fc: s.forecast })
    } catch {
      setToast(L('এই পরামর্শের হিসাব এখন দেখানো যাচ্ছে না', 'Could not preview this tip'))
    }
  }
  const respond = async (card: ActionCard, ok: boolean) => {
    await api.respond(uid, card.id, ok).catch(() => undefined)
    setData({ ...home, actions: home.actions.filter((a) => a.id !== card.id) })
    if (whatIf?.id === card.id) setWhatIf(null)
    setToast(ok ? L('ঠিক আছে! পরিকল্পনায় যোগ হলো।', 'Added to your plan.') : L('ঠিক আছে, এটা আর দেখাবো না।', 'Okay, hidden.'))
    window.setTimeout(() => setToast(''), 2500)
  }

  return (
    <div className="space-y-3 px-3 pb-6">
      <RiskCard home={home} />
      <Card>
        <div className="mb-1 flex items-center justify-between">
          <p className="font-semibold">{L('সামনের ৩০ দিনের হিসাব', 'Next 30 days')}</p>
          <AiBadge />
        </div>
        <ForecastChart forecast={home.forecast} whatIf={whatIf?.fc} />
        <div className="mt-1 flex flex-wrap gap-3 text-[11px] text-muted">
          <span><span className="mr-1 inline-block h-0.5 w-4 bg-upay-blue align-middle" />{L('সম্ভাব্য ব্যালেন্স', 'Expected')}</span>
          <span><span className="mr-1 inline-block h-2 w-4 bg-upay-blue/15 align-middle" />{L('সম্ভাব্য সীমা', 'Likely range')}</span>
          {whatIf && <span className="text-ok"><span className="mr-1 inline-block h-0.5 w-4 bg-ok align-middle" />{L('পরামর্শ মানলে', 'If you follow it')}</span>}
          <span className="text-bad">--- ৳২০০</span>
        </div>
      </Card>
      <Card className="flex items-center gap-3">
        <Icon name="wallet" className="text-upay-blue" />
        <div className="flex-1">
          {home.safe_today > 0 ? (
            <p className="font-semibold">{L(`আজ নিরাপদ খরচ ${taka(home.safe_today)}`, `Safe to spend today: ${taka(home.safe_today)}`)}</p>
          ) : (
            <>
              <p className="font-semibold">{L(`দৈনিক খরচসীমা ${taka(home.daily_budget)}-এর মধ্যে রাখার চেষ্টা করো`, `Try to keep daily spending under ${taka(home.daily_budget)}`)}</p>
              <p className="text-xs text-warn">{L('ঝুঁকি থাকছে — এই মাসে একটু সামলে চলো', 'Still risky — spend carefully this month')}</p>
            </>
          )}
        </div>
      </Card>
      {home.actions.length > 0 && <p className="pt-1 text-[15px] font-semibold text-upay-blue">{L('তোমার জন্য পরামর্শ', 'Suggestions for you')}</p>}
      {home.actions.map((a) => (
        <ActionItem key={a.id} card={a} active={whatIf?.id === a.id} onPreview={() => void preview(a.id)}
          onRespond={(ok) => void respond(a, ok)} />
      ))}
      {toast && <div className="fixed bottom-24 left-1/2 z-50 -translate-x-1/2 rounded-full bg-ink px-4 py-2 text-sm text-white">{toast}</div>}
    </div>
  )
}
