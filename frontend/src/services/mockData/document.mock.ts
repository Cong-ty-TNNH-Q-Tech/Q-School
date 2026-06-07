import type { Document, DocumentListResponse, DocumentUploadResponse } from '@/models/document'

// Mock Data
let MOCK_DOCUMENTS: Document[] = [
  {
    id: '11111111-1111-1111-1111-111111111111',
    uploader_id: '11111111-1111-1111-1111-111111111111',
    filename: 'De_cuong_Sinh_10.pdf',
    file_type: 'application/pdf',
    file_size: 2400000, // 2.4 MB
    is_public: false,
    status: 'ready',
    created_at: new Date(Date.now() - 3600 * 1000).toISOString(),
  },
  {
    id: '22222222-2222-2222-2222-222222222222',
    uploader_id: '11111111-1111-1111-1111-111111111111',
    filename: 'Sach_giao_khoa_Toan_11.docx',
    file_type: 'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
    file_size: 15000000, // 15.0 MB
    is_public: true,
    status: 'parsing',
    created_at: new Date(Date.now() - 7200 * 1000).toISOString(),
  },
  {
    id: '33333333-3333-3333-3333-333333333333',
    uploader_id: '11111111-1111-1111-1111-111111111111',
    filename: 'Hinh_anh_De_thi_thu.jpg',
    file_type: 'image/jpeg',
    file_size: 5100000, // 5.1 MB
    is_public: false,
    status: 'error',
    created_at: new Date(Date.now() - 86400 * 1000).toISOString(), // Yesterday
  },
]

// Mock API Functions
export const mockGetDocuments = async (): Promise<DocumentListResponse> => {
  // Simulate network delay
  await new Promise((resolve) => setTimeout(resolve, 800))

  // Simulate parsing logic: Randomly turn "parsing" to "ready" or keep it
  MOCK_DOCUMENTS = MOCK_DOCUMENTS.map((doc) => {
    if (doc.status === 'parsing') {
      const random = Math.random()
      if (random > 0.7) {
        return { ...doc, status: 'ready' }
      }
      if (random < 0.1) {
         return { ...doc, status: 'error' }
      }
    }
    return doc
  })

  return {
    status: 'success',
    data: [...MOCK_DOCUMENTS],
  }
}

export const mockUploadDocument = async (
  file: File,
  onProgress?: (progress: number) => void
): Promise<DocumentUploadResponse> => {
  // Simulate upload with progress
  for (let i = 10; i <= 100; i += 10) {
    await new Promise((resolve) => setTimeout(resolve, 300))
    if (onProgress) {
      onProgress(i)
    }
  }

  const newDoc: Document = {
    id: crypto.randomUUID(),
    uploader_id: '11111111-1111-1111-1111-111111111111', // Dummy teacher ID
    filename: file.name,
    file_type: file.type,
    file_size: file.size,
    is_public: false,
    status: 'parsing', // Initial status is parsing
    created_at: new Date().toISOString(),
  }

  MOCK_DOCUMENTS.unshift(newDoc)

  return {
    status: 'success',
    data: newDoc,
    message: 'Tải file lên thành công',
  }
}
