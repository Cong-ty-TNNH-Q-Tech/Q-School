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
      const data = await getRubricsMock()
      setRubrics(data)
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
      const url = await uploadEssayImageMock(file, (progress) => {
        setUploadProgress(progress)
      })
      setUploadedImageUrl(url)
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
      const result = await submitEssayMock(request)
      setSubmission(result)
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

  // Polling logic
  useEffect(() => {
    if (!submission) return
    if (submission.status === 'graded' || submission.status === 'failed') return

    // FIXME — Polling interval nên dùng exponential backoff thay vì fixed 3s
    const interval = setInterval(async () => {
      try {
        const updated = await pollEssayStatusMock(submission.id)
        if (updated) {
          setSubmission(updated)
          if (updated.status === 'graded' || updated.status === 'failed') {
            clearInterval(interval)
          }
        }
      } catch (err) {
        console.error("Polling error", err)
      }
    }, 3000)

    return () => clearInterval(interval)
  }, [submission])

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
