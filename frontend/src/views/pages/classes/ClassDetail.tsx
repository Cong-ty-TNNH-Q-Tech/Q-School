import { useParams, Link } from 'react-router-dom'
import { Button } from '@/components/ui/button'
import { Badge } from '@/components/ui/badge'
import {
  Card,
  CardContent,
  CardHeader,
  CardTitle,
} from '@/components/ui/card'
import {
  Tabs,
  TabsContent,
  TabsList,
  TabsTrigger,
} from '@/components/ui/tabs'

export default function ClassDetail() {
  const { id } = useParams<{ id: string }>()

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <div className="flex items-center gap-2 text-sm text-muted-foreground mb-1">
            <Link to="/classes" className="hover:underline">Lớp học</Link>
            <span>/</span>
            <span>Chi tiết</span>
          </div>
          <h2 className="text-2xl font-bold tracking-tight">Toán Cao Cấp A1</h2>
          <p className="text-muted-foreground">Mã lớp: {id}</p>
        </div>
        <Badge>Đang hoạt động</Badge>
      </div>

      <div className="grid gap-4 md:grid-cols-3">
        <Card>
          <CardHeader className="pb-2">
            <CardTitle className="text-sm font-medium">Học sinh</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">35</div>
          </CardContent>
        </Card>
        <Card>
          <CardHeader className="pb-2">
            <CardTitle className="text-sm font-medium">Bài học</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">12</div>
          </CardContent>
        </Card>
        <Card>
          <CardHeader className="pb-2">
            <CardTitle className="text-sm font-medium">Bài kiểm tra</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">5</div>
          </CardContent>
        </Card>
      </div>

      <Tabs defaultValue="students">
        <TabsList>
          <TabsTrigger value="students">Học sinh</TabsTrigger>
          <TabsTrigger value="lessons">Bài học</TabsTrigger>
          <TabsTrigger value="quizzes">Bài kiểm tra</TabsTrigger>
        </TabsList>
        <TabsContent value="students" className="mt-4">
          <Card>
            <CardContent className="pt-6">
              <p className="text-sm text-muted-foreground text-center py-8">
                Danh sách học sinh sẽ được hiển thị ở đây.
              </p>
            </CardContent>
          </Card>
        </TabsContent>
        <TabsContent value="lessons" className="mt-4">
          <Card>
            <CardContent className="pt-6">
              <div className="flex flex-col items-center gap-3 py-8">
                <p className="text-sm text-muted-foreground">Danh sách bài học sẽ được hiển thị ở đây.</p>
                <Button variant="outline" asChild>
                  <Link to="/lessons">Xem tất cả bài học</Link>
                </Button>
              </div>
            </CardContent>
          </Card>
        </TabsContent>
        <TabsContent value="quizzes" className="mt-4">
          <Card>
            <CardContent className="pt-6">
              <div className="flex flex-col items-center gap-3 py-8">
                <p className="text-sm text-muted-foreground">Danh sách bài kiểm tra sẽ được hiển thị ở đây.</p>
                <Button variant="outline" asChild>
                  <Link to="/quizzes">Xem tất cả bài kiểm tra</Link>
                </Button>
              </div>
            </CardContent>
          </Card>
        </TabsContent>
      </Tabs>
    </div>
  )
}
