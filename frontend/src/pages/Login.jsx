import { useState } from 'react'

import { useAuth } from '../auth'
import { Alert, Button, Field } from '../components/ui'

export default function Login() {
  const { login, signup } = useAuth()
  const [mode, setMode] = useState('login')
  const [email, setEmail] = useState('')
  const [password, setPassword] = useState('')
  const [orgName, setOrgName] = useState('')
  const [error, setError] = useState('')
  const [busy, setBusy] = useState(false)

  async function submit(e) {
    e.preventDefault()
    setError('')
    setBusy(true)
    try {
      if (mode === 'login') await login(email, password)
      else await signup(email, password, orgName)
    } catch (err) {
      setError(err.message)
    } finally {
      setBusy(false)
    }
  }

  return (
    <div className="auth">
      <div className="auth-card">
        <div className="brand brand-lg">
          <span className="brand-eq" aria-hidden="true">
            <span />
            <span />
            <span />
            <span />
            <span />
          </span>
          Vibeout
        </div>
        <h1>{mode === 'login' ? 'Welcome back' : 'Create your account'}</h1>
        <form onSubmit={submit}>
          <Field label="Email">
            <input type="email" autoComplete="email" value={email} onChange={(e) => setEmail(e.target.value)} required />
          </Field>
          <Field label="Password">
            <input
              type="password"
              autoComplete={mode === 'login' ? 'current-password' : 'new-password'}
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              required
            />
          </Field>
          {mode === 'signup' && (
            <Field label="Organization name">
              <input value={orgName} onChange={(e) => setOrgName(e.target.value)} required />
            </Field>
          )}
          {error && <Alert error={error} />}
          <Button type="submit" className="btn-block" loading={busy}>
            {mode === 'login' ? 'Log in' : 'Create account'}
          </Button>
        </form>
        <button type="button" className="btn btn-ghost btn-block" onClick={() => setMode(mode === 'login' ? 'signup' : 'login')}>
          {mode === 'login' ? 'New here? Create an account' : 'Have an account? Log in'}
        </button>
      </div>
    </div>
  )
}