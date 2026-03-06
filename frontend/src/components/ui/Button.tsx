import { cn } from '@/lib/utils'
import { Loader2 } from 'lucide-react'

type ButtonVariant = 'primary' | 'secondary' | 'ghost' | 'destructive'
type ButtonSize = 'sm' | 'md' | 'lg'

interface ButtonProps extends React.ButtonHTMLAttributes<HTMLButtonElement> {
  variant?: ButtonVariant
  size?: ButtonSize
  loading?: boolean
  children: React.ReactNode
}

const variants: Record<ButtonVariant, string> = {
  primary: 'bg-accent text-bg font-bold hover:bg-accent-dim',
  secondary: 'bg-surface text-text border border-border hover:bg-card hover:border-accent/50',
  ghost: 'text-text-dim hover:text-text hover:bg-surface',
  destructive: 'bg-red-950 text-red-400 border border-red-800 hover:bg-red-900',
}

const sizes: Record<ButtonSize, string> = {
  sm: 'px-3 py-1.5 text-xs',
  md: 'px-4 py-2 text-sm',
  lg: 'px-6 py-3 text-base',
}

export function Button({ variant = 'secondary', size = 'md', loading, children, className, disabled, ...props }: ButtonProps) {
  return (
    <button
      className={cn(
        'inline-flex items-center gap-2 rounded font-mono transition-all duration-150 cursor-pointer disabled:opacity-40 disabled:cursor-not-allowed',
        variants[variant],
        sizes[size],
        className
      )}
      disabled={disabled || loading}
      {...props}
    >
      {loading && <Loader2 className="w-3.5 h-3.5 animate-spin" />}
      {children}
    </button>
  )
}
