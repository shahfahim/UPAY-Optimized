import { useNavigate } from 'react-router-dom'
import { api } from '../api/client'
import { useShell } from '../components/AppShell'
import { Icon } from '../components/Icon'
import { ErrorNote, Spinner } from '../components/ui'
import { useLang } from '../i18n'
import { useApi } from '../lib/useApi'
import { PageTitle } from './common'

export default function Account() {
  const { L, taka } = useLang()
  const { uid, shell, demo } = useShell()
  const navigate = useNavigate()
  const { data, error, loading, reload } = useApi(() => api.savings(uid), [uid])
  const wallets = data && [
    { bn: 'প্রাইমারি', en: 'Primary', v: data.balance, c: 'bg-sky-50' },
    { bn: 'সঞ্চয় পকেট', en: 'Savings pockets', v: data.total, c: 'bg-emerald-50', to: '/app/savings' },
    { bn: 'ডিপিএস (মাসিক)', en: 'DPS (monthly)', v: data.dps?.monthly ?? 0, c: 'bg-violet-50', to: '/app/savings/dps' },
    { bn: 'পয়সা-সঞ্চয়', en: 'Paisa saving', v: data.paisa.total, c: 'bg-amber-50', to: '/app/savings', paisa: true },
  ]
  return (
    <div>
      <PageTitle bn="অ্যাকাউন্ট" en="Account" back={false} />
      <div className="mx-3 flex items-center gap-3 rounded-2xl bg-white p-4">
        <div className="flex size-12 items-center justify-center rounded-full bg-upay-yellow text-lg font-bold text-upay-blue">
          {shell?.avatar_initials}
        </div>
        <div className="flex-1">
          <p className="font-semibold">{shell?.name}</p>
          <p className="font-[Inter] text-xs text-muted">{shell?.phone_masked}</p>
        </div>
      </div>
      {loading && <Spinner />}
      {error && <ErrorNote message={error} onRetry={reload} />}
      {wallets && (
        <div className="mx-3 mt-3 grid grid-cols-2 gap-3">
          {wallets.map((w) => (
            <button key={w.bn} onClick={() => w.to && navigate(w.to)} className={`rounded-2xl ${w.c} p-4 text-left`}>
              <p className="text-sm text-muted">{L(w.bn, w.en)}</p>
              <p className="mt-2 text-xl font-bold">{taka(w.v, { paisa: w.paisa })}</p>
            </button>
          ))}
        </div>
      )}
      <div className="mx-3 mt-3 overflow-hidden rounded-2xl bg-white">
        {[['card', 'প্রিপেইড কার্ড', 'Prepaid card'], ['bank', 'লিংকড অ্যাকাউন্ট', 'Linked account'],
          ['chart', 'লিমিট ও ইউসেজ', 'Limits & usage'], ['bill', 'সার্ভিস চার্জ', 'Service charges']].map(([i, bn, en]) => (
          <button key={bn} onClick={() => demo(L(bn, en))}
            className="flex w-full items-center gap-3 border-b border-line px-4 py-3.5 text-left last:border-0">
            <Icon name={i} size={20} className="text-upay-blue" />
            <span className="flex-1">{L(bn, en)}</span>
            <Icon name="chevron" size={16} className="text-muted" />
          </button>
        ))}
      </div>
    </div>
  )
}
