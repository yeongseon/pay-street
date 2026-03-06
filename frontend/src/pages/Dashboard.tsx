import { useQuery } from '@tanstack/react-query'
import { getAdminMetrics, getAdminJobs } from '@/lib/api'
import { Card, CardHeader, CardTitle } from '@/components/ui/Card'
import { Badge } from '@/components/ui/Badge'
import { Activity, CheckCircle, Clock, XCircle, Layers } from 'lucide-react'

interface AdminMetrics {
  total_jobs: number
  completed: number
  pending: number
  failed: number
}

interface AdminJob {
  id: string
  type: string
  status: 'pending' | 'completed' | 'failed' | 'running'
  created_at: string
}

export function Dashboard() {
  const { data: metricsResponse, isLoading: metricsLoading, isError: metricsError } = useQuery({
    queryKey: ['metrics'],
    queryFn: getAdminMetrics,
    refetchInterval: 30000,
  })

  const { data: jobsResponse, isLoading: jobsLoading, isError: jobsError } = useQuery({
    queryKey: ['jobs'],
    queryFn: getAdminJobs,
    refetchInterval: 30000,
  })

  // Safely access data assuming the API returns the object directly
  const metrics: AdminMetrics = metricsResponse?.data || { total_jobs: 0, completed: 0, pending: 0, failed: 0 }
  const jobs: AdminJob[] = jobsResponse?.data || []

  if (metricsLoading || jobsLoading) {
    return (
      <div className="flex items-center justify-center h-full">
        <div className="text-accent animate-pulse font-mono">Loading metrics...</div>
      </div>
    )
  }

  if (metricsError || jobsError) {
    return (
      <div className="flex items-center justify-center h-full">
        <div className="text-red-400 font-mono">Failed to load data</div>
      </div>
    )
  }

  return (
    <div className="space-y-6">
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
        <Card className="border-l-4 border-l-border">
          <CardHeader className="mb-2">
            <CardTitle className="text-xs text-text-dim">Total Jobs</CardTitle>
            <Layers className="w-4 h-4 text-accent" />
          </CardHeader>
          <div className="text-2xl font-mono font-bold text-text">{metrics.total_jobs}</div>
        </Card>

        <Card className="border-l-4 border-l-green-900">
          <CardHeader className="mb-2">
            <CardTitle className="text-xs text-text-dim">Completed</CardTitle>
            <CheckCircle className="w-4 h-4 text-green-400" />
          </CardHeader>
          <div className="text-2xl font-mono font-bold text-text">{metrics.completed}</div>
        </Card>

        <Card className="border-l-4 border-l-yellow-900">
          <CardHeader className="mb-2">
            <CardTitle className="text-xs text-text-dim">Pending</CardTitle>
            <Clock className="w-4 h-4 text-yellow-400" />
          </CardHeader>
          <div className="text-2xl font-mono font-bold text-text">{metrics.pending}</div>
        </Card>

        <Card className="border-l-4 border-l-red-900">
          <CardHeader className="mb-2">
            <CardTitle className="text-xs text-text-dim">Failed</CardTitle>
            <XCircle className="w-4 h-4 text-red-400" />
          </CardHeader>
          <div className="text-2xl font-mono font-bold text-text">{metrics.failed}</div>
        </Card>
      </div>

      <Card>
        <CardHeader>
          <div className="flex items-center gap-2">
            <Activity className="w-4 h-4 text-accent" />
            <CardTitle>Recent Activity</CardTitle>
          </div>
          <Badge variant="default">Live</Badge>
        </CardHeader>
        
        <div className="overflow-x-auto">
          <table className="w-full text-sm text-left">
            <thead className="text-xs text-text-dim uppercase font-mono border-b border-border">
              <tr>
                <th className="px-4 py-3">Job ID</th>
                <th className="px-4 py-3">Type</th>
                <th className="px-4 py-3">Status</th>
                <th className="px-4 py-3">Created</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-border font-mono">
              {jobs.length === 0 ? (
                <tr>
                  <td colSpan={4} className="px-4 py-8 text-center text-text-dim">No recent jobs found</td>
                </tr>
              ) : (
                jobs.map((job) => (
                  <tr key={job.id} className="hover:bg-surface/50 transition-colors">
                    <td className="px-4 py-3 text-text font-mono text-xs">{job.id}</td>
                    <td className="px-4 py-3 text-text-dim">{job.type}</td>
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
