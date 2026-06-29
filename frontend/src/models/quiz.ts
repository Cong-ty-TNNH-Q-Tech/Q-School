/**
 * Quiz, Question, Answer TypeScript Models
 */

export interface Answer {
  id: string
  question_id: string
  answer_text: string
  media_url: string | null
  is_correct?: boolean   // Chỉ trả về cho teacher, ẩn với student
}

export interface Question {
  id: string
  quiz_id: string
  question_text: string
  media_url: string | null
  explanation: string | null
  display_order: number
  answers: Answer[]
}

export interface Quiz {
  id: string
  creator_id: string
  title: string
  content_source: string | null
  question_count?: number
  created_at: string
  updated_at: string
}

export interface QuizWithQuestions extends Quiz {
  questions: Question[]
}

export interface QuizAttempt {
  id: string
  student_id: string
  quiz_id: string
  score: number | null
  started_at: string
  completed_at: string | null
}

export interface StudentAnswer {
  question_id: string
  selected_answer_id: string | null
}

export interface SubmitQuizRequest {
  answers: StudentAnswer[]
}

// Rubric & Essay
export interface RubricCriteria {
  name: string
  description: string
  max_score: number
  levels: Array<{ score: number; description: string }>
}

export interface Rubric {
  id: string
  teacher_id: string
  title: string
  criteria_matrix: { criteria: RubricCriteria[] }
  created_at: string
}

// NOTE — Mở rộng EssaySubmission theo Issue [FE] Essay Submission
// NOTE — ERD chưa có cột image_url và status, FE thêm trước cho UX
// TODO:BACKEND — Cần migration thêm image_url, status vào bảng essay_submissions

export type EssaySubmissionStatus = 'pending' | 'processing' | 'completed' | 'failed'

export interface EssaySubmission {
  id: string
  student_id: string
  teacher_id: string
  rubric_id: string | null
  content: string | null         // null khi submit bằng ảnh (chờ OCR fill)
  image_url: string | null       // URL ảnh bài thi trên S3/R2
  ai_feedback: Record<string, unknown> | null
  score: number | null
  status: EssaySubmissionStatus  // Trạng thái xử lý AI
  created_at: string
}

/**
 * Response từ GET /api/v1/essays/{id}/status
 * Chỉ trả về các trường trạng thái, KHONG trả về toàn bộ EssaySubmission.
 * Frontend phải merge vào state hiện tại (để giữ lại id, content, v.v).
 *
 * TODO:BACKEND — GET /api/v1/essays/{id}/status
 */
export interface EssayStatusResponse {
  status: EssaySubmissionStatus
  ai_feedback: Record<string, unknown> | null
  score: number | null
}

/**
 * Request body khi student submit bài tự luận.
 * Phải có ít nhất 1 trong 2: content HOẶC image_url.
 * rubric_id bắt buộc — Teacher phải tạo Rubric trước.
 *
 * TODO:BACKEND — POST /api/v1/essays/submissions
 * Backend tạo EssaySubmission + AITask, trả HTTP 202.
 */
export interface EssaySubmissionRequest {
  content?: string               // Nhập text trực tiếp
  image_url?: string             // Upload ảnh → S3 URL
  rubric_id: string              // BẮT BUỘC — Teacher tạo trước
  teacher_id?: string            // GV phụ trách (tạm hardcode mock)
}

// Flashcard
export interface FlashcardSet {
  id: string
  creator_id: string
  title: string
  card_count?: number
  created_at: string
}

export interface Flashcard {
  id: string
  set_id: string
  front_text: string
  back_text: string
  media_url: string | null
}

export interface FlashcardReview {
  flashcard_id: string
  confidence_level: 1 | 2 | 3 | 4 | 5
  next_review_at: string | null
}
