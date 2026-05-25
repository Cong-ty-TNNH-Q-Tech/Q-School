/**
 * Mock Data — Auth & User
 * Dùng khi Backend chưa sẵn sàng. Mock theo chuẩn ApiResponse.
 *
 * Sử dụng:
 *   import { mockLogin } from '@/services/mockData'
 *   const response = await mockLogin({ email, password })
 */
import type { LoginRequest, LoginResponse, User } from '@/models'

// ──────────────────────────────────────────────
// Mock Users (Dữ liệu test)
// ──────────────────────────────────────────────
const MOCK_USERS: Array<User & { password: string }> = [
  {
    id: '11111111-1111-1111-1111-111111111111',
    username: 'giaovien01',
    email: 'teacher@qschool.vn',
    password: '123456',
    role: 'teacher',
    is_active: true,
    created_at: new Date().toISOString(),
    profile: {
      user_id: '11111111-1111-1111-1111-111111111111',
      full_name: 'Nguyễn Thị Lan',
      avatar_url: null,
      school_name: 'Trường THPT Nguyễn Du',
      bio: 'Giáo viên Toán với 10 năm kinh nghiệm',
      points: 150,
      updated_at: new Date().toISOString(),
    },
  },
  {
    id: '22222222-2222-2222-2222-222222222222',
    username: 'hocsinh01',
    email: 'student@qschool.vn',
    password: '123456',
    role: 'student',
    is_active: true,
    created_at: new Date().toISOString(),
    profile: {
      user_id: '22222222-2222-2222-2222-222222222222',
      full_name: 'Trần Văn Minh',
      avatar_url: null,
      school_name: 'Trường THPT Nguyễn Du',
      bio: null,
      points: 320,
      updated_at: new Date().toISOString(),
    },
  },
]

// ──────────────────────────────────────────────
// Mock API Functions
// ──────────────────────────────────────────────
export const mockLogin = async (req: LoginRequest): Promise<LoginResponse> => {
  // Backend cho ph\u00e9p login b\u1eb1ng username ho\u1eb7c email \u2014 mock t\u01b0\u01a1ng t\u1ef1
  const user = MOCK_USERS.find(
    (u) => (u.email === req.username || u.username === req.username) && u.password === req.password
  )

  if (!user) {
    throw {
      response: {
        status: 401,
        data: {
          status: 'error',
          data: null,
          message: 'Email hoặc mật khẩu không đúng',
          error_code: 4010,
        },
      },
    }
  }

  const { password: _, ...safeUser } = user

  return {
    user: safeUser,
    tokens: {
      access_token: `mock_token_${safeUser.id}_${Date.now()}`,
      refresh_token: `mock_refresh_${safeUser.id}_${Date.now()}`,
      token_type: 'bearer',
      expires_in: 900, // 15 phút
    },
  }
}

export const mockGetCurrentUser = async (userId: string): Promise<User> => {
  const user = MOCK_USERS.find((u) => u.id === userId)
  if (!user) throw new Error('User not found')
  const { password: _, ...safeUser } = user
  return safeUser
}
