import { useState } from 'react'

import { api } from '../api'
import { useAuth } from '../auth'
import { Alert, Badge, Button, Card, Field, PageHeader, StateCenter } from '../components/ui'
import { useAsync } from '../hooks'

export default function Telephony() {
  const { org } = useAuth()
  const { data, loading, error, reload } = useAsync(
    () =>
      Promise.all([api('/telephony/twilio-accounts/'), api('/telephony/phone-numbers/')]).then(
        ([accounts, numbers]) => ({ accounts: accounts.results, numbers: numbers.results }),
      ),
    [org],
  )
  const [accountSid, setAccountSid] = useState('')
  const [authToken, setAuthToken] = useState('')
  const [connecting, setConnecting] = useState(false)
  const [syncing, setSyncing] = useState('')
  const [formError, setFormError] = useState('')

  const accounts = data?.accounts || []
  const numbers = data?.numbers || []

  async function connect(e) {
    e.preventDefault()
    setConnecting(true)
    setFormError('')
    try {
      await api('/telephony/twilio-accounts/', {
        method: 'POST',
        body: { account_sid: accountSid, auth_token: authToken },
      })
      setAccountSid('')
      setAuthToken('')
      await reload()
    } catch (err) {
      setFormError(err.message)
    } finally {
      setConnecting(false)
    }
  }

  async function sync(accountId) {
    setSyncing(accountId)
    setFormError('')
    try {
      await api(`/telephony/twilio-accounts/${accountId}/sync-numbers/`, { method: 'POST' })
      await reload()
    } catch (err) {
      setFormError(err.message)
    } finally {
      setSyncing('')
    }
  }

  return (
    <section>
      <PageHeader title="Telephony" subtitle="Connect your Twilio account and import numbers" />
      <Card title="Connect Twilio account">
        <form onSubmit={connect}>
          <div className="form-grid">
            <Field label="Account SID">
              <input value={accountSid} onChange={(e) => setAccountSid(e.target.value)} required />
            </Field>
            <Field label="Auth token">
              <input
                type="password"
                autoComplete="off"
                value={authToken}
                onChange={(e) => setAuthToken(e.target.value)}
                required
              />
            </Field>
          </div>
          {formError && <Alert error={formError} />}
          <div className="form-actions">
            <Button type="submit" loading={connecting}>
              Connect
            </Button>
          </div>
        </form>
      </Card>

      <h2 className="section-title">Accounts</h2>
      <StateCenter
        loading={loading}
        error={error}
        onRetry={reload}
        empty={
          accounts.length
            ? { show: false }
            : { show: true, title: 'No Twilio account connected', hint: 'Connect your account above to begin.' }
        }
      >
        <div className="table-wrap">
          <table>
            <thead>
              <tr>
                <th>Account SID</th>
                <th>Status</th>
                <th className="text-right">Actions</th>
              </tr>
            </thead>
            <tbody>
              {accounts.map((a) => (
                <tr key={a.id}>
                  <td className="mono">{a.twilio_account_sid}</td>
                  <td>
                    <Badge status={a.status} />
                  </td>
                  <td className="text-right">
                    <Button className="btn-sm" loading={syncing === a.id} onClick={() => sync(a.id)}>
                      Sync numbers
                    </Button>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </StateCenter>

      <h2 className="section-title">Phone numbers</h2>
      <StateCenter
        loading={loading}
        error={error}
        onRetry={reload}
        empty={
          numbers.length
            ? { show: false }
            : { show: true, title: 'No numbers imported', hint: 'Sync numbers from a connected account to use them in campaigns.' }
        }
      >
        <div className="table-wrap">
          <table>
            <thead>
              <tr>
                <th>Number</th>
                <th>Friendly name</th>
              </tr>
            </thead>
            <tbody>
              {numbers.map((n) => (
                <tr key={n.id}>
                  <td className="mono">{n.phone_number}</td>
                  <td className="muted">{n.friendly_name || '—'}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </StateCenter>
    </section>
  )
}