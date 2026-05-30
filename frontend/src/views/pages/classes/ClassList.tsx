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

const MOCK_CLASSES = [
  { id: '1', name: 'Toán Cao Cấp A1', subject: 'Toán', studentCount: 35, status: 'active' as const },
  { id: '2', name: 'Vật Lý Đại Cương', subject: 'Vật Lý', studentCount: 42, status: 'active' as const },
  { id: '3', name: 'Lập Trình Python', subject: 'CNTT', studentCount: 28, status: 'archived' as const },
]

export default function ClassList() {
  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-2xl font-bold tracking-tight">Lớp học</h2>
          <p className="text-muted-foreground">
            Quản lý tất cả lớp học của bạn
          </p>
        </div>
        <Button>Tạo lớp mới</Button>
      </div>

      <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-3">
        {MOCK_CLASSES.map((cls) => (
          <Card key={cls.id}>
            <CardHeader>
              <div className="flex items-center justify-between">
                <CardTitle className="text-lg">{cls.name}</CardTitle>
                <Badge variant={cls.status === 'active' ? 'default' : 'secondary'}>
                  {cls.status === 'active' ? 'Đang hoạt động' : 'Đã lưu trữ'}
                </Badge>
              </div>
              <CardDescription>{cls.subject}</CardDescription>
            </CardHeader>
            <CardContent>
              <p className="text-sm text-muted-foreground">
                {cls.studentCount} học sinh
              </p>
            </CardContent>
            <CardFooter>
              <Button variant="outline" className="w-full" asChild>
                <Link to={`/classes/${cls.id}`}>Xem chi tiết</Link>
              </Button>
            </CardFooter>
          </Card>
        ))}
      </div>
    </div>
  )
}
