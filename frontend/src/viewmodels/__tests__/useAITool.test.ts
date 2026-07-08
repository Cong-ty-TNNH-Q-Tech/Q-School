import { renderHook, act } from '@testing-library/react'
import { describe, it, expect, vi, beforeEach, afterEach } from 'vitest'
import { useAITool, type AIStreamFn } from '../useAITool'

const createMockStreamFn = (chunks: string[], throwError: boolean = false): AIStreamFn => {
  return async function* (text: string) {
    if (throwError) {
      throw new Error(text)
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

  it('T2: Guard - empty input', async () => {
    const mockStream = createMockStreamFn(['test'])
    const { result } = renderHook(() => useAITool(mockStream))

    await act(async () => {
      await result.current.execute()
    })
    expect(result.current.isStreaming).toBe(false)
    expect(result.current.result).toBe('')
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

  it('T4: Guard - blocked if rateLimitSeconds > 0', async () => {
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
})
