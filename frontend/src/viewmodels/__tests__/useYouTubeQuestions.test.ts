import { renderHook, act } from '@testing-library/react'
import { describe, it, expect, vi, beforeEach, afterEach } from 'vitest'
import { useYouTubeQuestions } from '../useYouTubeQuestions'
import { extractMockYouTubeInfo, getMockYouTubeQuestions } from '../../services/mockData'
import type { YouTubeQuestion } from '@/models/ai'

vi.mock('../../services/mockData', () => ({
  extractMockYouTubeInfo: vi.fn(),
  getMockYouTubeQuestions: vi.fn(),
}))

describe('useYouTubeQuestions', () => {
  beforeEach(() => {
    vi.useFakeTimers()
    vi.clearAllMocks()
  })

  afterEach(() => {
    vi.clearAllTimers()
    vi.useRealTimers()
  })

  it('T1-T3: validateUrl', () => {
    const { result } = renderHook(() => useYouTubeQuestions())
    expect(result.current.validateUrl('https://www.youtube.com/watch?v=dQw4w9WgXcQ')).toBe(true)
    expect(result.current.validateUrl('https://youtu.be/dQw4w9WgXcQ')).toBe(true)
    expect(result.current.validateUrl('invalid-url')).toBe(false)
  })

  it('T4: generate() with empty URL sets error', async () => {
    const { result } = renderHook(() => useYouTubeQuestions())
    
    await act(async () => {
      await result.current.generate()
    })
    
    expect(result.current.error).toBe('Vui lòng nhập đường dẫn YouTube')
  })

  it('T5: generate() with invalid URL sets error', async () => {
    const { result } = renderHook(() => useYouTubeQuestions())
    
    act(() => {
      result.current.setYoutubeUrl('https://google.com')
    })
    
    await act(async () => {
      await result.current.generate()
    })
    
    expect(result.current.error).toBe('Đường dẫn YouTube không hợp lệ')
  })

  it('T7: Happy path valid URL calls mock services', async () => {
    const mockInfo = { title: 'Test Video', author: 'Test Channel', duration: '10:00', thumbnail: 'test.jpg' };
    vi.mocked(extractMockYouTubeInfo).mockResolvedValue(mockInfo);
    vi.mocked(getMockYouTubeQuestions).mockResolvedValue({ status: 'success', data: [{ id: '1', type: 'open', question: 'Q1', timestamp: 0, options: [], correct_answer: '', answer_hint: '' } as YouTubeQuestion] });

    const { result } = renderHook(() => useYouTubeQuestions())
    
    act(() => {
      result.current.setYoutubeUrl('https://youtube.com/watch?v=12345678901')
    })
    
    await act(async () => {
      await result.current.generate()
    })
    
    expect(extractMockYouTubeInfo).toHaveBeenCalledWith('https://youtube.com/watch?v=12345678901')
    expect(getMockYouTubeQuestions).toHaveBeenCalledWith('https://youtube.com/watch?v=12345678901', 10, 'mix')
    expect(result.current.videoInfo).toEqual(mockInfo)
    expect(result.current.questions).toHaveLength(1)
    expect(result.current.error).toBeNull()
  })

  it('T8 & T9: Simulate 402 and 429 via URL', async () => {
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

  it('T11: reset clears all state', () => {
    const { result } = renderHook(() => useYouTubeQuestions())
    
    act(() => {
      result.current.setYoutubeUrl('https://youtube.com/watch?v=12345678901')
      result.current.setError('Error')
      result.current.reset()
    })
    
    expect(result.current.youtubeUrl).toBe('')
    expect(result.current.error).toBeNull()
    expect(result.current.questionCount).toBe(10)
  })
})
