import { useEffect } from 'react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { BookOpen, Award, Library, Clock, PlayCircle } from 'lucide-react';
import type { Activity } from '@/models/student_dashboard';
import { useStudentDashboard } from '@/viewmodels/useStudentDashboard';

const StudentDashboard = () => {
  const { data, isLoading, error, fetchDashboardData } = useStudentDashboard();

  useEffect(() => {
    fetchDashboardData();
  }, [fetchDashboardData]);

  if (isLoading) return <div className="p-8">Đang tải dữ liệu...</div>;
  if (error) return <div className="p-8 text-red-500">Lỗi: {error}</div>;
  if (!data) return null;

  const getActivityIcon = (type: Activity['type']) => {
    switch (type) {
      case 'assignment': return <BookOpen className="h-5 w-5 text-blue-500" />;
      case 'flashcard': return <Library className="h-5 w-5 text-purple-500" />;
      case 'lesson': return <PlayCircle className="h-5 w-5 text-green-500" />;
      default: return <BookOpen className="h-5 w-5" />;
    }
  };

  const getStatusBadge = (status: Activity['status']) => {
    switch (status) {
      case 'completed': return <Badge variant="default" className="bg-green-100 text-green-800">Hoàn thành</Badge>;
      case 'pending': return <Badge variant="secondary" className="bg-yellow-100 text-yellow-800">Đang chờ</Badge>;
      case 'upcoming': return <Badge variant="outline" className="bg-blue-100 text-blue-800">Sắp tới</Badge>;
      default: return null;
    }
  };

  return (
    <div className="p-8 space-y-8">
      <h1 className="text-3xl font-bold tracking-tight">Tổng quan học tập</h1>
      
      {/* Stats Overview */}
      <div className="grid gap-4 md:grid-cols-3">
        <Card>
          <CardHeader className="flex flex-row items-center justify-between pb-2 space-y-0">
            <CardTitle className="text-sm font-medium">Bài tập sắp tới</CardTitle>
            <Clock className="w-4 h-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{data.stats.upcomingAssignments}</div>
            <p className="text-xs text-muted-foreground">Cần hoàn thành trong tuần này</p>
          </CardContent>
        </Card>
        <Card>
          <CardHeader className="flex flex-row items-center justify-between pb-2 space-y-0">
            <CardTitle className="text-sm font-medium">Điểm trung bình</CardTitle>
            <Award className="w-4 h-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{data.stats.averageScore}</div>
            <p className="text-xs text-muted-foreground">Thuộc top 15% của lớp</p>
          </CardContent>
        </Card>
        <Card>
          <CardHeader className="flex flex-row items-center justify-between pb-2 space-y-0">
            <CardTitle className="text-sm font-medium">Thẻ Flashcard cần ôn</CardTitle>
            <Library className="w-4 h-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{data.stats.flashcardsToReview}</div>
            <p className="text-xs text-muted-foreground">Đã đến hạn ôn tập Spaced Repetition</p>
          </CardContent>
        </Card>
      </div>

      <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-7">
        {/* Recent Activities */}
        <Card className="col-span-4">
          <CardHeader>
            <CardTitle>Lịch học & Hoạt động</CardTitle>
            <CardDescription>Các nhiệm vụ học tập gần đây của bạn.</CardDescription>
          </CardHeader>
          <CardContent>
            <div className="space-y-6">
              {data.recentActivities.map((activity) => (
                <div key={activity.id} className="flex items-center justify-between space-x-4">
                  <div className="flex items-center space-x-4">
                    <div className="p-2 bg-gray-100 rounded-full dark:bg-gray-800">
                      {getActivityIcon(activity.type)}
                    </div>
                    <div>
                      <p className="text-sm font-medium leading-none">{activity.title}</p>
                      <p className="text-sm text-muted-foreground">
                        {new Date(activity.date).toLocaleDateString('vi-VN', {
                          weekday: 'long',
                          year: 'numeric',
                          month: 'long',
                          day: 'numeric',
                        })}
                      </p>
                    </div>
                  </div>
                  <div>{getStatusBadge(activity.status)}</div>
                </div>
              ))}
            </div>
          </CardContent>
        </Card>

        {/* Quick Actions */}
        <Card className="col-span-3">
          <CardHeader>
            <CardTitle>Hành động nhanh</CardTitle>
            <CardDescription>Tiếp tục việc học của bạn ngay bây giờ.</CardDescription>
          </CardHeader>
          <CardContent className="space-y-4">
            <Button className="w-full flex justify-start items-center space-x-2" size="lg">
              <PlayCircle className="w-5 h-5" />
              <span>Vào không gian học tập</span>
            </Button>
            <Button variant="outline" className="w-full flex justify-start items-center space-x-2" size="lg">
              <BookOpen className="w-5 h-5" />
              <span>Làm bài kiểm tra sắp tới</span>
            </Button>
            <Button variant="secondary" className="w-full flex justify-start items-center space-x-2" size="lg">
              <Library className="w-5 h-5" />
              <span>Ôn tập Flashcards</span>
            </Button>
          </CardContent>
        </Card>
      </div>
    </div>
  );
};

export default StudentDashboard;
