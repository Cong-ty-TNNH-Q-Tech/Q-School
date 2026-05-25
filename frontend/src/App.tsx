import { Routes, Route, Navigate } from 'react-router-dom'
import MainLayout from '@/views/layouts/MainLayout'
import Dashboard from '@/views/pages/dashboard/Dashboard'
import Login from '@/views/pages/auth/Login'
import LandingPage from '@/views/pages/landing/LandingPage'
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
        {/* Add more protected routes here */}
      </Route>
    </Routes>
  )
}
