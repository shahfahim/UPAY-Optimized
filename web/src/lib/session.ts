/** localStorage access that never throws (private mode, blocked storage). */
export const storage = {
  get(key: string): string | null {
    try {
      return window.localStorage.getItem(key)
    } catch {
      return null
    }
  },
  set(key: string, value: string): void {
    try {
      window.localStorage.setItem(key, value)
    } catch {
      /* ignore */
    }
  },
  remove(key: string): void {
    try {
      window.localStorage.removeItem(key)
    } catch {
      /* ignore */
    }
  },
}

export type Session = { token: string; userId: string }

const KEY = 'hishab.session'

export function getSession(): Session | null {
  const raw = storage.get(KEY)
  if (!raw) return null
  try {
    const s = JSON.parse(raw) as Session
    return s && s.userId ? s : null
  } catch {
    return null
  }
}

export function setSession(s: Session): void {
  storage.set(KEY, JSON.stringify(s))
}

export function clearSession(): void {
  storage.remove(KEY)
}
