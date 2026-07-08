import { renderHook, act } from '@testing-library/react'
import { describe, it, expect, vi, beforeEach, afterEach } from 'vitest'
import { useYouTubeQuestions } from '../useYouTubeQuestions'
import { extractMockYouTubeInfo, getMockYouTubeQuestions } from '../../services/mockData'
import type { YouTubeQuestion } from '@/models/ai'
import { PaymentRequiredError, TooManyRequestsError } from '@/utils/aiApiError'

vi.mock('../../services/mockData', () => ({
  extractMockYouTubeInfo: vi.fn(),
  getMockYouTubeQuestions: vi.fn(),
}))

const VALID_YT_URL = 'https://youtube.com/watch?v=dQw4w9WgXcQ'

const mockVideoInfo = {
  title: 'Test Video',
  duration: '10:00',
  thumbnail_url: 'https://img.youtube.com/vi/test/maxresdefault.jpg'
}

const mockQuestion: YouTubeQuestion = {
  id: '1',
  type: 'mcq',
  question_text: 'What is covered in this video?',
  timestamp: '02:30',
  timestamp_seconds: 150,
  options: ['Option A', 'Option B', 'Option C', 'Option D'],
  correct_answer: 'Option A',
}

describe('useYouTubeQuestions', () => {
  beforeEach(() => {
    vi.useFakeTimers()
    vi.clearAllMocks()
    vi.mocked(extractMockYouTubeInfo).mockResolvedValue(mockVideoInfo)
    vi.mocked(getMockYouTubeQuestions).mockResolvedValue({ status: 'success', data: [mockQuestion] })
  })

  afterEach(() => {
    vi.clearAllTimers()
    vi.useRealTimers()
  })

  it('T1-T3: validateUrl - valid và invalid URLs', () => {
    const { result } = renderHook(() => useYouTubeQuestions())
    expect(result.current.validateUrl('https://www.youtube.com/watch?v=dQw4w9WgXcQ')).toBe(true)
    expect(result.current.validateUrl('https://youtu.be/dQw4w9WgXcQ')).toBe(true)
    expect(result.current.validateUrl('invalid-url')).toBe(false)
    expect(result.current.validateUrl('')).toBe(false)
  })

  it('T4: generate() với URL rỗng → set error', async () => {
    const { result } = renderHook(() => useYouTubeQuestions())

    await act(async () => { await result.current.generate() })

    expect(result.current.error).toBe('Vui lòng nhập đường dẫn YouTube')
  })

  it('T5: generate() với URL không hợp lệ → set error', async () => {
    const { result } = renderHook(() => useYouTubeQuestions())

    act(() => { result.current.setYoutubeUrl('https://google.com') })
    await act(async () => { await result.current.generate() })

    expect(result.current.error).toBe('Đường dẫn YouTube không hợp lệ')
  })

  it('T6: generate() với questionCount < 5 → set error', async () => {
    const { result } = renderHook(() => useYouTubeQuestions())

    act(() => {
      result.current.setYoutubeUrl(VALID_YT_URL)
      result.current.setQuestionCount(3)
    })
    await act(async () => { await result.current.generate() })

    expect(result.current.error).toBe('Số lượng câu hỏi phải từ 5 đến 20')
  })

  it('T7: Happy path - valid URL gọi mock services đúng args', async () => {
    const { result } = renderHook(() => useYouTubeQuestions())

    act(() => { result.current.setYoutubeUrl(VALID_YT_URL) })
    await act(async () => { await result.current.generate() })

    expect(extractMockYouTubeInfo).toHaveBeenCalledWith(VALID_YT_URL)
    expect(getMockYouTubeQuestions).toHaveBeenCalledWith(VALID_YT_URL, 10, 'mix')
    expect(result.current.videoInfo).toEqual(mockVideoInfo)
    expect(result.current.questions).toHaveLength(1)
    expect(result.current.questions[0].question_text).toBe('What is covered in this video?')
    expect(result.current.questions[0].timestamp).toBe('02:30')
    expect(result.current.error).toBeNull()
  })

  it('T8: getMockYouTubeQuestions throw PaymentRequiredError → isPaymentRequired = true', async () => {
    vi.mocked(getMockYouTubeQuestions).mockRejectedValue(new PaymentRequiredError())

    const { result } = renderHook(() => useYouTubeQuestions())

    act(() => { result.current.setYoutubeUrl(VALID_YT_URL) })
    await act(async () => { await result.current.generate() })

    expect(result.current.isPaymentRequired).toBe(true)
    expect(result.current.isLoading).toBe(false)
    expect(result.current.error).toBeNull()
    expect(result.current.rateLimitSeconds).toBe(0)
  })

  it('T9: getMockYouTubeQuestions throw TooManyRequestsError(10) → rateLimitSeconds = 10', async () => {
    vi.mocked(getMockYouTubeQuestions).mockRejectedValue(new TooManyRequestsError(10))

    const { result } = renderHook(() => useYouTubeQuestions())

    act(() => { result.current.setYoutubeUrl(VALID_YT_URL) })
    await act(async () => { await result.current.generate() })

    expect(result.current.rateLimitSeconds).toBe(10)
    expect(result.current.isLoading).toBe(false)
    expect(result.current.isPaymentRequired).toBe(false)
    expect(result.current.error).toBeNull()
  })

  it('T10: extractMockYouTubeInfo throw generic Error → error message được set', async () => {
    vi.mocked(extractMockYouTubeInfo).mockRejectedValue(new Error('Video không tìm thấy'))

    const { result } = renderHook(() => useYouTubeQuestions())

    act(() => { result.current.setYoutubeUrl(VALID_YT_URL) })
    await act(async () => { await result.current.generate() })

    expect(result.current.error).toBe('Video không tìm thấy')
    expect(result.current.isPaymentRequired).toBe(false)
    expect(result.current.rateLimitSeconds).toBe(0)
  })

  it('T11: handleUrlChange clears error', () => {
    const { result } = renderHook(() => useYouTubeQuestions())

    act(() => { result.current.setError('Some error') })
    act(() => { result.current.handleUrlChange('new-url') })

    expect(result.current.error).toBeNull()
    expect(result.current.youtubeUrl).toBe('new-url')
  })

  it('T12: reset() trả về toàn bộ state về mặc định', () => {
    const { result } = renderHook(() => useYouTubeQuestions())

    act(() => {
      result.current.setYoutubeUrl(VALID_YT_URL)
      result.current.setQuestionCount(15)
      result.current.setError('Error')
      result.current.reset()
    })

    expect(result.current.youtubeUrl).toBe('')
    expect(result.current.error).toBeNull()
    expect(result.current.questionCount).toBe(10)
    expect(result.current.isPaymentRequired).toBe(false)
    expect(result.current.rateLimitSeconds).toBe(0)
  })
})
