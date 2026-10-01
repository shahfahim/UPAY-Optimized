import { useShell } from '../../components/AppShell'
import { useLang } from '../../i18n'
import Flow from './Flow'

export default function Npsb() {
  const { uid } = useShell()
  const { L } = useLang()
  const contacts = [
    { id: `FAM-${uid}`, name: L('মা (অন্য wallet)', 'Mother (other wallet)'), sub: L('অন্য MFS wallet', 'Other MFS wallet'), destination: 'other_mfs_wallet' },
    { id: 'P-BRO', name: L('ভাই (অন্য wallet)', 'Brother (other wallet)'), sub: L('অন্য MFS wallet', 'Other MFS wallet'), destination: 'other_mfs_wallet' },
    { id: 'BANK-OWN', name: L('নিজের ব্যাংক অ্যাকাউন্ট', 'My bank account'), sub: L('ব্যাংক (demo)', 'Bank (demo)'), destination: 'bank_account' },
  ]
  return <Flow cfg={{ type: 'npsb', titleBn: 'এনপিএসবি', titleEn: 'NPSB transfer', contacts, routed: true }} />
}
