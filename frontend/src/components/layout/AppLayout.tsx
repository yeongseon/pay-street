import { Outlet } from 'react-router-dom'
import { Sidebar } from './Sidebar'
import { TopBar } from './TopBar'

export function AppLayout() {
  return (
    <div className="flex h-screen bg-bg overflow-hidden">
      <Sidebar />
      <div className="flex-1 flex flex-col ml-56 min-h-0">
        <TopBar />
        <main className="flex-1 overflow-auto pt-14 p-6">
          <Outlet />
        </main>
      </div>
    </div>
  )
}
