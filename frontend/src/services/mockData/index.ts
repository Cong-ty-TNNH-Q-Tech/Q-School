/**
 * Mock Data Index — Export tất cả mock functions.
 *
 * Quy tắc dùng Mock:
 * 1. Chỉ dùng trong development khi Backend chưa có endpoint tương ứng
 * 2. Khi Backend sẵn sàng, thay mock call bằng apiClient call
 * 3. Không import mock trong production code — dùng env flag nếu cần
 */
export * from './auth.mock'

// TODO: Thêm mock data khi implement các nhóm tính năng
export * from './class.mock'
export * from './lesson.mock'
// export * from './quiz.mock'
// export * from './ai.mock'
export * from './essay.mock'
export * from './admin_dashboard.mock'
