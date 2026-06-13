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
            {user?.profile?.full_name || user?.username || 'Guest'}
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
            <Link to="/dashboard" className="p-2 hover:bg-accent rounded-md text-sm font-medium">
              Dashboard
            </Link>
            <Link to="/dashboard/classes" className="p-2 hover:bg-accent rounded-md text-sm font-medium">
              Class Management
            </Link>
            <Link to="/dashboard/chat" className="p-2 hover:bg-accent rounded-md text-sm font-medium">
              AI Assistant
            </Link>
            <Link to="/dashboard/flashcards" className="p-2 hover:bg-accent rounded-md text-sm font-medium">
              Flashcards
            </Link>
            <Link to="/dashboard/documents" className="p-2 hover:bg-accent rounded-md text-sm font-medium">
              AI Knowledge Base
            </Link>
            <div className="my-2 border-t border-border"></div>
            <Link to="/dashboard/worksheet" className="p-2 bg-indigo-50 text-indigo-600 dark:bg-indigo-900/30 dark:text-indigo-400 rounded-md text-sm font-bold flex items-center gap-2">
              <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z"></path></svg>
              Tạo Bài Tập AI
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
