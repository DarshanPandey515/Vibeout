const BASE = '/api/v1'

export function getSession() {
  return {
    token: localStorage.getItem('token') || '',
    orgId: localStorage.getItem('orgId') || '',
  }
}

export function setSession({ token, orgId }) {
  if (token) localStorage.setItem('token', token)
  if (orgId) localStorage.setItem('orgId', orgId)
}

export function clearSession() {
  localStorage.removeItem('token')
  localStorage.removeItem('orgId')
}

function headers() {
  const { token, orgId } = getSession()
  const h = { 'Content-Type': 'application/json' }
  if (token) h.Authorization = `Token ${token}`
  if (orgId) h['X-Organization-Id'] = orgId
  return h
}

export function errorMessage(data, fallback = 'Request failed') {
  if (!data) return fallback
  if (typeof data === 'string') return data
  if (typeof data.detail === 'string') return data.detail
  if (typeof data.error === 'string') return data.error
  if (Array.isArray(data.non_field_errors)) return data.non_field_errors.join('; ')
  const entries = Object.entries(data)
  if (entries.length) {
    return entries.map(([k, v]) => `${k}: ${Array.isArray(v) ? v[0] : v}`).join('; ')
  }
  return fallback
}

export async function api(path, { method = 'GET', body } = {}) {
  const res = await fetch(BASE + path, {
    method,
    headers: headers(),
    body: body ? JSON.stringify(body) : undefined,
  })
  if (res.status === 204) return null
  const data = await res.json().catch(() => null)
  if (!res.ok) {
    const error = new Error(errorMessage(data, res.statusText))
    error.status = res.status
    throw error
  }
  return data
}