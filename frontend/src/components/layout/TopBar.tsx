import { useLocation } from 'react-router-dom'
import { Terminal } from 'lucide-react'

const pageTitles: Record<string, string> = {
  '/': 'Dashboard',
  '/topics': 'Topics',
  '/pipeline': 'Pipeline',
  '/salary': 'Salary Data',
  '/api-keys': 'API Keys',
}

export function TopBar() {
  const { pathname } = useLocation()
  const title = pageTitles[pathname] ?? 'Admin'

  return (
    <header className="h-14 border-b border-border bg-surface/80 backdrop-blur flex items-center px-6 gap-3 fixed top-0 left-56 right-0 z-10">
      <Terminal className="w-4 h-4 text-accent" />
      <h1 className="font-display font-semibold text-text text-sm tracking-wide uppercase">{title}</h1>
      <div className="ml-auto flex items-center gap-2">
        <div className="w-2 h-2 bg-green-400 rounded-full animate-pulse" />
        <span className="text-xs text-text-dim font-mono">system online</span>
      </div>
    </header>
  )
}
