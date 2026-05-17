/**
 * User & Auth TypeScript Models
 * Định nghĩa theo chuẩn openapi.yaml — Member Frontend dùng các type này để call API.
 */

// ──────────────────────────────────────────────
// User
// ──────────────────────────────────────────────
export type UserRole = 'student' | 'teacher' | 'admin'

export interface User {
  id: string
  username: string
  email: string
  role: UserRole
  is_active: boolean
  created_at: string
  profile?: Profile
}

export interface Profile {
  user_id: string
  full_name: string | null
  avatar_url: string | null
  school_name: string | null
  bio: string | null
  points: number
}

// ──────────────────────────────────────────────
// Auth Request / Response
// ──────────────────────────────────────────────
export interface LoginRequest {
  email: string
  password: string
}

export interface RegisterRequest {
  username: string
  email: string
  password: string
  role?: UserRole
  full_name?: string
}

export interface AuthTokens {
  access_token: string
  token_type: 'bearer'
  expires_in: number  // Seconds
}

export interface LoginResponse {
  user: User
  tokens: AuthTokens
}

// ──────────────────────────────────────────────
// Standard API Response Wrapper
// Chuẩn: {"status": "success"|"error", "data": T, "message": string, "error_code": number}
// ──────────────────────────────────────────────
export interface ApiResponse<T = unknown> {
  status: 'success' | 'error'
  data: T | null
  message: string
  error_code: number
}

export interface PaginatedResponse<T> {
  status: 'success'
  data: {
    items: T[]
    total: number
    cursor: string | null   // Cursor-based pagination
    has_more: boolean
  }
  message: string
  error_code: 0
}
