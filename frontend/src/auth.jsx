import { createContext, useCallback, useContext, useEffect, useState } from 'react'

import { api, clearSession, getSession, setSession } from './api'

const AuthContext = createContext(null)

export function AuthProvider({ children }) {
  const [token, setToken] = useState(getSession().token || null)
  const [orgs, setOrgs] = useState([])
  const [org, setOrg] = useState(getSession().orgId || null)
  const [ready, setReady] = useState(Boolean(getSession().token))

  const refreshOrgs = useCallback(async () => {
    const data = await api('/organizations/me/')
    setOrgs(data)
    const current = getSession().orgId
    if (!data.some((o) => o.id === current)) {
      const next = data[0]
      if (next) {
        setOrg(next.id)
        setSession({ orgId: next.id })
      }
    }
  }, [])

  useEffect(() => {
    if (token) refreshOrgs().catch(() => logout())
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [token])

  async function login(email, password) {
    const { token: newToken } = await api('/auth/login', {
      method: 'POST',
      body: { username: email, password },
    })
    setSession({ token: newToken })
    setToken(newToken)
    await refreshOrgs()
  }

  async function signup(email, password, orgName) {
    const data = await api('/auth/signup', {
      method: 'POST',
      body: { email, password, org_name: orgName },
    })
    setSession({ token: data.token, orgId: data.organization_id })
    setToken(data.token)
    setOrg(data.organization_id)
    setOrgs([{ id: data.organization_id, name: orgName, role: 'owner' }])
  }

  function logout() {
    clearSession()
    setToken(null)
    setOrg(null)
    setOrgs([])
    setReady(false)
  }

  function switchOrg(orgId) {
    setSession({ orgId })
    setOrg(orgId)
  }

  const value = { token, orgs, org, ready, login, signup, logout, switchOrg }
  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>
}

export function useAuth() {
  return useContext(AuthContext)
}