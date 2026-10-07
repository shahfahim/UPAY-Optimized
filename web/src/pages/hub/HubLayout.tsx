import { NavLink, Outlet } from 'react-router-dom'
import { AiBadge } from '../../components/ui'
import { useLang } from '../../i18n'

export default function HubLayout() {
  const { L } = useLang()
  const tabs = [
    { to: '/app/hishab', end: true, bn: 'পূর্বাভাস', en: 'Forecast', isAi: true },
    { to: '/app/hishab/calendar', bn: 'ক্যালেন্ডার', en: 'Calendar' },
    { to: '/app/hishab/ask', bn: 'জিজ্ঞাসা', en: 'Ask', isAi: true },
    { to: '/app/savings', bn: 'সঞ্চয়', en: 'Savings' },
  ]
  return (
    <div className="flex flex-col h-full flex-1">
      <nav className="no-scrollbar sticky top-0 z-30 flex items-center gap-1 overflow-x-auto bg-slate-50/95 backdrop-blur-xl px-3 py-3 border-b border-slate-200/50 shadow-sm transition-all">
        {tabs.map((t) => (
          <NavLink key={t.to} to={t.to} end={t.end}
            className={({ isActive }) => `shrink-0 rounded-full px-4 py-1.5 text-[14.5px] font-semibold flex items-center gap-1.5 transition-colors ${isActive ? 'bg-upay-blue text-white shadow-[0_2px_10px_-3px_rgba(11,78,162,0.4)]' : 'bg-transparent text-slate-600 hover:bg-slate-200/50'}`}>
            {t.isAi ? (
              <>
                <span className="font-bold">{L(t.bn, t.en)}</span>
                <AiBadge />
              </>
            ) : (
              L(t.bn, t.en)
            )}
          </NavLink>
        ))}
      </nav>
      <Outlet />
    </div>
  )
}
