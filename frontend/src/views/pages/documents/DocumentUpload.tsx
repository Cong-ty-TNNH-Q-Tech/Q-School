import React, { useState, useRef } from 'react'
import { UploadCloud, FileType, CheckCircle2, X } from 'lucide-react'
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogHeader,
  DialogTitle,
} from '@/components/ui/dialog'
import { Button } from '@/components/ui/button'
import { Progress } from '@/components/ui/progress'
import { mockUploadDocument } from '@/services/mockData/document.mock'
import type { Document } from '@/models/document'

interface DocumentUploadProps {
  open: boolean
  onOpenChange: (open: boolean) => void
  onUploadComplete: (doc: Document) => void
}

export function DocumentUpload({ open, onOpenChange, onUploadComplete }: DocumentUploadProps) {
  const [isDragging, setIsDragging] = useState(false)
  const [selectedFile, setSelectedFile] = useState<File | null>(null)
  const [isUploading, setIsUploading] = useState(false)
  const [progress, setProgress] = useState(0)
  const [error, setError] = useState<string | null>(null)
  const fileInputRef = useRef<HTMLInputElement>(null)

  const handleDragOver = (e: React.DragEvent) => {
    e.preventDefault()
    setIsDragging(true)
  }

  const handleDragLeave = (e: React.DragEvent) => {
    e.preventDefault()
    setIsDragging(false)
  }

  const validateFile = (file: File) => {
    setError(null)
    const validTypes = [
      'application/pdf',
      'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
      'image/jpeg',
      'image/png',
    ]
    if (!validTypes.includes(file.type)) {
      setError('Chỉ hỗ trợ file PDF, DOCX, hoặc Hình ảnh (JPG, PNG)')
      return false
    }
    if (file.size > 20 * 1024 * 1024) {
      setError('Kích thước file không được vượt quá 20MB')
      return false
    }
    return true
  }

  const handleDrop = (e: React.DragEvent) => {
    e.preventDefault()
    setIsDragging(false)
    if (e.dataTransfer.files && e.dataTransfer.files.length > 0) {
      const file = e.dataTransfer.files[0]
      if (validateFile(file)) {
        setSelectedFile(file)
      }
    }
  }

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files && e.target.files.length > 0) {
      const file = e.target.files[0]
      if (validateFile(file)) {
        setSelectedFile(file)
      }
    }
  }

  const handleUpload = async () => {
    if (!selectedFile) return
    setIsUploading(true)
    setProgress(0)
    setError(null)

    try {
      const response = await mockUploadDocument(selectedFile, (p) => setProgress(p))
      if (response.status === 'success') {
        onUploadComplete(response.data)
        setTimeout(() => {
          handleReset()
          onOpenChange(false)
        }, 500)
      }
    } catch (err) {
      setError('Đã xảy ra lỗi khi tải file lên')
    } finally {
      setIsUploading(false)
    }
  }

  const handleReset = () => {
    setSelectedFile(null)
    setProgress(0)
    setError(null)
    if (fileInputRef.current) {
      fileInputRef.current.value = ''
    }
  }

  return (
    <Dialog open={open} onOpenChange={onOpenChange}>
      <DialogContent className="sm:max-w-md">
        <DialogHeader>
          <DialogTitle>Tải tài liệu lên</DialogTitle>
          <DialogDescription>
            Kéo thả hoặc chọn file từ máy tính của bạn. Hỗ trợ PDF, DOCX, JPG, PNG (tối đa 20MB).
          </DialogDescription>
        </DialogHeader>

        <div className="flex flex-col gap-4 py-4">
          {!selectedFile ? (
            <div
              className={`border-2 border-dashed rounded-lg flex flex-col items-center justify-center p-10 transition-colors cursor-pointer ${
                isDragging
                  ? 'border-blue-500 bg-blue-50/50'
                  : 'border-slate-300 hover:border-slate-400 hover:bg-slate-50'
              }`}
              onDragOver={handleDragOver}
              onDragLeave={handleDragLeave}
              onDrop={handleDrop}
              onClick={() => fileInputRef.current?.click()}
            >
              <UploadCloud className="h-10 w-10 text-slate-400 mb-3" />
              <p className="text-sm font-medium text-slate-700">Kéo thả file vào đây</p>
              <p className="text-xs text-slate-500 mt-1">hoặc click để chọn file</p>
              <input
                type="file"
                className="hidden"
                ref={fileInputRef}
                onChange={handleFileChange}
                accept=".pdf,.docx,image/jpeg,image/png"
              />
            </div>
          ) : (
            <div className="border rounded-lg p-4 bg-slate-50 flex items-center gap-4">
              <div className="bg-blue-100 p-2 rounded text-blue-600">
                <FileType className="h-6 w-6" />
              </div>
              <div className="flex-1 overflow-hidden">
                <p className="text-sm font-medium truncate text-slate-800" title={selectedFile.name}>
                  {selectedFile.name}
                </p>
                <p className="text-xs text-slate-500">
                  {(selectedFile.size / (1024 * 1024)).toFixed(2)} MB
                </p>
              </div>
              {!isUploading && (
                <button
                  onClick={handleReset}
                  className="text-slate-400 hover:text-slate-600 p-1"
                >
                  <X className="h-5 w-5" />
                </button>
              )}
            </div>
          )}

          {error && <p className="text-sm text-red-500 font-medium">{error}</p>}

          {isUploading && (
            <div className="space-y-2">
              <div className="flex justify-between text-xs font-medium text-slate-600">
                <span>Đang tải lên...</span>
                <span>{progress}%</span>
              </div>
              <Progress value={progress} className="h-2" />
            </div>
          )}
        </div>

        <div className="flex justify-end gap-2 mt-2">
          <Button
            variant="outline"
            onClick={() => {
              handleReset()
              onOpenChange(false)
            }}
            disabled={isUploading}
          >
            Hủy
          </Button>
          <Button onClick={handleUpload} disabled={!selectedFile || isUploading}>
            {isUploading ? 'Đang tải...' : 'Tải lên ngay'}
          </Button>
        </div>
      </DialogContent>
    </Dialog>
  )
}
