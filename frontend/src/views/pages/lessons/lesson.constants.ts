/**
 * Shared constants cho Lesson pages.
 * Dùng chung giữa LessonList (filter) và LessonEditor (form select).
 */
export const SUBJECT_OPTIONS = [
  { value: 'Toán', label: 'Toán' },
  { value: 'Vật Lý', label: 'Vật Lý' },
  { value: 'Hóa', label: 'Hóa Học' },
  { value: 'Sinh Học', label: 'Sinh Học' },
  { value: 'Ngữ Văn', label: 'Ngữ Văn' },
  { value: 'Tiếng Anh', label: 'Tiếng Anh' },
  { value: 'Lịch Sử', label: 'Lịch Sử' },
  { value: 'Địa Lý', label: 'Địa Lý' },
] as const

export const GRADE_OPTIONS = [
  { value: '10', label: 'Khối 10' },
  { value: '11', label: 'Khối 11' },
  { value: '12', label: 'Khối 12' },
] as const
