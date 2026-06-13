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
            <Link to="/dashboard/grading" className="p-2 bg-emerald-50 text-emerald-600 dark:bg-emerald-900/30 dark:text-emerald-400 rounded-md text-sm font-bold flex items-center gap-2 mt-1">
              <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M3 9a2 2 0 012-2h.93a2 2 0 001.664-.89l.812-1.22A2 2 0 0110.07 4h3.86a2 2 0 011.664.89l.812 1.22A2 2 0 0018.07 7H19a2 2 0 012 2v9a2 2 0 01-2 2H5a2 2 0 01-2-2V9z"></path><path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M15 13a3 3 0 11-6 0 3 3 0 016 0z"></path></svg>
              Chấm Điểm Camera
            </Link>
            <Link to="/dashboard/comments" className="p-2 bg-blue-50 text-blue-600 dark:bg-blue-900/30 dark:text-blue-400 rounded-md text-sm font-bold flex items-center gap-2 mt-1">
              <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M8 10h.01M12 10h.01M16 10h.01M9 16H5a2 2 0 01-2-2V6a2 2 0 012-2h14a2 2 0 012 2v8a2 2 0 01-2 2h-5l-5 5v-5z"></path></svg>
              Sổ Liên Lạc AI
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
