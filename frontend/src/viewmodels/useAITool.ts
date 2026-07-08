import { useState, useCallback, useRef, useEffect } from 'react'
import type { AIToolSSEChunk } from '@/models/ai'
import { parseAIError } from '@/utils/aiApiError'
import { useRateLimitCountdown } from './useRateLimitCountdown'

export type AIStreamFn = (text: string) => AsyncGenerator<AIToolSSEChunk, void, unknown>

export function useAITool(streamFn: AIStreamFn) {
  const [inputText, setInputText] = useState('')
  const [result, setResult] = useState('')
  const [isStreaming, setIsStreaming] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const [uploadedFile, setUploadedFile] = useState<File | null>(null)

  // Error UX states
  const [isPaymentRequired, setIsPaymentRequired] = useState(false)
  const [rateLimitSeconds, setRateLimitSeconds] = useState(0)

  // Dùng boolean ref để abort AsyncGenerator thay vì AbortController
  const cancelledRef = useRef(false)

  const reset = useCallback(() => {
    cancelledRef.current = true
    setInputText('')
    setResult('')
    setIsStreaming(false)
    setError(null)
    setUploadedFile(null)
    setIsPaymentRequired(false)
    setRateLimitSeconds(0)
  }, [])

  const copyResult = useCallback(async () => {
    if (!result) return false
    try {
      await navigator.clipboard.writeText(result)
      return true
    } catch (err) {
      console.error('Failed to copy to clipboard:', err)
      return false
    }
  }, [result])

  const handleInputChange = useCallback((val: string) => {
    setInputText(val)
    if (error) setError(null)
  }, [error])

  const execute = useCallback(async () => {
    if (isStreaming) return
    if (!inputText.trim() && !uploadedFile) return
    if (isPaymentRequired || rateLimitSeconds > 0) return

    cancelledRef.current = false
    setIsStreaming(true)
    setError(null)
    setIsPaymentRequired(false)
    setResult('')

    try {
      const textToProcess = inputText.trim() || (uploadedFile ? `[Nội dung file: ${uploadedFile.name}]` : '')

      const stream = streamFn(textToProcess)

      for await (const chunk of stream) {
        if (cancelledRef.current) break
        setResult(prev => prev + chunk.chunk)
      }
    } catch (err: unknown) {
      const errState = parseAIError(err)
      if (errState.type === 'payment_required') {
        setIsPaymentRequired(true)
      } else if (errState.type === 'rate_limit') {
        setRateLimitSeconds(errState.seconds)
      } else {
        setError(errState.message)
      }
    } finally {
      setIsStreaming(false)
    }
  }, [isStreaming, inputText, uploadedFile, isPaymentRequired, rateLimitSeconds, streamFn])

  // Cleanup khi unmount: cancel bất kỳ stream nào đang chạy
  useEffect(() => {
    return () => {
      cancelledRef.current = true
    }
  }, [])

  // Timer cho Rate Limit countdown
  useRateLimitCountdown(rateLimitSeconds, setRateLimitSeconds)

  return {
    inputText, setInputText,
    result, setResult,
    isStreaming,
    error, setError,
    uploadedFile, setUploadedFile,
    isPaymentRequired,
    rateLimitSeconds,
    execute,
    reset,
    copyResult,
    handleInputChange,
  }
}
