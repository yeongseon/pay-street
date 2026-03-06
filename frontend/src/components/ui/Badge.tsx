import { cn } from '@/lib/utils'

type BadgeVariant = 'default' | 'success' | 'warning' | 'error' | 'accent'

interface BadgeProps {
  children: React.ReactNode
  variant?: BadgeVariant
  className?: string
}

const variants: Record<BadgeVariant, string> = {
  default: 'bg-surface text-text-dim border border-border',
  success: 'bg-green-950 text-green-400 border border-green-800',
  warning: 'bg-yellow-950 text-yellow-400 border border-yellow-800',
  error: 'bg-red-950 text-red-400 border border-red-800',
  accent: 'bg-accent/10 text-accent border border-accent/30',
}

export function Badge({ children, variant = 'default', className }: BadgeProps) {
  return (
    <span className={cn('inline-flex items-center px-2 py-0.5 rounded text-xs font-mono font-medium', variants[variant], className)}>
      {children}
    </span>
  )
}
