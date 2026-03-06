import axios from 'axios'

const api = axios.create({ baseURL: '/api/v1', timeout: 10000 })

// Response interceptor to unwrap { success, data } envelope
api.interceptors.response.use(
  (response) => response,
  (error) => Promise.reject(error)
)

export const healthCheck = () => api.get('/health')

export const getSalaryRecords = (params?: {
  job_title?: string
  experience_years?: number
  region?: string
  company_size?: string
}) => api.get('/salary-records', { params })

export const generateTopics = (body: {
  content_type: string
  job_title: string
  region: string
  experience_range: [number, number]
  company_size: string
  limit: number
}) => api.post('/topics/generate', body)

export const getTopics = () => api.get('/topics')

export const enqueueTopics = (topicId: string) =>
  api.post(`/topics/${topicId}/enqueue`)

export const generateScript = (topicId: string) =>
  api.post('/scripts/generate', { topic_id: topicId })

export const getScript = (scriptId: string) =>
  api.get(`/scripts/${scriptId}`)

export const runPipeline = (body: {
  topic_id: string
  template_id: string
}) => api.post('/pipeline/run', body)

export const batchRunPipeline = (body: {
  topic_ids: string[]
  template_id: string
}) => api.post('/pipeline/batch-run', body)

export const getAdminJobs = () => api.get('/admin/jobs')

export const getAdminMetrics = () => api.get('/admin/metrics')
