import { useNavigate } from 'react-router-dom'
import { api } from '../api/client'
import { useShell } from '../components/AppShell'
import { Icon } from '../components/Icon'
import { ErrorNote, Spinner } from '../components/ui'
import { useLang } from '../i18n'
import { PageTitle } from './common'
import { useApi } from '../lib/useApi'

export default function Account() {
  const { L, taka } = useLang()
  const { uid, shell, demo } = useShell()
  const navigate = useNavigate()
  const { data, error, loading, reload } = useApi(() => api.savings(uid), [uid])

  const wallets = data && [
    { bn: 'প্রাইমারি', en: 'Primary', v: data.balance, c: 'bg-gradient-to-br from-blue-100 to-blue-200', ic: 'text-blue-700', i: 'wallet' },
    { bn: 'সঞ্চয় পকেট', en: 'Savings pockets', v: data.total, c: 'bg-gradient-to-br from-emerald-100 to-emerald-200', ic: 'text-emerald-700', i: 'pig', to: '/app/savings' },
    { bn: 'ডিপিএস (মাসিক)', en: 'DPS (monthly)', v: data.dps?.monthly ?? 0, c: 'bg-gradient-to-br from-violet-100 to-violet-200', ic: 'text-violet-700', i: 'calendar', to: '/app/savings/dps' },
    { bn: 'পয়সা-সঞ্চয়', en: 'Paisa saving', v: data.paisa.total, c: 'bg-gradient-to-br from-amber-100 to-amber-200', ic: 'text-amber-700', i: 'chart', to: '/app/savings', paisa: true },
  ]

  return (
    <div className="pb-8">
      <PageTitle bn="অ্যাকাউন্ট" en="Account" back={false} />
      
      {/* Profile Card */}
      <div className="mx-3 mt-2 flex items-center gap-4 rounded-2xl bg-white p-4 shadow-sm border border-slate-100 relative overflow-hidden">
        {/* Subtle background decoration */}
        <div className="absolute -right-6 -top-6 size-24 rounded-full bg-upay-blue/5 blur-xl"></div>
        
        <div className="flex size-14 shrink-0 items-center justify-center rounded-full bg-white text-[#0b4ea2] ring-4 ring-slate-50 shadow-sm overflow-hidden z-10">
          {shell && (shell as any).profile_pic ? (
            <img src={(shell as any).profile_pic} alt="Profile" className="w-full h-full object-cover" />
          ) : (
            <img src="/upay-logo.png" alt="Upay Logo" className="w-full h-full object-contain p-1.5" />
          )}
        </div>
        
        <div className="flex-1 z-10">
          <div className="flex items-center gap-2">
            <h2 className="text-lg font-bold text-slate-800">{shell?.name}</h2>
            <Icon name="check" size={14} className="rounded-full bg-emerald-100 text-emerald-600 p-0.5" strokeWidth={3} />
          </div>
          <p className="font-[Inter] text-sm font-medium text-slate-500 mt-0.5">{shell?.phone_masked}</p>
        </div>
      </div>

      {loading && <div className="mt-6"><Spinner /></div>}
      {error && <div className="mt-4"><ErrorNote message={error} onRetry={reload} /></div>}
      
      {/* Balances Grid */}
      {wallets && (
        <div className="mx-3 mt-4 grid grid-cols-2 gap-3">
          {wallets.map((w) => (
            <button key={w.bn} onClick={() => w.to && navigate(w.to)} 
              className={`relative overflow-hidden rounded-2xl ${w.c} p-4 text-left shadow-[0_2px_10px_-4px_rgba(0,0,0,0.05)] transition-transform active:scale-95`}>
              <div className="mb-3 flex size-8 items-center justify-center rounded-full bg-white shadow-sm">
                <Icon name={w.i} size={18} className={w.ic} />
              </div>
              <p className="text-[13px] font-medium text-slate-600">{L(w.bn, w.en)}</p>
              <p className="mt-1 text-[19px] font-extrabold tracking-tight text-slate-800">{taka(w.v, { paisa: w.paisa })}</p>
            </button>
          ))}
        </div>
      )}

      {/* Options Menu */}
      <div className="mx-3 mt-4 overflow-hidden rounded-2xl bg-white shadow-sm border border-slate-100">
        {[
          ['card', 'প্রিপেইড কার্ড', 'Prepaid card', 'text-sky-600', 'bg-sky-50'], 
          ['bank', 'লিংকড অ্যাকাউন্ট', 'Linked account', 'text-emerald-600', 'bg-emerald-50'],
          ['chart', 'লিমিট ও ব্যবহার', 'Limits & usage', 'text-indigo-600', 'bg-indigo-50'], 
          ['bill', 'সার্ভিস চার্জ', 'Service charges', 'text-amber-600', 'bg-amber-50']
        ].map(([i, bn, en, tc, bc]) => (
          <button key={bn} onClick={() => demo(L(bn, en))}
            className="flex w-full items-center gap-4 border-b border-slate-100 px-4 py-4 text-left last:border-0 hover:bg-slate-50 transition-colors">
            <div className={`flex size-10 items-center justify-center rounded-full ${bc}`}>
              <Icon name={i} size={20} className={tc} />
            </div>
            <span className="flex-1 text-[15px] font-semibold text-slate-700">{L(bn, en)}</span>
            <Icon name="chevron" size={18} className="text-slate-400" />
          </button>
        ))}
      </div>
    </div>
  )
}
