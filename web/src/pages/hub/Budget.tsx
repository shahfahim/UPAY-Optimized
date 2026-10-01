import { useState } from 'react'
import { api } from '../../api/client'
import { useShell } from '../../components/AppShell'
import { AiBadge, Button, Card, ErrorNote, ProgressBar, Spinner } from '../../components/ui'
import { useLang } from '../../i18n'
import { parseAmount } from '../../lib/format'
import { useApi } from '../../lib/useApi'

type Period = 'day' | 'week' | 'month'

export default function Budget() {
  const { L, taka, num } = useLang()
  const { uid } = useShell()
  const [period, setPeriod] = useState<Period>('month')
  const { data, error, loading, reload } = useApi(() => api.budget(uid, period), [uid, period])
  const [editing, setEditing] = useState(false)
  const [draft, setDraft] = useState<Record<string, string>>({})
  const [err, setErr] = useState('')

  const setMode = async (mode: 'auto' | 'manual') => {
    if (mode === 'manual') {
      setDraft(Object.fromEntries((data?.items ?? []).map((i) => [i.category, String(Math.round(i.budget * 30 / ({ day: 1, week: 7, month: 30 }[period])))])))
      setEditing(true)
      return
    }
    await api.setBudget(uid, 'auto')
    setEditing(false)
    void reload()
  }
  const save = async () => {
    const manual: Record<string, number> = {}
    for (const [c, v] of Object.entries(draft)) {
      if (v.trim() === '') continue
      const n = parseAmount(v)
      if (n === null) return setErr(L('সঠিক পরিমাণ লিখুন', 'Enter valid amounts'))
      manual[c] = n
    }
    await api.setBudget(uid, 'manual', manual)
    setEditing(false)
    setErr('')
    void reload()
  }

  return (
    <div className="space-y-3 px-3 pb-6">
      <div className="flex rounded-xl bg-white p-1">
        {(['day', 'week', 'month'] as Period[]).map((p) => (
          <button key={p} onClick={() => setPeriod(p)}
            className={`flex-1 rounded-lg py-2 text-sm font-semibold ${period === p ? 'bg-upay-yellow' : 'text-muted'}`}>
            {{ day: L('দৈনিক', 'Daily'), week: L('সাপ্তাহিক', 'Weekly'), month: L('মাসিক', 'Monthly') }[p]}
          </button>
        ))}
      </div>
      <div className="flex items-center justify-between rounded-xl bg-white px-3 py-2">
        <span className="text-sm font-semibold">{L('বাজেট ঠিক করবে', 'Budget set by')}</span>
        <div className="flex gap-1">
          <button onClick={() => void setMode('auto')}
            className={`rounded-full px-3 py-1 text-xs font-semibold ${data?.mode === 'auto' && !editing ? 'bg-upay-blue text-white' : 'bg-surface'}`}>
            AI {L('(নিজে থেকে)', '(auto)')}
          </button>
          <button onClick={() => void setMode('manual')}
            className={`rounded-full px-3 py-1 text-xs font-semibold ${data?.mode === 'manual' || editing ? 'bg-upay-blue text-white' : 'bg-surface'}`}>
            {L('আমি নিজে', 'Manual')}
          </button>
        </div>
      </div>
      {loading && <Spinner />}
      {error && <ErrorNote message={error} onRetry={reload} />}
      {editing && (
        <Card>
          <p className="mb-2 text-sm font-semibold">{L('মাসিক বাজেট লিখুন', 'Monthly budget per category')}</p>
          <div className="space-y-2">
            {Object.keys(draft).map((c) => (
              <label key={c} className="flex items-center gap-2 text-sm">
                <span className="flex-1">{data?.items.find((i) => i.category === c)?.category_bn ?? c}</span>
                <input inputMode="decimal" value={draft[c]} onChange={(e) => setDraft({ ...draft, [c]: e.target.value })}
                  className="h-10 w-28 rounded-lg border border-line px-2 text-right" />
              </label>
            ))}
          </div>
          {err && <p className="mt-2 text-sm text-bad">{err}</p>}
          <Button full className="mt-3" onClick={() => void save()}>{L('সংরক্ষণ', 'Save')}</Button>
        </Card>
      )}
      {data && !editing && (
        <>
          <p className="flex items-center gap-2 px-1 text-xs text-muted">{data.mode === 'auto' && <AiBadge />}{data.reason_bn}</p>
          <Card className="space-y-3">
            {data.items.length === 0 && <p className="text-sm text-muted">{L('এই সময়ে কোনো খরচ নেই', 'No spending in this period')}</p>}
            {data.items.map((i) => (
              <div key={i.category}>
                <div className="flex justify-between text-sm">
                  <span className="font-semibold">{i.category_bn}</span>
                  <span>{taka(i.spent)} / {taka(i.budget)}</span>
                </div>
                <div className="mt-1"><ProgressBar value={i.budget > 0 ? i.spent / i.budget : 1}
                  tone={i.status === 'over' ? 'bad' : i.status === 'warn' ? 'warn' : 'ok'} /></div>
                {i.status !== 'ok' && (
                  <p className={`mt-0.5 text-[11px] ${i.status === 'over' ? 'text-bad' : 'text-warn'}`}>
                    {i.status === 'over' ? L(`বাজেটের ${num(i.pct)}% খরচ হয়ে গেছে`, `${i.pct}% of budget used`)
                      : L(`বাজেটের ${num(i.pct)}% — সাবধান`, `${i.pct}% of budget — careful`)}
                  </p>
                )}
              </div>
            ))}
          </Card>
        </>
      )}
    </div>
  )
}
