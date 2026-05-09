import { Outlet, Link } from 'react-router-dom'
import { useAuthStore } from '@/stores/useAuthStore'

export default function MainLayout() {
  const { user, logout } = useAuthStore()

  return (
    <div className="min-h-screen bg-background flex flex-col">
      {/* Header */}
      <header className="h-16 border-b border-border bg-card flex items-center justify-between px-6">
        <div className="font-bold text-xl">Q-School AI</div>
        <div className="flex items-center gap-4">
          <span className="text-sm text-muted-foreground">
            {user?.name || 'Guest'}
          </span>
          <button 
            onClick={logout}
            className="text-sm font-medium text-destructive hover:underline"
          >
            Logout
          </button>
        </div>
      </header>

      <div className="flex flex-1">
        {/* Sidebar */}
        <aside className="w-64 border-r border-border bg-card p-4 hidden md:block">
          <nav className="flex flex-col gap-2">
            <Link to="/" className="p-2 hover:bg-accent rounded-md text-sm font-medium">
              Dashboard
            </Link>
            <Link to="/classes" className="p-2 hover:bg-accent rounded-md text-sm font-medium">
              Classes
            </Link>
            <Link to="/ai-chat" className="p-2 hover:bg-accent rounded-md text-sm font-medium">
              AI Assistant
            </Link>
          </nav>
        </aside>

        {/* Main Content */}
        <main className="flex-1 p-6 overflow-y-auto">
          <Outlet />
        </main>
      </div>
    </div>
  )
}
