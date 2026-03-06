import { useState } from 'react'
import { useQuery } from '@tanstack/react-query'
import { getSalaryRecords } from '@/lib/api'
import { Card, CardHeader, CardTitle } from '@/components/ui/Card'
import { Button } from '@/components/ui/Button'
import { Input } from '@/components/ui/Input'
import { Select } from '@/components/ui/Select'
import { Badge } from '@/components/ui/Badge'
import { Search, Filter } from 'lucide-react'

interface SalaryRecord {
  job_title: string
  region: string
  experience_years: number
  company_size: string
  salary_min: number
  salary_max: number
  currency: string
}

export function SalaryData() {
  const [filters, setFilters] = useState({
    job_title: '',
    region: '',
    company_size: 'All',
    experience_years: '',
  })
  
  const [activeFilters, setActiveFilters] = useState(filters)

  const { data: salaryResponse, isLoading, isError, refetch } = useQuery({
    queryKey: ['salary-records', activeFilters],
    queryFn: () => getSalaryRecords({
      job_title: activeFilters.job_title || undefined,
      region: activeFilters.region || undefined,
      company_size: activeFilters.company_size === 'All' ? undefined : activeFilters.company_size,
      experience_years: activeFilters.experience_years ? parseInt(activeFilters.experience_years) : undefined,
    }),
    enabled: true, // Auto-fetch on mount
  })

  const handleApplyFilters = () => {
    setActiveFilters(filters)
    refetch()
  }

  const records: SalaryRecord[] = salaryResponse?.data || []

  return (
    <div className="space-y-6">
      <Card>
        <CardHeader>
          <div className="flex items-center gap-2">
            <Filter className="w-4 h-4 text-accent" />
            <CardTitle>Filter Data</CardTitle>
          </div>
        </CardHeader>
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4 items-end">
          <Input
            label="Job Title"
            placeholder="Search roles..."
            value={filters.job_title}
            onChange={(e) => setFilters({ ...filters, job_title: e.target.value })}
          />
          <Input
            label="Region"
            placeholder="Search regions..."
            value={filters.region}
            onChange={(e) => setFilters({ ...filters, region: e.target.value })}
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
            value={filters.company_size}
            onChange={(e) => setFilters({ ...filters, company_size: e.target.value })}
          />
          <Input
            type="number"
            label="Experience (Years)"
            placeholder="Any"
            value={filters.experience_years}
            onChange={(e) => setFilters({ ...filters, experience_years: e.target.value })}
          />
        </div>
        <div className="mt-4 flex justify-end">
          <Button variant="secondary" onClick={handleApplyFilters}>
            <Search className="w-4 h-4 mr-2" />
            Apply Filters
          </Button>
        </div>
      </Card>

      <Card>
        <CardHeader>
          <CardTitle>Salary Records</CardTitle>
          <Badge variant="default">{records.length} records</Badge>
        </CardHeader>

        {isLoading ? (
          <div className="text-accent animate-pulse font-mono text-sm py-8 text-center">Loading salary data...</div>
        ) : isError ? (
          <div className="text-red-400 font-mono text-sm py-8 text-center">Failed to load salary data</div>
        ) : (
          <div className="overflow-x-auto">
            <table className="w-full text-sm text-left">
              <thead className="text-xs text-text-dim uppercase font-mono border-b border-border">
                <tr>
                  <th className="px-4 py-3">Job Title</th>
                  <th className="px-4 py-3">Region</th>
                  <th className="px-4 py-3">Experience</th>
                  <th className="px-4 py-3">Company Size</th>
                  <th className="px-4 py-3 text-right">Salary Range</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-border font-mono">
                {records.length === 0 ? (
                  <tr>
                    <td colSpan={5} className="px-4 py-8 text-center text-text-dim">No records found matching filters</td>
                  </tr>
                ) : (
                  records.map((record, idx) => (
                    <tr key={idx} className="hover:bg-surface/50 transition-colors">
                      <td className="px-4 py-3 text-text font-medium">{record.job_title}</td>
                      <td className="px-4 py-3 text-text-dim">{record.region}</td>
                      <td className="px-4 py-3 text-text-dim">{record.experience_years} yrs</td>
                      <td className="px-4 py-3 text-text-dim">{record.company_size}</td>
                      <td className="px-4 py-3 text-right text-accent">
                        {record.salary_min?.toLocaleString()} - {record.salary_max?.toLocaleString()} {record.currency}
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
