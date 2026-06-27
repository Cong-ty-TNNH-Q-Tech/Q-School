import { useEffect } from 'react';
import type { Document, DocumentStatus } from '@/models/document';
import type { Document, DocumentStatus } from '@/models/document';
import { FileText, Image as ImageIcon, File, Loader2, CheckCircle2, AlertCircle, Clock } from 'lucide-react';

interface DocumentListProps {
  documents: Document[];
}

export default function DocumentList({ documents }: DocumentListProps) {
  
  const getFileIcon = (format?: string) => {
    if (!format) return <File className="w-5 h-5 text-gray-400" />;
    if (format.includes('PDF')) return <FileText className="w-5 h-5 text-red-500" />;
    if (format.includes('Word')) return <FileText className="w-5 h-5 text-blue-500" />;
    if (format.includes('Image')) return <ImageIcon className="w-5 h-5 text-purple-500" />;
    return <File className="w-5 h-5 text-gray-400" />;
  };

  const getStatusBadge = (status: DocumentStatus) => {
    switch (status) {
      case 'ready':
        return (
          <span className="inline-flex items-center gap-1.5 px-3 py-1 rounded-full text-xs font-medium bg-green-50 text-green-700 border border-green-200">
            <CheckCircle2 className="w-3.5 h-3.5" />
            Ready (Sẵn sàng)
          </span>
        );
      case 'parsing':
        return (
          <span className="inline-flex items-center gap-1.5 px-3 py-1 rounded-full text-xs font-medium bg-yellow-50 text-yellow-700 border border-yellow-200">
            <Loader2 className="w-3.5 h-3.5 animate-spin" />
            Parsing (Đang xử lý...)
          </span>
        );
      case 'error':
        return (
          <span className="inline-flex items-center gap-1.5 px-3 py-1 rounded-full text-xs font-medium bg-red-50 text-red-700 border border-red-200">
            <AlertCircle className="w-3.5 h-3.5" />
            Error (Lỗi)
          </span>
        );
      case 'pending':
      default:
        return (
          <span className="inline-flex items-center gap-1.5 px-3 py-1 rounded-full text-xs font-medium bg-gray-50 text-gray-600 border border-gray-200">
            <Clock className="w-3.5 h-3.5" />
            Pending (Đang chờ)
          </span>
        );
    }
  };

  const formatSize = (bytes?: number) => {
    if (!bytes) return '--';
    return (bytes / (1024 * 1024)).toFixed(1) + ' MB';
  };

  const formatDate = (dateString?: string) => {
    if (!dateString) return '--';
    const date = new Date(dateString);
    const today = new Date();
    const isToday = date.getDate() === today.getDate() && date.getMonth() === today.getMonth() && date.getFullYear() === today.getFullYear();
    
    if (isToday) return 'Hôm nay';
    return date.toLocaleDateString('vi-VN');
  };

  return (
    <div className="bg-white rounded-xl border border-gray-200 overflow-hidden shadow-sm">
      <div className="overflow-x-auto">
        <table className="w-full text-left border-collapse">
          <thead>
            <tr className="bg-gray-50/50 border-b border-gray-200">
              <th className="px-6 py-4 text-xs font-semibold text-gray-500 uppercase tracking-wider w-[35%]">Tên File</th>
              <th className="px-6 py-4 text-xs font-semibold text-gray-500 uppercase tracking-wider w-[15%]">Định Dạng</th>
              <th className="px-6 py-4 text-xs font-semibold text-gray-500 uppercase tracking-wider w-[15%]">Kích Thước</th>
              <th className="px-6 py-4 text-xs font-semibold text-gray-500 uppercase tracking-wider w-[20%]">Trạng Thái Xử Lý AI</th>
              <th className="px-6 py-4 text-xs font-semibold text-gray-500 uppercase tracking-wider w-[15%]">Ngày Tải Lên</th>
            </tr>
          </thead>
          <tbody className="divide-y divide-gray-100">
            {documents.length === 0 ? (
              <tr>
                <td colSpan={5} className="px-6 py-12 text-center text-gray-500">
                  Chưa có tài liệu nào. Hãy tải file lên để bắt đầu.
                </td>
              </tr>
            ) : (
              documents.map((doc) => (
                <tr key={doc.id} className="hover:bg-gray-50/50 transition-colors group">
                  <td className="px-6 py-4">
                    <div className="flex items-center gap-3">
                      <div className="w-8 h-8 rounded bg-gray-50 flex items-center justify-center shrink-0 border border-gray-100">
                        {getFileIcon(doc.format)}
                      </div>
                      <span className="font-medium text-gray-900 text-sm truncate max-w-[250px]" title={doc.filename}>
                        {doc.filename}
                      </span>
                    </div>
                  </td>
                  <td className="px-6 py-4">
                    <span className="text-sm text-gray-500">{doc.format || '--'}</span>
                  </td>
                  <td className="px-6 py-4">
                    <span className="text-sm text-gray-500">{formatSize(doc.size)}</span>
                  </td>
                  <td className="px-6 py-4">
                    {getStatusBadge(doc.status)}
                  </td>
                  <td className="px-6 py-4">
                    <span className="text-sm text-gray-500">{formatDate(doc.created_at)}</span>
                  </td>
                </tr>
              ))
            )}
          </tbody>
        </table>
      </div>
      
      {/* Pagination footer (Static for now as per design) */}
      <div className="px-6 py-4 border-t border-gray-200 bg-gray-50/30 flex items-center justify-between">
        <span className="text-sm text-gray-500">
          Hiển thị 1-{documents.length} trong số {documents.length} tài liệu
        </span>
        <div className="flex items-center gap-2">
          <button className="w-8 h-8 rounded border border-gray-200 flex items-center justify-center text-gray-400 disabled:opacity-50" disabled>
            &lt;
          </button>
          <button className="w-8 h-8 rounded border border-gray-200 flex items-center justify-center text-gray-400 disabled:opacity-50" disabled>
            &gt;
          </button>
        </div>
      </div>
    </div>
  );
}
