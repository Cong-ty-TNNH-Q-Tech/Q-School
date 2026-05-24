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
  updated_at: string  // ISO datetime — thêm bởi migration 0003
}

// ──────────────────────────────────────────────
// Auth Request / Response
// ──────────────────────────────────────────────
// Backend: POST /auth/login nhận `username` (có thể là username hoặc email)
export interface LoginRequest {
  username: string   // username hoặc email — backend tự detect
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
  refresh_token: string
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
  data: T[]
  next_cursor_created_at: string | null  // Composite cursor — ISO datetime của record cuối
  next_cursor_id: string | null          // UUID tiebreaker của record cuối
  has_more: boolean
  message: string
  error_code: 0
}
