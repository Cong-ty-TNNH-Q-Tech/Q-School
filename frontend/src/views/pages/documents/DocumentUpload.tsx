import { useState, useRef, type DragEvent, type ChangeEvent } from 'react';
import { UploadCloud, File as FileIcon, X, CheckCircle2 } from 'lucide-react';
import { Button } from '@/components/ui/button';
import { uploadDocumentMock } from '@/services/mockData/document.mock';
import type { Document } from '@/models/document';
import { cn } from '@/lib/utils';

interface DocumentUploadProps {
  isOpen: boolean;
  onClose: () => void;
  onUploadSuccess: (doc: Document) => void;
}

export default function DocumentUpload({ isOpen, onClose, onUploadSuccess }: DocumentUploadProps) {
  const [isDragging, setIsDragging] = useState(false);
  const [selectedFile, setSelectedFile] = useState<File | null>(null);
  const [isUploading, setIsUploading] = useState(false);
  const [progress, setProgress] = useState(0);
  const fileInputRef = useRef<HTMLInputElement>(null);

  if (!isOpen) return null;

  const handleDragOver = (e: DragEvent<HTMLDivElement>) => {
    e.preventDefault();
    setIsDragging(true);
  };

  const handleDragLeave = () => {
    setIsDragging(false);
  };

  const handleDrop = (e: DragEvent<HTMLDivElement>) => {
    e.preventDefault();
    setIsDragging(false);
    
    if (e.dataTransfer.files && e.dataTransfer.files.length > 0) {
      handleFileSelection(e.dataTransfer.files[0]);
    }
  };

  const handleFileChange = (e: ChangeEvent<HTMLInputElement>) => {
    if (e.target.files && e.target.files.length > 0) {
      handleFileSelection(e.target.files[0]);
    }
  };

  const handleFileSelection = (file: File) => {
    // Validate file type (PDF, DOCX, Images)
    const validTypes = ['application/pdf', 'application/vnd.openxmlformats-officedocument.wordprocessingml.document', 'image/jpeg', 'image/png', 'image/jpg'];
    const validExts = ['.pdf', '.docx', '.jpg', '.jpeg', '.png'];
    
    const isValidType = validTypes.includes(file.type);
    const isValidExt = validExts.some(ext => file.name.toLowerCase().endsWith(ext));

    if (isValidType || isValidExt) {
      setSelectedFile(file);
    } else {
      alert('Vui lòng chọn file PDF, DOCX hoặc Hình ảnh (JPG, PNG).');
    }
  };

  const handleUpload = async () => {
    if (!selectedFile) return;
    
    setIsUploading(true);
    setProgress(0);
    
    try {
      const newDoc = await uploadDocumentMock(selectedFile, (p) => setProgress(p));
      onUploadSuccess(newDoc);
      
      // Reset state and close after short delay to show 100%
      setTimeout(() => {
        handleClose();
      }, 500);
    } catch (error) {
      console.error("Lỗi upload:", error);
      setIsUploading(false);
    }
  };

  const handleClose = () => {
    if (isUploading) return;
    setSelectedFile(null);
    setProgress(0);
    setIsUploading(false);
    onClose();
  };

  return (
    <div className="fixed inset-0 z-50 bg-black/50 flex items-center justify-center p-4">
      <div className="bg-white rounded-xl shadow-xl w-full max-w-md overflow-hidden relative">
        <button 
          onClick={handleClose}
          disabled={isUploading}
          className="absolute right-4 top-4 text-gray-400 hover:text-gray-600 disabled:opacity-50"
        >
          <X className="w-5 h-5" />
        </button>

        <div className="p-6">
          <h2 className="text-xl font-semibold text-gray-900 mb-6">Tải tài liệu lên</h2>

          {!selectedFile ? (
            <div 
              onDragOver={handleDragOver}
              onDragLeave={handleDragLeave}
              onDrop={handleDrop}
              onClick={() => fileInputRef.current?.click()}
              className={cn(
                "border-2 border-dashed rounded-xl p-8 flex flex-col items-center justify-center cursor-pointer transition-colors",
                isDragging ? "border-primary bg-primary/5" : "border-gray-200 hover:border-primary/50 hover:bg-gray-50"
              )}
            >
              <input 
                type="file" 
                ref={fileInputRef}
                className="hidden" 
                accept=".pdf,.docx,.jpg,.jpeg,.png,application/pdf,application/vnd.openxmlformats-officedocument.wordprocessingml.document,image/jpeg,image/png"
                onChange={handleFileChange}
              />
              <UploadCloud className="w-10 h-10 text-gray-400 mb-4" />
              <p className="text-sm font-medium text-gray-700 mb-1">
                Kéo thả file vào đây hoặc <span className="text-primary">chọn file</span>
              </p>
              <p className="text-xs text-gray-500">
                Hỗ trợ PDF, DOCX, JPG, PNG (Tối đa 50MB)
              </p>
            </div>
          ) : (
            <div className="border rounded-xl p-4 mb-6">
              <div className="flex items-start">
                <div className="w-10 h-10 rounded-lg bg-blue-50 flex items-center justify-center mr-3 shrink-0">
                  <FileIcon className="w-5 h-5 text-blue-500" />
                </div>
                <div className="flex-1 min-w-0">
                  <p className="text-sm font-medium text-gray-900 truncate">{selectedFile.name}</p>
                  <p className="text-xs text-gray-500">{(selectedFile.size / (1024 * 1024)).toFixed(2)} MB</p>
                  
                  {isUploading && (
                    <div className="mt-3">
                      <div className="flex justify-between text-xs mb-1">
                        <span className="text-gray-500">Đang tải lên...</span>
                        <span className="font-medium text-primary">{progress}%</span>
                      </div>
                      <div className="w-full bg-gray-100 rounded-full h-1.5 overflow-hidden">
                        <div 
                          className="bg-primary h-1.5 rounded-full transition-all duration-200 ease-out"
                          style={{ width: `${progress}%` }}
                        ></div>
                      </div>
                    </div>
                  )}
                  {progress === 100 && (
                    <div className="mt-2 flex items-center text-xs text-green-600 font-medium">
                      <CheckCircle2 className="w-3.5 h-3.5 mr-1" />
                      Hoàn tất
                    </div>
                  )}
                </div>
              </div>
            </div>
          )}
        </div>

        <div className="bg-gray-50 px-6 py-4 flex justify-end gap-3 border-t">
          <Button variant="outline" onClick={handleClose} disabled={isUploading}>
            Hủy
          </Button>
          <Button 
            onClick={handleUpload} 
            disabled={!selectedFile || isUploading}
            className="bg-primary hover:bg-primary/90"
          >
            {isUploading ? 'Đang tải...' : 'Bắt đầu tải lên'}
          </Button>
        </div>
      </div>
    </div>
  );
}
