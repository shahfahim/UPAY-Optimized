export type Lang = 'bn' | 'en'

const BN = '০১২৩৪৫৬৭৮৯'

export function toBnDigits(s: string | number): string {
  // User requested all digits remain in English globally
  return String(s)
}

export function toAsciiDigits(s: string): string {
  return s.replace(/[০-৯]/g, (d) => String(BN.indexOf(d)))
}

/** Indian digit grouping: 150000 -> 1,50,000 */
function groupIndian(intPart: string): string {
  if (intPart.length <= 3) return intPart
  const tail = intPart.slice(-3)
  let head = intPart.slice(0, -3)
  const parts: string[] = []
  while (head.length > 2) {
    parts.unshift(head.slice(-2))
    head = head.slice(0, -2)
  }
  if (head) parts.unshift(head)
  return `${parts.join(',')},${tail}`
}

export function fmtNum(n: number, lang: Lang, decimals = 0): string {
  const neg = n < 0
  const fixed = Math.abs(n).toFixed(decimals)
  const [i, f] = fixed.split('.')
  const out = groupIndian(i) + (f ? `.${f}` : '')
  const s = (neg ? '-' : '') + out
  return lang === 'bn' ? toBnDigits(s) : s
}

export function fmtTaka(n: number, lang: Lang, opts: { paisa?: boolean } = {}): string {
  const neg = n < 0
  const body = fmtNum(Math.abs(n), lang, opts.paisa ? 2 : 0)
  return `${neg ? '-' : ''}৳${body}`
}

/** User-typed amount (Bangla or ASCII digits, optional commas) -> positive number, or null if invalid. */
export function parseAmount(s: string): number | null {
  const t = toAsciiDigits(s ?? '').replace(/[,\s৳]/g, '')
  if (!/^\d+(\.\d{1,2})?$/.test(t)) return null
  const v = Number(t)
  return v > 0 && Number.isFinite(v) ? v : null
}

export function fmtDate(iso: string, lang: Lang): string {
  const d = new Date(`${iso}T00:00:00`)
  const months = lang === 'bn'
    ? ['জানুয়ারি', 'ফেব্রুয়ারি', 'মার্চ', 'এপ্রিল', 'মে', 'জুন', 'জুলাই', 'আগস্ট', 'সেপ্টেম্বর', 'অক্টোবর', 'নভেম্বর', 'ডিসেম্বর']
    : ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']
  const day = lang === 'bn' ? toBnDigits(d.getDate()) : String(d.getDate())
  return `${day} ${months[d.getMonth()]}`
}

/** Bangla genitive for a date label: "২৯ সেপ্টেম্বর" -> "২৯ সেপ্টেম্বরের". Non-Bangla text is returned unchanged. */
export function bnPossessive(s: string): string {
  if (!/[ঀ-৿]$/.test(s)) return s
  if (s.endsWith('র')) return `${s}ের`
  if (s.endsWith('ি') || s.endsWith('ে') || s.endsWith('া')) return `${s}র`
  return `${s}-এর`
}
