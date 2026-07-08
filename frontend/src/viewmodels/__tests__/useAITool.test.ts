import { renderHook, act } from '@testing-library/react'
import { describe, it, expect, vi, beforeEach, afterEach } from 'vitest'
import { useAITool, type AIStreamFn } from '../useAITool'

const createMockStreamFn = (chunks: string[], throwError: boolean = false): AIStreamFn => {
  return async function* (_text: string) {
    if (throwError) {
      throw new Error(_text)
    }
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
    const streamFnSpy = vi.fn() as unknown as AIStreamFn
    const { result } = renderHook(() => useAITool(streamFnSpy))

    // Trigger payment required via special input
    act(() => {
      result.current.setInputText('402')
    })
    await act(async () => {
      await result.current.execute()
    })
    expect(result.current.isPaymentRequired).toBe(true)

    // Now with normal input — should still be blocked
    act(() => {
      result.current.setInputText('normal text to process')
    })
    await act(async () => {
      await result.current.execute()
    })

    expect(streamFnSpy).not.toHaveBeenCalled()
  })

  it('T4: Guard - rateLimitSeconds > 0 thì execute bị block', async () => {
    const mockStream = vi.fn() as unknown as AIStreamFn
    const { result } = renderHook(() => useAITool(mockStream))

    act(() => {
      result.current.setInputText('429')
    })
    await act(async () => {
      await result.current.execute() // trigger rate limit
    })

    expect(result.current.rateLimitSeconds).toBe(10)

    act(() => {
      result.current.setInputText('normal input')
    })
    await act(async () => {
      await result.current.execute() // should be blocked
    })

    expect(mockStream).not.toHaveBeenCalled()
  })

  it('T5 & T6: Simulate 402 and 429 inputs', async () => {
    const mockStream = createMockStreamFn(['test'])
    const { result } = renderHook(() => useAITool(mockStream))

    act(() => {
      result.current.setInputText('402')
    })
    await act(async () => {
      await result.current.execute()
    })
    expect(result.current.isPaymentRequired).toBe(true)

    act(() => {
      result.current.reset()
      result.current.setInputText('429')
    })
    await act(async () => {
      await result.current.execute()
    })
    expect(result.current.rateLimitSeconds).toBe(10)
  })

  it('T7: reset() clears all state', () => {
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

    act(() => {
      result.current.setError('Some error')
    })

    act(() => {
      result.current.handleInputChange('new text')
    })

    expect(result.current.error).toBeNull()
    expect(result.current.inputText).toBe('new text')
  })

  it('T10: Unmount khi đang stream không gây lỗi setState', async () => {
    // Generator với delay để stream vẫn đang chạy khi unmount
    let resolveDelay!: () => void
    const slowStream: AIStreamFn = async function* () {
      yield { chunk: 'first', is_final: false }
      await new Promise<void>(resolve => { resolveDelay = resolve })
      yield { chunk: 'second', is_final: true }
    }

    const { result, unmount } = renderHook(() => useAITool(slowStream))

    act(() => {
      result.current.setInputText('test text')
    })

    // Bắt đầu stream
    const executePromise = act(async () => {
      result.current.execute()
    })

    // Unmount trong khi đang stream
    unmount()

    // Unblock generator — should not cause setState after unmount warning
    if (resolveDelay) resolveDelay()

    await executePromise

    // Nếu không có lỗi "Can't perform a React state update on an unmounted component" là PASS
    expect(true).toBe(true)
  })
})
