import { BrowserRouter, Navigate, Route, Routes } from 'react-router-dom'

import { AuthProvider, useAuth } from './auth'
import Layout from './components/Layout'
import Agents from './pages/Agents'
import Calls from './pages/Calls'
import Campaigns from './pages/Campaigns'
import CampaignDetail from './pages/CampaignDetail'
import Login from './pages/Login'
import Telephony from './pages/Telephony'

function Router() {
  const { token } = useAuth()
  return (
    <Routes>
      <Route
        path="/login"
        element={token ? <Navigate to="/campaigns" replace /> : <Login />}
      />
      <Route
        element={token ? <Layout /> : <Navigate to="/login" replace />}
      >
        <Route path="/agents" element={<Agents />} />
        <Route path="/campaigns" element={<Campaigns />} />
        <Route path="/campaigns/:id" element={<CampaignDetail />} />
        <Route path="/telephony" element={<Telephony />} />
        <Route path="/calls" element={<Calls />} />
      </Route>
      <Route
        path="*"
        element={<Navigate to={token ? '/campaigns' : '/login'} replace />}
      />
    </Routes>
  )
}

export default function App() {
  return (
    <BrowserRouter>
      <AuthProvider>
        <Router />
      </AuthProvider>
    </BrowserRouter>
  )
}