import { NavLink } from 'react-router-dom'
import { LayoutGrid, Plus, MessageSquare, User } from 'lucide-react'

const LINKS = [
  { to: '/dashboard', label: 'All Projects', icon: LayoutGrid, end: true },
  { to: '/dashboard/new', label: 'Add Project', icon: Plus },
  { to: '/dashboard/messages', label: 'Messages', icon: MessageSquare },
  { to: '/profile', label: 'Profile', icon: User },
]

export default function DashboardLayout({ children }) {
  return (
    <div className="max-w-7xl mx-auto px-6 py-10 grid grid-cols-1 lg:grid-cols-[220px_1fr] gap-8">
      <aside className="glass-card p-4 h-fit lg:sticky lg:top-24">
        <p className="text-xs uppercase tracking-wider text-slate-500 px-2 mb-2">Admin Dashboard</p>
        <nav className="flex lg:flex-col gap-1 overflow-x-auto">
          {LINKS.map(({ to, label, icon: Icon, end }) => (
            <NavLink
              key={to}
              to={to}
              end={end}
              className={({ isActive }) =>
                `flex items-center gap-2 px-3 py-2 rounded-lg text-sm whitespace-nowrap transition-colors ${
                  isActive ? 'bg-gradient-to-r from-accent-blue/20 to-accent-purple/20 text-white' : 'text-slate-400 hover:text-white hover:bg-white/5'
                }`
              }
            >
              <Icon size={16} /> {label}
            </NavLink>
          ))}
        </nav>
      </aside>
      <div>{children}</div>
    </div>
  )
}
