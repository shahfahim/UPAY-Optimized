import { useState } from 'react'
import { Link, useNavigate } from 'react-router-dom'
import { api } from '../api/client'
import type { DemoUser } from '../api/types'
import { useShell } from '../components/AppShell'
import { Icon } from '../components/Icon'
import { Sheet } from '../components/ui'
import { useLang } from '../i18n'
import { clearSession, setSession } from '../lib/session'
import { PageTitle } from './common'

export default function More() {
  const { L, lang, setLang, date } = useLang()
  const { refresh, demo } = useShell()
  const navigate = useNavigate()
  const [users, setUsers] = useState<DemoUser[] | null>(null)
  const [toast, setToast] = useState('')

  const say = (m: string) => {
    setToast(m)
    window.setTimeout(() => setToast(''), 3000)
  }
  const travel = async (days: 7 | 14 | 30) => {
    const r = await api.timeTravel(days)
    await refresh()
    say(L(`demo-র তারিখ এখন ${date(r.today)}`, `Demo date is now ${date(r.today)}`))
  }
  const reset = async () => {
    await api.reset()
    await refresh()
    say(L('Demo আগের অবস্থায় ফিরেছে', 'Demo reset'))
  }
  const switchTo = async (u: DemoUser) => {
    try {
      const r = await api.login(u.phone, '123456') // every seeded demo user's PIN; registered users log in themselves
      setSession({ token: r.token, userId: r.user_id })
      window.location.assign('/app/home')
    } catch {
      say(L('এই user-এর জন্য লগইন করুন', 'Log in as this user from the login page'))
    }
  }

  const row = (icon: string, bn: string, en: string, onClick: () => void, tone = '') => (
    <button onClick={onClick} className={`flex w-full items-center gap-3 border-b border-line px-4 py-3.5 text-left last:border-0 ${tone}`}>
      <Icon name={icon} size={20} className="text-upay-blue" />
      <span className="flex-1 text-[15px]">{L(bn, en)}</span>
      <Icon name="chevron" size={16} className="text-muted" />
    </button>
  )

  return (
    <div>
      <PageTitle bn="আরো" en="More" />
      <p className="px-4 pb-1 pt-2 text-xs font-semibold text-muted">{L('Demo নিয়ন্ত্রণ', 'Demo controls')}</p>
      <div className="mx-3 overflow-hidden rounded-2xl bg-white">
        {row('clock', 'সময় এগিয়ে দাও: ৭ দিন', 'Time travel: 7 days', () => void travel(7))}
        {row('clock', 'সময় এগিয়ে দাও: ১৪ দিন', 'Time travel: 14 days', () => void travel(14))}
        {row('clock', 'সময় এগিয়ে দাও: ৩০ দিন', 'Time travel: 30 days', () => void travel(30))}
        {row('close', 'Demo reset', 'Demo reset', () => void reset())}
        {row('wallet', 'অন্য demo user', 'Switch demo user', () => api.users().then(setUsers))}
        {row('chart', 'Impact (judges)', 'Impact (judges)', () => navigate('/impact'))}
      </div>
      <p className="px-4 pb-1 pt-4 text-xs font-semibold text-muted">{L('সেটিংস', 'Settings')}</p>
      <div className="mx-3 overflow-hidden rounded-2xl bg-white">
        {row('book', lang === 'bn' ? 'ভাষা: English' : 'Language: বাংলা', lang === 'bn' ? 'ভাষা: English' : 'Language: বাংলা',
          () => setLang(lang === 'bn' ? 'en' : 'bn'))}
        {row('shield', 'পিন পরিবর্তন', 'Change PIN', () => demo(L('পিন পরিবর্তন', 'Change PIN')))}
        {row('info', 'অনুমতি পরিবর্তন', 'Permissions', () => demo(L('অনুমতি পরিবর্তন', 'Permissions')))}
        {row('chat', '২৪x৭ সেবা', '24x7 support', () => demo(L('২৪x৭ সেবা', '24x7 support')))}
        {row('book', 'শর্তাবলী', 'Terms', () => demo(L('শর্তাবলী', 'Terms')))}
        {row('shield', 'গোপনীয়তা নীতিমালা', 'Privacy policy', () => demo(L('গোপনীয়তা নীতিমালা', 'Privacy policy')))}
      </div>
      <div className="mx-3 mt-4 overflow-hidden rounded-2xl bg-white">
        {row('back', 'লগ আউট', 'Log out', () => { clearSession(); navigate('/welcome', { replace: true }) }, 'text-bad')}
      </div>
      <p className="mt-4 px-4 text-center text-[11px] text-muted">
        <Link to="/impact" className="underline">Impact</Link> · {L('সব তথ্য synthetic', 'All data is synthetic')}
      </p>
      {toast && (
        <div className="fixed bottom-24 left-1/2 z-50 -translate-x-1/2 rounded-full bg-ink px-4 py-2 text-sm text-white">{toast}</div>
      )}
      <Sheet open={users !== null} onClose={() => setUsers(null)} title={L('Demo user বেছে নিন', 'Choose a demo user')}>
        <div className="space-y-2">
          {users?.map((u) => (
            <button key={u.user_id} onClick={() => void switchTo(u)}
              className="flex w-full items-center justify-between rounded-xl border border-line px-3 py-2 text-left">
              <span className="text-sm font-semibold">{u.name}</span>
              <span className="text-xs text-muted">{u.area}</span>
            </button>
          ))}
        </div>
      </Sheet>
    </div>
  )
}
