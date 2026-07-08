import { useEffect, useState } from 'react'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Badge } from '@/components/ui/badge'
import { Progress } from '@/components/ui/progress'
import {
  Users,
  GraduationCap,
  DollarSign,
  Activity,
  Shield,
  UserCheck,
  TrendingUp,
  Server,
  Database,
  Cpu,
  Clock,
  ChevronRight,
  BellRing
} from 'lucide-react'
import { useAdminDashboard } from '@/viewmodels/useAdminDashboard'
import type { RecentUserActivity } from '@/models/admin_dashboard'

export default function AdminDashboard() {
  const { data, isLoading, error, fetchDashboardData } = useAdminDashboard()
  const [toastMessage, setToastMessage] = useState<string | null>(null)

  useEffect(() => {
    fetchDashboardData()
  }, [fetchDashboardData])

  // Tự động ẩn Toast sau 3 giây
  useEffect(() => {
    if (toastMessage) {
      const timer = setTimeout(() => {
        setToastMessage(null)
      }, 3000)
      return () => clearTimeout(timer)
    }
  }, [toastMessage])

  if (isLoading) {
    return (
      <div className="flex items-center justify-center min-h-[400px]">
        <div className="flex flex-col items-center gap-2">
          <Activity className="h-8 w-8 text-primary animate-pulse" />
          <p className="text-sm text-muted-foreground animate-pulse">Đang tải thống kê hệ thống...</p>
        </div>
      </div>
    )
  }

  if (error) {
    return (
      <div className="p-6 border border-destructive/20 bg-destructive/10 rounded-lg text-destructive text-sm flex flex-col gap-2">
        <p className="font-semibold">Lỗi tải dữ liệu:</p>
        <p>{error}</p>
        <Button variant="outline" className="w-fit mt-2 border-destructive/20 text-destructive hover:bg-destructive/10" onClick={() => fetchDashboardData()}>
          Thử lại
        </Button>
      </div>
    )
  }

  if (!data) return null

  const showUnderDevelopment = (actionName: string) => {
    setToastMessage(`Tính năng "${actionName}" đang được phát triển.`)
  }

  const getActivityIcon = (action: RecentUserActivity['action']) => {
    switch (action) {
      case 'registered':
        return <UserCheck className="h-4 w-4 text-emerald-500" />
      case 'subscription_changed':
        return <DollarSign className="h-4 w-4 text-amber-500" />
      case 'content_created':
        return <Cpu className="h-4 w-4 text-blue-500" />
      case 'login':
      default:
        return <Activity className="h-4 w-4 text-slate-400" />
    }
  }

  const getRoleBadge = (role: RecentUserActivity['role']) => {
    switch (role) {
      case 'admin':
        return <Badge variant="destructive" className="text-[10px] px-1.5 py-0">Admin</Badge>
      case 'teacher':
        return <Badge variant="secondary" className="text-[10px] px-1.5 py-0 bg-blue-100 text-blue-800 dark:bg-blue-900/30 dark:text-blue-400">GV</Badge>
      case 'student':
      default:
        return <Badge variant="outline" className="text-[10px] px-1.5 py-0 bg-emerald-100 text-emerald-800 dark:bg-emerald-900/30 dark:text-emerald-400">HS</Badge>
    }
  }

  // Định dạng tiền tệ VNĐ
  const formatCurrency = (val: number) => {
    return new Intl.NumberFormat('vi-VN', { style: 'currency', currency: 'VND' }).format(val)
  }

  return (
    <div className="space-y-8 relative">
      {/* Toast Notification Container */}
      {toastMessage && (
        <div className="fixed bottom-6 right-6 z-50 bg-card border border-border rounded-lg shadow-lg p-4 flex items-center gap-3 animate-in slide-in-from-bottom-5 duration-300">
          <div className="h-8 w-8 rounded-full bg-primary/10 flex items-center justify-center">
            <BellRing className="h-4 w-4 text-primary" />
          </div>
          <div>
            <p className="text-sm font-medium text-foreground">{toastMessage}</p>
            <p className="text-xs text-muted-foreground">Vui lòng quay lại sau.</p>
          </div>
        </div>
      )}

      {/* Header */}
      <div className="flex flex-col gap-1">
        <h1 className="text-3xl font-bold tracking-tight">Tổng quan Hệ thống</h1>
        <p className="text-muted-foreground">
          Trang quản trị vận hành, thống kê tài nguyên, doanh thu và trạng thái server của Q-School AI.
        </p>
      </div>

      {/* 4 Stats Cards Grid */}
      <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-4">
        {/* Card Users */}
        <Card className="hover:shadow-md transition-shadow">
          <CardHeader className="flex flex-row items-center justify-between pb-2 space-y-0">
            <CardTitle className="text-sm font-medium">Người dùng</CardTitle>
            <Users className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{data.user_stats.total_users.toLocaleString()}</div>
            <div className="flex justify-between items-center mt-2 text-xs text-muted-foreground">
              <span>HS: {data.user_stats.total_students} | GV: {data.user_stats.total_teachers}</span>
              <span className="text-emerald-500 font-medium">+{data.user_stats.new_users_this_month} tháng này</span>
            </div>
          </CardContent>
        </Card>

        {/* Card Revenue */}
        <Card className="hover:shadow-md transition-shadow">
          <CardHeader className="flex flex-row items-center justify-between pb-2 space-y-0">
            <CardTitle className="text-sm font-medium">Doanh thu tháng</CardTitle>
            <DollarSign className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{formatCurrency(data.revenue_stats.monthly_revenue)}</div>
            <div className="flex items-center gap-1 mt-2 text-xs text-muted-foreground">
              <TrendingUp className="h-3 w-3 text-emerald-500" />
              <span className="text-emerald-500 font-medium">+{data.revenue_stats.revenue_growth_percent}%</span>
              <span>so với tháng trước</span>
            </div>
          </CardContent>
        </Card>

        {/* Card Active Subs */}
        <Card className="hover:shadow-md transition-shadow">
          <CardHeader className="flex flex-row items-center justify-between pb-2 space-y-0">
            <CardTitle className="text-sm font-medium">Gói cước hoạt động</CardTitle>
            <GraduationCap className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{data.revenue_stats.active_subscriptions}</div>
            <p className="text-xs text-muted-foreground mt-2">
              Tổng doanh thu: {formatCurrency(data.revenue_stats.total_revenue)}
            </p>
          </CardContent>
        </Card>

        {/* Card System Health */}
        <Card className="hover:shadow-md transition-shadow">
          <CardHeader className="flex flex-row items-center justify-between pb-2 space-y-0">
            <CardTitle className="text-sm font-medium">Trạng thái Server</CardTitle>
            <Server className="h-4 w-4 text-emerald-500" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold flex items-center gap-2">
              <span>{data.system_health.uptime_percent}%</span>
              <span className="h-2 w-2 rounded-full bg-emerald-500 inline-block animate-ping"></span>
            </div>
            <p className="text-xs text-muted-foreground mt-2">
              AI Service: <span className="text-emerald-500 font-medium capitalize">{data.system_health.ai_service_status}</span>
            </p>
          </CardContent>
        </Card>
      </div>

      {/* Grid: Activities & Health/Actions */}
      <div className="grid gap-6 md:grid-cols-2 lg:grid-cols-7">
        {/* Left Side: Recent Activities */}
        <Card className="lg:col-span-4 hover:shadow-md transition-shadow">
          <CardHeader className="flex flex-row items-center justify-between pb-4">
            <div>
              <CardTitle>Hoạt động gần đây</CardTitle>
              <CardDescription>Các sự kiện đăng ký và tác vụ mới nhất của hệ thống.</CardDescription>
            </div>
            <Activity className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="space-y-4">
              {data.recent_activities.map((activity) => (
                <div key={activity.id} className="flex items-start gap-3 justify-between pb-3 border-b border-border last:pb-0 last:border-b-0">
                  <div className="flex items-start gap-3">
                    <div className="p-2 bg-muted rounded-lg mt-0.5">
                      {getActivityIcon(activity.action)}
                    </div>
                    <div>
                      <div className="flex items-center gap-2 flex-wrap">
                        <span className="font-semibold text-sm">{activity.full_name || activity.username}</span>
                        {getRoleBadge(activity.role)}
                      </div>
                      <p className="text-sm text-muted-foreground mt-0.5">{activity.detail}</p>
                      <div className="flex items-center gap-1 mt-1 text-[10px] text-muted-foreground">
                        <Clock className="h-3 w-3" />
                        <span>
                          {new Date(activity.created_at).toLocaleDateString('vi-VN', {
                            hour: '2-digit',
                            minute: '2-digit',
                            year: 'numeric',
                            month: 'short',
                            day: 'numeric'
                          })}
                        </span>
                      </div>
                    </div>
                  </div>
                </div>
              ))}
            </div>
          </CardContent>
        </Card>

        {/* Right Side: Quick Actions & System Resource Info */}
        <div className="lg:col-span-3 space-y-6">
          {/* Quick Actions Card */}
          <Card className="hover:shadow-md transition-shadow">
            <CardHeader>
              <CardTitle>Hành động nhanh</CardTitle>
              <CardDescription>Quản trị viên thực hiện nhanh cấu hình.</CardDescription>
            </CardHeader>
            <CardContent className="flex flex-col gap-3">
              <Button
                variant="outline"
                className="w-full justify-between group"
                onClick={() => showUnderDevelopment('Quản lý Người dùng')}
              >
                <span className="flex items-center gap-2">
                  <Users className="h-4 w-4 text-blue-500" />
                  <span>Quản lý Người dùng</span>
                </span>
                <ChevronRight className="h-4 w-4 text-muted-foreground group-hover:translate-x-1 transition-transform" />
              </Button>
              <Button
                variant="outline"
                className="w-full justify-between group"
                onClick={() => showUnderDevelopment('Cấu hình Gói cước SaaS')}
              >
                <span className="flex items-center gap-2">
                  <DollarSign className="h-4 w-4 text-amber-500" />
                  <span>Quản lý Gói cước SaaS</span>
                </span>
                <ChevronRight className="h-4 w-4 text-muted-foreground group-hover:translate-x-1 transition-transform" />
              </Button>
              <Button
                variant="outline"
                className="w-full justify-between group"
                onClick={() => showUnderDevelopment('Cấu hình System Prompts')}
              >
                <span className="flex items-center gap-2">
                  <Shield className="h-4 w-4 text-purple-500" />
                  <span>Cấu hình System Prompts</span>
                </span>
                <ChevronRight className="h-4 w-4 text-muted-foreground group-hover:translate-x-1 transition-transform" />
              </Button>
            </CardContent>
          </Card>

          {/* Infrastructure status card */}
          <Card className="hover:shadow-md transition-shadow">
            <CardHeader>
              <CardTitle>Tài nguyên Hạ tầng</CardTitle>
              <CardDescription>Giám sát dung lượng và tiến trình AI đang chạy.</CardDescription>
            </CardHeader>
            <CardContent className="space-y-4">
              {/* Storage details */}
              <div className="space-y-2">
                <div className="flex justify-between text-xs font-medium">
                  <span className="flex items-center gap-1">
                    <Database className="h-3.5 w-3.5 text-muted-foreground" />
                    <span>Dung lượng lưu trữ (MinIO/R2)</span>
                  </span>
                  <span>{data.system_health.storage_used_percent}%</span>
                </div>
                <Progress value={data.system_health.storage_used_percent} className="h-2" />
              </div>

              {/* Celery tasks details */}
              <div className="flex justify-between items-center text-xs pt-2 border-t border-border">
                <span className="flex items-center gap-1">
                  <Cpu className="h-3.5 w-3.5 text-muted-foreground" />
                  <span>Tác vụ AI chạy ngầm (Celery)</span>
                </span>
                <Badge variant="secondary" className="font-semibold text-xs">
                  {data.system_health.active_ai_tasks} đang chạy
                </Badge>
              </div>

              <div className="flex justify-between items-center text-xs pt-2">
                <span className="flex items-center gap-1">
                  <Activity className="h-3.5 w-3.5 text-muted-foreground" />
                  <span>Độ trễ API vLLM</span>
                </span>
                <span className="text-emerald-500 font-semibold">Tốt (~150ms)</span>
              </div>
            </CardContent>
          </Card>
        </div>
      </div>
    </div>
  )
}
