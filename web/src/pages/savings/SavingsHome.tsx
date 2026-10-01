import { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { api } from '../../api/client'
import { useShell } from '../../components/AppShell'
import { Icon } from '../../components/Icon'
import { AiBadge, ErrorNote, Sheet, Spinner } from '../../components/ui'
import { useLang } from '../../i18n'
import { useApi } from '../../lib/useApi'
import { PageTitle } from '../common'

export default function SavingsHome() {
  const { L, taka, num } = useLang()
  const { uid } = useShell()
  const navigate = useNavigate()
  const [etin, setEtin] = useState(false)
  const { data, error, loading, reload } = useApi(
    () => Promise.all([api.savings(uid), api.levels(uid)]), [uid])

  const rows = [
    { icon: 'pig', bn: 'আমার পকেট', en: 'My pockets', ai: true, to: '/app/savings/pockets',
      sub: data ? L(`মোট জমা ${taka(data[0].total)}`, `Saved ${taka(data[0].total)}`) : '' },
    { icon: 'chart', bn: 'সঞ্চয় লেভেল', en: 'Savings level', ai: true, to: '/app/savings/levels',
      sub: data ? L(`লেভেল ${num(data[1].level)} · ${data[1].name_bn}`, `Level ${data[1].level}`) : '' },
    { icon: 'shield', bn: 'জরুরি টাকা', en: 'Emergency money', ai: true, to: '/app/savings/emergency',
      sub: L('হঠাৎ টাকা লাগলে কোথা থেকে নেবে', 'Where to find money in a pinch') },
    { icon: 'bank', bn: 'ডিপিএস', en: 'DPS', ai: false, to: '/app/savings/dps',
      sub: data?.[0].dps ? L(`মাসে ${taka(data[0].dps.monthly)} চালু`, `${taka(data[0].dps.monthly)}/month active`)
        : L('Smart DPS পরামর্শসহ', 'With Smart DPS advice') },
    { icon: 'bill', bn: 'ই-টিন ও সঞ্চয় বিবরণী', en: 'e-TIN & savings statement', ai: false, to: null,
      sub: L('বার্ষিক বিবরণী', 'Yearly statement') },
  ]

  return (
    <div className="pb-6">
      <PageTitle bn="সঞ্চয়" en="Savings" />
      {loading && !data && <Spinner />}
      {error && <ErrorNote message={error} onRetry={reload} />}
      {data && (
        <div className="mx-3 mb-3 rounded-2xl bg-upay-blue p-4 text-white">
          <p className="text-sm text-white/80">{L('মোট সঞ্চয়', 'Total savings')}</p>
          <p className="mt-1 text-2xl font-bold">{taka(data[0].total, { paisa: data[0].total % 1 !== 0 })}</p>
          <p className="mt-1 text-xs text-white/80">
            {L(`টানা সঞ্চয় ${num(data[1].streak_days)} দিন`, `${data[1].streak_days}-day saving streak`)}
            {data[1].dps_ready && <span className="ml-2 rounded-full bg-upay-yellow px-2 py-0.5 font-semibold text-ink">{L('DPS-এর জন্য প্রস্তুত', 'DPS-ready')}</span>}
          </p>
        </div>
      )}
      <div className="mx-3 overflow-hidden rounded-2xl bg-white">
        {rows.map((r) => (
          <button key={r.bn} onClick={() => (r.to ? navigate(r.to) : setEtin(true))}
            className="flex w-full items-center gap-3 border-b border-line px-4 py-3.5 text-left last:border-0">
            <span className="flex size-10 items-center justify-center rounded-xl bg-upay-blue/10 text-upay-blue">
              <Icon name={r.icon} size={20} />
            </span>
            <span className="flex-1">
              <span className="flex items-center gap-2 font-semibold">{L(r.bn, r.en)}{r.ai && <AiBadge />}</span>
              {r.sub && <span className="block text-xs text-muted">{r.sub}</span>}
            </span>
            <Icon name="chevron" size={16} className="text-muted" />
          </button>
        ))}
      </div>
      <Sheet open={etin} onClose={() => setEtin(false)} title={L('ই-টিন ও সঞ্চয় বিবরণী', 'e-TIN & savings statement')}>
        <p className="text-sm text-muted">
          {L('এই অংশ upay-এর বর্তমান সেবার মতোই থাকবে — demo-তে চালু নেই।',
            'This stays as in the current upay app — not active in the demo.')}
        </p>
      </Sheet>
    </div>
  )
}
