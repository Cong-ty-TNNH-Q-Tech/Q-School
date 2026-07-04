import { useState, useCallback } from 'react'
import type { YouTubeQuestion, YouTubeQuestionType } from '@/models/ai'
import { getMockYouTubeQuestions, extractMockYouTubeInfo, type YouTubeInfo } from '@/services/mockData'

const YOUTUBE_URL_REGEX = /^(https?:\/\/)?(www\.)?(youtube\.com\/watch\?v=|youtu\.be\/)([a-zA-Z0-9_-]{11})/

export function useYouTubeQuestions() {
  const [youtubeUrl, setYoutubeUrl] = useState('')
  const [questionCount, setQuestionCount] = useState<number>(10)
  const [questionType, setQuestionType] = useState<YouTubeQuestionType>('mix')
  const [questions, setQuestions] = useState<YouTubeQuestion[]>([])
  const [videoInfo, setVideoInfo] = useState<YouTubeInfo | null>(null)
  const [isLoading, setIsLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)

  // [FIX #4] useCallback để tránh recreate mỗi render khi pass làm prop/dependency
  const validateUrl = useCallback((url: string): boolean => {
    if (!url) return false
    return YOUTUBE_URL_REGEX.test(url)
  }, [])

  const generate = useCallback(async () => {
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
    setQuestions([])
    setVideoInfo(null)
    
    try {
      const info = await extractMockYouTubeInfo(youtubeUrl)
      setVideoInfo(info)

      const res = await getMockYouTubeQuestions(youtubeUrl, questionCount, questionType)
      setQuestions(res.data)
    } catch (err: unknown) {
      // [FIX #5] Dùng unknown thay vì any — theo pattern useEssaySubmission.ts
      setError(err instanceof Error ? err.message : 'Có lỗi xảy ra khi tạo câu hỏi. Vui lòng thử lại.')
    } finally {
      setIsLoading(false)
    }
  }, [youtubeUrl, questionCount, questionType])

  const reset = useCallback(() => {
    setYoutubeUrl('')
    setQuestionCount(10)
    setQuestionType('mix')
    setQuestions([])
    setVideoInfo(null)
    setError(null)
    setIsLoading(false)
  }, [])

  return {
    youtubeUrl, setYoutubeUrl,
    questionCount, setQuestionCount,
    questionType, setQuestionType,
    questions,
    videoInfo,
    isLoading,
    error, setError,
    generate,
    reset,
    validateUrl
  }
}
