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

export default function LessonDetail() {
  const { id } = useParams<{ id: string }>()

  return (
    <div className="space-y-6">
      <div>
        <div className="flex items-center gap-2 text-sm text-muted-foreground mb-1">
          <Link to="/lessons" className="hover:underline">Bài học</Link>
          <span>/</span>
          <span>Chi tiết</span>
        </div>
        <div className="flex items-center justify-between">
          <h2 className="text-2xl font-bold tracking-tight">Giới hạn và Liên tục</h2>
          <Badge>Đã xuất bản</Badge>
        </div>
        <p className="text-muted-foreground">Mã bài học: {id}</p>
      </div>

      <div className="grid gap-4 md:grid-cols-4">
        <Card>
          <CardHeader className="pb-2">
            <CardTitle className="text-sm font-medium">Thời lượng</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">45 phút</div>
          </CardContent>
        </Card>
        <Card>
          <CardHeader className="pb-2">
            <CardTitle className="text-sm font-medium">Lớp</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">Toán A1</div>
          </CardContent>
        </Card>
        <Card>
          <CardHeader className="pb-2">
            <CardTitle className="text-sm font-medium">Tài liệu</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">3</div>
          </CardContent>
        </Card>
        <Card>
          <CardHeader className="pb-2">
            <CardTitle className="text-sm font-medium">Bài kiểm tra</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">1</div>
          </CardContent>
        </Card>
      </div>

      <Separator />

      <Card>
        <CardHeader>
          <CardTitle>Nội dung bài học</CardTitle>
        </CardHeader>
        <CardContent>
          <p className="text-sm text-muted-foreground text-center py-12">
            Nội dung bài học sẽ được hiển thị ở đây khi Backend sẵn sàng.
          </p>
        </CardContent>
      </Card>

      <div className="flex gap-3">
        <Button variant="outline" asChild>
          <Link to="/lessons">Quay lại</Link>
        </Button>
        <Button>Chỉnh sửa</Button>
      </div>
    </div>
  )
}
