import { NavLink, Outlet } from 'react-router-dom'
import { AiBadge } from '../../components/ui'
import { useLang } from '../../i18n'

export default function HubLayout() {
  const { L } = useLang()
  const tabs = [
    { to: '/app/hishab', end: true, bn: 'ওভারভিউ', en: 'Overview' },
    { to: '/app/hishab/calendar', bn: 'ক্যালেন্ডার', en: 'Calendar' },
    { to: '/app/hishab/learn', bn: 'শেখো', en: 'Learn' },
    { to: '/app/hishab/ask', bn: 'জিজ্ঞেস', en: 'Ask' },
  ]
  return (
    <div>
      <div className="flex items-center gap-2 px-4 pt-3">
        <h1 className="text-lg font-bold">{L('হিসাব', 'Hishab')}</h1>
        <AiBadge />
      </div>
      <nav className="no-scrollbar sticky top-0 z-30 mt-2 flex gap-1 overflow-x-auto bg-surface px-3 pb-2">
        {tabs.map((t) => (
          <NavLink key={t.to} to={t.to} end={t.end}
            className={({ isActive }) => `shrink-0 rounded-full px-3.5 py-1.5 text-sm font-semibold ${isActive ? 'bg-upay-blue text-white' : 'bg-white text-ink'}`}>
            {L(t.bn, t.en)}
          </NavLink>
        ))}
      </nav>
      <Outlet />
    </div>
  )
}
