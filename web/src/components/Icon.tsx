/** Small outline icon set (24×24, stroke-based) so the app has no icon-font dependency. */
const PATHS: Record<string, string> = {
  send: 'M22 2 11 13M22 2l-7 20-4-9-9-4 20-7Z',
  phone: 'M7 2h10a1 1 0 0 1 1 1v18a1 1 0 0 1-1 1H7a1 1 0 0 1-1-1V3a1 1 0 0 1 1-1Zm4 17h2',
  cashout: 'M3 7h18v10H3zM12 9.5a2.5 2.5 0 1 0 0 5 2.5 2.5 0 0 0 0-5ZM6 7V5m12 2V5',
  bill: 'M6 2h12v20l-3-2-3 2-3-2-3 2V2Zm3 6h6m-6 4h6m-6 4h3',
  add: 'M12 5v14M5 12h14M3 3h18v18H3z',
  pig: 'M19 10c0-3.3-3.1-6-7-6S5 6.7 5 10c0 1.7.8 3.3 2.1 4.4L7 18h3l.5-1.5h3L14 18h3l-.1-3.6A6 6 0 0 0 19 10Zm0 0h2m-12-1h.01',
  bank: 'M3 10 12 4l9 6M5 10v8m4-8v8m6-8v8m4-8v8M3 20h18',
  request: 'M4 12a8 8 0 1 0 8-8M4 4v4h4m4 0v8m-3-3 3 3 3-3',
  pay: 'M4 4h6v6H4zM14 4h6v6h-6zM4 14h6v6H4zM14 14h2m4 0v6h-6',
  gift: 'M20 12v9H4v-9M2 7h20v5H2zM12 22V7m0 0H7.5a2.5 2.5 0 1 1 0-5C11 2 12 7 12 7Zm0 0h4.5a2.5 2.5 0 1 0 0-5C13 2 12 7 12 7Z',
  npsb: 'M7 7h13l-4-4m4 4-4 4M17 17H4l4 4m-4-4 4-4',
  grid: 'M4 4h7v7H4zm9 0h7v7h-7zM4 13h7v7H4zm9 0h7v7h-7z',
  home: 'M3 11 12 3l9 8M5 9.5V21h5v-6h4v6h5V9.5',
  wallet: 'M3 7a2 2 0 0 1 2-2h13v4M3 7v11a2 2 0 0 0 2 2h15V9H5a2 2 0 0 1-2-2Zm14 7h.01',
  clock: 'M12 7v5l3 2M21 12a9 9 0 1 1-18 0 9 9 0 0 1 18 0Z',
  spark: 'M12 3v4m0 10v4M3 12h4m10 0h4M6 6l2.5 2.5M15.5 15.5 18 18M6 18l2.5-2.5M15.5 8.5 18 6',
  bell: 'M6 8a6 6 0 1 1 12 0c0 7 3 9 3 9H3s3-2 3-9m4.3 13a2 2 0 0 0 3.4 0',
  menu: 'M4 6h16M4 12h16M4 18h16',
  back: 'M15 18l-6-6 6-6',
  chevron: 'M9 18l6-6-6-6',
  qr: 'M3 3h7v7H3zm11 0h7v7h-7zM3 14h7v7H3zm11 0h3v3h-3zm4 4h3v3h-3zm-4 0h0',
  card: 'M2 6h20v12H2zM2 10h20M6 15h4',
  chart: 'M3 20h18M6 16v-5m5 5V8m5 8v-7m4 7V5',
  calendar: 'M4 5h16v16H4zM4 9h16M9 3v4m6-4v4',
  book: 'M4 19V5a2 2 0 0 1 2-2h14v16H6a2 2 0 0 0-2 2Zm0 0a2 2 0 0 0 2 2h14',
  chat: 'M21 12a8 8 0 0 1-11.6 7.1L4 20l1-4.6A8 8 0 1 1 21 12Z',
  mic: 'M12 3a3 3 0 0 0-3 3v6a3 3 0 0 0 6 0V6a3 3 0 0 0-3-3Zm-7 9a7 7 0 0 0 14 0m-7 7v3',
  shield: 'M12 3 4 6v6c0 5 3.5 8 8 9 4.5-1 8-4 8-9V6l-8-3Z',
  heart: 'M20.8 5.6a5 5 0 0 0-7.1 0L12 7.3l-1.7-1.7a5 5 0 1 0-7.1 7.1L12 21.4l8.8-8.7a5 5 0 0 0 0-7.1Z',
  close: 'M18 6 6 18M6 6l12 12',
  check: 'M5 12l5 5L20 7',
  info: 'M12 16v-5m0-3h.01M21 12a9 9 0 1 1-18 0 9 9 0 0 1 18 0Z',
}

export function Icon({ name, size = 24, className = '', strokeWidth = 1.8 }: {
  name: keyof typeof PATHS | string; size?: number; className?: string; strokeWidth?: number
}) {
  return (
    <svg width={size} height={size} viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth={strokeWidth}
      strokeLinecap="round" strokeLinejoin="round" className={className} aria-hidden="true">
      <path d={PATHS[name] ?? PATHS.info} />
    </svg>
  )
}
