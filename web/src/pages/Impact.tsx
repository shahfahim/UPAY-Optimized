import { Link } from 'react-router-dom'
import { CartesianGrid, Legend, Line, LineChart, ResponsiveContainer, Tooltip, XAxis, YAxis } from 'recharts'
import { api } from '../api/client'
import type { Impact as ImpactData } from '../api/types'
import { ErrorNote, PrototypeRibbon, Spinner } from '../components/ui'
import { useApi } from '../lib/useApi'

type Better = 'higher' | 'lower'
const pct = (x: number) => `${(x * 100).toFixed(1)}%`
const bdt = (x: number) => `৳${Math.round(x).toLocaleString('en-IN')}`
const n1 = (x: number) => x.toFixed(2)

const HEADLINES: { key: string; label: string; better: Better; fmt: (x: number) => string }[] = [
  { key: 'shortfall_days_per_user_month', label: 'Shortfall days per user-month', better: 'lower', fmt: n1 },
  { key: 'fees_per_user_month', label: 'Transfer fees per user-month', better: 'lower', fmt: bdt },
  { key: 'cash_dependency', label: 'Cash dependency (cash-out / income)', better: 'lower', fmt: pct },
  { key: 'shortfall_free_months', label: 'Shortfall-free months', better: 'higher', fmt: pct },
  { key: 'emergency_days', label: 'Emergency buffer (days of living cost)', better: 'higher', fmt: n1 },
  { key: 'salary_retained_d10', label: 'Salary left on day 10', better: 'higher', fmt: pct },
]

type Row = { model: string; metric: string; value: number | null; baseline: number | null; baselineLabel: string; better: Better; fmt: (x: number) => string }

function modelRows(m: ImpactData['models']): Row[] {
  const g = (k: string, f: string) => {
    const v = m[k]?.[f]
    return typeof v === 'number' ? v : null
  }
  return [
    { model: 'E2 Forecaster', metric: 'Balance MAE, day 14', value: g('E2', 'mae_day14'), baseline: g('E2', 'baseline_last_month_mae_day14'), baselineLabel: 'same as last month', better: 'lower', fmt: bdt },
    { model: 'E2 Forecaster', metric: 'Balance MAE, day 30', value: g('E2', 'mae_day30'), baseline: g('E2', 'baseline_last_month_mae_day30'), baselineLabel: 'same as last month', better: 'lower', fmt: bdt },
    { model: 'E2 Forecaster', metric: 'P10–P90 band coverage, day 14', value: g('E2', 'p10_p90_coverage_day14'), baseline: 0.8, baselineLabel: 'target 80%', better: 'higher', fmt: pct },
    { model: 'E3 Shortfall risk', metric: 'PR-AUC', value: g('E3', 'pr_auc'), baseline: g('E3', 'baseline_rule_pr_auc'), baselineLabel: 'balance-rule', better: 'higher', fmt: n1 },
    { model: 'E3 Shortfall risk', metric: 'Precision at alert', value: g('E3', 'precision_at_alert'), baseline: g('E3', 'baseline_rule_precision'), baselineLabel: 'balance-rule', better: 'higher', fmt: pct },
    { model: 'E3 Shortfall risk', metric: 'Recall at alert', value: g('E3', 'recall_at_alert'), baseline: g('E3', 'baseline_rule_recall'), baselineLabel: 'balance-rule', better: 'higher', fmt: pct },
    { model: 'E3 Shortfall risk', metric: 'Median warning lead (new shortfalls), days', value: g('E3', 'median_lead_days_new_shortfalls'), baseline: null, baselineLabel: '—', better: 'higher', fmt: (x) => x.toFixed(0) },
    { model: 'E6 Category', metric: 'Top-1 accuracy', value: g('E6', 'top1_accuracy'), baseline: g('E6', 'baseline_majority_top1'), baselineLabel: 'majority class', better: 'higher', fmt: pct },
    { model: 'E6 Category', metric: 'Top-3 accuracy', value: g('E6', 'top3_accuracy'), baseline: null, baselineLabel: '—', better: 'higher', fmt: pct },
    { model: 'E15 Recent payments', metric: 'Next-payee hit rate', value: g('E15', 'hit_rate'), baseline: g('E15', 'baseline_recency_hit_rate'), baselineLabel: 'most recent', better: 'higher', fmt: pct },
    { model: 'E8 Eid planner', metric: 'Eid spend MAE', value: g('E8', 'mae'), baseline: g('E8', 'baseline_global_mean_mae'), baselineLabel: 'global mean', better: 'lower', fmt: bdt },
    { model: 'E16 Smart DPS', metric: 'Missed-installment rate', value: g('E16', 'smart_missed_rate'), baseline: g('E16', 'naive_10pct_missed_rate'), baselineLabel: '10% of income', better: 'lower', fmt: pct },
    { model: 'E16 Smart DPS', metric: 'Average monthly installment', value: g('E16', 'smart_avg_monthly'), baseline: g('E16', 'naive_avg_monthly'), baselineLabel: '10% of income', better: 'higher', fmt: bdt },
    { model: 'E9 Bandit', metric: 'Action acceptance (day 60)', value: g('E9', 'actions_acceptance_bandit'), baseline: g('E9', 'actions_acceptance_static'), baselineLabel: 'static ranking', better: 'higher', fmt: pct },
    { model: 'E9 Bandit', metric: 'Lesson acceptance (day 60)', value: g('E9', 'lessons_acceptance_bandit'), baseline: g('E9', 'lessons_acceptance_static'), baselineLabel: 'static ranking', better: 'higher', fmt: pct },
  ]
}

function wins(v: number, b: number, better: Better) {
  return better === 'higher' ? v > b : v < b
}

function Section({ title, sub, children }: { title: string; sub?: string; children: React.ReactNode }) {
  return (
    <section className="rounded-2xl border border-line bg-white p-4 md:p-6">
      <h2 className="text-lg font-bold text-upay-blue">{title}</h2>
      {sub && <p className="mt-0.5 text-sm text-muted">{sub}</p>}
      <div className="mt-4">{children}</div>
    </section>
  )
}

function Curve({ c, title }: { c: ImpactData['bandit_curve']; title: string }) {
  const data = c.day.map((d, i) => ({ day: d, bandit: c.bandit[i], static: c.static[i], random: c.random[i] }))
  return (
    <div>
      <p className="mb-1 text-sm font-semibold">{title}</p>
      <div className="h-56">
        <ResponsiveContainer width="100%" height="100%">
          <LineChart data={data} margin={{ top: 5, right: 8, left: -18, bottom: 0 }}>
            <CartesianGrid stroke="#eef0f4" vertical={false} />
            <XAxis dataKey="day" tick={{ fontSize: 11 }} interval={9} />
            <YAxis tick={{ fontSize: 11 }} domain={[0.3, 0.6]} ticks={[0.3, 0.4, 0.5, 0.6]} tickFormatter={(v: number) => `${Math.round(v * 100)}%`} />
            <Tooltip formatter={(v) => pct(Number(v))} labelFormatter={(d) => `Day ${d}`} />
            <Legend wrapperStyle={{ fontSize: 12 }} />
            <Line type="monotone" dataKey="bandit" name="Thompson bandit" stroke="#0b4ea2" strokeWidth={2.5} dot={false} />
            <Line type="monotone" dataKey="static" name="Static ranking" stroke="#d97706" strokeWidth={1.5} dot={false} />
            <Line type="monotone" dataKey="random" name="Random" stroke="#9ca3af" strokeWidth={1.5} dot={false} strokeDasharray="4 3" />
          </LineChart>
        </ResponsiveContainer>
      </div>
    </div>
  )
}

const SIGNAL_LABEL: Record<string, string> = {
  emergency_buffer: 'Emergency buffer', income_regularity: 'Income regularity', on_time_bills: 'On-time bills',
  saving_consistency: 'Saving consistency', shortfall_frequency: 'Rare shortfalls',
}
const label = (s: string) => SIGNAL_LABEL[s] ?? s.replace(/_/g, ' ').replace(/^\w/, (c) => c.toUpperCase())

export default function Impact() {
  const { data: d, error, loading, reload } = useApi(() => api.impact(), [])

  return (
    <div className="min-h-dvh bg-surface font-[Inter]">
      <PrototypeRibbon />
      <header className="bg-upay-blue px-4 py-6 text-white md:px-8">
        <div className="mx-auto max-w-5xl">
          <Link to="/app/more" className="text-sm text-white/80 underline">← Back to app</Link>
          <h1 className="mt-2 text-2xl font-bold md:text-3xl">Hishab impact — Track 03 cash-flow copilot</h1>
          <p className="mt-1 text-sm text-white/85">Simulated on synthetic data; assumptions in docs.</p>
        </div>
      </header>
      <main className="mx-auto max-w-5xl space-y-4 px-4 py-5 md:px-8">
        {loading && !d && <Spinner label="Loading…" />}
        {error && <ErrorNote message={error} onRetry={reload} />}
        {d && (
          <>
            <Section title="Headline: baseline vs with Hishab" sub={`${d.user_months} held-out user-months replayed · mean action acceptance ${pct(d.acceptance_mean)}`}>
              <div className="grid grid-cols-1 gap-3 sm:grid-cols-2 lg:grid-cols-3">
                {HEADLINES.filter((h) => d.headline[h.key]).map((h) => {
                  const p = d.headline[h.key]
                  const good = wins(p.with_hishab, p.baseline, h.better)
                  const same = Math.abs(p.with_hishab - p.baseline) < 1e-9
                  return (
                    <div key={h.key} className="rounded-xl bg-surface p-3">
                      <p className="text-xs text-muted">{h.label}</p>
                      <p className="mt-1 flex items-baseline gap-2">
                        <span className="text-sm text-muted line-through decoration-muted/50">{h.fmt(p.baseline)}</span>
                        <span className="text-xl font-bold">{h.fmt(p.with_hishab)}</span>
                        <span className={`text-xs font-semibold ${same ? 'text-muted' : good ? 'text-ok' : 'text-bad'}`}>{same ? '=' : good ? '▲ better' : '▼ worse'}</span>
                      </p>
                    </div>
                  )
                })}
              </div>
              <div className="mt-3 grid grid-cols-1 gap-3 sm:grid-cols-2">
                <div className="rounded-xl border border-ok/30 bg-ok-bg p-3 text-sm">
                  <p className="font-semibold text-ok">Per 100,000 users, per month</p>
                  <p className="mt-1">{Number(d.per_100k.shortfall_days_avoided_per_month).toLocaleString('en-IN')} shortfall days avoided</p>
                  <p>{bdt(Number(d.per_100k.fees_saved_per_month_bdt))} in transfer fees saved</p>
                  <p className="mt-1 text-xs text-muted">{String(d.per_100k.note ?? '')}</p>
                </div>
                <div className="rounded-xl bg-surface p-3 text-sm">
                  <p className="font-semibold">Monthly active rate</p>
                  <p className="mt-1">{pct(d.active_rate.baseline)} → <b>{pct(d.active_rate.with_hishab)}</b></p>
                  <p className="mt-1 text-xs text-muted">Uses the generator's assumed inactivity mechanism.</p>
                </div>
              </div>
            </Section>

            <Section title="Models vs baselines" sub="Time-based held-out evaluation on the synthetic population.">
              <div className="-mx-4 overflow-x-auto md:mx-0">
                <table className="w-full min-w-[560px] text-left text-sm">
                  <thead className="text-xs uppercase text-muted">
                    <tr><th className="px-4 py-2 md:px-2">Model</th><th className="px-2 py-2">Metric</th><th className="px-2 py-2 text-right">Hishab</th><th className="px-2 py-2 text-right">Baseline</th><th className="px-2 py-2">Baseline is</th></tr>
                  </thead>
                  <tbody>
                    {modelRows(d.models).filter((r) => r.value !== null).map((r) => {
                      const ok = r.baseline === null ? null : wins(r.value!, r.baseline, r.better)
                      return (
                        <tr key={r.model + r.metric} className="border-t border-line">
                          <td className="px-4 py-2 font-semibold md:px-2">{r.model}</td>
                          <td className="px-2 py-2">{r.metric}</td>
                          <td className={`px-2 py-2 text-right font-semibold ${ok === null ? '' : ok ? 'text-ok' : 'text-bad'}`}>{r.fmt(r.value!)}</td>
                          <td className="px-2 py-2 text-right text-muted">{r.baseline === null ? '—' : r.fmt(r.baseline)}</td>
                          <td className="px-2 py-2 text-xs text-muted">{r.baselineLabel}</td>
                        </tr>
                      )
                    })}
                  </tbody>
                </table>
              </div>
            </Section>

            <Section title="Learning nudges (contextual bandit)" sub="Cumulative acceptance over 60 simulated days.">
              <div className="grid grid-cols-1 gap-4 md:grid-cols-2">
                <Curve c={d.bandit_curve} title="Action cards" />
                <Curve c={d.lesson_curve} title="Literacy lessons" />
              </div>
            </Section>

            <Section title="Fairness" sub="Outcome and alert quality by persona and area. Gaps above 10 pp are flagged.">
              {d.fairness.flags.length > 0 && (
                <ul className="mb-3 space-y-1.5">
                  {d.fairness.flags.map((f) => (
                    <li key={f.group_type + f.metric} className="rounded-lg bg-warn-bg px-3 py-2 text-sm text-warn">
                      <b>{f.group_type} · {f.metric.replace(/_/g, ' ')}</b>: gap {(f.gap * 100).toFixed(0)} pp — {f.note}
                    </li>
                  ))}
                </ul>
              )}
              <div className="-mx-4 overflow-x-auto md:mx-0">
                <table className="w-full min-w-[480px] text-left text-sm">
                  <thead className="text-xs uppercase text-muted">
                    <tr><th className="px-4 py-2 md:px-2">Group</th><th className="px-2 py-2">Metric</th><th className="px-2 py-2 text-right">Value</th><th className="px-2 py-2 text-right">n</th></tr>
                  </thead>
                  <tbody>
                    {d.fairness.rows.map((r) => (
                      <tr key={r.group_type + r.group + r.metric} className="border-t border-line">
                        <td className="px-4 py-1.5 md:px-2">{r.group_type}: <b>{r.group.replace(/_/g, ' ')}</b></td>
                        <td className="px-2 py-1.5">{r.metric.replace(/_/g, ' ')}</td>
                        <td className="px-2 py-1.5 text-right">{r.metric === 'shortfall_days_reduction' ? `${n1(r.value)} days/month` : pct(r.value)}</td>
                        <td className="px-2 py-1.5 text-right text-muted">{r.n}</td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            </Section>

            <Section title="Readiness signals distribution" sub="Share of users with a green signal. Educational consistency signals — not a credit score; no lending decision uses them.">
              <ReadinessTable rows={d.readiness_distribution} />
            </Section>

            <section className="rounded-2xl border border-line bg-white p-4 text-sm text-ink/80 md:p-6">
              <h2 className="mb-1 font-bold text-ink">Assumptions</h2>
              <p>{d.assumptions_note}</p>
              <p className="mt-2 text-xs text-muted">All fees are placeholder assumptions, not upay tariffs. No real customer data is used anywhere.</p>
            </section>
          </>
        )}
      </main>
    </div>
  )
}

function ReadinessTable({ rows }: { rows: ImpactData['readiness_distribution'] }) {
  const signals = [...new Set(rows.map((r) => r.signal))]
  const groups = [...new Set(rows.map((r) => `${r.group_type}|${r.group}`))]
  const cell = (g: string, s: string) => rows.find((r) => `${r.group_type}|${r.group}` === g && r.signal === s)
  return (
    <div className="-mx-4 overflow-x-auto md:mx-0">
      <table className="w-full min-w-[560px] text-left text-sm">
        <thead className="text-xs uppercase text-muted">
          <tr><th className="px-4 py-2 md:px-2">Group</th>{signals.map((s) => <th key={s} className="px-2 py-2 text-right">{label(s)}</th>)}</tr>
        </thead>
        <tbody>
          {groups.map((g) => {
            const [type, name] = g.split('|')
            const n = rows.find((r) => `${r.group_type}|${r.group}` === g)?.n
            return (
              <tr key={g} className="border-t border-line">
                <td className="px-4 py-1.5 md:px-2">{type}: <b>{name.replace(/_/g, ' ')}</b> <span className="text-xs text-muted">n={n}</span></td>
                {signals.map((s) => {
                  const c = cell(g, s)
                  const v = c?.green_share ?? 0
                  return (
                    <td key={s} className="px-2 py-1.5 text-right">
                      <span className="inline-block min-w-12 rounded px-1.5" style={{ background: `rgba(22,163,74,${0.08 + v * 0.35})` }}>{c ? pct(v) : '—'}</span>
                    </td>
                  )
                })}
              </tr>
            )
          })}
        </tbody>
      </table>
    </div>
  )
}
