import { useState, useRef, useId } from 'react';
import { Upload, X, FileText } from 'lucide-react';
import { Textarea } from '@/components/ui/textarea';
import { Button } from '@/components/ui/button';
import { cn } from '@/lib/utils';

const ALLOWED_MIME_TYPES = [
  'application/pdf',
  'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
  'text/plain',
]

const ALLOWED_EXTENSIONS = ['.pdf', '.docx', '.txt']
const MAX_SIZE_BYTES = 10 * 1024 * 1024

interface TextInputAreaProps {
  value: string;
  onChange: (val: string) => void;
  placeholder?: string;
  onFileUpload: (file: File | null) => void;
  uploadedFile: File | null;
  disabled?: boolean;
}

export function TextInputArea({
  value,
  onChange,
  placeholder = 'Nhập văn bản vào đây...',
  onFileUpload,
  uploadedFile,
  disabled = false
}: TextInputAreaProps) {
  // [FIX #1] Dùng error state thay vì alert() để hiển thị lỗi inline
  const [fileError, setFileError] = useState<string | null>(null);
  const fileInputRef = useRef<HTMLInputElement>(null);
  // [FIX Phase6-B3] Dùng useId() để generate unique ID — tránh duplicate ID khi nhiều trang mount cùng lúc
  const fileInputId = useId();
  const fileErrorId = useId();

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (!file) return;

    setFileError(null);

    // [FIX #4] Validate MIME type + extension để tương thích cross-browser
    const ext = '.' + file.name.split('.').pop()?.toLowerCase();
    const isValidType = ALLOWED_MIME_TYPES.includes(file.type) || ALLOWED_EXTENSIONS.includes(ext);
    if (!isValidType) {
      setFileError('Chỉ hỗ trợ file PDF, DOCX hoặc TXT');
      if (fileInputRef.current) fileInputRef.current.value = '';
      return;
    }

    if (file.size > MAX_SIZE_BYTES) {
      setFileError('Kích thước file không được vượt quá 10MB');
      if (fileInputRef.current) fileInputRef.current.value = '';
      return;
    }

    onFileUpload(file);
    if (fileInputRef.current) fileInputRef.current.value = '';
  };

  const clearFile = () => {
    onFileUpload(null);
    setFileError(null);
  };

  const acceptAttr = `${ALLOWED_EXTENSIONS.join(',')},${ALLOWED_MIME_TYPES.join(',')}`

  return (
    <div className="flex flex-col gap-1.5">
      <div className="relative rounded-lg border border-gray-200 bg-white shadow-sm focus-within:ring-2 focus-within:ring-primary/20 focus-within:border-primary transition-all">
        <Textarea
          value={value}
          onChange={(e) => onChange(e.target.value)}
          placeholder={placeholder}
          aria-label={placeholder || 'Nhập văn bản'}
          disabled={disabled || !!uploadedFile}
          className={cn(
            "min-h-[200px] resize-y border-0 focus-visible:ring-0 p-4 pb-14 bg-transparent",
            uploadedFile ? "opacity-50" : ""
          )}
        />

        <div className="absolute bottom-3 left-3 right-3 flex items-center justify-between bg-white pt-2">
          <div className="flex items-center gap-2">
            {uploadedFile ? (
              <div className="flex items-center gap-2 bg-primary/5 text-primary px-3 py-1.5 rounded-md text-sm border border-primary/10">
                <FileText className="w-4 h-4 flex-shrink-0" />
                <span className="truncate max-w-[200px]">{uploadedFile.name}</span>
                <button
                  onClick={clearFile}
                  disabled={disabled}
                  className="hover:bg-primary/10 p-0.5 rounded-full transition-colors ml-1 flex-shrink-0 focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-primary/50"
                  title="Xóa tệp"
                  aria-label="Xóa tệp đính kèm"
                  type="button"
                >
                  <X className="w-3.5 h-3.5" />
                </button>
              </div>
            ) : (
              <>
                <input
                  type="file"
                  ref={fileInputRef}
                  onChange={handleFileChange}
                  accept={acceptAttr}
                  className="hidden"
                  id={fileInputId}
                  aria-label="Tải lên tài liệu"
                  disabled={disabled || value.length > 0}
                />
                <Button
                  type="button"
                  variant="ghost"
                  size="sm"
                  className={cn(
                    "text-gray-500 hover:text-primary hover:bg-primary/5 h-8 px-3 transition-colors",
                    (disabled || value.length > 0) && "opacity-50 cursor-not-allowed"
                  )}
                  onClick={() => fileInputRef.current?.click()}
                  disabled={disabled || value.length > 0}
                >
                  <Upload className="w-4 h-4 mr-2" />
                  Tải lên tài liệu
                </Button>
              </>
            )}
          </div>

          <div className="text-xs text-gray-400">
            {!uploadedFile && `${value.length} ký tự`}
          </div>
        </div>
      </div>

      {/* [FIX #1] Inline error message — không dùng alert() */}
      {fileError && (
        <p id={fileErrorId} role="alert" className="text-sm text-red-500 font-medium">{fileError}</p>
      )}
    </div>
  );
}
