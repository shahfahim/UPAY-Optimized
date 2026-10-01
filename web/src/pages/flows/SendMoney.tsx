import { useShell } from '../../components/AppShell'
import { useLang } from '../../i18n'
import Flow, { type Contact } from './Flow'

export default function SendMoney() {
  const { uid, shell } = useShell()
  const { L } = useLang()
  const recent: Contact[] = (shell?.recent ?? []).filter((r) => r.type === 'send_money')
    .map((r) => ({ id: r.counterparty_id, name: r.name, sub: L('upay wallet', 'upay wallet'), destination: 'upay_wallet' }))
  const contacts: Contact[] = [
    ...recent,
    { id: `FAM-${uid}`, name: L('মা (অন্য wallet)', 'Mother (other wallet)'), sub: L('অন্য MFS wallet — NPSB দিয়ে যাবে', 'Other MFS wallet — goes via NPSB'), destination: 'other_mfs_wallet' },
    { id: 'P-FRIEND', name: L('সহকর্মী (upay)', 'Co-worker (upay)'), sub: 'upay wallet', destination: 'upay_wallet' },
  ]
  return <Flow cfg={{ type: 'send_money', titleBn: 'সেন্ড মানি', titleEn: 'Send money', contacts, routed: true, freeRecipient: true }} />
}
