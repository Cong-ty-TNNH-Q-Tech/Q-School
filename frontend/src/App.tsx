import { Routes, Route, Navigate } from 'react-router-dom'
import MainLayout from '@/views/layouts/MainLayout'
import Dashboard from '@/views/pages/dashboard/Dashboard'
import Login from '@/views/pages/auth/Login'
import LandingPage from '@/views/pages/landing/LandingPage'
import FlashcardSetList from '@/views/pages/flashcards/FlashcardSetList'
import FlashcardStudy from '@/views/pages/flashcards/FlashcardStudy'
import ClassList from '@/views/pages/classes/ClassList'
import ClassDetail from '@/views/pages/classes/ClassDetail'
import ChatPage from '@/views/pages/chat/ChatPage'
import KnowledgeBasePage from '@/views/pages/documents'
import WorksheetGenerator from '@/views/pages/dashboard/WorksheetGenerator'
import { useAuthStore } from '@/stores/useAuthStore'

function ProtectedRoute({ children }: { children: React.ReactNode }) {
  const isAuthenticated = useAuthStore((state) => state.isAuthenticated)
  
  if (!isAuthenticated) {
    return <Navigate to="/login" replace />
  }
  
  return <>{children}</>
}

export default function App() {
  return (
    <Routes>
      {/* Public routes */}
      <Route path="/" element={<LandingPage />} />
      <Route path="/login" element={<Login />} />
      
      {/* Protected routes */}
      <Route 
        path="/dashboard" 
        element={
          <ProtectedRoute>
            <MainLayout />
          </ProtectedRoute>
        }
      >
        <Route index element={<Dashboard />} />
        {/* Flashcards */}
        <Route path="flashcards" element={<FlashcardSetList />} />
        <Route path="flashcards/:setId" element={<FlashcardStudy />} />
        
        {/* Classes */}
        <Route path="classes">
          <Route index element={<ClassList />} />
          <Route path=":id" element={<ClassDetail />} />
        </Route>
        
        {/* AI Chat */}
        <Route path="chat" element={<ChatPage />} />

        {/* Documents / Knowledge Base */}
        <Route path="documents" element={<KnowledgeBasePage />} />
        
        {/* Worksheet Generator */}
        <Route path="worksheet" element={<WorksheetGenerator />} />
      </Route>
    </Routes>
  )
}
