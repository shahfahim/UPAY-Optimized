import type {
  ActionCard, Budget, Calendar, CategoryOption, ChatAnswer, DemoUser, DpsAdvice, EmergencyResult, GoalPlan,
  HealthReport, Home, Impact, Lesson, LevelStatus, Notification, Readiness, RouteResult, SendResult, SendType,
  Savings, Shell, Simulation, TxList,
} from './types'
import { clearSession, getSession } from '../lib/session'

export class ApiError extends Error {
  status: number
  constructor(status: number, message: string) {
    super(message)
    this.status = status
  }
}

async function req<T>(method: string, path: string, body?: unknown): Promise<T> {
  const headers: Record<string, string> = {}
  if (body !== undefined) headers['Content-Type'] = 'application/json'
  const token = getSession()?.token
  if (token) headers.Authorization = `Bearer ${token}`
  let res: Response
  try {
    res = await fetch(`/api${path}`, {
      method,
      headers,
      body: body === undefined ? undefined : JSON.stringify(body),
    })
  } catch {
    throw new ApiError(0, 'সংযোগ পাওয়া যাচ্ছে না। আবার চেষ্টা করুন।')
  }
  const text = await res.text()
  const data = text ? JSON.parse(text) : null
  if ((res.status === 401 || res.status === 403) && !path.startsWith('/auth/')) {
    clearSession() // expired (server restarted) or someone else's account: log in again
    window.location.assign('/login')
  }
  if (!res.ok) {
    const detail = data && typeof data.detail === 'string' ? data.detail : 'কিছু একটা ভুল হয়েছে'
    throw new ApiError(res.status, detail)
  }
  return data as T
}

const u = (uid: string) => `/users/${encodeURIComponent(uid)}`

export const api = {
  users: () => req<DemoUser[]>('GET', '/users'),
  login: (mobile: string, pin: string) => req<{ token: string; user_id: string }>('POST', '/auth/login', { mobile, pin }),
  registerStart: (mobile: string) => req<{ otp: string; demo: boolean }>('POST', '/auth/register/start', { mobile }),
  registerVerify: (mobile: string, otp: string, name: string, pin: string) =>
    req<{ token: string; user_id: string }>('POST', '/auth/register/verify', { mobile, otp, name, pin }),

  shell: (uid: string) => req<Shell>('GET', `${u(uid)}/shell`),
  home: (uid: string) => req<Home>('GET', `${u(uid)}/home`),
  notifications: (uid: string) => req<Notification[]>('GET', `${u(uid)}/notifications`),
  simulate: (uid: string, actionId: string) => req<Simulation>('POST', `${u(uid)}/actions/simulate`, { action_id: actionId }),
  respond: (uid: string, actionId: string, accepted: boolean) =>
    req<{ ok: boolean }>('POST', `${u(uid)}/actions/${encodeURIComponent(actionId)}/respond`, { accepted }),

  health: (uid: string) => req<HealthReport>('GET', `${u(uid)}/health`),
  lessons: (uid: string) => req<Lesson[]>('GET', `${u(uid)}/lessons`),
  lessonRespond: (uid: string, id: string, accepted: boolean) =>
    req<{ ok: boolean }>('POST', `${u(uid)}/lessons/${encodeURIComponent(id)}/respond`, { accepted }),
  readiness: (uid: string) => req<Readiness>('GET', `${u(uid)}/readiness`),
  levels: (uid: string) => req<LevelStatus>('GET', `${u(uid)}/levels`),
  calendar: (uid: string, month: string) => req<Calendar>('GET', `${u(uid)}/calendar?month=${month}`),

  savings: (uid: string) => req<Savings>('GET', `${u(uid)}/savings`),
  movePocket: (uid: string, pocket: string, direction: 'in' | 'out', amount: number) =>
    req<Savings>('POST', `${u(uid)}/savings/pockets/${pocket}/move`, { direction, amount }),
  setPaisa: (uid: string, on: boolean) => req<Savings>('PUT', `${u(uid)}/savings/paisa`, { on }),
  planGoal: (uid: string, target: number, months: number, pocket?: string) =>
    req<GoalPlan>('POST', `${u(uid)}/goals/plan`, { target, months, pocket }),
  dpsAdvice: (uid: string, goalTarget?: number) => req<DpsAdvice>('POST', `${u(uid)}/dps/advice`, { goal_target: goalTarget ?? null }),
  dpsOpen: (uid: string, monthly: number, tenure: number) =>
    req<{ ok: boolean }>('POST', `${u(uid)}/dps/open`, { monthly, tenure_months: tenure }),
  emergency: (uid: string, amount: number) => req<EmergencyResult>('POST', `${u(uid)}/emergency/options`, { amount }),

  categorySuggest: (uid: string, counterpartyId: string | null, counterpartyType: string, amount: number) =>
    req<CategoryOption[]>('POST', `${u(uid)}/category/suggest`,
      { counterparty_id: counterpartyId, counterparty_type: counterpartyType, amount }),
  categoryConfirm: (uid: string, counterpartyId: string, category: string) =>
    req<{ ok: boolean }>('POST', `${u(uid)}/category/confirm`, { counterparty_id: counterpartyId, category }),
  route: (uid: string, amount: number, destination: string) =>
    req<RouteResult>('POST', `${u(uid)}/route`, { amount, destination }),
  send: (uid: string, body: { type: SendType; amount: number; counterparty_id?: string; counterparty_name?: string;
    destination?: string; category?: string; route?: string[] }) => req<SendResult>('POST', `${u(uid)}/send`, body),

  transactions: (uid: string, limit = 60) => req<TxList>('GET', `${u(uid)}/transactions?limit=${limit}`),
  chat: (uid: string, message: string) => req<ChatAnswer>('POST', `${u(uid)}/chat`, { message }),
  impact: () => req<Impact>('GET', '/impact'),
  timeTravel: (days: 7 | 14 | 30) => req<{ today: string }>('POST', '/demo/time-travel', { days }),
  reset: () => req<{ ok: boolean }>('POST', '/demo/reset'),
}

export type { ActionCard }
