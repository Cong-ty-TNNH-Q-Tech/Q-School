import { useParams, Link } from 'react-router-dom'
import { Button } from '@/components/ui/button'
import { Badge } from '@/components/ui/badge'
import {
  Card,
  CardContent,
  CardHeader,
  CardTitle,
} from '@/components/ui/card'
import { Separator } from '@/components/ui/separator'

export default function QuizDetail() {
  const { id } = useParams<{ id: string }>()

  return (
    <div className="space-y-6">
      <div>
        <div className="flex items-center gap-2 text-sm text-muted-foreground mb-1">
          <Link to="/quizzes" className="hover:underline">Bài kiểm tra</Link>
          <span>/</span>
          <span>Chi tiết</span>
        </div>
        <div className="flex items-center justify-between">
          <h2 className="text-2xl font-bold tracking-tight">Kiểm tra Giới hạn</h2>
          <div className="flex items-center gap-2">
            <Badge>Đã xuất bản</Badge>
            <Button asChild>
              <Link to={`/quizzes/${id}/take`}>Làm bài ngay</Link>
            </Button>
          </div>
        </div>
        <p className="text-muted-foreground">Mã bài kiểm tra: {id}</p>
      </div>

      <div className="grid gap-4 md:grid-cols-4">
        <Card>
          <CardHeader className="pb-2">
            <CardTitle className="text-sm font-medium">Số câu hỏi</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">20</div>
          </CardContent>
        </Card>
        <Card>
          <CardHeader className="pb-2">
            <CardTitle className="text-sm font-medium">Thời gian</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">30 phút</div>
          </CardContent>
        </Card>
        <Card>
          <CardHeader className="pb-2">
            <CardTitle className="text-sm font-medium">Lượt làm</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">128</div>
          </CardContent>
        </Card>
        <Card>
          <CardHeader className="pb-2">
            <CardTitle className="text-sm font-medium">Điểm TB</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">7.5</div>
          </CardContent>
        </Card>
      </div>

      <Separator />

      <Card>
        <CardHeader>
          <CardTitle>Danh sách câu hỏi</CardTitle>
        </CardHeader>
        <CardContent>
          <p className="text-sm text-muted-foreground text-center py-12">
            Danh sách câu hỏi sẽ được hiển thị ở đây khi Backend sẵn sàng.
          </p>
        </CardContent>
      </Card>

      <Button variant="outline" asChild>
        <Link to="/quizzes">Quay lại</Link>
      </Button>
    </div>
  )
}
