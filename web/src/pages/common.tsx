import type { ReactNode } from 'react'
import { useNavigate } from 'react-router-dom'
import { Icon } from '../components/Icon'
import { useLang } from '../i18n'

export function PageTitle({ bn, en, right, back = true }: { bn: string; en: string; right?: ReactNode; back?: boolean }) {
  const { L } = useLang()
  const navigate = useNavigate()
  return (
    <div className="flex items-center gap-2 px-3 pb-2 pt-3">
      {back && (
        <button onClick={() => navigate(-1)} aria-label={L('ফিরে যান', 'Back')} className="rounded-full p-1 hover:bg-white">
          <Icon name="back" />
        </button>
      )}
      <h1 className="flex-1 text-lg font-bold">{L(bn, en)}</h1>
      {right}
    </div>
  )
}

export function InsufficientHistory() {
  const { L } = useLang()
  return (
    <div className="m-4 rounded-2xl bg-white p-6 text-center">
      <p className="text-3xl" aria-hidden="true">⏳</p>
      <p className="mt-2 font-semibold">{L('আরও কিছু দিনের লেনদেন লাগবে', 'A few more days of activity needed')}</p>
      <p className="mt-1 text-sm text-muted">
        {L('৩০ দিনের লেনদেন হলে হিসাব তোমার জন্য পূর্বাভাস আর পরামর্শ দেখাবে।',
          'After 30 days of activity, Hishab shows your forecast and tips.')}
      </p>
    </div>
  )
}
