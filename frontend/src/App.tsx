import { BrowserRouter, Routes, Route } from 'react-router-dom'
import { QueryClient, QueryClientProvider } from '@tanstack/react-query'
import { AppLayout } from '@/components/layout/AppLayout'
import { Dashboard } from '@/pages/Dashboard'
import { Topics } from '@/pages/Topics'
import { Pipeline } from '@/pages/Pipeline'
import { SalaryData } from '@/pages/SalaryData'
import { ApiKeys } from '@/pages/ApiKeys'
const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      retry: 1,
      staleTime: 30_000,
    },
  },
})

export default function App() {
  return (
    <QueryClientProvider client={queryClient}>
      <BrowserRouter>
        <Routes>
          <Route element={<AppLayout />}>
            <Route path="/" element={<Dashboard />} />
            <Route path="/topics" element={<Topics />} />
            <Route path="/pipeline" element={<Pipeline />} />
            <Route path="/salary" element={<SalaryData />} />
            <Route path="/api-keys" element={<ApiKeys />} />
          </Route>
        </Routes>
      </BrowserRouter>
    </QueryClientProvider>
  )
}
