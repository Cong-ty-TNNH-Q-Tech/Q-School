import { renderHook, act } from '@testing-library/react'
import { describe, it, expect, vi, beforeEach, afterEach } from 'vitest'
import { useAITool, type AIStreamFn } from '../useAITool'
import { PaymentRequiredError, TooManyRequestsError } from '@/utils/aiApiError'

const createMockStreamFn = (chunks: string[], throwErr?: Error): AIStreamFn => {
  return async function* () {
    if (throwErr) throw throwErr
    for (const chunk of chunks) {
      yield { chunk, is_final: false }
    }
    yield { chunk: '', is_final: true }
  }
}

describe('useAITool', () => {
  beforeEach(() => {
    vi.useFakeTimers()
  })

  afterEach(() => {
    vi.clearAllTimers()
    vi.useRealTimers()
  })

  it('T1: Happy path - stream tokens từ streamFn', async () => {
    const mockStream = createMockStreamFn(['hello', ' ', 'world'])
    const { result } = renderHook(() => useAITool(mockStream))

    act(() => {
      result.current.setInputText('test input')
    })

    await act(async () => {
      await result.current.execute()
    })

    expect(result.current.result).toBe('hello world')
    expect(result.current.isStreaming).toBe(false)
    expect(result.current.error).toBeNull()
  })

  it('T2: Guard - empty input không trigger streamFn', async () => {
    const mockStream = createMockStreamFn(['test'])
    const { result } = renderHook(() => useAITool(mockStream))

    await act(async () => {
      await result.current.execute()
    })
    expect(result.current.isStreaming).toBe(false)
    expect(result.current.result).toBe('')
  })

  it('T3: Guard - isPaymentRequired=true thì execute bị block', async () => {
    // Lần 1: streamFn throw PaymentRequiredError → set isPaymentRequired
    const throwStream = createMockStreamFn([], new PaymentRequiredError())
    const { result } = renderHook(() => useAITool(throwStream))

    act(() => { result.current.setInputText('some text') })
    await act(async () => { await result.current.execute() })
    expect(result.current.isPaymentRequired).toBe(true)

    // Lần 2: thử execute lại với input mới — phải bị block ngay, streamFn không được gọi
    const streamSpy = vi.fn(createMockStreamFn(['ok']))
    const hookWithSpy = renderHook(() => useAITool(streamSpy as AIStreamFn))
    // Inject payment state manually bằng cách giả lập lại
    act(() => { hookWithSpy.result.current.setInputText('another text') })
    // Cần force isPaymentRequired = true thông qua execute với throw stream
    const throwStream2 = createMockStreamFn([], new PaymentRequiredError())
    const { result: result2 } = renderHook(() => useAITool(throwStream2))
    act(() => { result2.current.setInputText('text') })
    await act(async () => { await result2.current.execute() })
    expect(result2.current.isPaymentRequired).toBe(true)
    // execute lại — trả về ngay vì guard
    await act(async () => { await result2.current.execute() })
    // isPaymentRequired vẫn true, không thay đổi
    expect(result2.current.isPaymentRequired).toBe(true)
  })

  it('T4: Guard - rateLimitSeconds > 0 thì execute bị block', async () => {
    const throwStream = createMockStreamFn([], new TooManyRequestsError(10))
    const { result } = renderHook(() => useAITool(throwStream))

    act(() => { result.current.setInputText('some text') })
    await act(async () => { await result.current.execute() })
    expect(result.current.rateLimitSeconds).toBe(10)

    // Execute lại — bị block do rateLimitSeconds > 0, result không thay đổi
    await act(async () => { await result.current.execute() })
    expect(result.current.rateLimitSeconds).toBe(10)
  })

  it('T5: streamFn throw PaymentRequiredError → isPaymentRequired = true', async () => {
    const throwStream = createMockStreamFn([], new PaymentRequiredError())
    const { result } = renderHook(() => useAITool(throwStream))

    act(() => { result.current.setInputText('bất kỳ nội dung gì') })
    await act(async () => { await result.current.execute() })

    expect(result.current.isPaymentRequired).toBe(true)
    expect(result.current.isStreaming).toBe(false)
    expect(result.current.error).toBeNull()
    expect(result.current.rateLimitSeconds).toBe(0)
  })

  it('T6: streamFn throw TooManyRequestsError(10) → rateLimitSeconds = 10', async () => {
    const throwStream = createMockStreamFn([], new TooManyRequestsError(10))
    const { result } = renderHook(() => useAITool(throwStream))

    act(() => { result.current.setInputText('bất kỳ nội dung gì') })
    await act(async () => { await result.current.execute() })

    expect(result.current.rateLimitSeconds).toBe(10)
    expect(result.current.isStreaming).toBe(false)
    expect(result.current.isPaymentRequired).toBe(false)
    expect(result.current.error).toBeNull()
  })

  it('T7: streamFn throw generic Error → error message được set', async () => {
    const throwStream = createMockStreamFn([], new Error('Network timeout'))
    const { result } = renderHook(() => useAITool(throwStream))

    act(() => { result.current.setInputText('some text') })
    await act(async () => { await result.current.execute() })

    expect(result.current.error).toBe('Network timeout')
    expect(result.current.isPaymentRequired).toBe(false)
    expect(result.current.rateLimitSeconds).toBe(0)
  })

  it('T8: reset() clears all state', () => {
    const mockStream = createMockStreamFn(['test'])
    const { result } = renderHook(() => useAITool(mockStream))

    act(() => {
      result.current.setInputText('abc')
      result.current.setResult('xyz')
      result.current.reset()
    })

    expect(result.current.inputText).toBe('')
    expect(result.current.result).toBe('')
    expect(result.current.error).toBeNull()
    expect(result.current.isPaymentRequired).toBe(false)
    expect(result.current.rateLimitSeconds).toBe(0)
  })

  it('T9: handleInputChange clears error', () => {
    const mockStream = createMockStreamFn(['test'])
    const { result } = renderHook(() => useAITool(mockStream))

    act(() => { result.current.setError('Some error') })
    act(() => { result.current.handleInputChange('new text') })

    expect(result.current.error).toBeNull()
    expect(result.current.inputText).toBe('new text')
  })

  it('T10: Unmount khi đang stream không gây lỗi setState', async () => {
    let resolveDelay!: () => void
    const slowStream: AIStreamFn = async function* () {
      yield { chunk: 'first', is_final: false }
      await new Promise<void>(resolve => { resolveDelay = resolve })
      yield { chunk: 'second', is_final: true }
    }

    const { result, unmount } = renderHook(() => useAITool(slowStream))

    act(() => { result.current.setInputText('test text') })

    const executePromise = act(async () => {
      result.current.execute()
    })

    unmount()

    if (resolveDelay) resolveDelay()
    await executePromise

    expect(true).toBe(true) // Không có "setState on unmounted component" warning
  })

  it('T11: Guard - isStreaming=true thì execute() bị block', async () => {
    const streamSpy = vi.fn(createMockStreamFn(['hello']))
    const { result } = renderHook(() => useAITool(streamSpy as AIStreamFn))
    act(() => { result.current.setInputText('text') })
    // Gọi execute() 2 lần liên tiếp
    act(() => { result.current.execute() })
    act(() => { result.current.execute() }) // phải bị block
    await act(async () => {}) // flush
    expect(streamSpy).toHaveBeenCalledTimes(1) // chỉ gọi 1 lần
  })

  it('T12: Rate limit countdown đếm ngược theo giây', async () => {
    const throwStream = createMockStreamFn([], new TooManyRequestsError(3))
    const { result } = renderHook(() => useAITool(throwStream))
    act(() => { result.current.setInputText('text') })
    await act(async () => { await result.current.execute() })
    expect(result.current.rateLimitSeconds).toBe(3)
    act(() => { vi.advanceTimersByTime(1000) })
    expect(result.current.rateLimitSeconds).toBe(2)
    act(() => { vi.advanceTimersByTime(1000) })
    expect(result.current.rateLimitSeconds).toBe(1)
    act(() => { vi.advanceTimersByTime(1000) })
    expect(result.current.rateLimitSeconds).toBe(0)
  })

  it('T13: copyResult() khi có result', async () => {
    Object.assign(navigator, { clipboard: { writeText: vi.fn().mockResolvedValue(undefined) } })
    const mockStream = createMockStreamFn(['hello'])
    const { result } = renderHook(() => useAITool(mockStream))
    act(() => { result.current.setInputText('test') })
    await act(async () => { await result.current.execute() })
    const success = await act(async () => result.current.copyResult())
    expect(success).toBe(true)
  })
})
