import axios from 'axios'
import { useAuthStore } from '@/stores/useAuthStore'

// Base URL can be configured via environment variables
export const apiClient = axios.create({
  baseURL: import.meta.env.VITE_API_URL || 'http://localhost:8000/api/v1',
  headers: {
    'Content-Type': 'application/json',
  },
})

// Add token to requests — đọc từ Zustand store (source of truth), không đọc localStorage trực tiếp
apiClient.interceptors.request.use(
  (config) => {
    const token = useAuthStore.getState().accessToken   // accessToken, không phải 'token'
    if (token && config.headers) {
      config.headers.Authorization = `Bearer ${token}`
    }
    return config
  },
  (error) => Promise.reject(error)
)

// Intercept responses for global errors like 401, 402, 429
apiClient.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response) {
      if (error.response.status === 401) {
        // Clear cả Zustand store lẫn localStorage để tránh race condition
        useAuthStore.getState().logout()
        // Tránh redirect loop nếu đang ở trang /login
        if (!window.location.pathname.startsWith('/login')) {
          window.location.href = '/login'
        }
      } else if (error.response.status === 402) {
        // Dispatch custom event để UI layer (Modal, Toast) bắt và hiển thị upgrade prompt
        window.dispatchEvent(new CustomEvent('qschool:payment-required', {
          detail: { error_code: error.response.data?.error_code }
        }))
      } else if (error.response.status === 429) {
        // Dispatch custom event để UI layer hiển thị rate limit toast
        window.dispatchEvent(new CustomEvent('qschool:rate-limited', {
          detail: { retry_after: error.response.headers?.['retry-after'] }
        }))
      }
    }
    return Promise.reject(error)
  }
)

/**
 * Mock API Helper for frontend parallel development.
 * Automatically wraps response in openapi.yaml standard format:
 * {"status": "success", "data": ...}
 */
export const mockApiResponse = <T>(data: T, delayMs = 500): Promise<{ status: string; data: T }> => {
  return new Promise((resolve) => {
    setTimeout(() => resolve({ status: 'success', data }), delayMs)
  })
}
