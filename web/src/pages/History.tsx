import { useState } from 'react'
import { api } from '../api/client'
import { useShell } from '../components/AppShell'
import { ErrorNote, Spinner } from '../components/ui'
import { useLang } from '../i18n'
import { useApi } from '../lib/useApi'
import { PageTitle } from './common'
import Calendar from './hub/Calendar'

const TYPE_BN: Record<string, [string, string]> = {
  salary_in: ['আয়', 'Income'], bonus_in: ['বোনাস', 'Bonus'], cash_in: ['ক্যাশ ইন', 'Cash in'],
  cash_out: ['ক্যাশ আউট', 'Cash out'], send_money: ['সেন্ড মানি', 'Send money'], receive_money: ['রিসিভড মানি', 'Received'],
  merchant_pay: ['পেমেন্ট', 'Payment'], bill_pay: ['পে বিল', 'Bill'], mobile_recharge: ['মোবাইল রিচার্জ', 'Recharge'],
  pocket_in: ['পকেটে জমা', 'To pocket'], pocket_out: ['পকেট থেকে', 'From pocket'], dps_installment: ['ডিপিএস কিস্তি', 'DPS'],
}

export default function History() {
  const { L, taka, date } = useLang()
  const { uid } = useShell()
  const [tab, setTab] = useState<'list' | 'summary' | 'calendar'>('list')
  const { data, error, loading, reload } = useApi(() => api.transactions(uid, 60), [uid])
  const max = data ? Math.max(1, ...data.summary.by_category.map((c) => c.amount)) : 1
  return (
    <div>
      <PageTitle bn="হিস্টরি" en="History" back={false} />
      <div className="mx-3 mb-3 flex rounded-xl bg-white p-1">
        {(['list', 'summary', 'calendar'] as const).map((t) => (
          <button key={t} onClick={() => setTab(t)}
            className={`flex-1 rounded-lg py-2 text-[13px] font-semibold ${tab === t ? 'bg-upay-yellow' : 'text-muted'}`}>
            {t === 'list' ? L('তালিকা', 'List') : t === 'summary' ? L('সারসংক্ষেপ', 'Summary') : L('ক্যালেন্ডার', 'Calendar')}
          </button>
        ))}
      </div>
      {loading && <Spinner />}
      {error && <ErrorNote message={error} onRetry={reload} />}
      {data && tab === 'list' && (
        <div className="mx-3 overflow-hidden rounded-2xl bg-white">
          {data.items.map((t, k) => {
            const [bn, en] = TYPE_BN[t.type] ?? [t.type, t.type]
            const inflow = t.direction > 0
            return (
              <div key={k} className="flex items-center gap-3 border-b border-line px-4 py-3 last:border-0">
                <div className="flex-1">
                  <p className="text-sm font-semibold">{L(bn, en)} · {t.name}</p>
                  <p className="text-[11px] text-muted">{date(t.ts.slice(0, 10))} · {t.category_bn}{t.fee > 0 ? ` · fee ${taka(t.fee, { paisa: true })}` : ''}</p>
                </div>
                <p className={`text-sm font-bold ${inflow ? 'text-ok' : ''}`}>{inflow ? '+' : '−'}{taka(t.amount, { paisa: t.amount % 1 !== 0 })}</p>
              </div>
            )
          })}
        </div>
      )}
      {data && tab === 'summary' && (
        <div className="mx-3 space-y-3">
          <div className="grid grid-cols-3 gap-2">
            {[['আয়', 'Income', data.summary.income_total], ['খরচ', 'Spent', data.summary.spend_total],
              ['cash-out fee', 'cash-out fees', data.summary.cash_out_fees]].map(([bn, en, v]) => (
              <div key={String(bn)} className="rounded-2xl bg-white p-3">
                <p className="text-[11px] text-muted">{L(String(bn), String(en))} · {L('৩০ দিন', '30 days')}</p>
                <p className="mt-1 font-bold">{taka(Number(v))}</p>
              </div>
            ))}
          </div>
          <div className="space-y-2 rounded-2xl bg-white p-4">
            {data.summary.by_category.map((c) => (
              <div key={c.category_bn}>
                <div className="flex justify-between text-sm"><span>{c.category_bn}</span><span className="font-semibold">{taka(c.amount)}</span></div>
                <div className="mt-1 h-2 rounded-full bg-surface"><div className="h-2 rounded-full bg-upay-blue" style={{ width: `${(100 * c.amount) / max}%` }} /></div>
              </div>
            ))}
          </div>
        </div>
      )}
      {tab === 'calendar' && (
        <div className="mt-3">
          <Calendar />
        </div>
      )}
    </div>
  )
}
