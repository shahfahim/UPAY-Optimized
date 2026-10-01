import type { ReactNode } from 'react'
import { Navigate, Route, Routes } from 'react-router-dom'
import AppShell from './components/AppShell'
import { PrototypeRibbon } from './components/ui'
import { getSession } from './lib/session'
import Account from './pages/Account'
import Login from './pages/auth/Login'
import Register from './pages/auth/Register'
import Splash from './pages/auth/Splash'
import Welcome from './pages/auth/Welcome'
import History from './pages/History'
import Home from './pages/Home'
import More from './pages/More'
import Notifications from './pages/Notifications'
import Payments from './pages/Payments'
import Health from './pages/Health'
import Budget from './pages/hub/Budget'
import Calendar from './pages/hub/Calendar'
import HubLayout from './pages/hub/HubLayout'
import Learn from './pages/hub/Learn'
import Overview from './pages/hub/Overview'
import Dps from './pages/savings/Dps'
import Emergency from './pages/savings/Emergency'
import Levels from './pages/savings/Levels'
import Pockets from './pages/savings/Pockets'
import SavingsHome from './pages/savings/SavingsHome'

function RequireSession({ children }: { children: ReactNode }) {
  return getSession() ? <>{children}</> : <Navigate to="/login" replace />
}

function Frame({ children }: { children: ReactNode }) {
  return (
    <div className="app-frame">
      <PrototypeRibbon />
      {children}
    </div>
  )
}

function Soon() {
  return <p className="m-6 rounded-2xl bg-white p-6 text-center text-sm text-muted">…</p>
}

export default function App() {
  return (
    <Routes>
      <Route path="/" element={<Frame><Splash /></Frame>} />
      <Route path="/welcome" element={<Frame><Welcome /></Frame>} />
      <Route path="/login" element={<Frame><Login /></Frame>} />
      <Route path="/register" element={<Frame><Register /></Frame>} />
      <Route path="/app" element={<RequireSession><AppShell /></RequireSession>}>
        <Route index element={<Navigate to="home" replace />} />
        <Route path="home" element={<Home />} />
        <Route path="account" element={<Account />} />
        <Route path="history" element={<History />} />
        <Route path="notifications" element={<Notifications />} />
        <Route path="more" element={<More />} />
        <Route path="payments" element={<Payments />} />
        <Route path="hishab" element={<HubLayout />}>
          <Route index element={<Overview />} />
          <Route path="budget" element={<Budget />} />
          <Route path="calendar" element={<Calendar />} />
          <Route path="learn" element={<Learn />} />
          <Route path="ask" element={<Soon />} />
        </Route>
        <Route path="hishab/health" element={<Health />} />
        <Route path="savings" element={<SavingsHome />} />
        <Route path="savings/pockets" element={<Pockets />} />
        <Route path="savings/levels" element={<Levels />} />
        <Route path="savings/emergency" element={<Emergency />} />
        <Route path="savings/dps" element={<Dps />} />
        <Route path="*" element={<Soon />} />
      </Route>
      <Route path="*" element={<Navigate to="/" replace />} />
    </Routes>
  )
}
