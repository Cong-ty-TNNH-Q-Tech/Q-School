import { Button } from '@/components/ui/button'
import { Badge } from '@/components/ui/badge'
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from '@/components/ui/table'
import { Input } from '@/components/ui/input'

const MOCK_DOCUMENTS = [
  { id: '1', name: 'Giáo trình Toán Cao Cấp A1.pdf', type: 'PDF', size: '2.4 MB', uploadedAt: '2025-05-15', status: 'indexed' as const },
  { id: '2', name: 'Bài giảng Vật Lý - Chương 3.docx', type: 'DOCX', size: '1.1 MB', uploadedAt: '2025-05-18', status: 'indexed' as const },
  { id: '3', name: 'Slide Python OOP.pptx', type: 'PPTX', size: '5.8 MB', uploadedAt: '2025-05-20', status: 'processing' as const },
  { id: '4', name: 'Đề cương ôn thi cuối kỳ.pdf', type: 'PDF', size: '820 KB', uploadedAt: '2025-05-22', status: 'indexed' as const },
]

export default function Documents() {
  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-2xl font-bold tracking-tight">Tài liệu</h2>
          <p className="text-muted-foreground">
            Quản lý và tìm kiếm tài liệu học tập
          </p>
        </div>
        <Button>Tải lên tài liệu</Button>
      </div>

      <div className="flex gap-3">
        <Input
          id="document-search"
          placeholder="Tìm kiếm tài liệu..."
          className="max-w-sm"
        />
        <Button variant="outline">Tìm kiếm</Button>
      </div>

      <div className="rounded-md border">
        <Table>
          <TableHeader>
            <TableRow>
              <TableHead>Tên tài liệu</TableHead>
              <TableHead>Loại</TableHead>
              <TableHead>Kích thước</TableHead>
              <TableHead>Ngày tải lên</TableHead>
              <TableHead>Trạng thái</TableHead>
              <TableHead className="text-right">Hành động</TableHead>
            </TableRow>
          </TableHeader>
          <TableBody>
            {MOCK_DOCUMENTS.map((doc) => (
              <TableRow key={doc.id}>
                <TableCell className="font-medium">{doc.name}</TableCell>
                <TableCell>
                  <Badge variant="outline">{doc.type}</Badge>
                </TableCell>
                <TableCell>{doc.size}</TableCell>
                <TableCell>{doc.uploadedAt}</TableCell>
                <TableCell>
                  <Badge variant={doc.status === 'indexed' ? 'default' : 'secondary'}>
                    {doc.status === 'indexed' ? 'Đã index' : 'Đang xử lý'}
                  </Badge>
                </TableCell>
                <TableCell className="text-right">
                  <Button variant="ghost" size="sm">Xem</Button>
                </TableCell>
              </TableRow>
            ))}
          </TableBody>
        </Table>
      </div>
    </div>
  )
}
