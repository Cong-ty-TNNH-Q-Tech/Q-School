import { Link } from 'react-router-dom'
import { Button } from '@/components/ui/button'
import { Badge } from '@/components/ui/badge'
import {
  Card,
  CardContent,
  CardDescription,
  CardFooter,
  CardHeader,
  CardTitle,
} from '@/components/ui/card'

const MOCK_LESSONS = [
  { id: '1', title: 'Giới hạn và Liên tục', subject: 'Toán Cao Cấp A1', duration: '45 phút', status: 'published' as const },
  { id: '2', title: 'Đạo hàm', subject: 'Toán Cao Cấp A1', duration: '60 phút', status: 'published' as const },
  { id: '3', title: 'Tích phân', subject: 'Toán Cao Cấp A1', duration: '50 phút', status: 'draft' as const },
  { id: '4', title: 'Chuyển động Newton', subject: 'Vật Lý Đại Cương', duration: '55 phút', status: 'published' as const },
]

export default function LessonList() {
  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-2xl font-bold tracking-tight">Bài học</h2>
          <p className="text-muted-foreground">
            Quản lý nội dung bài học
          </p>
        </div>
        <Button>Tạo bài học mới</Button>
      </div>

      <div className="grid gap-4 md:grid-cols-2">
        {MOCK_LESSONS.map((lesson) => (
          <Card key={lesson.id}>
            <CardHeader>
              <div className="flex items-center justify-between">
                <CardTitle className="text-lg">{lesson.title}</CardTitle>
                <Badge variant={lesson.status === 'published' ? 'default' : 'secondary'}>
                  {lesson.status === 'published' ? 'Đã xuất bản' : 'Bản nháp'}
                </Badge>
              </div>
              <CardDescription>{lesson.subject}</CardDescription>
            </CardHeader>
            <CardContent>
              <p className="text-sm text-muted-foreground">
                Thời lượng: {lesson.duration}
              </p>
            </CardContent>
            <CardFooter>
              <Button variant="outline" className="w-full" asChild>
                <Link to={`/lessons/${lesson.id}`}>Xem bài học</Link>
              </Button>
            </CardFooter>
          </Card>
        ))}
      </div>
    </div>
  )
}
