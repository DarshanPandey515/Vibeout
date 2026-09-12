import { useState } from 'react'
import { Link, useParams } from 'react-router-dom'

import { api } from '../api'
import { useAuth } from '../auth'
import { Alert, Badge, Button, Card, EmptyState, PageHeader, Spinner } from '../components/ui'
import { useAsync } from '../hooks'

function ContextView({ context, onClose }) {
  const sections = [
    ['Source facts', context.source_facts],
    ['Extracted facts', context.extracted_facts],
    ['Allowed claims', context.allowed_claims],
    ['Unknowns', context.unknowns],
    ['Prohibited assumptions', context.prohibited_assumptions],
    ['Opening guidance', context.opening_guidance],
    ['Qualification guidance', context.qualification_guidance],
    ['Agent notes', context.agent_notes],
  ]
  return (
    <div className="drawer">
      <div className="drawer-header">
        <h2>Generated context</h2>
        <button type="button" className="btn btn-ghost" onClick={onClose}>
          Close
        </button>
      </div>
      {sections.map(([label, value]) => {
        if (Array.isArray(value)) {
          return (
            <div key={label} className="ctx-section">
              <h3>{label}</h3>
              {value.length ? (
                <ul className="ctx-list">
                  {value.map((item, i) => (
                    <li key={i}>{item}</li>
                  ))}
                </ul>
              ) : (
                <p className="muted">—</p>
              )}
            </div>
          )
        }
        if (!value) return null
        return (
          <div key={label} className="ctx-section">
            <h3>{label}</h3>
            <p>{value}</p>
          </div>
        )
      })}
    </div>
  )
}

export default function CampaignDetail() {
  const { id } = useParams()
  const { org } = useAuth()
  const { data, loading, error, reload } = useAsync(
    () =>
      Promise.all([
        api(`/campaigns/${id}/`),
        api(`/campaigns/${id}/leads`),
        api(`/calls/?campaign=${id}`),
      ]).then(([campaign, leads, calls]) => ({ campaign, leads, calls: calls.results })),
    [org, id],
  )
  const [file, setFile] = useState(null)
  const [busy, setBusy] = useState('')
  const [pageError, setPageError] = useState('')
  const [leadDetail, setLeadDetail] = useState(null)
  const [reviewing, setReviewing] = useState('')

  const campaign = data?.campaign
  const leads = data?.leads || []
  const calls = data?.calls || []

  async function upload() {
    if (!file) return
    setBusy('upload')
    setPageError('')
    try {
      const { upload_url, lead_import_id } = await api(`/campaigns/${id}/leads/upload`, {
        method: 'POST',
        body: {
          filename: file.name,
          content_type: file.type || 'text/csv',
          size_bytes: file.size,
        },
      })
      await fetch(upload_url, {
        method: 'PUT',
        body: file,
        headers: { 'Content-Type': file.type || 'text/csv' },
      })
      await api(`/leads/imports/${lead_import_id}/confirm`, { method: 'POST' })
      let status = 'parsing'
      for (let i = 0; i < 30 && status === 'parsing'; i++) {
        await new Promise((r) => setTimeout(r, 2000))
        const imp = await api(`/leads/imports/${lead_import_id}`)
        status = imp.status
      }
      if (status === 'failed') throw new Error('Import failed — check the import status.')
      setFile(null)
      await reload()
    } catch (err) {
      setPageError(err.message)
    } finally {
      setBusy('')
    }
  }

  async function start() {
    setBusy('start')
    setPageError('')
    try {
      await api(`/campaigns/${id}/start/`, { method: 'POST' })
      await reload()
    } catch (err) {
      setPageError(err.message)
    } finally {
      setBusy('')
    }
  }

  async function review(leadId) {
    setReviewing(leadId)
    setPageError('')
    try {
      const detail = await api(`/leads/${leadId}`)
      setLeadDetail(detail)
    } catch (err) {
      setPageError(err.message)
    } finally {
      setReviewing('')
    }
  }

  async function approve(leadId) {
    setBusy(`approve:${leadId}`)
    setPageError('')
    try {
      await api(`/leads/${leadId}/context/approve`, { method: 'POST' })
      setLeadDetail(null)
      await reload()
    } catch (err) {
      setPageError(err.message)
    } finally {
      setBusy('')
    }
  }

  async function retry(callId) {
    setBusy(`retry:${callId}`)
    setPageError('')
    try {
      await api(`/calls/${callId}/retry/`, { method: 'POST' })
      await reload()
    } catch (err) {
      setPageError(err.message)
    } finally {
      setBusy('')
    }
  }

  if (loading) {
    return (
      <div className="state-center">
        <Spinner size={24} />
      </div>
    )
  }
  if (error || !campaign) {
    return (
      <div className="state-center">
        <Alert error={error || 'Campaign not found'} />
        <Button onClick={reload}>Retry</Button>
      </div>
    )
  }

  const running = campaign.status === 'running'

  return (
    <section>
      <PageHeader
        title={campaign.name}
        subtitle={<Badge status={campaign.status} />}
        actions={
          <Button loading={busy === 'start'} disabled={running} onClick={start}>
            {running ? 'Running' : 'Start campaign'}
          </Button>
        }
      />
      {pageError && <Alert error={pageError} onClose={() => setPageError('')} />}

      <Card title="Upload leads">
        <div className="upload-row">
          <input type="file" accept=".csv" onChange={(e) => setFile(e.target.files[0])} />
          <Button loading={busy === 'upload'} disabled={!file} onClick={upload}>
            Upload CSV
          </Button>
        </div>
        <p className="hint">CSV headers: name, phone, company, notes — phone is required.</p>
      </Card>

      <h2 className="section-title">Leads</h2>
      <div className="table-wrap">
        <table>
          <thead>
            <tr>
              <th>Name</th>
              <th>Phone</th>
              <th>Company</th>
              <th>Status</th>
              <th className="text-right">Actions</th>
            </tr>
          </thead>
          <tbody>
            {leads.length ? (
              leads.map((l) => (
                <tr key={l.id}>
                  <td>{l.name || '—'}</td>
                  <td className="muted">{l.phone_number}</td>
                  <td className="muted">{l.company || '—'}</td>
                  <td>
                    <Badge status={l.status} />
                  </td>
                  <td className="text-right">
                    <Button className="btn-sm" loading={reviewing === l.id} onClick={() => review(l.id)}>
                      Review
                    </Button>
                    {l.status === 'needs_review' && (
                      <Button
                        className="btn-sm btn-primary"
                        loading={busy === `approve:${l.id}`}
                        onClick={() => approve(l.id)}
                      >
                        Approve
                      </Button>
                    )}
                  </td>
                </tr>
              ))
            ) : (
              <tr>
                <td colSpan={5}>
                  <EmptyState title="No leads yet" hint="Upload a CSV to import leads." />
                </td>
              </tr>
            )}
          </tbody>
        </table>
      </div>

      {leadDetail && (
        <ContextView context={leadDetail.latest_context} onClose={() => setLeadDetail(null)} />
      )}

      <h2 className="section-title">Calls</h2>
      <div className="table-wrap">
        <table>
          <thead>
            <tr>
              <th>Lead</th>
              <th>Status</th>
              <th>Outcome</th>
              <th>Started</th>
              <th className="text-right">Actions</th>
            </tr>
          </thead>
          <tbody>
            {calls.length ? (
              calls.map((c) => (
                <tr key={c.id}>
                  <td>
                    <Link className="link" to={`/calls?call=${c.id}`}>
                      {c.lead_name}
                    </Link>
                  </td>
                  <td>
                    <Badge status={c.status} />
                  </td>
                  <td className="muted">{c.outcome || '—'}</td>
                  <td className="muted">{c.started_at ? new Date(c.started_at).toLocaleString() : '—'}</td>
                  <td className="text-right">
                    {['failed', 'busy', 'no_answer', 'canceled'].includes(c.status) && (
                      <Button className="btn-sm" loading={busy === `retry:${c.id}`} onClick={() => retry(c.id)}>
                        Retry
                      </Button>
                    )}
                  </td>
                </tr>
              ))
            ) : (
              <tr>
                <td colSpan={5}>
                  <EmptyState title="No calls yet" hint="Start the campaign to dial call-ready leads." />
                </td>
              </tr>
            )}
          </tbody>
        </table>
      </div>
    </section>
  )
}