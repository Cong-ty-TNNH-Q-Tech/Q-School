/**
 * Class TypeScript Models
 */

export interface Class {
  id: string
  teacher_id: string
  name: string
  grade_level: string | null
  subject: string | null
  created_at: string
  student_count?: number
}

export interface ClassStudent {
  class_id: string
  student_id: string
  joined_at: string
}

export interface ClassAssignment {
  id: string
  class_id: string
  resource_type: 'lesson' | 'quiz'
  resource_id: string
  unlock_date: string | null
  due_date: string | null
  created_at: string
}

export interface CreateClassRequest {
  name: string
  grade_level?: string
  subject?: string
}
