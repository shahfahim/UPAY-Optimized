import { Link } from 'react-router-dom'
import { api } from '../api/client'
import type { Indicators, Readiness } from '../api/types'
import { useShell } from '../components/AppShell'
import { AiBadge, Card, ErrorNote, riskClasses, Spinner } from '../components/ui'
import { useLang } from '../i18n'
import { useApi } from '../lib/useApi'
import { InsufficientHistory, PageTitle } from './common'

function Spark({ values, invert = false }: { values: number[]; invert?: boolean }) {
  const max = Math.max(...values, 0.0001)
  return (
    <div className="mt-2 flex h-8 items-end gap-0.5" aria-hidden="true">
      {values.map((v, i) => (
        <span key={i} className={`flex-1 rounded-sm ${invert ? 'bg-warn/60' : 'bg-upay-blue/50'} ${i === values.length - 1 ? '!bg-upay-blue' : ''}`}
          style={{ height: `${Math.max(6, (v / max) * 100)}%` }} />
      ))}
    </div>
  )
}

function ReadinessCard({ r }: { r: Readiness }) {
  const { L } = useLang()
  return (
    <Card>
      <p className="font-semibold">{L('নিয়মিততার signal', 'Consistency signals')}</p>
      <p className="mt-1 rounded-lg bg-surface p-2 text-xs leading-relaxed text-ink/80">{r.disclaimer_bn}</p>
      <div className="mt-3 space-y-2">
        {r.signals.map((s) => (
          <div key={s.id} className={`rounded-xl p-3 ${riskClasses(s.state)}`}>
            <p className="text-sm font-semibold">
              {s.state === 'green' ? '●' : s.state === 'amber' ? '◐' : '○'} {s.name_bn}
            </p>
            <p className="mt-0.5 text-[13px] text-ink/80">{s.reason_bn}</p>
            {s.improve_bn && <p className="mt-1 text-[13px] text-ink"><b>{L('কী করলে উন্নতি হবে:', 'How to improve:')}</b> {s.improve_bn}</p>}
          </div>
        ))}
      </div>
    </Card>
  )
}

export default function Health() {
  const { L, num, taka } = useLang()
  const { uid } = useShell()
  const h = useApi(() => api.health(uid), [uid])
  const r = useApi(() => api.readiness(uid), [uid])
  if (h.loading) return <><PageTitle bn="আর্থিক স্বাস্থ্য" en="Financial health" /><Spinner /></>
  if (h.error) return <ErrorNote message={h.error} onRetry={h.reload} />
  if (!h.data) return null
  if (h.data.insufficient_history) return <><PageTitle bn="আর্থিক স্বাস্থ্য" en="Financial health" /><InsufficientHistory /></>
  const t = h.data.trend6 ?? []
  const cur = h.data.current as Indicators
  const rep = h.data.monthly_report!
  return (
    <div className="pb-6">
      <PageTitle bn="আর্থিক স্বাস্থ্য" en="Financial health" />
      <div className="space-y-3 px-3">
        <div className="grid grid-cols-3 gap-2">
          {[
            { bn: 'জরুরি তহবিল', en: 'Emergency fund', v: L(`${num(cur.emergency_days)} দিন`, `${num(cur.emergency_days)} d`), s: t.map((x) => x.emergency_days) },
            { bn: 'Cash-নির্ভরতা', en: 'Cash dependency', v: `${num(Math.round(cur.cash_dependency * 100))}%`, s: t.map((x) => x.cash_dependency), inv: true },
            { bn: 'ঘাটতিমুক্ত', en: 'Shortfall-free', v: L(`${num(cur.shortfall_free_months)}/৩`, `${cur.shortfall_free_months}/3`), s: t.map((x) => x.shortfall_free_months) },
          ].map((i) => (
            <Card key={i.bn} className="!p-3">
              <p className="text-[11px] text-muted">{L(i.bn, i.en)}</p>
              <p className="text-lg font-bold">{i.v}</p>
              <Spark values={i.s} invert={i.inv} />
              <p className="text-[10px] text-muted">{L('৬ মাস', '6 months')}</p>
            </Card>
          ))}
        </div>
        <Card>
          <div className="mb-2 flex items-center gap-2"><p className="font-semibold">{L('তোমার অভ্যাস', 'Your habits')}</p><AiBadge /></div>
          <ul className="space-y-2">
            {(h.data.habits ?? []).map((x) => (
              <li key={x.id} className="flex items-start justify-between gap-2 text-sm">
                <span>{L(x.text_bn, x.text_en)}</span>
                {x.taka_impact > 0 && <span className="shrink-0 text-xs text-muted">≈{taka(x.taka_impact)}</span>}
              </li>
            ))}
          </ul>
        </Card>
        <Card>
          <div className="mb-2 flex items-center gap-2"><p className="font-semibold">{L('মাসিক হিসাব রিপোর্ট', 'Monthly report')}</p><AiBadge /></div>
          <p className="text-sm">✅ {rep.went_well_bn}</p>
          <p className="mt-1 text-sm">💡 {rep.change_bn}</p>
          <p className="mt-2 text-xs text-muted">
            {rep.shortfall_avoided ? L('এই মাসে টাকা কম পড়েনি', 'No shortfall this month') : L('এই মাসে টাকা কম পড়েছে', 'You ran short this month')}
            {rep.fees_saved > 0 && ` · ${L('fee বাঁচিয়েছ', 'fees saved')} ${taka(rep.fees_saved)}`}
          </p>
        </Card>
        <Link to="/app/hishab/learn" className="block rounded-2xl bg-upay-blue p-4 font-semibold text-white">
          {L('তোমার জন্য ছোট পাঠগুলো দেখো →', 'See your short lessons →')}
        </Link>
        {r.data && <ReadinessCard r={r.data} />}
      </div>
    </div>
  )
}
