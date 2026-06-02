import { describe, it, expect, beforeEach, vi } from 'vitest'
import { renderHook, act } from '@testing-library/react'
import { useClasses } from './useClasses'
import * as mockAPI from '@/services/mockData/class.mock'

vi.mock('@/services/mockData/class.mock', () => ({
  mockGetClasses: vi.fn(),
  mockGetClassById: vi.fn(),
  mockCreateClass: vi.fn(),
  mockUpdateClass: vi.fn(),
  mockDeleteClass: vi.fn(),
  mockGetClassStudents: vi.fn(),
  mockAddStudentToClass: vi.fn(),
  mockRemoveStudentFromClass: vi.fn(),
}))

const dummyClass = { id: 'c1', name: 'Lớp 10A1', grade_level: '10', subject: 'Toán', created_at: '2023', updated_at: '2023', teacher_id: 't1', student_count: 0 }
const dummyStudent = { id: 'cs1', class_id: 'c1', student_id: 's1', joined_at: '2023' }

describe('useClasses ViewModel', () => {
  beforeEach(() => {
    vi.clearAllMocks()
    useClasses.setState({
      classes: [],
      selectedClass: null,
      classStudents: [],
      isLoading: false,
      error: null,
    })
  })

  it('should initialize with default state', () => {
    const { result } = renderHook(() => useClasses())
    expect(result.current.classes).toEqual([])
    expect(result.current.isLoading).toBe(false)
    expect(result.current.error).toBeNull()
  })

  it('fetchClasses updates classes on success', async () => {
    vi.mocked(mockAPI.mockGetClasses).mockResolvedValue([dummyClass])
    const { result } = renderHook(() => useClasses())

    await act(async () => {
      await result.current.fetchClasses('t1')
    })

    expect(mockAPI.mockGetClasses).toHaveBeenCalledWith('t1')
    expect(result.current.classes).toEqual([dummyClass])
    expect(result.current.error).toBeNull()
  })

  it('fetchClasses sets error on failure', async () => {
    vi.mocked(mockAPI.mockGetClasses).mockRejectedValue(new Error('Network error'))
    const { result } = renderHook(() => useClasses())

    await act(async () => {
      await result.current.fetchClasses('t1')
    })

    expect(result.current.error).toBe('Network error')
  })

  it('createClass adds a new class to the top of the list', async () => {
    vi.mocked(mockAPI.mockCreateClass).mockResolvedValue(dummyClass)
    const { result } = renderHook(() => useClasses())

    await act(async () => {
      await result.current.createClass({ name: 'Lớp 10A1' }, 't1')
    })

    expect(mockAPI.mockCreateClass).toHaveBeenCalled()
    expect(result.current.classes).toHaveLength(1)
    expect(result.current.classes[0]).toEqual(dummyClass)
  })

  it('deleteClass removes a class from the list', async () => {
    useClasses.setState({ classes: [dummyClass] })
    vi.mocked(mockAPI.mockDeleteClass).mockResolvedValue(undefined)
    const { result } = renderHook(() => useClasses())

    await act(async () => {
      await result.current.deleteClass('c1')
    })

    expect(mockAPI.mockDeleteClass).toHaveBeenCalledWith('c1')
    expect(result.current.classes).toHaveLength(0)
  })

  it('addStudent updates classStudents and increments student_count', async () => {
    useClasses.setState({ selectedClass: dummyClass, classStudents: [] })
    vi.mocked(mockAPI.mockAddStudentToClass).mockResolvedValue(dummyStudent)
    const { result } = renderHook(() => useClasses())

    await act(async () => {
      await result.current.addStudent('c1', 's1')
    })

    expect(result.current.classStudents).toContainEqual(dummyStudent)
    expect(result.current.selectedClass?.student_count).toBe(1)
  })
})
