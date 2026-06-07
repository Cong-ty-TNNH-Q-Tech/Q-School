export type DocumentStatus = 'pending' | 'parsing' | 'ready' | 'error'

export interface Document {
  id: string
  uploader_id: string
  filename: string
  file_type: string
  file_size?: number // Bytes
  s3_url?: string
  is_public: boolean
  status: DocumentStatus
  created_at: string
  deleted_at?: string
}

export interface DocumentUploadResponse {
  status: 'success' | 'error'
  data: Document
  message: string
}

export interface DocumentListResponse {
  status: 'success' | 'error'
  data: Document[]
  message?: string
}
