import { useState } from 'react';
import { Upload } from 'lucide-react';
import { Button } from '@/components/ui/button';
import DocumentList from './DocumentList';
import { DocumentUpload } from './DocumentUpload';
import { useDocuments } from '@/viewmodels/useDocuments';

export default function DocumentPage() {
  const [isUploadOpen, setIsUploadOpen] = useState(false);
  const { documents, loading, error, addDocument } = useDocuments();

  return (
    <div className="w-full max-w-6xl mx-auto py-8 px-4">
      <div className="flex items-center justify-between mb-8">
        <div>
          <h1 className="text-2xl font-bold text-gray-900 mb-1">Kho Tài Liệu AI (Knowledge Base)</h1>
          <p className="text-gray-500 text-sm">
            Nơi lưu trữ và xử lý tài liệu để AI có thể đọc và trả lời câu hỏi của bạn.
          </p>
        </div>
        
        <Button 
          onClick={() => setIsUploadOpen(true)}
          className="bg-primary hover:bg-primary/90 text-white font-medium flex items-center gap-2 rounded-lg"
        >
          <Upload className="w-4 h-4" />
          Tải file lên (Upload)
        </Button>
      </div>

      {error && (
        <div className="bg-red-50 text-red-600 p-4 rounded-lg mb-6 border border-red-100">
          {error}
        </div>
      )}

      {loading ? (
        <div className="flex justify-center items-center h-64">
          <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-primary"></div>
        </div>
      ) : (
        <DocumentList documents={documents} />
      )}

      <DocumentUpload 
        open={isUploadOpen} 
        onOpenChange={setIsUploadOpen} 
        onUploadComplete={addDocument}
      />
    </div>
  );
}
