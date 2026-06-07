import React, { useState } from 'react'
import { Upload } from 'lucide-react'
import { Button } from '@/components/ui/button'
import { DocumentList } from './DocumentList'
import { DocumentUpload } from './DocumentUpload'
import { useDocuments } from '@/viewmodels/useDocuments'

export default function KnowledgeBasePage() {
  const [isUploadOpen, setIsUploadOpen] = useState(false)
  const { documents, loading, error, addDocument } = useDocuments()

  return (
    <div className="p-8 max-w-6xl mx-auto w-full">
      <div className="flex flex-col md:flex-row justify-between items-start md:items-center mb-8 gap-4">
        <div>
          <h1 className="text-2xl font-bold text-slate-900 tracking-tight">Kho Tài Liệu AI (Knowledge Base)</h1>
          <p className="text-slate-500 mt-1">Nơi lưu trữ và xử lý tài liệu để AI có thể đọc và trả lời câu hỏi của bạn.</p>
        </div>
        <Button 
          onClick={() => setIsUploadOpen(true)}
          className="bg-indigo-600 hover:bg-indigo-700 text-white shadow-sm gap-2"
        >
          <Upload className="h-4 w-4" />
          Tải file lên (Upload)
        </Button>
      </div>

      {error && (
        <div className="bg-red-50 text-red-600 p-4 rounded-lg mb-6 border border-red-100">
          {error}
        </div>
      )}

      <DocumentList documents={documents} loading={loading} />

      <DocumentUpload 
        open={isUploadOpen} 
        onOpenChange={setIsUploadOpen} 
        onUploadComplete={addDocument}
      />
    </div>
  )
}
