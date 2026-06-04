import type { Class, ClassStudent, CreateClassRequest } from '@/models'

// ──────────────────────────────────────────────
// Mock Data
// ──────────────────────────────────────────────
let MOCK_CLASSES: Class[] = [
  {
    id: 'c1',
    teacher_id: '11111111-1111-1111-1111-111111111111',
    name: '10A1 - Toán Nâng Cao',
    grade_level: '10',
    subject: 'Toán',
    created_at: '2023-09-05T00:00:00.000Z',
    student_count: 42,
  },
  {
    id: 'c2',
    teacher_id: '11111111-1111-1111-1111-111111111111',
    name: '11B2 - Vật Lý Cơ Bản',
    grade_level: '11',
    subject: 'Vật Lý',
    created_at: '2023-09-12T00:00:00.000Z',
    student_count: 38,
  },
  {
    id: 'c3',
    teacher_id: '11111111-1111-1111-1111-111111111111',
    name: '12A1 - Ôn thi THPT QG',
    grade_level: '12',
    subject: 'Toán',
    created_at: '2023-10-01T00:00:00.000Z',
    student_count: 45,
  },
  {
    id: 'c4',
    teacher_id: '11111111-1111-1111-1111-111111111111',
    name: '10C4 - Hóa Học Đại Cương',
    grade_level: '10',
    subject: 'Hóa',
    created_at: '2023-10-15T00:00:00.000Z',
    student_count: 40,
  },
  {
    id: 'c5',
    teacher_id: '11111111-1111-1111-1111-111111111111',
    name: '11A1 - Toán Hình Học',
    grade_level: '11',
    subject: 'Toán',
    created_at: '2023-10-20T00:00:00.000Z',
    student_count: 41,
  },
]

let MOCK_CLASS_STUDENTS: ClassStudent[] = [
  { class_id: 'c1', student_id: '22222222-2222-2222-2222-222222222222', joined_at: '2023-09-06T00:00:00.000Z' },
]

// ──────────────────────────────────────────────
// Helpers to simulate network delay
// ──────────────────────────────────────────────
const delay = (ms: number) => new Promise((resolve) => setTimeout(resolve, ms))

// ──────────────────────────────────────────────
// Mock API Functions
// ──────────────────────────────────────────────
export const mockGetClasses = async (teacherId?: string): Promise<Class[]> => {
  await delay(500)
  if (teacherId) {
    return MOCK_CLASSES.filter((c) => c.teacher_id === teacherId)
  }
  return [...MOCK_CLASSES]
}

export const mockGetClassById = async (id: string): Promise<Class> => {
  await delay(300)
  const cls = MOCK_CLASSES.find((c) => c.id === id)
  if (!cls) {
    throw new Error('Class not found')
  }
  return { ...cls }
}

export const mockCreateClass = async (req: CreateClassRequest, teacherId: string): Promise<Class> => {
  await delay(500)
  const newClass: Class = {
    id: `c_${Date.now()}`,
    teacher_id: teacherId,
    name: req.name,
    grade_level: req.grade_level || null,
    subject: req.subject || null,
    created_at: new Date().toISOString(),
    student_count: 0,
  }
  MOCK_CLASSES = [newClass, ...MOCK_CLASSES]
  return { ...newClass }
}

export const mockUpdateClass = async (id: string, req: Partial<CreateClassRequest>): Promise<Class> => {
  await delay(500)
  const index = MOCK_CLASSES.findIndex((c) => c.id === id)
  if (index === -1) {
    throw new Error('Class not found')
  }
  
  MOCK_CLASSES[index] = {
    ...MOCK_CLASSES[index],
    name: req.name ?? MOCK_CLASSES[index].name,
    grade_level: req.grade_level !== undefined ? req.grade_level : MOCK_CLASSES[index].grade_level,
    subject: req.subject !== undefined ? req.subject : MOCK_CLASSES[index].subject,
  }
  return { ...MOCK_CLASSES[index] }
}

export const mockDeleteClass = async (id: string): Promise<void> => {
  await delay(500)
  MOCK_CLASSES = MOCK_CLASSES.filter((c) => c.id !== id)
  MOCK_CLASS_STUDENTS = MOCK_CLASS_STUDENTS.filter((cs) => cs.class_id !== id)
}

export const mockGetClassStudents = async (classId: string): Promise<ClassStudent[]> => {
  await delay(300)
  return MOCK_CLASS_STUDENTS.filter((cs) => cs.class_id === classId)
}

export const mockAddStudentToClass = async (classId: string, studentId: string): Promise<ClassStudent> => {
  await delay(400)
  const exists = MOCK_CLASS_STUDENTS.some((cs) => cs.class_id === classId && cs.student_id === studentId)
  if (exists) {
    throw new Error('Student already in class')
  }
  
  const newMapping: ClassStudent = {
    class_id: classId,
    student_id: studentId,
    joined_at: new Date().toISOString()
  }
  MOCK_CLASS_STUDENTS = [...MOCK_CLASS_STUDENTS, newMapping]
  
  // Update count
  const index = MOCK_CLASSES.findIndex((c) => c.id === classId)
  if (index !== -1) {
    MOCK_CLASSES[index].student_count = (MOCK_CLASSES[index].student_count || 0) + 1
  }
  
  return newMapping
}

export const mockRemoveStudentFromClass = async (classId: string, studentId: string): Promise<void> => {
  await delay(400)
  MOCK_CLASS_STUDENTS = MOCK_CLASS_STUDENTS.filter(
    (cs) => !(cs.class_id === classId && cs.student_id === studentId)
  )
  
  // Update count
  const index = MOCK_CLASSES.findIndex((c) => c.id === classId)
  if (index !== -1) {
    MOCK_CLASSES[index].student_count = Math.max(0, (MOCK_CLASSES[index].student_count || 0) - 1)
  }
}
