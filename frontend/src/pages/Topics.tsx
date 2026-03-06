import { useState } from 'react'
import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query'
import { generateTopics, getTopics, enqueueTopics } from '@/lib/api'
import { Card, CardHeader, CardTitle } from '@/components/ui/Card'
import { Button } from '@/components/ui/Button'
import { Input } from '@/components/ui/Input'
import { Select } from '@/components/ui/Select'
import { Badge } from '@/components/ui/Badge'
import { Plus, Send } from 'lucide-react'

interface Topic {
  id: string
  title: string
  status: string
  created_at: string
}

export function Topics() {
  const queryClient = useQueryClient()
  const [formData, setFormData] = useState({
    job_title: '',
    region: '',
    company_size: 'All',
    limit: 10,
  })

  const { data: topicsResponse, isLoading: topicsLoading } = useQuery({
    queryKey: ['topics'],
    queryFn: getTopics,
  })

  const generateMutation = useMutation({
    mutationFn: generateTopics,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['topics'] })
    },
  })

  const enqueueMutation = useMutation({
    mutationFn: enqueueTopics,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['topics'] })
    },
  })

  const handleGenerate = () => {
    generateMutation.mutate({
      content_type: 'short',
      job_title: formData.job_title,
      region: formData.region,
      experience_range: [1, 5],
      company_size: formData.company_size,
      limit: formData.limit,
    })
  }

  const topics: Topic[] = topicsResponse?.data || []

  return (
    <div className="space-y-6">
      <Card>
        <CardHeader>
          <div className="flex items-center gap-2">
            <Plus className="w-4 h-4 text-accent" />
            <CardTitle>Generate Topics</CardTitle>
          </div>
        </CardHeader>
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4 items-end">
          <Input
            label="Job Title"
            placeholder="Backend Developer"
            value={formData.job_title}
            onChange={(e) => setFormData({ ...formData, job_title: e.target.value })}
          />
          <Input
            label="Region"
            placeholder="Pangyo"
            value={formData.region}
            onChange={(e) => setFormData({ ...formData, region: e.target.value })}
          />
          <Select
            label="Company Size"
            options={[
              { value: 'All', label: 'All' },
              { value: 'Small', label: 'Small' },
              { value: 'Medium', label: 'Medium' },
              { value: 'Large', label: 'Large' },
              { value: 'Startup', label: 'Startup' },
            ]}
            value={formData.company_size}
            onChange={(e) => setFormData({ ...formData, company_size: e.target.value })}
          />
          <Input
            type="number"
            label="Limit"
            value={formData.limit}
            onChange={(e) => setFormData({ ...formData, limit: parseInt(e.target.value) || 10 })}
          />
        </div>
        <div className="mt-4 flex justify-end">
          <Button variant="primary" onClick={handleGenerate} loading={generateMutation.isPending}>
            Generate Topics
          </Button>
        </div>
      </Card>

      <Card>
        <CardHeader>
          <CardTitle>Generated Topics</CardTitle>
          <Badge variant="default">{topics.length} items</Badge>
        </CardHeader>
        
        {topicsLoading ? (
           <div className="text-accent animate-pulse font-mono text-sm">Loading topics...</div>
        ) : (
          <div className="overflow-x-auto">
            <table className="w-full text-sm text-left">
              <thead className="text-xs text-text-dim uppercase font-mono border-b border-border">
                <tr>
                  <th className="px-4 py-3">ID</th>
                  <th className="px-4 py-3">Title / Content</th>
                  <th className="px-4 py-3">Status</th>
                  <th className="px-4 py-3 text-right">Action</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-border font-mono">
                {topics.length === 0 ? (
                  <tr>
                    <td colSpan={4} className="px-4 py-8 text-center text-text-dim">No topics found</td>
                  </tr>
                ) : (
                  topics.map((topic) => (
                    <tr key={topic.id} className="hover:bg-surface/50 transition-colors">
                      <td className="px-4 py-3 text-text-dim text-xs">{topic.id.substring(0, 8)}...</td>
                      <td className="px-4 py-3 text-text">{topic.title}</td>
                      <td className="px-4 py-3">
                        <Badge variant={topic.status === 'enqueued' ? 'success' : 'default'}>
                          {topic.status}
                        </Badge>
                      </td>
                      <td className="px-4 py-3 text-right">
                        <Button
                          variant="ghost"
                          size="sm"
                          onClick={() => enqueueMutation.mutate(topic.id)}
                          disabled={topic.status === 'enqueued'}
                        >
                          <Send className="w-3 h-3 mr-1" />
                          Enqueue
                        </Button>
                      </td>
                    </tr>
                  ))
                )}
              </tbody>
            </table>
          </div>
        )}
      </Card>
    </div>
  )
}
