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

export interface EssaySubmission {
  id: string
  student_id: string
  teacher_id: string
  rubric_id: string | null
  content: string
  ai_feedback: Record<string, unknown> | null
  score: number | null
  created_at: string
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
