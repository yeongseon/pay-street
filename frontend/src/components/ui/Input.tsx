import { cn } from '@/lib/utils'

interface InputProps extends React.InputHTMLAttributes<HTMLInputElement> {
  label?: string
}

export function Input({ label, className, ...props }: InputProps) {
  return (
    <div className="flex flex-col gap-1.5">
      {label && <label className="text-xs font-mono text-text-dim uppercase tracking-wider">{label}</label>}
      <input
        className={cn(
          'bg-surface border border-border rounded px-3 py-2 text-sm text-text font-mono',
          'placeholder:text-muted focus:outline-none focus:border-accent/60 focus:ring-1 focus:ring-accent/20 transition-colors',
          className
        )}
        {...props}
      />
    </div>
  )
}
