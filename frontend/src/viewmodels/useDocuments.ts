import { useState, useEffect, useCallback } from 'react'
import type { Document } from '@/models/document'
import { getDocumentsMock } from '@/services/mockData/document.mock'

export function useDocuments() {
  const [documents, setDocuments] = useState<Document[]>([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  const fetchDocuments = useCallback(async () => {
    try {
      const data = await getDocumentsMock()
      setDocuments(data)
    } catch {
      setError('Lỗi tải danh sách tài liệu')
    } finally {
      setLoading(false)
    }
  }, [])

  useEffect(() => {
    // eslint-disable-next-line react-hooks/set-state-in-effect
    fetchDocuments()
  }, [fetchDocuments])

  // Polling logic: if any document is "parsing", poll every 5 seconds
  useEffect(() => {
    const hasParsing = documents.some((doc) => doc.status === 'parsing')
    let interval: number

    if (hasParsing) {
      interval = window.setInterval(() => {
        fetchDocuments()
      }, 5000)
    }

    return () => {
      if (interval) clearInterval(interval)
    }
  }, [documents, fetchDocuments])

  const addDocument = (newDoc: Document) => {
    setDocuments((prev) => [newDoc, ...prev])
  }

  return {
    documents,
    loading,
    error,
    addDocument,
  }
}
