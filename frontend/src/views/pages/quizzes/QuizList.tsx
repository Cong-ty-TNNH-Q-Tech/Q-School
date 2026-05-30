import { Link } from 'react-router-dom'
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

const MOCK_QUIZZES = [
  { id: '1', title: 'Kiểm tra Giới hạn', subject: 'Toán', questionCount: 20, duration: '30 phút', status: 'published' as const },
  { id: '2', title: 'Kiểm tra Đạo hàm', subject: 'Toán', questionCount: 15, duration: '25 phút', status: 'published' as const },
  { id: '3', title: 'Trắc nghiệm Vật Lý', subject: 'Vật Lý', questionCount: 30, duration: '45 phút', status: 'draft' as const },
  { id: '4', title: 'Python Basics Quiz', subject: 'CNTT', questionCount: 25, duration: '40 phút', status: 'published' as const },
]

export default function QuizList() {
  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-2xl font-bold tracking-tight">Bài kiểm tra</h2>
          <p className="text-muted-foreground">
            Quản lý tất cả bài kiểm tra
          </p>
        </div>
        <Button>Tạo bài kiểm tra</Button>
      </div>

      <div className="rounded-md border">
        <Table>
          <TableHeader>
            <TableRow>
              <TableHead>Tên bài kiểm tra</TableHead>
              <TableHead>Môn</TableHead>
              <TableHead className="text-center">Số câu</TableHead>
              <TableHead>Thời gian</TableHead>
              <TableHead>Trạng thái</TableHead>
              <TableHead className="text-right">Hành động</TableHead>
            </TableRow>
          </TableHeader>
          <TableBody>
            {MOCK_QUIZZES.map((quiz) => (
              <TableRow key={quiz.id}>
                <TableCell className="font-medium">{quiz.title}</TableCell>
                <TableCell>{quiz.subject}</TableCell>
                <TableCell className="text-center">{quiz.questionCount}</TableCell>
                <TableCell>{quiz.duration}</TableCell>
                <TableCell>
                  <Badge variant={quiz.status === 'published' ? 'default' : 'secondary'}>
                    {quiz.status === 'published' ? 'Đã xuất bản' : 'Bản nháp'}
                  </Badge>
                </TableCell>
                <TableCell className="text-right">
                  <div className="flex justify-end gap-2">
                    <Button variant="ghost" size="sm" asChild>
                      <Link to={`/quizzes/${quiz.id}`}>Chi tiết</Link>
                    </Button>
                    <Button variant="outline" size="sm" asChild>
                      <Link to={`/quizzes/${quiz.id}/take`}>Làm bài</Link>
                    </Button>
                  </div>
                </TableCell>
              </TableRow>
            ))}
          </TableBody>
        </Table>
      </div>
    </div>
  )
}
