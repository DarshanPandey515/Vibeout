import { useState } from 'react'
import { Link } from 'react-router-dom'

import { api } from '../api'
import { useAuth } from '../auth'
import { Alert, Badge, Button, Card, Field, PageHeader, StateCenter } from '../components/ui'
import { useAsync } from '../hooks'

export default function Campaigns() {
  const { org } = useAuth()
  const { data, loading, reload } = useAsync(
    () =>
      Promise.allSettled([
        api('/campaigns/').then((r) => r.results),
        api('/agents/').then((r) => r.results),
        api('/telephony/phone-numbers/').then((r) => r.results),
      ]).then(([campaigns, agents, numbers]) => ({
        campaigns: campaigns.status === 'fulfilled' ? campaigns.value : [],
        agents: agents.status === 'fulfilled' ? agents.value : [],
        numbers: numbers.status === 'fulfilled' ? numbers.value : [],
        campaignsError: campaigns.status === 'rejected' ? campaigns.reason.message : '',
      })),
    [org],
  )
  const [name, setName] = useState('')
  const [agentId, setAgentId] = useState('')
  const [numberId, setNumberId] = useState('')
  const [saving, setSaving] = useState(false)
  const [formError, setFormError] = useState('')

  const campaigns = data?.campaigns || []
  const agents = data?.agents || []
  const numbers = data?.numbers || []
  const tableError = data?.campaignsError || ''
  const noNumbers = !numbers.length
  const noAgents = !agents.length

  async function create(e) {
    e.preventDefault()
    setSaving(true)
    setFormError('')
    try {
      await api('/campaigns/', {
        method: 'POST',
        body: { name, agent: agentId, caller_number: numberId },
      })
      setName('')
      setAgentId('')
      setNumberId('')
      await reload()
    } catch (err) {
      setFormError(err.message)
    } finally {
      setSaving(false)
    }
  }

  return (
    <section>
      <PageHeader title="Campaigns" subtitle="Group leads, pick a caller number, and run outbound calls" />
      <Card title="New campaign">
        <form onSubmit={create}>
          <div className="form-grid">
            <Field label="Name">
              <input value={name} onChange={(e) => setName(e.target.value)} required />
            </Field>
            <Field label="Agent">
              <select value={agentId} onChange={(e) => setAgentId(e.target.value)} required>
                <option value="">Select…</option>
                {agents.map((a) => (
                  <option key={a.id} value={a.id}>
                    {a.name}
                  </option>
                ))}
              </select>
            </Field>
            <Field label="Caller number">
              <select value={numberId} onChange={(e) => setNumberId(e.target.value)} required>
                <option value="">Select…</option>
                {numbers.map((n) => (
                  <option key={n.id} value={n.id}>
                    {n.phone_number}
                  </option>
                ))}
              </select>
            </Field>
          </div>
          {!loading && noAgents && <Alert error="No agents yet — create one on the Agents page first." />}
          {!loading && noNumbers && <Alert error="No caller numbers — connect Twilio and sync numbers on the Telephony page first." />}
          {formError && <Alert error={formError} />}
          <div className="form-actions">
            <Button type="submit" loading={saving} disabled={!loading && (noAgents || noNumbers)}>
              Create campaign
            </Button>
          </div>
        </form>
      </Card>
      <StateCenter
        loading={loading}
        error={tableError}
        onRetry={reload}
        empty={
          campaigns.length
            ? { show: false }
            : { show: true, title: 'No campaigns yet', hint: 'Create a campaign to upload leads and start calling.' }
        }
      >
        <div className="table-wrap">
          <table>
            <thead>
              <tr>
                <th>Name</th>
                <th>Status</th>
                <th>Created</th>
              </tr>
            </thead>
            <tbody>
              {campaigns.map((c) => (
                <tr key={c.id}>
                  <td>
                    <Link className="link" to={`/campaigns/${c.id}`}>
                      {c.name}
                    </Link>
                  </td>
                  <td>
                    <Badge status={c.status} />
                  </td>
                  <td className="muted">{new Date(c.created_at).toLocaleString()}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </StateCenter>
    </section>
  )
}