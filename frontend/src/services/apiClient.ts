import axios from 'axios'

// Base URL can be configured via environment variables
export const apiClient = axios.create({
  baseURL: import.meta.env.VITE_API_URL || 'http://localhost:8000/api/v1',
  headers: {
    'Content-Type': 'application/json',
  },
})

// Add token to requests
apiClient.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('token')
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
        // Handle unauthenticated
        localStorage.removeItem('token')
        window.location.href = '/login'
      } else if (error.response.status === 402) {
        // Handle payment required (SaaS billing)
        console.warn('Payment Required: Subscription expired or quota reached.')
        // Dispatch custom event or open modal
      } else if (error.response.status === 429) {
        // Handle rate limit
        console.warn('Too Many Requests: Rate limit exceeded.')
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
