import { NavLink, Outlet } from 'react-router-dom'

import { useAuth } from '../auth'

export default function Layout() {
  const { orgs, org, switchOrg, logout } = useAuth()
  const items = [
    { to: '/campaigns', label: 'Campaigns' },
    { to: '/telephony', label: 'Telephony' },
    { to: '/agents', label: 'Agents' },
    { to: '/calls', label: 'Calls' },
  ]
  return (
    <div className="app">
      <aside className="sidebar">
        <div className="brand">
          <span className="brand-eq" aria-hidden="true">
            <span />
            <span />
            <span />
            <span />
            <span />
          </span>
          Vibeout
        </div>
        <nav>
          {items.map((item) => (
            <NavLink key={item.to} to={item.to} className={({ isActive }) => (isActive ? 'nav-item active' : 'nav-item')}>
              {item.label}
            </NavLink>
          ))}
        </nav>
        <div className="sidebar-footer">
          <select className="org-select" value={org || ''} onChange={(e) => switchOrg(e.target.value)}>
            {orgs.map((o) => (
              <option key={o.id} value={o.id}>
                {o.name}
              </option>
            ))}
          </select>
          <button type="button" className="btn btn-ghost" onClick={logout}>
            Log out
          </button>
        </div>
      </aside>
      <main className="main">
        <Outlet />
      </main>
    </div>
  )
}