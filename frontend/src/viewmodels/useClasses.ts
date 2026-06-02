import { create } from 'zustand'
import type { Class, ClassStudent, CreateClassRequest } from '@/models'
import {
  mockGetClasses,
  mockGetClassById,
  mockCreateClass,
  mockUpdateClass,
  mockDeleteClass,
  mockGetClassStudents,
  mockAddStudentToClass,
  mockRemoveStudentFromClass
} from '@/services/mockData/class.mock'

interface ClassesState {
  classes: Class[]
  selectedClass: Class | null
  classStudents: ClassStudent[]
  isLoading: boolean
  error: string | null

  fetchClasses: (teacherId?: string) => Promise<void>
  fetchClassDetail: (id: string) => Promise<void>
  createClass: (req: CreateClassRequest, teacherId: string) => Promise<void>
  updateClass: (id: string, req: Partial<CreateClassRequest>) => Promise<void>
  deleteClass: (id: string) => Promise<void>
  fetchClassStudents: (classId: string) => Promise<void>
  addStudent: (classId: string, studentId: string) => Promise<void>
  removeStudent: (classId: string, studentId: string) => Promise<void>
}

export const useClasses = create<ClassesState>((set, get) => ({
  classes: [],
  selectedClass: null,
  classStudents: [],
  isLoading: false,
  error: null,

  fetchClasses: async (teacherId) => {
    set({ isLoading: true, error: null })
    try {
      const data = await mockGetClasses(teacherId)
      set({ classes: data })
    } catch (err: unknown) {
      set({ error: (err as Error).message || 'Lỗi khi lấy danh sách lớp học' })
    } finally {
      set({ isLoading: false })
    }
  },

  fetchClassDetail: async (id) => {
    set({ isLoading: true, error: null })
    try {
      const cls = await mockGetClassById(id)
      set({ selectedClass: cls })
    } catch (err: unknown) {
      set({ error: (err as Error).message || 'Lỗi khi lấy thông tin lớp học' })
    } finally {
      set({ isLoading: false })
    }
  },

  createClass: async (req, teacherId) => {
    set({ isLoading: true, error: null })
    try {
      const newCls = await mockCreateClass(req, teacherId)
      set({ classes: [newCls, ...get().classes] })
    } catch (err: unknown) {
      set({ error: (err as Error).message || 'Lỗi khi tạo lớp học' })
      throw err
    } finally {
      set({ isLoading: false })
    }
  },

  updateClass: async (id, req) => {
    set({ isLoading: true, error: null })
    try {
      const updatedCls = await mockUpdateClass(id, req)
      set({
        classes: get().classes.map((c) => (c.id === id ? updatedCls : c)),
        selectedClass: get().selectedClass?.id === id ? updatedCls : get().selectedClass
      })
    } catch (err: unknown) {
      set({ error: (err as Error).message || 'Lỗi khi cập nhật lớp học' })
      throw err
    } finally {
      set({ isLoading: false })
    }
  },

  deleteClass: async (id) => {
    set({ isLoading: true, error: null })
    try {
      await mockDeleteClass(id)
      set({ classes: get().classes.filter((c) => c.id !== id) })
    } catch (err: unknown) {
      set({ error: (err as Error).message || 'Lỗi khi xóa lớp học' })
      throw err
    } finally {
      set({ isLoading: false })
    }
  },

  fetchClassStudents: async (classId) => {
    set({ isLoading: true, error: null })
    try {
      const students = await mockGetClassStudents(classId)
      set({ classStudents: students })
    } catch (err: unknown) {
      set({ error: (err as Error).message || 'Lỗi khi lấy danh sách học sinh' })
    } finally {
      set({ isLoading: false })
    }
  },

  addStudent: async (classId, studentId) => {
    set({ isLoading: true, error: null })
    try {
      const newStudent = await mockAddStudentToClass(classId, studentId)
      set({ classStudents: [...get().classStudents, newStudent] })
      // Update count locally
      const cls = get().selectedClass
      if (cls && cls.id === classId) {
        set({ selectedClass: { ...cls, student_count: (cls.student_count || 0) + 1 } })
      }
    } catch (err: unknown) {
      set({ error: (err as Error).message || 'Lỗi khi thêm học sinh' })
      throw err
    } finally {
      set({ isLoading: false })
    }
  },

  removeStudent: async (classId, studentId) => {
    set({ isLoading: true, error: null })
    try {
      await mockRemoveStudentFromClass(classId, studentId)
      set({
        classStudents: get().classStudents.filter((cs) => cs.student_id !== studentId)
      })
      // Update count locally
      const cls = get().selectedClass
      if (cls && cls.id === classId) {
        set({ selectedClass: { ...cls, student_count: Math.max(0, (cls.student_count || 0) - 1) } })
      }
    } catch (err: unknown) {
      set({ error: (err as Error).message || 'Lỗi khi xóa học sinh' })
      throw err
    } finally {
      set({ isLoading: false })
    }
  }
}))
