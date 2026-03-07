import { NavLink } from 'react-router-dom'
import { LayoutDashboard, MessageSquare, Play, Database, Zap, KeyRound } from 'lucide-react'
import { cn } from '@/lib/utils'

const navItems = [
  { to: '/', icon: LayoutDashboard, label: 'Dashboard' },
  { to: '/topics', icon: MessageSquare, label: 'Topics' },
  { to: '/pipeline', icon: Play, label: 'Pipeline' },
  { to: '/salary', icon: Database, label: 'Salary Data' },
  { to: '/api-keys', icon: KeyRound, label: 'API Keys' },
]

export function Sidebar() {
  return (
    <aside className="w-56 bg-surface border-r border-border flex flex-col h-full fixed left-0 top-0 z-20">
      {/* Logo */}
      <div className="px-5 py-5 border-b border-border">
        <div className="flex items-center gap-2.5">
          <div className="w-7 h-7 bg-accent rounded flex items-center justify-center">
            <Zap className="w-4 h-4 text-bg" />
          </div>
          <span className="font-display font-bold text-text text-base tracking-tight">PayStreet</span>
        </div>
        <p className="text-text-dim text-xs mt-1.5 font-mono">Content Engine</p>
      </div>

      {/* Nav */}
      <nav className="flex-1 px-3 py-4 space-y-1">
        {navItems.map(({ to, icon: Icon, label }) => (
          <NavLink
            key={to}
            to={to}
            end={to === '/'}
            className={({ isActive }) =>
              cn(
                'flex items-center gap-3 px-3 py-2.5 rounded text-sm font-mono transition-all duration-150',
                isActive
                  ? 'bg-accent/10 text-accent border border-accent/20'
                  : 'text-text-dim hover:text-text hover:bg-card'
              )
            }
          >
            <Icon className="w-4 h-4 flex-shrink-0" />
            {label}
          </NavLink>
        ))}
      </nav>

      {/* Footer */}
      <div className="px-5 py-4 border-t border-border">
        <p className="text-muted text-xs font-mono">v0.1.0 · Admin</p>
      </div>
    </aside>
  )
}
