import type { EssaySubmission, EssaySubmissionRequest, Rubric } from '@/models/quiz'

// ============================================================
// [MOCK] Danh sách Rubric — hardcode data
// TODO:BACKEND — Replace with: GET /api/v1/rubrics?teacher_id={id}
// ============================================================
export const MOCK_RUBRICS: Rubric[] = [
  {
    id: 'rubric-1',
    teacher_id: 'teacher-1',
    title: 'Tiêu chí chấm văn Nghị luận xã hội',
    criteria_matrix: { criteria: [] },
    created_at: new Date().toISOString()
  },
  {
    id: 'rubric-2',
    teacher_id: 'teacher-1',
    title: 'Tiêu chí chấm IELTS Writing Task 2',
    criteria_matrix: { criteria: [] },
    created_at: new Date().toISOString()
  }
]

export const getRubricsMock = async (): Promise<Rubric[]> => {
  return new Promise((resolve) => {
    setTimeout(() => resolve([...MOCK_RUBRICS]), 300)
  })
}

// ============================================================
// [MOCK] Upload ảnh bài thi
// TODO:BACKEND — Replace with: POST /api/v1/uploads/image
// ============================================================
export const uploadEssayImageMock = async (
  file: File,
  onProgress?: (progress: number) => void
): Promise<string> => {
  return new Promise((resolve, reject) => {
    // Validate file size (10MB)
    if (file.size > 10 * 1024 * 1024) {
      reject(new Error("File quá lớn (tối đa 10MB)"))
      return
    }

    let progress = 0;
    const interval = setInterval(() => {
      progress += Math.random() * 20 + 10;
      if (progress >= 100) {
        progress = 100;
        clearInterval(interval);
        
        if (onProgress) onProgress(100);
        
        // Mock S3 URL
        const mockUrl = `https://mock-s3-bucket.qschool.vn/essays/${Date.now()}_${file.name}`
        setTimeout(() => resolve(mockUrl), 200);
      } else {
        if (onProgress) onProgress(Math.floor(progress));
      }
    }, 200);
  });
}

// ============================================================
// [MOCK] State lưu trữ submissions
// ============================================================
let mockSubmissions: EssaySubmission[] = []

// ============================================================
// [MOCK] Submit essay
// TODO:BACKEND — Replace with: POST /api/v1/essays/submit
// Request: EssaySubmissionRequest
// Response: EssaySubmission (status: 'pending')
// ============================================================
export const submitEssayMock = async (request: EssaySubmissionRequest): Promise<EssaySubmission> => {
  return new Promise((resolve, reject) => {
    setTimeout(() => {
      if (!request.rubric_id) {
        reject(new Error("Vui lòng chọn tiêu chí đánh giá"))
        return
      }
      
      if (!request.content && !request.image_url) {
        reject(new Error("Vui lòng nhập bài viết hoặc tải ảnh"))
        return
      }

      const newSubmission: EssaySubmission = {
        id: `submission-${Date.now()}`,
        student_id: 'student-1',
        teacher_id: request.teacher_id || 'teacher-1',
        rubric_id: request.rubric_id,
        content: request.content || null,
        image_url: request.image_url || null,
        ai_feedback: null,
        score: null,
        status: 'pending',
        created_at: new Date().toISOString()
      }

      mockSubmissions.push(newSubmission)
      resolve(newSubmission)
    }, 500)
  })
}

// ============================================================
// [MOCK] Poll essay status
// TODO:BACKEND — Replace with: GET /api/v1/essays/{id}/status
// NOTE — Mỗi lần gọi sẽ simulate tiến 1 bước trong pipeline
// ============================================================
export const pollEssayStatusMock = async (id: string): Promise<EssaySubmission | null> => {
  return new Promise(resolve => {
    setTimeout(() => {
      const subIndex = mockSubmissions.findIndex(s => s.id === id)
      if (subIndex === -1) return resolve(null)
      
      const sub = mockSubmissions[subIndex]
      
      // Simulate state transitions: pending -> processing -> graded
      if (sub.status === 'pending') {
        mockSubmissions[subIndex] = { ...sub, status: 'processing' }
      } else if (sub.status === 'processing') {
        mockSubmissions[subIndex] = { 
          ...sub, 
          status: 'graded',
          score: Math.floor(Math.random() * 3) + 7, // 7-9 points
          ai_feedback: {
            summary: "Bài viết có bố cục rõ ràng, lập luận chặt chẽ.",
            strengths: ["Sử dụng từ vựng phong phú", "Lập luận logic"],
            weaknesses: ["Còn một vài lỗi chính tả nhỏ"],
            details: [
              { criterion: "Bố cục", score: 9, comment: "Mở bài, thân bài, kết bài đầy đủ." },
              { criterion: "Ngữ pháp", score: 8, comment: "Ít lỗi ngữ pháp." }
            ]
          }
        }
      }
      
      resolve({ ...mockSubmissions[subIndex] })
    }, 300)
  })
}
