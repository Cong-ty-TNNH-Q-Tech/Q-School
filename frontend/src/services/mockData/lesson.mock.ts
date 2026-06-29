import type { Lesson, CreateLessonRequest, UpdateLessonRequest } from '@/models'

// ──────────────────────────────────────────────
// Mock Data
// ──────────────────────────────────────────────
let MOCK_LESSONS: Lesson[] = [
  {
    id: 'l1',
    teacher_id: '11111111-1111-1111-1111-111111111111',
    teacher_name: 'Nguyễn Văn A',
    title: 'Giới hạn và Liên tục',
    subject: 'Toán',
    grade_level: '11',
    created_at: '2023-09-05T00:00:00.000Z',
    updated_at: '2023-09-05T00:00:00.000Z',
    content: {
      objectives: ['Hiểu khái niệm giới hạn của dãy số và hàm số', 'Biết cách tính giới hạn cơ bản', 'Hiểu định nghĩa hàm số liên tục'],
      sections: [
        { title: 'Khởi động', content: 'Ôn tập lại dãy số và hàm số.', duration_minutes: 5 },
        { title: 'Giới hạn của dãy số', content: 'Định nghĩa và các định lý cơ bản.', duration_minutes: 15 },
        { title: 'Giới hạn của hàm số', content: 'Định nghĩa và bài tập ví dụ.', duration_minutes: 15 },
        { title: 'Hàm số liên tục', content: 'Định nghĩa và điều kiện liên tục tại một điểm.', duration_minutes: 10 }
      ],
      materials: ['SGK Toán 11 Tập 1', 'Máy tính cầm tay'],
      homework: 'Làm bài tập 1, 2, 3 trang 120 SGK.'
    }
  },
  {
    id: 'l2',
    teacher_id: '11111111-1111-1111-1111-111111111111',
    teacher_name: 'Nguyễn Văn A',
    title: 'Đạo hàm',
    subject: 'Toán',
    grade_level: '11',
    created_at: '2023-09-12T00:00:00.000Z',
    updated_at: '2023-09-12T00:00:00.000Z',
    content: {
      objectives: ['Hiểu ý nghĩa của đạo hàm', 'Tính được đạo hàm của các hàm số cơ bản'],
      sections: [
        { title: 'Định nghĩa', content: 'Đạo hàm tại một điểm.', duration_minutes: 15 },
        { title: 'Quy tắc tính đạo hàm', content: 'Đạo hàm của tổng, hiệu, tích, thương.', duration_minutes: 20 },
        { title: 'Luyện tập', content: 'Làm bài tập nhóm.', duration_minutes: 10 }
      ],
      materials: ['SGK Toán 11', 'Phiếu bài tập'],
      homework: 'Hoàn thành phiếu bài tập số 2.'
    }
  },
  {
    id: 'l3',
    teacher_id: '11111111-1111-1111-1111-111111111111',
    teacher_name: 'Nguyễn Văn A',
    title: 'Tích phân',
    subject: 'Toán',
    grade_level: '12',
    created_at: '2023-10-01T00:00:00.000Z',
    updated_at: '2023-10-01T00:00:00.000Z',
    content: {
      objectives: ['Hiểu khái niệm tích phân', 'Tính được tích phân của các hàm số cơ bản'],
      sections: [
        { title: 'Nguyên hàm', content: 'Định nghĩa nguyên hàm.', duration_minutes: 15 },
        { title: 'Tích phân', content: 'Công thức Newton-Leibniz.', duration_minutes: 20 },
        { title: 'Bài tập', content: 'Giải bài tập mẫu.', duration_minutes: 10 }
      ],
      materials: ['SGK Toán 12'],
      homework: 'Làm bài tập 1 đến 5 trang 80.'
    }
  },
  {
    id: 'l4',
    teacher_id: '11111111-1111-1111-1111-111111111111',
    teacher_name: 'Nguyễn Văn A',
    title: 'Chuyển động Newton',
    subject: 'Vật Lý',
    grade_level: '10',
    created_at: '2023-10-15T00:00:00.000Z',
    updated_at: '2023-10-15T00:00:00.000Z',
    content: {
      objectives: ['Hiểu ba định luật Newton', 'Vận dụng định luật vào bài toán thực tế'],
      sections: [
        { title: 'Định luật I', content: 'Quán tính.', duration_minutes: 10 },
        { title: 'Định luật II', content: 'F = ma.', duration_minutes: 15 },
        { title: 'Định luật III', content: 'Lực và phản lực.', duration_minutes: 10 },
        { title: 'Thực hành', content: 'Làm thí nghiệm ảo.', duration_minutes: 10 }
      ],
      materials: ['SGK Vật Lý 10', 'Phần mềm mô phỏng PhET'],
      homework: 'Viết báo cáo thí nghiệm.'
    }
  },
  {
    id: 'l5',
    teacher_id: '11111111-1111-1111-1111-111111111111',
    teacher_name: 'Nguyễn Văn A',
    title: 'Cấu tạo nguyên tử',
    subject: 'Hóa',
    grade_level: '10',
    created_at: '2023-10-20T00:00:00.000Z',
    updated_at: '2023-10-20T00:00:00.000Z',
    content: {
      objectives: ['Nắm được thành phần cấu tạo nguyên tử', 'Hiểu về đồng vị'],
      sections: [
        { title: 'Thành phần nguyên tử', content: 'Proton, nơtron, electron.', duration_minutes: 20 },
        { title: 'Đồng vị', content: 'Định nghĩa và bài tập tính nguyên tử khối trung bình.', duration_minutes: 25 }
      ],
      materials: ['SGK Hóa 10', 'Bảng tuần hoàn'],
      homework: 'Bài tập 2, 4 trang 20 SGK.'
    }
  }
]

// ──────────────────────────────────────────────
// Helpers to simulate network delay
// ──────────────────────────────────────────────
const delay = (ms: number) => new Promise((resolve) => setTimeout(resolve, ms))

// ──────────────────────────────────────────────
// Mock API Functions
// ──────────────────────────────────────────────
export const mockGetLessons = async (teacherId?: string): Promise<Lesson[]> => {
  await delay(500)
  if (teacherId) {
    return MOCK_LESSONS.filter((l) => l.teacher_id === teacherId)
  }
  return [...MOCK_LESSONS]
}

export const mockGetLessonById = async (id: string): Promise<Lesson> => {
  await delay(300)
  const lesson = MOCK_LESSONS.find((l) => l.id === id)
  if (!lesson) {
    throw new Error('Lesson not found')
  }
  return { ...lesson }
}

export const mockCreateLesson = async (req: CreateLessonRequest, teacherId: string): Promise<Lesson> => {
  await delay(500)
  const newLesson: Lesson = {
    id: `l_${Date.now()}`,
    teacher_id: teacherId,
    teacher_name: 'Nguyễn Văn A',
    title: req.title,
    subject: req.subject || null,
    grade_level: req.grade_level || null,
    content: req.content || null,
    created_at: new Date().toISOString(),
    updated_at: new Date().toISOString(),
  }
  MOCK_LESSONS = [newLesson, ...MOCK_LESSONS]
  return { ...newLesson }
}

export const mockUpdateLesson = async (id: string, req: UpdateLessonRequest): Promise<Lesson> => {
  await delay(500)
  const index = MOCK_LESSONS.findIndex((l) => l.id === id)
  if (index === -1) {
    throw new Error('Lesson not found')
  }
  
  MOCK_LESSONS[index] = {
    ...MOCK_LESSONS[index],
    title: req.title !== undefined ? req.title : MOCK_LESSONS[index].title,
    subject: req.subject !== undefined ? req.subject : MOCK_LESSONS[index].subject,
    grade_level: req.grade_level !== undefined ? req.grade_level : MOCK_LESSONS[index].grade_level,
    content: req.content !== undefined ? req.content : MOCK_LESSONS[index].content,
    updated_at: new Date().toISOString()
  }
  return { ...MOCK_LESSONS[index] }
}

export const mockDeleteLesson = async (id: string): Promise<void> => {
  await delay(500)
  MOCK_LESSONS = MOCK_LESSONS.filter((l) => l.id !== id)
}
