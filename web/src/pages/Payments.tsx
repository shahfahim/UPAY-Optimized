import { useNavigate } from 'react-router-dom'
import { useShell } from '../components/AppShell'
import { Icon } from '../components/Icon'
import { useLang } from '../i18n'
import { PageTitle } from './common'

const ITEMS = [
  { bn: 'ট্রাফিক ফাইন', en: 'Traffic fine', icon: 'shield' },
  { bn: 'টোল পেমেন্ট', en: 'Toll payment', icon: 'card' },
  { bn: 'সরকারি পেমেন্ট', en: 'Government payment', icon: 'bank' },
  { bn: 'এডুকেশন', en: 'Education', icon: 'book', to: '/app/pay?type=bill_pay&cp=BILL-edu&name=%E0%A6%B6%E0%A6%BF%E0%A6%95%E0%A7%8D%E0%A6%B7%E0%A6%BE%20%E0%A6%AA%E0%A7%8D%E0%A6%B0%E0%A6%A4%E0%A6%BF%E0%A6%B7%E0%A7%8D%E0%A6%A0%E0%A6%BE%E0%A6%A8' },
  { bn: 'এন জি ও', en: 'NGO', icon: 'heart' },
  { bn: 'বীমা', en: 'Insurance', icon: 'shield' },
  { bn: 'ডোনেশন', en: 'Donation', icon: 'gift' },
  { bn: 'যাকাত পেমেন্ট', en: 'Zakat', icon: 'heart' },
  { bn: 'টিকেট', en: 'Tickets', icon: 'card' },
  { bn: 'জিপি ফ্লেক্সিপ্ল্যান', en: 'GP Flexiplan', icon: 'phone', to: '/app/pay?type=mobile_recharge' },
  { bn: 'হোটেল', en: 'Hotel', icon: 'home' },
  { bn: 'আবেদন ফি', en: 'Application fee', icon: 'bill' },
  { bn: 'Othoba', en: 'Othoba', icon: 'grid' },
  { bn: 'মেট্রোরেল', en: 'Metro rail', icon: 'card' },
  { bn: 'বিদ্যুৎ বিল', en: 'Electricity bill', icon: 'bill', to: '/app/pay?type=bill_pay&cp=BILL-electric&name=%E0%A6%AC%E0%A6%BF%E0%A6%A6%E0%A7%8D%E0%A6%AF%E0%A7%81%E0%A7%8E%20%E0%A6%AC%E0%A6%BF%E0%A6%B2' },
  { bn: 'দোকানে পেমেন্ট', en: 'Pay a shop', icon: 'pay', to: '/app/pay?type=merchant_pay' },
]

export default function Payments() {
  const { L } = useLang()
  const { demo } = useShell()
  const navigate = useNavigate()
  return (
    <div>
      <PageTitle bn="উপায় পেমেন্ট" en="upay Payment" />
      <div className="mx-3 grid grid-cols-4 gap-y-4 rounded-2xl bg-white px-1 py-4">
        {ITEMS.map((i) => (
          <button key={i.bn} onClick={() => (i.to ? navigate(i.to) : demo(L(i.bn, i.en)))} className="flex flex-col items-center gap-1.5 px-1">
            <span className="flex size-12 items-center justify-center rounded-2xl bg-upay-blue/8 text-upay-blue"><Icon name={i.icon} /></span>
            <span className="text-center text-[12px] font-semibold leading-tight">{L(i.bn, i.en)}</span>
          </button>
        ))}
      </div>
    </div>
  )
}
