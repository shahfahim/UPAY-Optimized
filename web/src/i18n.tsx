import { createContext, useCallback, useContext, useEffect, useMemo, useState, type ReactNode } from 'react'
import { fmtDate, fmtNum, fmtTaka, type Lang } from './lib/format'
import { storage } from './lib/session'

type LangCtx = {
  lang: Lang
  setLang: (l: Lang) => void
  /** Pick the string for the current language. */
  L: (bn: string, en: string) => string
  taka: (n: number, opts?: { paisa?: boolean }) => string
  num: (n: number, decimals?: number) => string
  date: (iso: string) => string
}

const Ctx = createContext<LangCtx | null>(null)

export function LangProvider({ children }: { children: ReactNode }) {
  const [lang, setLangState] = useState<Lang>(() => (storage.get('hishab.lang') === 'en' ? 'en' : 'bn'))
  useEffect(() => {
    document.documentElement.lang = lang
  }, [lang])
  const setLang = useCallback((l: Lang) => {
    setLangState(l)
    storage.set('hishab.lang', l)
  }, [])
  const value = useMemo<LangCtx>(() => ({
    lang,
    setLang,
    L: (bn, en) => (lang === 'bn' ? bn : en),
    taka: (n, opts) => fmtTaka(n, lang, opts),
    num: (n, d = 0) => fmtNum(n, lang, d),
    date: (iso) => fmtDate(iso, lang),
  }), [lang, setLang])
  return <Ctx.Provider value={value}>{children}</Ctx.Provider>
}

export function useLang(): LangCtx {
  const v = useContext(Ctx)
  if (!v) throw new Error('useLang outside LangProvider')
  return v
}
