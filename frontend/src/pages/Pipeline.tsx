import { useState } from 'react'
import { useMutation, useQuery } from '@tanstack/react-query'
import { runPipeline, getAdminJobs } from '@/lib/api'
import { Card, CardHeader, CardTitle } from '@/components/ui/Card'
import { Button } from '@/components/ui/Button'
import { Input } from '@/components/ui/Input'
import { Badge } from '@/components/ui/Badge'
import { Play, RefreshCw } from 'lucide-react'

interface PipelineJob {
  id: string
  topic_id?: string
  status: 'pending' | 'completed' | 'failed' | 'running'
  created_at: string
  duration?: number
}

export function Pipeline() {
  const [topicId, setTopicId] = useState('')
  const [templateId, setTemplateId] = useState('street_interview_v1')
  const [message, setMessage] = useState<{ type: 'success' | 'error', text: string } | null>(null)

  const { data: jobsResponse, refetch: refetchJobs, isRefetching } = useQuery({
    queryKey: ['jobs'],
    queryFn: getAdminJobs,
    refetchInterval: 10000,
  })

  const pipelineMutation = useMutation({
    mutationFn: runPipeline,
    onSuccess: () => {
      setMessage({ type: 'success', text: 'Pipeline started successfully' })
      refetchJobs()
    },
    onError: () => {
      setMessage({ type: 'error', text: 'Failed to start pipeline' })
    },
  })

  const handleRun = () => {
    if (!topicId) return
    pipelineMutation.mutate({ topic_id: topicId, template_id: templateId })
  }

  const jobs: PipelineJob[] = jobsResponse?.data || []

  return (
    <div className="space-y-6">
      <Card>
        <CardHeader>
          <div className="flex items-center gap-2">
            <Play className="w-4 h-4 text-accent" />
            <CardTitle>Run Pipeline</CardTitle>
          </div>
        </CardHeader>
        <div className="flex flex-col gap-4">
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <Input
              label="Topic ID"
              placeholder="Enter Topic ID"
              value={topicId}
              onChange={(e) => setTopicId(e.target.value)}
            />
            <Input
              label="Template ID"
              placeholder="Template ID"
              value={templateId}
              onChange={(e) => setTemplateId(e.target.value)}
            />
          </div>
          <div className="flex justify-between items-center">
             {message && (
                <Badge variant={message.type === 'success' ? 'success' : 'error'}>
                  {message.text}
                </Badge>
             )}
             <Button
              variant="primary"
              onClick={handleRun}
              loading={pipelineMutation.isPending}
              disabled={!topicId}
              className="ml-auto"
            >
              Run Pipeline
            </Button>
          </div>
        </div>
      </Card>

      <Card>
        <CardHeader>
          <div className="flex items-center justify-between w-full">
            <CardTitle>Pipeline Jobs</CardTitle>
            <Button variant="ghost" size="sm" onClick={() => refetchJobs()} disabled={isRefetching}>
              <RefreshCw className={`w-3 h-3 mr-1 ${isRefetching ? 'animate-spin' : ''}`} />
              Refresh
            </Button>
          </div>
        </CardHeader>
        
        <div className="overflow-x-auto">
          <table className="w-full text-sm text-left">
            <thead className="text-xs text-text-dim uppercase font-mono border-b border-border">
              <tr>
                <th className="px-4 py-3">Job ID</th>
                <th className="px-4 py-3">Topic</th>
                <th className="px-4 py-3">Status</th>
                <th className="px-4 py-3">Created</th>
                <th className="px-4 py-3">Duration</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-border font-mono">
              {jobs.length === 0 ? (
                <tr>
                  <td colSpan={5} className="px-4 py-8 text-center text-text-dim">No pipeline jobs found</td>
                </tr>
              ) : (
                jobs.map((job) => (
                  <tr key={job.id} className="hover:bg-surface/50 transition-colors">
                    <td className="px-4 py-3 text-text font-mono text-xs">{job.id.substring(0, 8)}...</td>
                    <td className="px-4 py-3 text-text-dim text-xs">{job.topic_id ? job.topic_id.substring(0, 8) + '...' : '-'}</td>
                    <td className="px-4 py-3">
                      <Badge variant={
                        job.status === 'completed' ? 'success' :
                        job.status === 'failed' ? 'error' :
                        job.status === 'running' ? 'accent' :
                        'warning'
                      }>
                        {job.status}
                      </Badge>
                    </td>
                    <td className="px-4 py-3 text-text-dim">{new Date(job.created_at).toLocaleString()}</td>
                    <td className="px-4 py-3 text-text-dim">{job.duration ? `${job.duration}s` : '-'}</td>
                  </tr>
                ))
              )}
            </tbody>
          </table>
        </div>
      </Card>
    </div>
  )
}
