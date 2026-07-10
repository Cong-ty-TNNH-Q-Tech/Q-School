import { describe, it, expect, beforeEach } from 'vitest'
import { useAdminDashboard } from '../useAdminDashboard'
import { mockAdminDashboardResponse } from '../../services/mockData/admin_dashboard.mock'

describe('useAdminDashboard', () => {
  beforeEach(() => {
    // Reset state của Zustand store trước mỗi test case
    useAdminDashboard.setState({
      data: null,
      isLoading: false,
      error: null
    })
  })

  it('T1: Trạng thái ban đầu chính xác', () => {
    const state = useAdminDashboard.getState()
    expect(state.data).toBeNull()
    expect(state.isLoading).toBeFalsy()
    expect(state.error).toBeNull()
  })

  it('T2: Tải thành công dữ liệu mock', async () => {
    const store = useAdminDashboard.getState()
    
    // Gọi fetch
    const fetchPromise = store.fetchDashboardData()
    
    // Kiểm tra isLoading thành true ngay lập tức
    expect(useAdminDashboard.getState().isLoading).toBeTruthy()
    expect(useAdminDashboard.getState().error).toBeNull()

    // Chờ fetch hoàn tất
    await fetchPromise

    const state = useAdminDashboard.getState()
    expect(state.isLoading).toBeFalsy()
    expect(state.data).toEqual(mockAdminDashboardResponse.data)
    expect(state.error).toBeNull()
  })

  it('T3: Xử lý lỗi khi status phản hồi không phải success', async () => {
    // Lưu tạm phản hồi cũ để khôi phục
    const originalStatus = mockAdminDashboardResponse.status
    const originalMessage = mockAdminDashboardResponse.message
    
    // Thay đổi mock response thành lỗi
    ;(mockAdminDashboardResponse as { status: string }).status = 'error'
    mockAdminDashboardResponse.message = 'Lỗi kết nối database'

    try {
      const store = useAdminDashboard.getState()
      await store.fetchDashboardData()

      const state = useAdminDashboard.getState()
      expect(state.isLoading).toBeFalsy()
      expect(state.data).toBeNull()
      expect(state.error).toBe('Lỗi kết nối database')
    } finally {
      // Khôi phục lại mock response ban đầu
      ;(mockAdminDashboardResponse as { status: string }).status = originalStatus
      mockAdminDashboardResponse.message = originalMessage
    }
  })
})
