import { create } from 'zustand'
import type { Lesson, CreateLessonRequest, UpdateLessonRequest } from '@/models'
import {
  mockGetLessons,
  mockGetLessonById,
  mockCreateLesson,
  mockUpdateLesson,
  mockDeleteLesson
} from '@/services/mockData'

interface LessonsState {
  lessons: Lesson[]
  selectedLesson: Lesson | null
  isLoading: boolean
  error: string | null

  fetchLessons: (teacherId?: string) => Promise<void>
  fetchLessonDetail: (id: string) => Promise<void>
  createLesson: (req: CreateLessonRequest, teacherId: string) => Promise<void>
  updateLesson: (id: string, req: UpdateLessonRequest) => Promise<void>
  deleteLesson: (id: string) => Promise<void>
}

export const useLessons = create<LessonsState>((set, get) => ({
  lessons: [],
  selectedLesson: null,
  isLoading: false,
  error: null,

  fetchLessons: async (teacherId) => {
    set({ isLoading: true, error: null })
    try {
      const data = await mockGetLessons(teacherId)
      set({ lessons: data })
    } catch (err: unknown) {
      set({ error: (err as Error).message || 'Lỗi khi lấy danh sách bài giảng' })
    } finally {
      set({ isLoading: false })
    }
  },

  fetchLessonDetail: async (id) => {
    set({ isLoading: true, error: null })
    try {
      const lesson = await mockGetLessonById(id)
      set({ selectedLesson: lesson })
    } catch (err: unknown) {
      set({ error: (err as Error).message || 'Lỗi khi lấy thông tin bài giảng' })
    } finally {
      set({ isLoading: false })
    }
  },

  createLesson: async (req, teacherId) => {
    set({ isLoading: true, error: null })
    try {
      const newLesson = await mockCreateLesson(req, teacherId)
      set({ lessons: [newLesson, ...get().lessons] })
    } catch (err: unknown) {
      set({ error: (err as Error).message || 'Lỗi khi tạo bài giảng' })
      throw err
    } finally {
      set({ isLoading: false })
    }
  },

  updateLesson: async (id, req) => {
    set({ isLoading: true, error: null })
    try {
      const updatedLesson = await mockUpdateLesson(id, req)
      set({
        lessons: get().lessons.map((l) => (l.id === id ? updatedLesson : l)),
        selectedLesson: get().selectedLesson?.id === id ? updatedLesson : get().selectedLesson
      })
    } catch (err: unknown) {
      set({ error: (err as Error).message || 'Lỗi khi cập nhật bài giảng' })
      throw err
    } finally {
      set({ isLoading: false })
    }
  },

  deleteLesson: async (id) => {
    set({ isLoading: true, error: null })
    try {
      await mockDeleteLesson(id)
      set({ lessons: get().lessons.filter((l) => l.id !== id) })
    } catch (err: unknown) {
      set({ error: (err as Error).message || 'Lỗi khi xóa bài giảng' })
      throw err
    } finally {
      set({ isLoading: false })
    }
  }
}))
