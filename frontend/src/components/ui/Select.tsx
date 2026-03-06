import { cn } from '@/lib/utils'

interface SelectProps extends React.SelectHTMLAttributes<HTMLSelectElement> {
  label?: string
  options: { value: string; label: string }[]
}

export function Select({ label, options, className, ...props }: SelectProps) {
  return (
    <div className="flex flex-col gap-1.5">
      {label && <label className="text-xs font-mono text-text-dim uppercase tracking-wider">{label}</label>}
      <select
        className={cn(
          'bg-surface border border-border rounded px-3 py-2 text-sm text-text font-mono',
          'focus:outline-none focus:border-accent/60 focus:ring-1 focus:ring-accent/20 transition-colors appearance-none cursor-pointer',
          className
        )}
        {...props}
      >
        {options.map((opt) => (
          <option key={opt.value} value={opt.value}>{opt.label}</option>
        ))}
      </select>
    </div>
  )
}
