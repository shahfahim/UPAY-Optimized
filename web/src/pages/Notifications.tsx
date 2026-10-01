import { useEffect } from 'react'
import { useNavigate } from 'react-router-dom'
import { api } from '../api/client'
import { useShell } from '../components/AppShell'
import { Icon } from '../components/Icon'
import { AiBadge, ErrorNote, Spinner } from '../components/ui'
import { useLang } from '../i18n'
import { useApi } from '../lib/useApi'
import { PageTitle } from './common'

const ICONS: Record<string, string> = {
  risk_red: 'info', bill_due: 'bill', salary_plan: 'wallet', level_milestone: 'spark', pocket_80: 'pig', reengage: 'bell',
}

export default function Notifications() {
  const { L, date } = useLang()
  const { uid, refresh } = useShell()
  const navigate = useNavigate()
  const { data, error, loading, reload } = useApi(() => api.notifications(uid), [uid])
  useEffect(() => {
    if (data) void refresh() // unread count goes to zero once the list is opened
  }, [data, refresh])
  return (
    <div>
      <PageTitle bn="নোটিফিকেশন" en="Notifications" />
      {loading && <Spinner />}
      {error && <ErrorNote message={error} onRetry={reload} />}
      {data && data.length === 0 && (
        <p className="m-4 rounded-2xl bg-white p-6 text-center text-sm text-muted">
          {L('এখন কোনো নোটিফিকেশন নেই। আরো মেনু থেকে "সময় এগিয়ে দাও" দিয়ে demo দেখতে পারো।',
            'No notifications yet. Use "time travel" in the More menu to see the demo.')}
        </p>
      )}
      <div className="space-y-2 px-3">
        {data?.map((n) => (
          <button key={n.id} onClick={() => navigate(n.link)}
            className="flex w-full items-start gap-3 rounded-2xl bg-white p-3 text-left">
            <span className="mt-0.5 flex size-9 shrink-0 items-center justify-center rounded-full bg-upay-yellow/40 text-upay-blue">
              <Icon name={ICONS[n.type] ?? 'bell'} size={20} />
            </span>
            <span className="flex-1">
              <span className="block text-sm leading-snug">{L(n.text_bn, n.text_en)}</span>
              <span className="mt-1 flex items-center gap-2 text-[11px] text-muted">
                {date(n.created)} {n.ai && <AiBadge />}
              </span>
            </span>
          </button>
        ))}
      </div>
    </div>
  )
}
