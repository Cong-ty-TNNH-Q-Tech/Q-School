/**
 * Lesson TypeScript Models
 */

export interface LessonContent {
  objectives?: string[]
  sections?: Array<{
    title: string
    content: string
    duration_minutes?: number
  }>
  materials?: string[]
  homework?: string
}

export interface Lesson {
  id: string
  teacher_id: string
  title: string
  subject: string | null
  grade_level: string | null
  content: LessonContent | null
  created_at: string
  updated_at: string
}

export interface CreateLessonRequest {
  title: string
  subject?: string
  grade_level?: string
  content?: LessonContent
}

// AI Generate Lesson Plan
export interface GenerateLessonPlanRequest {
  subject: string
  grade_level: string
  topic: string
  duration_minutes?: number
  learning_objectives?: string
}
