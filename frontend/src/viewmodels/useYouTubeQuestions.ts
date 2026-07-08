import { useState, useCallback, useEffect, useRef } from 'react'
import type { YouTubeQuestion, YouTubeQuestionType, YouTubeInfo } from '@/models/ai'
import { parseAIError } from '@/utils/aiApiError'
import { useRateLimitCountdown } from './useRateLimitCountdown'

const YOUTUBE_URL_REGEX = /^(https?:\/\/)?(www\.)?(youtube\.com\/watch\?v=|youtu\.be\/)([a-zA-Z0-9_-]{11})/

export type FetchYouTubeFn = (
  url: string,
  count: number,
  type: YouTubeQuestionType
) => Promise<{ status: string; data: YouTubeQuestion[] }>

export type ExtractInfoFn = (url: string) => Promise<YouTubeInfo>

export function useYouTubeQuestions(
  fetchFn: FetchYouTubeFn,
  extractInfoFn: ExtractInfoFn
) {
  const [youtubeUrl, setYoutubeUrl] = useState('')
  const [questionCount, setQuestionCount] = useState<number>(10)
  const [questionType, setQuestionType] = useState<YouTubeQuestionType>('mix')
  const [questions, setQuestions] = useState<YouTubeQuestion[]>([])
  const [videoInfo, setVideoInfo] = useState<YouTubeInfo | null>(null)
  const [isLoading, setIsLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)

  // Error UX states
  const [isPaymentRequired, setIsPaymentRequired] = useState(false)
  const [rateLimitSeconds, setRateLimitSeconds] = useState(0)

  const isMountedRef = useRef(true)

  useEffect(() => {
    isMountedRef.current = true
    return () => {
      isMountedRef.current = false
    }
  }, [])

  // [FIX #4] useCallback để tránh recreate mỗi render khi pass làm prop/dependency
  const validateUrl = useCallback((url: string): boolean => {
    if (!url) return false
    return YOUTUBE_URL_REGEX.test(url)
  }, [])

  // [FIX Phase6-B2] Wrap setYoutubeUrl để tự clear error khi user thay đổi URL
  const handleUrlChange = useCallback((url: string) => {
    setYoutubeUrl(url)
    if (error) setError(null)
  }, [error])

  const generate = useCallback(async () => {
    // ViewModel-level guard — không phụ thuộc vào UI disable
    if (isPaymentRequired || rateLimitSeconds > 0) return

    if (!youtubeUrl.trim()) {
      setError('Vui lòng nhập đường dẫn YouTube')
      return
    }

    if (!validateUrl(youtubeUrl)) {
      setError('Đường dẫn YouTube không hợp lệ')
      return
    }

    if (questionCount < 5 || questionCount > 20) {
      setError('Số lượng câu hỏi phải từ 5 đến 20')
      return
    }

    setIsLoading(true)
    setError(null)
    setIsPaymentRequired(false)
    setQuestions([])
    setVideoInfo(null)

    try {
      const info = await extractInfoFn(youtubeUrl)
      if (!isMountedRef.current) return
      setVideoInfo(info)

      const res = await fetchFn(youtubeUrl, questionCount, questionType)
      if (!isMountedRef.current) return
      setQuestions(res.data)
    } catch (err: unknown) {
      if (!isMountedRef.current) return
      setVideoInfo(null) // Reset videoInfo when getMockYouTubeQuestions/fetchFn fails (Minor #8)
      const errState = parseAIError(err)
      if (errState.type === 'payment_required') {
        setIsPaymentRequired(true)
      } else if (errState.type === 'rate_limit') {
        setRateLimitSeconds(errState.seconds)
      } else {
        setError(errState.message)
      }
    } finally {
      if (isMountedRef.current) {
        setIsLoading(false)
      }
    }
  }, [youtubeUrl, questionCount, questionType, isPaymentRequired, rateLimitSeconds, validateUrl, fetchFn, extractInfoFn])

  const reset = useCallback(() => {
    isMountedRef.current = true
    setYoutubeUrl('')
    setQuestionCount(10)
    setQuestionType('mix')
    setQuestions([])
    setVideoInfo(null)
    setError(null)
    setIsLoading(false)
    setIsPaymentRequired(false)
    setRateLimitSeconds(0)
  }, [])

  // Timer cho Rate Limit countdown
  useRateLimitCountdown(rateLimitSeconds, setRateLimitSeconds)

  return {
    youtubeUrl, setYoutubeUrl,
    handleUrlChange,
    questionCount, setQuestionCount,
    questionType, setQuestionType,
    questions,
    videoInfo,
    isLoading,
    error, setError,
    isPaymentRequired,
    rateLimitSeconds,
    generate,
    reset,
    validateUrl
  }
}
