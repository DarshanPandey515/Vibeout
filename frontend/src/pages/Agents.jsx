import { useState } from 'react'

import { api } from '../api'
import { useAuth } from '../auth'
import { Alert, Badge, Button, Card, Field, PageHeader, StateCenter } from '../components/ui'
import { useAsync } from '../hooks'

export default function Agents() {
  const { org } = useAuth()
  const { data, loading, error, reload } = useAsync(
    () => api('/agents/').then((d) => d.results),
    [org],
  )
  const [name, setName] = useState('')
  const [objective, setObjective] = useState('')
  const [prompt, setPrompt] = useState('')
  const [saving, setSaving] = useState(false)
  const [formError, setFormError] = useState('')
  const agents = data || []

  async function create(e) {
    e.preventDefault()
    setSaving(true)
    setFormError('')
    try {
      await api('/agents/', {
        method: 'POST',
        body: { name, objective_template: objective, system_prompt_template: prompt },
      })
      setName('')
      setObjective('')
      setPrompt('')
      await reload()
    } catch (err) {
      setFormError(err.message)
    } finally {
      setSaving(false)
    }
  }

  return (
    <section>
      <PageHeader title="Agents" subtitle="Conversation personas reused across campaigns" />
      <div className="grid-2">
        <Card title="New agent">
          <form onSubmit={create}>
            <Field label="Name">
              <input value={name} onChange={(e) => setName(e.target.value)} required />
            </Field>
            <Field label="Objective">
              <input value={objective} onChange={(e) => setObjective(e.target.value)} required />
            </Field>
            <Field label="System prompt">
              <textarea value={prompt} onChange={(e) => setPrompt(e.target.value)} required />
            </Field>
            {formError && <Alert error={formError} />}
            <div className="form-actions">
              <Button type="submit" loading={saving}>
                Create agent
              </Button>
            </div>
          </form>
        </Card>
        <div>
          <StateCenter
            loading={loading}
            error={error}
            onRetry={reload}
            empty={
              agents.length
                ? { show: false }
                : { show: true, title: 'No agents yet', hint: 'Create your first agent to start a campaign.' }
            }
          >
            <div className="table-wrap">
              <table>
                <thead>
                  <tr>
                    <th>Name</th>
                    <th>Objective</th>
                    <th>Status</th>
                  </tr>
                </thead>
                <tbody>
                  {agents.map((a) => (
                    <tr key={a.id}>
                      <td>{a.name}</td>
                      <td className="muted">{a.objective_template}</td>
                      <td>
                        <Badge status={a.is_active ? 'active' : 'inactive'} />
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </StateCenter>
        </div>
      </div>
    </section>
  )
}