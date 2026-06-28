import { useState, useEffect, useCallback } from 'react'
import type { EssaySubmission, EssaySubmissionRequest, Rubric } from '@/models/quiz'
import { getRubricsMock, uploadEssayImageMock, submitEssayMock, pollEssayStatusMock } from '@/services/mockData'

export function useEssaySubmission() {
  const [rubrics, setRubrics] = useState<Rubric[]>([])
  const [loadingRubrics, setLoadingRubrics] = useState(false)

  const [uploadedImageUrl, setUploadedImageUrl] = useState<string | null>(null)
  const [uploading, setUploading] = useState(false)
  const [uploadProgress, setUploadProgress] = useState(0)

  const [submission, setSubmission] = useState<EssaySubmission | null>(null)
  const [submitting, setSubmitting] = useState(false)

  const [error, setError] = useState<string | null>(null)

  const fetchRubrics = useCallback(async () => {
    setLoadingRubrics(true)
    setError(null)
    try {
      const response = await getRubricsMock()
      setRubrics(response.data)
    } catch (err: unknown) {
      setError(err instanceof Error ? err.message : "Không thể tải danh sách tiêu chí")
    } finally {
      setLoadingRubrics(false)
    }
  }, [])

  const uploadImage = useCallback(async (file: File) => {
    setUploading(true)
    setUploadProgress(0)
    setError(null)
    try {
      const response = await uploadEssayImageMock(file, (progress) => {
        setUploadProgress(progress)
      })
      setUploadedImageUrl(response.data.url)
    } catch (err: unknown) {
      setError(err instanceof Error ? err.message : "Upload ảnh thất bại")
    } finally {
      setUploading(false)
      setUploadProgress(0)
    }
  }, [])

  const removeImage = useCallback(() => {
    setUploadedImageUrl(null)
  }, [])

  const submitEssay = useCallback(async (request: EssaySubmissionRequest) => {
    setSubmitting(true)
    setError(null)
    try {
      const response = await submitEssayMock(request)
      setSubmission(response.data)
    } catch (err: unknown) {
      setError(err instanceof Error ? err.message : "Nộp bài thất bại")
    } finally {
      setSubmitting(false)
    }
  }, [])

  const resetForm = useCallback(() => {
    setUploadedImageUrl(null)
    setUploadProgress(0)
    setSubmission(null)
    setError(null)
  }, [])

  // Polling logic with exponential backoff
  useEffect(() => {
    if (!submission?.id) return
    if (submission.status === 'completed' || submission.status === 'failed') return

    let timeoutId: ReturnType<typeof setTimeout>
    let isCancelled = false
    const submissionId = submission.id

    const poll = async (currentDelay: number) => {
      if (isCancelled) return

      try {
        const response = await pollEssayStatusMock(submissionId)
        if (isCancelled) return
        
        const updated = response.data
        if (updated) {
          setSubmission((prev) => {
            if (prev && prev.status === updated.status && prev.score === updated.score) {
              return prev
            }
            return updated
          })
          
          if (updated.status === 'completed' || updated.status === 'failed') {
            return
          }
        }
      } catch (err) {
        console.error("Polling error", err)
      }

      const nextDelay = Math.min(currentDelay * 2, 15000)
      timeoutId = setTimeout(() => poll(nextDelay), nextDelay)
    }

    timeoutId = setTimeout(() => poll(2000), 2000)

    return () => {
      isCancelled = true
      clearTimeout(timeoutId)
    }
  }, [submission?.id, submission?.status])

  return {
    rubrics,
    loadingRubrics,
    fetchRubrics,
    uploadedImageUrl,
    uploading,
    uploadProgress,
    uploadImage,
    removeImage,
    submission,
    submitting,
    submitEssay,
    error,
    resetForm
  }
}
