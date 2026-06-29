import { Routes, Route, Navigate } from 'react-router-dom'
import MainLayout from '@/views/layouts/MainLayout'
import TeacherDashboard from '@/views/pages/teacher/dashboard/TeacherDashboard'
import StudentDashboard from '@/views/pages/student/dashboard/StudentDashboard'
import Login from '@/views/pages/auth/Login'
import LandingPage from '@/views/pages/landing/LandingPage'
import FlashcardSetList from '@/views/pages/flashcards/FlashcardSetList'
import FlashcardStudy from '@/views/pages/flashcards/FlashcardStudy'
import ClassList from '@/views/pages/classes/ClassList'
import ClassDetail from '@/views/pages/classes/ClassDetail'
import ChatPage from '@/views/pages/chat/ChatPage'
import DocumentPage from '@/views/pages/documents/DocumentPage'
import LessonList from '@/views/pages/lessons/LessonList'
import LessonDetail from '@/views/pages/lessons/LessonDetail'
import LessonEditor from '@/views/pages/lessons/LessonEditor'
import QuizList from '@/views/pages/quizzes/QuizList'
import QuizDetail from '@/views/pages/quizzes/QuizDetail'
import QuizTake from '@/views/pages/quizzes/QuizTake'
import Profile from '@/views/pages/profile/Profile'
import Register from '@/views/pages/auth/Register'
import ForgotPassword from '@/views/pages/auth/ForgotPassword'
import NotFound from '@/views/pages/errors/NotFound'
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
      <Route path="/register" element={<Register />} />
      <Route path="/forgot-password" element={<ForgotPassword />} />
      
      {/* Protected routes */}
      <Route 
        path="/" 
        element={
          <ProtectedRoute>
            <MainLayout />
          </ProtectedRoute>
        }
      >
        <Route path="teacher/dashboard" element={<TeacherDashboard />} />
        <Route path="student/dashboard" element={<StudentDashboard />} />
        <Route path="classes" element={<ClassList />} />
        <Route path="classes/:id" element={<ClassDetail />} />
        <Route path="lessons" element={<LessonList />} />
        <Route path="lessons/new" element={<LessonEditor />} />
        <Route path="lessons/:id" element={<LessonDetail />} />
        <Route path="lessons/:id/edit" element={<LessonEditor />} />
        <Route path="quizzes" element={<QuizList />} />
        <Route path="quizzes/:id" element={<QuizDetail />} />
        <Route path="quizzes/:id/take" element={<QuizTake />} />
        <Route path="chat" element={<ChatPage />} />
        <Route path="flashcards" element={<FlashcardSetList />} />
        <Route path="flashcards/:setId" element={<FlashcardStudy />} />
        <Route path="documents" element={<DocumentPage />} />
        <Route path="profile" element={<Profile />} />
      </Route>

      {/* 404 Not Found */}
      <Route path="*" element={<NotFound />} />
    </Routes>
  )
}
