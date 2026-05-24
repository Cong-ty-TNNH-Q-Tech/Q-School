import { create } from 'zustand'
import { persist } from 'zustand/middleware'
import type { User } from '@/models'

interface AuthState {
  user: User | null
  accessToken: string | null
  isAuthenticated: boolean
  login: (user: User, accessToken: string) => void
  logout: () => void
  setUser: (user: User) => void
}

export const useAuthStore = create<AuthState>()(
  persist(
    (set) => ({
      user: null,
      accessToken: null,
      isAuthenticated: false,

      login: (user, accessToken) => {
        // persist middleware tự động lưu vào localStorage qua key 'qschool-auth'
        // localStorage.setItem('token', accessToken) — để backward compat với code cũ dùng getItem('token')
        localStorage.setItem('token', accessToken)
        set({ user, accessToken, isAuthenticated: true })
      },

      logout: () => {
        localStorage.removeItem('token')
        set({ user: null, accessToken: null, isAuthenticated: false })
      },

      setUser: (user) => set({ user }),
    }),
    {
      name: 'qschool-auth',            // Key trong localStorage
      partialize: (state) => ({        // Chỉ persist những gì cần thiết
        user: state.user,
        accessToken: state.accessToken,
        isAuthenticated: state.isAuthenticated,
      }),
    }
  )
)

