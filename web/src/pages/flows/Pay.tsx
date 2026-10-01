import { useSearchParams } from 'react-router-dom'
import type { SendType } from '../../api/types'
import { useShell } from '../../components/AppShell'
import { useLang } from '../../i18n'
import Flow, { type Contact } from './Flow'

const TYPES = ['merchant_pay', 'bill_pay', 'mobile_recharge'] as const
type PayType = (typeof TYPES)[number]

export default function Pay() {
  const [params] = useSearchParams()
  const { shell } = useShell()
  const { L } = useLang()
  const raw = params.get('type')
  const type: PayType = (TYPES as readonly string[]).includes(raw ?? '') ? (raw as PayType) : 'merchant_pay'
  const recent: Contact[] = (shell?.recent ?? []).filter((r) => r.type === type).map((r) => ({ id: r.counterparty_id, name: r.name }))
  const fixed: Record<PayType, Contact[]> = {
    merchant_pay: [{ id: 'M-001', name: L('মুদি দোকান (demo)', 'Grocery shop (demo)') }],
    bill_pay: [
      { id: 'BILL-electric', name: L('বিদ্যুৎ বিল', 'Electricity bill') },
      { id: 'BILL-gas', name: L('গ্যাস বিল', 'Gas bill') },
      { id: 'BILL-water', name: L('পানির বিল', 'Water bill') },
      { id: 'BILL-edu', name: L('শিক্ষা প্রতিষ্ঠান', 'School fees') },
    ],
    mobile_recharge: [{ id: 'BILL-recharge', name: L('নিজের নম্বর', 'My number'), sub: shell?.phone_masked }],
  }
  const seen = new Set(recent.map((c) => c.id))
  const contacts = [...recent, ...fixed[type].filter((c) => !seen.has(c.id))]
  const titles: Record<PayType, [string, string]> = {
    merchant_pay: ['মেক পেমেন্ট', 'Make payment'], bill_pay: ['পে বিল', 'Pay bill'], mobile_recharge: ['মোবাইল রিচার্জ', 'Mobile recharge'],
  }
  return (
    <Flow key={type} cfg={{ type: type as SendType, titleBn: titles[type][0], titleEn: titles[type][1], contacts,
      freeRecipient: type === 'mobile_recharge' }} />
  )
}
