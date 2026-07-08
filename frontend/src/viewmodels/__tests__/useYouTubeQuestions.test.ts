import { renderHook, act } from '@testing-library/react'
import { describe, it, expect, vi, beforeEach, afterEach } from 'vitest'
import { useYouTubeQuestions } from '../useYouTubeQuestions'
import { extractMockYouTubeInfo, getMockYouTubeQuestions } from '../../services/mockData'
import type { YouTubeQuestion } from '@/models/ai'

vi.mock('../../services/mockData', () => ({
  extractMockYouTubeInfo: vi.fn(),
  getMockYouTubeQuestions: vi.fn(),
}))

// YouTubeInfo type as used in the mock (has title, duration, thumbnail_url)
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

    await act(async () => {
      await result.current.generate()
    })

    expect(result.current.error).toBe('Vui lòng nhập đường dẫn YouTube')
  })

  it('T5: generate() với URL không hợp lệ → set error', async () => {
    const { result } = renderHook(() => useYouTubeQuestions())

    act(() => {
      result.current.setYoutubeUrl('https://google.com')
    })

    await act(async () => {
      await result.current.generate()
    })

    expect(result.current.error).toBe('Đường dẫn YouTube không hợp lệ')
  })

  it('T6: generate() với questionCount < 5 → set error', async () => {
    const { result } = renderHook(() => useYouTubeQuestions())

    act(() => {
      result.current.setYoutubeUrl('https://youtube.com/watch?v=12345678901')
      result.current.setQuestionCount(3)
    })

    await act(async () => {
      await result.current.generate()
    })

    expect(result.current.error).toBe('Số lượng câu hỏi phải từ 5 đến 20')
  })

  it('T7: Happy path - valid URL gọi mock services đúng', async () => {
    vi.mocked(extractMockYouTubeInfo).mockResolvedValue(mockVideoInfo)
    vi.mocked(getMockYouTubeQuestions).mockResolvedValue({
      status: 'success',
      data: [mockQuestion],
    })

    const { result } = renderHook(() => useYouTubeQuestions())

    act(() => {
      result.current.setYoutubeUrl('https://youtube.com/watch?v=12345678901')
    })

    await act(async () => {
      await result.current.generate()
    })

    expect(extractMockYouTubeInfo).toHaveBeenCalledWith('https://youtube.com/watch?v=12345678901')
    expect(getMockYouTubeQuestions).toHaveBeenCalledWith('https://youtube.com/watch?v=12345678901', 10, 'mix')
    expect(result.current.videoInfo).toEqual(mockVideoInfo)
    expect(result.current.questions).toHaveLength(1)
    expect(result.current.questions[0].question_text).toBe('What is covered in this video?')
    expect(result.current.questions[0].timestamp).toBe('02:30')
    expect(result.current.error).toBeNull()
  })

  it('T8 & T9: URL chứa 402 → isPaymentRequired, 429 → rateLimitSeconds', async () => {
    const { result } = renderHook(() => useYouTubeQuestions())

    act(() => {
      result.current.setYoutubeUrl('https://youtube.com/watch?v=40240240240')
    })

    await act(async () => {
      await result.current.generate()
    })

    expect(result.current.isPaymentRequired).toBe(true)

    act(() => {
      result.current.reset()
      result.current.setYoutubeUrl('https://youtube.com/watch?v=42942942942')
    })

    await act(async () => {
      await result.current.generate()
    })

    expect(result.current.rateLimitSeconds).toBe(10)
  })

  it('T10: handleUrlChange clears error', () => {
    const { result } = renderHook(() => useYouTubeQuestions())

    act(() => {
      result.current.setError('Some error')
    })

    act(() => {
      result.current.handleUrlChange('new-url')
    })

    expect(result.current.error).toBeNull()
    expect(result.current.youtubeUrl).toBe('new-url')
  })

  it('T11: reset() trả về state mặc định', () => {
    const { result } = renderHook(() => useYouTubeQuestions())

    act(() => {
      result.current.setYoutubeUrl('https://youtube.com/watch?v=12345678901')
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
