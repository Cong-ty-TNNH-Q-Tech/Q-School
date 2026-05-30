import { Link } from 'react-router-dom'
import { Button } from '@/components/ui/button'

export default function NotFound() {
  return (
    <div className="flex min-h-screen flex-col items-center justify-center bg-background px-4">
      <div className="text-center space-y-6">
        <div className="space-y-2">
          <h1 className="text-8xl font-bold tracking-tighter text-primary">404</h1>
          <h2 className="text-2xl font-semibold tracking-tight">Trang không tồn tại</h2>
          <p className="text-muted-foreground max-w-md">
            Xin lỗi, trang bạn đang tìm kiếm không tồn tại hoặc đã bị di chuyển.
          </p>
        </div>
        <div className="flex gap-3 justify-center">
          <Button asChild>
            <Link to="/dashboard">Về Dashboard</Link>
          </Button>
          <Button variant="outline" asChild>
            <Link to="/">Về trang chủ</Link>
          </Button>
        </div>
      </div>
    </div>
  )
}
