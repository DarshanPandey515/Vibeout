export function Spinner({ size = 16 }) {
  return <span className="spinner" style={{ width: size, height: size }} />
}

export function Button({ loading, children, className = '', disabled, ...props }) {
  return (
    <button className={`btn ${className}`} disabled={loading || disabled} {...props}>
      {loading && <Spinner />}
      {children}
    </button>
  )
}

export function Alert({ error, onClose }) {
  if (!error) return null
  return (
    <div className="alert" role="alert">
      <span>{error?.message ?? error}</span>
      {onClose && (
        <button type="button" className="alert-close" onClick={onClose} aria-label="Dismiss">
          ×
        </button>
      )}
    </div>
  )
}

export function EmptyState({ title, hint, action }) {
  return (
    <div className="empty">
      <p className="empty-title">{title}</p>
      {hint && <p className="empty-hint">{hint}</p>}
      {action}
    </div>
  )
}

const LIVE = new Set(['running', 'in-progress', 'dialing', 'connected', 'active', 'queued', 'parsing', 'processing'])

export function Badge({ status }) {
  const cls = String(status).toLowerCase().replace(/[\s_]+/g, '-')
  return (
    <span className={`badge badge-${cls}`}>
      {LIVE.has(cls) && <span className="live-dot" />}
      {status}
    </span>
  )
}

export function PageHeader({ title, subtitle, actions }) {
  return (
    <div className="page-header">
      <div>
        <h1>{title}</h1>
        {subtitle && <p>{subtitle}</p>}
      </div>
      {actions && <div className="page-actions">{actions}</div>}
    </div>
  )
}

export function Field({ label, children }) {
  return (
    <label className="field">
      <span>{label}</span>
      {children}
    </label>
  )
}

export function Card({ title, children, className = '' }) {
  return (
    <div className={`card ${className}`}>
      {title && <h2 className="card-title">{title}</h2>}
      {children}
    </div>
  )
}

export function StateCenter({ loading, error, empty, onRetry, children }) {
  if (loading) {
    return (
      <div className="state-center">
        <Spinner size={24} />
      </div>
    )
  }
  if (error) {
    return (
      <div className="state-center">
        <Alert error={error} />
        {onRetry && <Button onClick={onRetry}>Retry</Button>}
      </div>
    )
  }
  if (empty && empty.show) {
    return <EmptyState title={empty.title} hint={empty.hint} action={empty.action} />
  }
  return children
}