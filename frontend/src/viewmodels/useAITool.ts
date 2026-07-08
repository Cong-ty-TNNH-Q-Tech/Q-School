import { useState, useCallback, useRef, useEffect } from 'react'

export type AIStreamFn = (text: string) => AsyncGenerator<{ chunk: string; is_final: boolean }, void, unknown>

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

    // [Simulate 402/429 based on special input for demo/testing]
    if (inputText.trim() === '402') {
      setIsStreaming(false);
      setIsPaymentRequired(true);
      return;
    }
    if (inputText.trim() === '429') {
      setIsStreaming(false);
      setRateLimitSeconds(10);
      return;
    }

    try {
      const textToProcess = inputText.trim() || (uploadedFile ? `[Nội dung file: ${uploadedFile.name}]` : '')
      
      const stream = streamFn(textToProcess)

      for await (const chunk of stream) {
        if (cancelledRef.current) break
        setResult(prev => prev + chunk.chunk)
      }
    } catch (err: unknown) {
      const msg = err instanceof Error ? err.message : 'Đã có lỗi xảy ra. Vui lòng thử lại.'
      if (msg.includes('402')) setIsPaymentRequired(true)
      else if (msg.includes('429')) setRateLimitSeconds(15)
      else setError(msg)
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
  useEffect(() => {
    if (rateLimitSeconds > 0) {
      const timer = setTimeout(() => setRateLimitSeconds(prev => prev - 1), 1000)
      return () => clearTimeout(timer)
    }
  }, [rateLimitSeconds])

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
