import { useEffect, useState } from 'react'
import { useSearchParams } from 'react-router-dom'

import { api } from '../api'
import { useAuth } from '../auth'
import { Alert, Badge, Button, Card, PageHeader, Spinner, StateCenter } from '../components/ui'
import { useAsync } from '../hooks'

export default function Calls() {
  const { org } = useAuth()
  const [searchParams] = useSearchParams()
  const selected = searchParams.get('call')
  const { data, loading, error, reload } = useAsync(() => api('/calls/').then((d) => d.results), [org])
  const [transcript, setTranscript] = useState(null)
  const [loadingTranscript, setLoadingTranscript] = useState(false)
  const [transcriptError, setTranscriptError] = useState('')

  const calls = data || []

  async function showTranscript(callId) {
    setLoadingTranscript(true)
    setTranscriptError('')
    try {
      const t = await api(`/calls/${callId}/transcript/`)
      setTranscript(t.turns)
    } catch (err) {
      setTranscriptError(err.message)
    } finally {
      setLoadingTranscript(false)
    }
  }

  useEffect(() => {
    if (selected) showTranscript(selected)
  }, [selected])

  return (
    <section>
      <PageHeader title="Calls" subtitle="History and transcripts for this organization" />
      <StateCenter
        loading={loading}
        error={error}
        onRetry={reload}
        empty={
          calls.length
            ? { show: false }
            : { show: true, title: 'No calls yet', hint: 'Start a campaign to begin dialing.' }
        }
      >
        <div className="table-wrap">
          <table>
            <thead>
              <tr>
                <th>Lead</th>
                <th>Status</th>
                <th>Outcome</th>
                <th>Created</th>
                <th className="text-right">Actions</th>
              </tr>
            </thead>
            <tbody>
              {calls.map((c) => (
                <tr key={c.id} className={c.id === selected ? 'row-active' : ''}>
                  <td>{c.lead_name}</td>
                  <td>
                    <Badge status={c.status} />
                  </td>
                  <td className="muted">{c.outcome || '—'}</td>
                  <td className="muted">{new Date(c.created_at).toLocaleString()}</td>
                  <td className="text-right">
                    <Button
                      className="btn-sm"
                      loading={loadingTranscript && selected === c.id}
                      onClick={() => showTranscript(c.id)}
                    >
                      Transcript
                    </Button>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </StateCenter>

      {loadingTranscript && (
        <div className="state-center">
          <Spinner size={20} />
        </div>
      )}
      {transcriptError && <Alert error={transcriptError} onClose={() => setTranscriptError('')} />}
      {transcript && (
        <Card title="Transcript">
          <div className="transcript">
            {transcript.map((turn, i) => (
              <div key={i} className={`turn turn-${turn.role}`}>
                <span className="turn-label">{turn.role === 'agent' ? 'Agent' : 'Lead'}</span>
                <span className="turn-text">
                  {turn.text}
                  {turn.truncated && <span className="muted"> (cut off)</span>}
                </span>
              </div>
            ))}
            {!transcript.length && <p className="muted">No turns recorded.</p>}
          </div>
        </Card>
      )}
    </section>
  )
}