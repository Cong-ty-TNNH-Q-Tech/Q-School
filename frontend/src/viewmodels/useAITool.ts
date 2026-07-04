import { useState, useCallback, useRef, useEffect } from 'react'
import type { AIToolType, SummarizeLevel, RewriteTone } from '@/models/ai'
import { streamMockSummarize, streamMockTranslate, streamMockRewrite } from '@/services/mockData'

export function useAITool(toolType: AIToolType) {
  const [inputText, setInputText] = useState('')
  const [result, setResult] = useState('')
  const [isStreaming, setIsStreaming] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const [uploadedFile, setUploadedFile] = useState<File | null>(null)

  // Error UX states
  const [isPaymentRequired, setIsPaymentRequired] = useState(false)
  const [rateLimitSeconds, setRateLimitSeconds] = useState(0)

  // Options per tool
  const [summarizeLevel, setSummarizeLevel] = useState<SummarizeLevel>('medium')
  const [sourceLang, setSourceLang] = useState<string>('vi')
  const [targetLang, setTargetLang] = useState<string>('en')
  const [rewriteTone, setRewriteTone] = useState<RewriteTone>('formal')

  // [FIX #1] Dùng boolean ref để abort AsyncGenerator thay vì AbortController
  // AbortController chỉ work với fetch/EventSource, không work với async generator
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

  // [FIX #3] Kiểm tra result trước khi swap, không clear inputText nếu result rỗng
  const swapLanguages = useCallback(() => {
    const temp = sourceLang
    setSourceLang(targetLang)
    setTargetLang(temp)
    if (result) {
      setInputText(result)
      setResult('')
    }
  }, [sourceLang, targetLang, result])

  // [FIX Phase6-B1] Wrap setInputText để tự clear error khi user gõ lại
  const handleInputChange = useCallback((val: string) => {
    setInputText(val)
    if (error) setError(null)
  }, [error])

  const execute = useCallback(async () => {
    // [FIX #2] Guard: không cho double-submit khi đang stream
    if (isStreaming) return
    if (!inputText.trim() && !uploadedFile) return
    // [FIX Phase6-B1] ViewModel-level guard — không phụ thuộc vào UI disable
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

      let stream: AsyncGenerator<{ chunk: string; is_final: boolean }, void, unknown>

      if (toolType === 'summarize') {
        stream = streamMockSummarize(textToProcess, summarizeLevel)
      } else if (toolType === 'translate') {
        stream = streamMockTranslate(textToProcess, sourceLang, targetLang)
      } else if (toolType === 'rewrite') {
        stream = streamMockRewrite(textToProcess, rewriteTone)
      } else {
        throw new Error('Unsupported tool type for streaming')
      }

      // [FIX #1] Kiểm tra cancelledRef thay vì AbortController signal
      for await (const chunk of stream) {
        if (cancelledRef.current) break
        setResult(prev => prev + chunk.chunk)
      }
    } catch (err: unknown) {
      // [FIX #5] Dùng unknown thay vì any — theo pattern useEssaySubmission.ts
      const msg = err instanceof Error ? err.message : 'Đã có lỗi xảy ra. Vui lòng thử lại.'
      if (msg.includes('402')) setIsPaymentRequired(true)
      else if (msg.includes('429')) setRateLimitSeconds(15)
      else setError(msg)
    } finally {
      setIsStreaming(false)
    }
  }, [isStreaming, inputText, uploadedFile, toolType, summarizeLevel, sourceLang, targetLang, rewriteTone])

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
    summarizeLevel, setSummarizeLevel,
    sourceLang, setSourceLang,
    targetLang, setTargetLang,
    rewriteTone, setRewriteTone,
    isPaymentRequired,
    rateLimitSeconds,
    execute,
    reset,
    copyResult,
    swapLanguages,
    handleInputChange,
  }
}
