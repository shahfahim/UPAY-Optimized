export type RiskLevel = 'green' | 'amber' | 'red'

export type DemoUser = { user_id: string; name: string; persona: string; area: string; phone: string }

export type Driver = { feature: string; text_bn: string; text_en: string; impact: number }

export type Forecast = {
  dates: string[]
  p10: number[]
  p50: number[]
  p90: number[]
  shortfall_date: string | null
  shortfall_amount: number
}

export type ActionCard = {
  id: string
  title_bn: string
  title_en: string
  why_bn: string
  why_en: string
  params: Record<string, unknown>
  risk_before: number
  risk_after: number
  fees_saved: number
  score: number
}

export type Indicators = { emergency_days: number; cash_dependency: number; shortfall_free_months: number }

export type Lesson = { id: string; title_bn: string; body_bn: string; action_id: string | null }

export type Milestone = { days: number; reached: boolean; badge_bn: string }

export type LevelStatus = {
  level: number
  name_bn: string
  streak_days: number
  milestones: Milestone[]
  next_level: number | null
  progress: number
  projection_days: number | null
  dps_ready: boolean
  unlocks_bn: string[]
  note_bn: string
}

export type UserPublic = {
  user_id: string
  name: string
  persona: string
  area: string
  phone_masked: string
  avatar_initials: string
}

export type Home = {
  user: UserPublic
  balance: number
  today: string
  insufficient_history: boolean
  forecast: Forecast | null
  risk: { prob: number; level: RiskLevel; drivers: Driver[] } | null
  safe_today: number
  daily_budget: number
  next_income?: string | null
  actions: ActionCard[]
  health: Indicators | null
  health_previous?: Indicators | null
  lesson: Lesson | null
  level: LevelStatus | null
}

export type StripMessage = { priority: number; text_bn: string; text_en: string; link: string }

export type Shortcut = {
  counterparty_id: string
  name: string
  type: string
  category: string
  last_amount: number
  due_in_days: number | null
}

export type Shell = UserPublic & {
  balance: number
  today: string
  insufficient_history: boolean
  nav_badge: { level: RiskLevel; days_left: number | null } | null
  strip: StripMessage[]
  safe_today: number
  daily_budget: number
  recent: Shortcut[]
  unread: number
}

export type Notification = {
  id: string
  type: string
  created: string
  text_bn: string
  text_en: string
  ai: boolean
  link: string
  read?: boolean
}

export type Simulation = {
  action_id: string
  forecast: Forecast
  risk: { prob: number; level: RiskLevel }
}

export type Habit = { id: string; text_bn: string; text_en: string; taka_impact: number }

export type HealthReport = {
  insufficient_history: boolean
  current?: Indicators
  previous?: Indicators
  trend6?: Indicators[]
  habits?: Habit[]
  monthly_report?: { went_well_bn: string; change_bn: string; fees_saved: number; shortfall_avoided: boolean }
}

export type Signal = { id: string; name_bn: string; state: RiskLevel; reason_bn: string; improve_bn: string | null }
export type Readiness = { signals: Signal[]; disclaimer_bn: string }

export type CalendarDay = {
  date: string
  out_total: number
  in_total: number
  events: string[]
  predicted: boolean
  risk: RiskLevel | null
}
export type Calendar = { month: string; today: string; days: CalendarDay[] }


export type Pocket = {
  name: string
  name_bn: string
  balance: number
  goal: { target: number; months?: number; date?: string } | null
  progress: number | null
}

export type EidPlan = {
  eid_name: string
  eid_name_bn: string
  eid_date: string
  days_left: number
  last_eid_spend: number
  expected_bonus: number
  need: number
  weekly: number
  pocket_balance: number
}

export type Dps = { monthly: number; tenure_months: number; day: number; opened: string; simulated?: boolean }

export type Savings = {
  pockets: Pocket[]
  paisa: { on: boolean; paused: boolean; total: number }
  total: number
  eid_plan: EidPlan
  dps: Dps | null
  balance: number
}

export type GoalPlan = {
  target: number
  months: number
  monthly: number
  feasibility: number
  enabling_actions: string[]
  insufficient_history: boolean
}

export type DpsAdvice = {
  status: 'ok' | 'not_now'
  safe_monthly: number | null
  day: number | null
  tenure_months: number | null
  maturity_estimate: number | null
  reason_bn: string
  options?: number[]
  naive_monthly?: number
}

export type EmergencyOption = {
  kind: 'emergency_pocket' | 'pocket' | 'dps_loan'
  pocket: string | null
  available: number
  tradeoff_bn: string
  affordability_bn: string | null
}
export type EmergencyResult = { amount: number; options: EmergencyOption[]; note_bn: string }

export type CategoryOption = { category: string; category_bn: string; confidence: number }

export type Route = { nodes: string[]; fee: number; minutes: number; label_bn: string }
export type CostlyHabit = {
  kind: string
  monthly_count: number
  avg_amount: number
  current_fee: number
  best_fee: number
  annual_saving: number
  best_route: string[]
}
export type RouteResult = { routes: Route[]; habits: CostlyHabit[]; fees_placeholder: boolean }

export type SendType = 'send_money' | 'cash_out' | 'merchant_pay' | 'bill_pay' | 'mobile_recharge' | 'npsb' | 'fund_transfer'
export type SendResult = {
  balance: number
  swept: number
  fee: number
  category: string
  nudge: { text_bn: string; saving_year: number; link: string } | null
}

export type ChatAnswer = {
  text: string
  used_tools: { name: string; result: unknown }[]
  numbers_source: string
  ai: boolean
}

export type ImpactPair = { baseline: number; with_hishab: number }
export type Impact = {
  headline: Record<string, ImpactPair>
  per_100k: Record<string, number | string>
  active_rate: ImpactPair
  user_months: number
  acceptance_mean: number
  bandit_curve: { day: number[]; bandit: number[]; static: number[]; random: number[] }
  lesson_curve: { day: number[]; bandit: number[]; static: number[]; random: number[] }
  fairness: {
    rows: { group_type: string; group: string; metric: string; value: number; n: number }[]
    flags: { group_type: string; metric: string; gap: number; note: string }[]
  }
  readiness_distribution: { group_type: string; group: string; signal: string; green_share: number; n: number }[]
  models: Record<string, Record<string, number | string | null>>
  assumptions_note: string
}

export type TxItem = {
  ts: string; type: string; name: string; amount: number; direction: number; fee: number
  category: string; category_bn: string; balance_after: number
}
export type TxList = {
  items: TxItem[]
  summary: { income_total: number; spend_total: number; cash_out_count: number; cash_out_fees: number
    by_category: { category: string; category_bn: string; amount: number }[] }
}

export type NearbyAgent = {
  id: string
  name: string
  lat: number
  lng: number
  distance_m: number
  cash_hint: number // fixed sample value, not a prediction
  cash_status: RiskLevel
  is_demo: boolean
}
