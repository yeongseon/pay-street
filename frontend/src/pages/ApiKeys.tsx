import { useState } from 'react'
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { getApiKeys, upsertApiKey, deleteApiKey, toggleApiKey } from '@/lib/api'
import { Card, CardHeader, CardTitle } from '@/components/ui/Card'
import { Button } from '@/components/ui/Button'
import { Input } from '@/components/ui/Input'
import { Badge } from '@/components/ui/Badge'
import { KeyRound, Plus, Trash2, ToggleLeft, ToggleRight, CheckCircle2, AlertCircle } from 'lucide-react'

interface ApiKeyRecord {
  id: string
  provider: string
  label: string | null
  is_active: boolean
  key_masked: string
}

const PROVIDERS = [
  { value: 'openai', label: 'OpenAI (GPT)', description: 'Used for script generation via GPT-4o' },
  { value: 'elevenlabs', label: 'ElevenLabs', description: 'Used for voice synthesis' },
]

export function ApiKeys() {
  const qc = useQueryClient()
  const [form, setForm] = useState({ provider: 'openai', key_value: '', label: '' })
  const [showForm, setShowForm] = useState(false)
  const [feedback, setFeedback] = useState<{ type: 'success' | 'error'; msg: string } | null>(null)

  const { data, isLoading } = useQuery({
    queryKey: ['api-keys'],
    queryFn: getApiKeys,
  })

  const keys: ApiKeyRecord[] = data?.data?.data ?? []

  const showFeedback = (type: 'success' | 'error', msg: string) => {
    setFeedback({ type, msg })
    setTimeout(() => setFeedback(null), 3000)
  }

  const upsertMutation = useMutation({
    mutationFn: upsertApiKey,
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: ['api-keys'] })
      setForm({ provider: 'openai', key_value: '', label: '' })
      setShowForm(false)
      showFeedback('success', 'API key saved.')
    },
    onError: () => showFeedback('error', 'Failed to save key.'),
  })

  const deleteMutation = useMutation({
    mutationFn: deleteApiKey,
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: ['api-keys'] })
      showFeedback('success', 'API key deleted.')
    },
    onError: () => showFeedback('error', 'Failed to delete key.'),
  })

  const toggleMutation = useMutation({
    mutationFn: toggleApiKey,
    onSuccess: () => qc.invalidateQueries({ queryKey: ['api-keys'] }),
  })

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault()
    if (!form.key_value.trim()) return
    upsertMutation.mutate({
      provider: form.provider,
      key_value: form.key_value.trim(),
      label: form.label.trim() || undefined,
    })
  }

  return (
    <div className="space-y-6 max-w-3xl">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h2 className="font-display font-bold text-text text-lg flex items-center gap-2">
            <KeyRound className="w-5 h-5 text-accent" />
            API Keys
          </h2>
          <p className="text-text-dim text-xs font-mono mt-1">
            Manage provider API keys. Keys are stored in DB and loaded dynamically at runtime.
          </p>
        </div>
        <Button
          variant="primary"
          size="sm"
          onClick={() => setShowForm((v) => !v)}
        >
          <Plus className="w-3.5 h-3.5" />
          {showForm ? 'Cancel' : 'Add Key'}
        </Button>
      </div>

      {/* Feedback banner */}
      {feedback && (
        <div className={`flex items-center gap-2 px-4 py-2.5 rounded border text-sm font-mono ${
          feedback.type === 'success'
            ? 'bg-green-950 border-green-800 text-green-400'
            : 'bg-red-950 border-red-800 text-red-400'
        }`}>
          {feedback.type === 'success'
            ? <CheckCircle2 className="w-4 h-4" />
            : <AlertCircle className="w-4 h-4" />}
          {feedback.msg}
        </div>
      )}

      {/* Add / Edit form */}
      {showForm && (
        <Card>
          <CardHeader>
            <CardTitle>New API Key</CardTitle>
          </CardHeader>
          <form onSubmit={handleSubmit} className="space-y-4">
            {/* Provider select */}
            <div className="flex flex-col gap-1.5">
              <label className="text-xs font-mono text-text-dim uppercase tracking-wider">Provider</label>
              <div className="grid grid-cols-2 gap-2">
                {PROVIDERS.map((p) => (
                  <button
                    key={p.value}
                    type="button"
                    onClick={() => setForm((f) => ({ ...f, provider: p.value }))}
                    className={`text-left px-4 py-3 rounded border transition-all font-mono ${
                      form.provider === p.value
                        ? 'bg-accent/10 border-accent/40 text-text'
                        : 'bg-surface border-border text-text-dim hover:border-accent/20'
                    }`}
                  >
                    <div className="text-sm font-semibold">{p.label}</div>
                    <div className="text-xs mt-0.5 text-text-dim">{p.description}</div>
                  </button>
                ))}
              </div>
            </div>

            <Input
              label="API Key"
              type="password"
              placeholder="sk-..."
              value={form.key_value}
              onChange={(e) => setForm((f) => ({ ...f, key_value: e.target.value }))}
              required
            />
            <Input
              label="Label (optional)"
              placeholder="e.g. Production GPT-4o key"
              value={form.label}
              onChange={(e) => setForm((f) => ({ ...f, label: e.target.value }))}
            />
            <div className="flex justify-end gap-2 pt-1">
              <Button type="button" variant="ghost" size="sm" onClick={() => setShowForm(false)}>
                Cancel
              </Button>
              <Button
                type="submit"
                variant="primary"
                size="sm"
                loading={upsertMutation.isPending}
              >
                Save Key
              </Button>
            </div>
          </form>
        </Card>
      )}

      {/* Existing keys */}
      <Card>
        <CardHeader>
          <CardTitle>Stored Keys</CardTitle>
          <span className="text-xs text-text-dim font-mono">{keys.length} configured</span>
        </CardHeader>

        {isLoading ? (
          <p className="text-text-dim text-sm font-mono py-4 text-center">Loading...</p>
        ) : keys.length === 0 ? (
          <div className="py-8 text-center">
            <KeyRound className="w-8 h-8 text-muted mx-auto mb-2" />
            <p className="text-text-dim text-sm font-mono">No API keys configured yet.</p>
            <p className="text-muted text-xs font-mono mt-1">
              Add an OpenAI key to enable GPT script generation.
            </p>
          </div>
        ) : (
          <div className="space-y-2">
            {keys.map((key) => {
              const providerInfo = PROVIDERS.find((p) => p.value === key.provider)
              return (
                <div
                  key={key.id}
                  className="flex items-center gap-4 px-4 py-3 bg-surface rounded border border-border"
                >
                  {/* Provider + label */}
                  <div className="flex-1 min-w-0">
                    <div className="flex items-center gap-2 mb-0.5">
                      <span className="text-text text-sm font-mono font-semibold">
                        {providerInfo?.label ?? key.provider}
                      </span>
                      <Badge variant={key.is_active ? 'success' : 'default'}>
                        {key.is_active ? 'active' : 'inactive'}
                      </Badge>
                    </div>
                    <div className="text-text-dim text-xs font-mono truncate">
                      {key.label && <span className="text-text-dim mr-2">{key.label} ·</span>}
                      <span className="font-mono tracking-wider">{key.key_masked}</span>
                    </div>
                  </div>

                  {/* Actions */}
                  <div className="flex items-center gap-1 flex-shrink-0">
                    <Button
                      variant="ghost"
                      size="sm"
                      onClick={() => toggleMutation.mutate(key.provider)}
                      title={key.is_active ? 'Deactivate' : 'Activate'}
                    >
                      {key.is_active
                        ? <ToggleRight className="w-4 h-4 text-accent" />
                        : <ToggleLeft className="w-4 h-4 text-muted" />}
                    </Button>
                    <Button
                      variant="ghost"
                      size="sm"
                      onClick={() => {
                        if (confirm(`Delete ${key.provider} API key?`)) {
                          deleteMutation.mutate(key.provider)
                        }
                      }}
                      title="Delete"
                    >
                      <Trash2 className="w-4 h-4 text-red-400" />
                    </Button>
                  </div>
                </div>
              )
            })}
          </div>
        )}
      </Card>

      {/* Info box */}
      <div className="flex gap-3 px-4 py-3 bg-surface border border-border rounded text-xs font-mono text-text-dim">
        <AlertCircle className="w-4 h-4 text-accent flex-shrink-0 mt-0.5" />
        <div>
          <p className="text-text mb-1">Key resolution order at runtime:</p>
          <ol className="list-decimal list-inside space-y-0.5">
            <li>DB (this page) — active key for the provider</li>
            <li><code className="text-accent">.env</code> / environment variable (fallback)</li>
          </ol>
        </div>
      </div>
    </div>
  )
}
