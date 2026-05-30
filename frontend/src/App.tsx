import { Routes, Route, Navigate } from 'react-router-dom'
import MainLayout from '@/views/layouts/MainLayout'
import { useAuthStore } from '@/stores/useAuthStore'

// Public pages
import LandingPage from '@/views/pages/landing/LandingPage'
import Login from '@/views/pages/auth/Login'
import Register from '@/views/pages/auth/Register'
import ForgotPassword from '@/views/pages/auth/ForgotPassword'

// Protected pages
import Dashboard from '@/views/pages/dashboard/Dashboard'
import ClassList from '@/views/pages/classes/ClassList'
import ClassDetail from '@/views/pages/classes/ClassDetail'
import LessonList from '@/views/pages/lessons/LessonList'
import LessonDetail from '@/views/pages/lessons/LessonDetail'
import QuizList from '@/views/pages/quizzes/QuizList'
import QuizDetail from '@/views/pages/quizzes/QuizDetail'
import QuizTake from '@/views/pages/quizzes/QuizTake'
import Chat from '@/views/pages/chat/Chat'
import Flashcards from '@/views/pages/flashcards/Flashcards'
import Documents from '@/views/pages/documents/Documents'
import Profile from '@/views/pages/profile/Profile'

// Error pages
import NotFound from '@/views/pages/errors/NotFound'

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
      <Route path="/register" element={<Register />} />
      <Route path="/forgot-password" element={<ForgotPassword />} />

      {/* Protected routes — wrapped in MainLayout */}
      <Route
        element={
          <ProtectedRoute>
            <MainLayout />
          </ProtectedRoute>
        }
      >
        <Route path="/dashboard" element={<Dashboard />} />
        <Route path="/classes" element={<ClassList />} />
        <Route path="/classes/:id" element={<ClassDetail />} />
        <Route path="/lessons" element={<LessonList />} />
        <Route path="/lessons/:id" element={<LessonDetail />} />
        <Route path="/quizzes" element={<QuizList />} />
        <Route path="/quizzes/:id" element={<QuizDetail />} />
        <Route path="/quizzes/:id/take" element={<QuizTake />} />
        <Route path="/chat" element={<Chat />} />
        <Route path="/flashcards" element={<Flashcards />} />
        <Route path="/documents" element={<Documents />} />
        <Route path="/profile" element={<Profile />} />
      </Route>

      {/* 404 Not Found */}
      <Route path="*" element={<NotFound />} />
    </Routes>
  )
}
