import React, { useCallback, useRef, useState } from 'react'
import { UploadCloud, X, FileImage } from 'lucide-react'
import { Progress } from '@/components/ui/progress'
import { cn } from '@/lib/utils'

interface ImageDropzoneProps {
  onFileSelect: (file: File) => void
  uploading: boolean
  uploadProgress: number
  imageUrl: string | null
  onRemove: () => void
  acceptedFormats?: string[]
  maxSizeMB?: number
}

export default function ImageDropzone({
  onFileSelect,
  uploading,
  uploadProgress,
  imageUrl,
  onRemove,
  acceptedFormats = ['image/jpeg', 'image/png', 'image/webp'],
  maxSizeMB = 10
}: ImageDropzoneProps) {
  const [isDragActive, setIsDragActive] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const fileInputRef = useRef<HTMLInputElement>(null)

  const handleDragEnter = useCallback((e: React.DragEvent) => {
    e.preventDefault()
    e.stopPropagation()
    setIsDragActive(true)
  }, [])

  const handleDragLeave = useCallback((e: React.DragEvent) => {
    e.preventDefault()
    e.stopPropagation()
    setIsDragActive(false)
  }, [])

  const handleDragOver = useCallback((e: React.DragEvent) => {
    e.preventDefault()
    e.stopPropagation()
  }, [])

  const processFile = useCallback((file: File) => {
    setError(null)
    
    // Validate format
    if (!acceptedFormats.includes(file.type)) {
      setError(`Định dạng không hỗ trợ. Chỉ chấp nhận: ${acceptedFormats.map(f => f.replace('image/', '')).join(', ')}`)
      return
    }

    // Validate size
    if (file.size > maxSizeMB * 1024 * 1024) {
      setError(`File quá lớn. Tối đa ${maxSizeMB}MB`)
      return
    }

    onFileSelect(file)
  }, [acceptedFormats, maxSizeMB, onFileSelect])

  const handleDrop = useCallback((e: React.DragEvent) => {
    e.preventDefault()
    e.stopPropagation()
    setIsDragActive(false)

    if (e.dataTransfer.files && e.dataTransfer.files.length > 0) {
      processFile(e.dataTransfer.files[0])
    }
  }, [processFile])

  const handleFileChange = useCallback((e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files && e.target.files.length > 0) {
      processFile(e.target.files[0])
    }
  }, [processFile])

  const handleClick = useCallback(() => {
    if (!imageUrl && !uploading) {
      fileInputRef.current?.click()
    }
  }, [imageUrl, uploading])

  return (
    <div className="w-full">
      <div
        className={cn(
          "relative flex flex-col items-center justify-center w-full h-64 rounded-lg border-2 border-dashed transition-all duration-200",
          isDragActive ? "border-primary bg-primary/5" : "border-muted-foreground/25 bg-muted/20",
          !imageUrl && !uploading && "cursor-pointer hover:bg-muted/50",
          error && "border-destructive bg-destructive/5"
        )}
        onDragEnter={handleDragEnter}
        onDragLeave={handleDragLeave}
        onDragOver={handleDragOver}
        onDrop={handleDrop}
        onClick={handleClick}
      >
        <input
          ref={fileInputRef}
          type="file"
          className="hidden"
          accept={acceptedFormats.join(',')}
          onChange={handleFileChange}
          disabled={uploading || !!imageUrl}
        />

        {!imageUrl && !uploading && (
          <div className="flex flex-col items-center justify-center pt-5 pb-6 text-center px-4">
            <UploadCloud className="w-10 h-10 mb-3 text-muted-foreground" />
            <p className="mb-2 text-sm font-medium">
              <span className="text-primary font-semibold">Nhấn để chọn file</span> hoặc kéo thả ảnh vào đây
            </p>
            <p className="text-xs text-muted-foreground">
              Hỗ trợ {acceptedFormats.map(f => f.replace('image/', '').toUpperCase()).join(', ')} (Tối đa {maxSizeMB}MB)
            </p>
          </div>
        )}

        {uploading && (
          <div className="flex flex-col items-center justify-center w-full px-8">
            <FileImage className="w-8 h-8 mb-4 text-primary animate-pulse" />
            <div className="w-full max-w-xs space-y-2">
              <div className="flex justify-between text-xs text-muted-foreground">
                <span>Đang tải ảnh lên...</span>
                <span>{uploadProgress}%</span>
              </div>
              <Progress value={uploadProgress} className="h-2" />
            </div>
          </div>
        )}

        {imageUrl && !uploading && (
          <div className="relative w-full h-full p-2 group">
            <img 
              src={imageUrl} 
              alt="Uploaded preview" 
              className="w-full h-full object-contain rounded-md"
            />
            <button
              type="button"
              onClick={(e) => {
                e.stopPropagation()
                onRemove()
              }}
              className="absolute top-4 right-4 p-1.5 bg-background/80 backdrop-blur-sm rounded-full text-muted-foreground hover:text-destructive hover:bg-background transition-colors opacity-0 group-hover:opacity-100"
            >
              <X className="w-5 h-5" />
            </button>
          </div>
        )}
      </div>
      
      {error && (
        <p className="mt-2 text-sm text-destructive font-medium">{error}</p>
      )}
    </div>
  )
}
