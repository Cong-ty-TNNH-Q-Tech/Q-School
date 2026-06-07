import { FileText, FileImage, FileCode, CheckCircle2, Loader2, AlertCircle, MoreHorizontal } from 'lucide-react'
import type { Document } from '@/models/document'
import { Badge } from '@/components/ui/badge'
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from '@/components/ui/table'
import { Button } from '@/components/ui/button'

interface DocumentListProps {
  documents: Document[]
  loading: boolean
}

export function DocumentList({ documents, loading }: DocumentListProps) {
  const getFileIcon = (fileType: string) => {
    if (fileType.includes('pdf')) return <FileText className="h-5 w-5 text-red-500" />
    if (fileType.includes('word')) return <FileCode className="h-5 w-5 text-blue-500" />
    if (fileType.includes('image')) return <FileImage className="h-5 w-5 text-purple-500" />
    return <FileText className="h-5 w-5 text-slate-500" />
  }

  const getFormatName = (fileType: string) => {
    if (fileType.includes('pdf')) return 'PDF Document'
    if (fileType.includes('word')) return 'Word Document'
    if (fileType.includes('image')) return 'Image'
    return 'Document'
  }

  const getStatusBadge = (status: string) => {
    switch (status) {
      case 'ready':
        return (
          <Badge variant="outline" className="bg-emerald-50 text-emerald-700 border-emerald-200">
            <CheckCircle2 className="mr-1 h-3 w-3" /> Ready (Sẵn sàng)
          </Badge>
        )
      case 'parsing':
        return (
          <Badge variant="outline" className="bg-amber-50 text-amber-700 border-amber-200">
            <Loader2 className="mr-1 h-3 w-3 animate-spin" /> Parsing (Đang băm nhỏ...)
          </Badge>
        )
      case 'error':
        return (
          <Badge variant="outline" className="bg-red-50 text-red-700 border-red-200">
            <AlertCircle className="mr-1 h-3 w-3" /> Error (Lỗi đọc chữ OCR)
          </Badge>
        )
      default:
        return (
          <Badge variant="outline" className="bg-slate-50 text-slate-700 border-slate-200">
            Pending
          </Badge>
        )
    }
  }

  const formatSize = (bytes?: number) => {
    if (!bytes) return '--'
    return (bytes / (1024 * 1024)).toFixed(1) + ' MB'
  }

  const formatDate = (isoString: string) => {
    const date = new Date(isoString)
    const today = new Date()
    const isToday =
      date.getDate() === today.getDate() &&
      date.getMonth() === today.getMonth() &&
      date.getFullYear() === today.getFullYear()

    if (isToday) return 'Hôm nay'
    
    const yesterday = new Date(today)
    yesterday.setDate(yesterday.getDate() - 1)
    const isYesterday =
      date.getDate() === yesterday.getDate() &&
      date.getMonth() === yesterday.getMonth() &&
      date.getFullYear() === yesterday.getFullYear()

    if (isYesterday) return 'Hôm qua'

    return date.toLocaleDateString('vi-VN')
  }

  if (loading) {
    return (
      <div className="flex justify-center p-10">
        <Loader2 className="h-8 w-8 animate-spin text-primary" />
      </div>
    )
  }

  return (
    <div className="bg-white rounded-lg border shadow-sm">
      <Table>
        <TableHeader>
          <TableRow className="bg-slate-50 hover:bg-slate-50 text-slate-500 text-xs uppercase">
            <TableHead className="w-[300px]">Tên File</TableHead>
            <TableHead>Định dạng</TableHead>
            <TableHead>Kích thước</TableHead>
            <TableHead>Trạng thái xử lý AI</TableHead>
            <TableHead>Ngày tải lên</TableHead>
            <TableHead className="text-right">Thao tác</TableHead>
          </TableRow>
        </TableHeader>
        <TableBody>
          {documents.length === 0 ? (
            <TableRow>
              <TableCell colSpan={6} className="text-center py-10 text-slate-500">
                Chưa có tài liệu nào. Hãy tải lên file đầu tiên của bạn!
              </TableCell>
            </TableRow>
          ) : (
            documents.map((doc) => (
              <TableRow key={doc.id} className="group">
                <TableCell className="font-medium">
                  <div className="flex items-center gap-3">
                    <div className="p-2 bg-slate-50 rounded-lg group-hover:bg-white transition-colors border border-transparent group-hover:border-slate-100">
                      {getFileIcon(doc.file_type)}
                    </div>
                    <span className="truncate max-w-[200px]" title={doc.filename}>{doc.filename}</span>
                  </div>
                </TableCell>
                <TableCell className="text-slate-500">
                  <div className="flex flex-col">
                    <span>{doc.file_type.split('/')[1]?.toUpperCase() || 'FILE'}</span>
                    <span className="text-xs">{getFormatName(doc.file_type)}</span>
                  </div>
                </TableCell>
                <TableCell className="text-slate-500">{formatSize(doc.file_size)}</TableCell>
                <TableCell>{getStatusBadge(doc.status)}</TableCell>
                <TableCell className="text-slate-500">{formatDate(doc.created_at)}</TableCell>
                <TableCell className="text-right">
                  <Button variant="ghost" size="icon" className="text-slate-400 hover:text-slate-700">
                    <MoreHorizontal className="h-5 w-5" />
                  </Button>
                </TableCell>
              </TableRow>
            ))
          )}
        </TableBody>
      </Table>
      <div className="p-4 border-t text-sm text-slate-500 flex justify-between items-center">
        <span>Hiển thị 1-{documents.length} trong số {documents.length} tài liệu</span>
        <div className="flex gap-2">
          <Button variant="outline" size="sm" disabled>
            &lt;
          </Button>
          <Button variant="outline" size="sm" disabled>
            &gt;
          </Button>
        </div>
      </div>
    </div>
  )
}
