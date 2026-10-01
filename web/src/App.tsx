import type { ReactNode } from 'react'
import { Navigate, Route, Routes } from 'react-router-dom'
import { PrototypeRibbon } from './components/ui'
import { getSession } from './lib/session'
import Login from './pages/auth/Login'
import Register from './pages/auth/Register'
import Splash from './pages/auth/Splash'
import Welcome from './pages/auth/Welcome'

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

export default function App() {
  return (
    <Routes>
      <Route path="/" element={<Frame><Splash /></Frame>} />
      <Route path="/welcome" element={<Frame><Welcome /></Frame>} />
      <Route path="/login" element={<Frame><Login /></Frame>} />
      <Route path="/register" element={<Frame><Register /></Frame>} />
      <Route path="/app/*" element={<RequireSession><Frame><div className="p-6">Hishab</div></Frame></RequireSession>} />
      <Route path="*" element={<Navigate to="/" replace />} />
    </Routes>
  )
}
