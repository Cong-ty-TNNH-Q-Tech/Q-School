import { useEffect } from 'react'
import { useParams, Link, useNavigate } from 'react-router-dom'
import { Pencil, Clock, Target, Layers, FileText, ChevronLeft, Calendar, User } from 'lucide-react'

import { Button } from '@/components/ui/button'
import { Badge } from '@/components/ui/badge'
import {
  Card,
  CardContent,
  CardHeader,
  CardTitle,
} from '@/components/ui/card'

import { useLessons } from '@/viewmodels/useLessons'

export default function LessonDetail() {
  const { id } = useParams<{ id: string }>()
  const navigate = useNavigate()
  const { selectedLesson, fetchLessonDetail, isLoading, error } = useLessons()

  useEffect(() => {
    if (id) {
      fetchLessonDetail(id)
    }
  }, [id, fetchLessonDetail])

  if (isLoading) {
    return (
      <div className="flex items-center justify-center min-h-[400px]">
        <div className="text-muted-foreground animate-pulse">Đang tải thông tin bài giảng...</div>
      </div>
    )
  }

  if (error || !selectedLesson) {
    return (
      <div className="flex flex-col items-center justify-center min-h-[400px] space-y-4">
        <div className="text-destructive font-medium">{error || 'Không tìm thấy bài giảng'}</div>
        <Button variant="outline" onClick={() => navigate('/lessons')}>
          <ChevronLeft className="mr-2 h-4 w-4" /> Quay lại danh sách
        </Button>
      </div>
    )
  }

  const { title, subject, grade_level, content, created_at, teacher_name } = selectedLesson
  
  // Calculate total duration
  const totalDuration = content?.sections?.reduce((acc, section) => acc + (section.duration_minutes || 0), 0) || 0

  return (
    <div className="space-y-6 max-w-5xl mx-auto pb-10">
      {/* Header Area */}
      <div>
        <div className="flex items-center gap-2 text-sm text-muted-foreground mb-3">
          <Link to="/lessons" className="hover:text-foreground transition-colors flex items-center">
            <ChevronLeft className="h-4 w-4 mr-1" /> Danh sách
          </Link>
          <span>/</span>
          <span className="text-foreground font-medium truncate max-w-[200px]">{title}</span>
        </div>
        
        <div className="flex flex-col sm:flex-row sm:items-start justify-between gap-4">
          <div className="space-y-1">
            <h2 className="text-3xl font-bold tracking-tight">{title}</h2>
            <div className="flex flex-wrap items-center gap-3 text-muted-foreground pt-1">
              {subject && <Badge variant="outline">{subject}</Badge>}
              {grade_level && <Badge variant="secondary">Khối {grade_level}</Badge>}
              {teacher_name && (
                <div className="flex items-center text-sm">
                  <User className="mr-1 h-3.5 w-3.5" /> {teacher_name}
                </div>
              )}
              <div className="flex items-center text-sm">
                <Calendar className="mr-1 h-3.5 w-3.5" /> 
                {new Date(created_at).toLocaleDateString('vi-VN')}
              </div>
            </div>
          </div>
          <Button onClick={() => navigate(`/lessons/${id}/edit`)}>
            <Pencil className="mr-2 h-4 w-4" /> Chỉnh sửa
          </Button>
        </div>
      </div>

      {/* Stat Cards */}
      <div className="grid gap-4 grid-cols-2 md:grid-cols-4">
        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Thời lượng</CardTitle>
            <Clock className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{totalDuration} <span className="text-base font-normal text-muted-foreground">phút</span></div>
          </CardContent>
        </Card>
        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Cấu trúc</CardTitle>
            <Layers className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{content?.sections?.length || 0} <span className="text-base font-normal text-muted-foreground">phần</span></div>
          </CardContent>
        </Card>
        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Mục tiêu</CardTitle>
            <Target className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{content?.objectives?.length || 0}</div>
          </CardContent>
        </Card>
        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Tài liệu</CardTitle>
            <FileText className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{content?.materials?.length || 0}</div>
          </CardContent>
        </Card>
      </div>

      {/* Content Area */}
      <div className="space-y-6">
        
        {/* Objectives */}
        {content?.objectives && content.objectives.length > 0 && (
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center text-lg">
                <Target className="mr-2 h-5 w-5 text-indigo-500" /> Mục tiêu bài học
              </CardTitle>
            </CardHeader>
            <CardContent>
              <ul className="space-y-2">
                {content.objectives.map((obj, i) => (
                  <li key={i} className="flex items-start">
                    <span className="flex h-6 w-6 shrink-0 items-center justify-center rounded-full bg-indigo-100 text-indigo-700 text-xs font-medium mr-3 mt-0.5">
                      {i + 1}
                    </span>
                    <span className="leading-relaxed">{obj}</span>
                  </li>
                ))}
              </ul>
            </CardContent>
          </Card>
        )}

        {/* Sections */}
        {content?.sections && content.sections.length > 0 && (
          <div className="space-y-4">
            <h3 className="text-xl font-bold tracking-tight pt-4">Nội dung chi tiết</h3>
            <div className="space-y-4">
              {content.sections.map((section, i) => (
                <Card key={i} className="overflow-hidden">
                  <div className="bg-muted/50 px-6 py-3 border-b flex flex-col sm:flex-row sm:items-center justify-between gap-2">
                    <h4 className="font-semibold text-base flex items-center">
                      <span className="text-muted-foreground mr-2 text-sm font-normal">Phần {i + 1}:</span>
                      {section.title}
                    </h4>
                    {section.duration_minutes && (
                      <Badge variant="outline" className="w-fit bg-background">
                        <Clock className="mr-1 h-3 w-3" /> {section.duration_minutes} phút
                      </Badge>
                    )}
                  </div>
                  <CardContent className="pt-6">
                    <div className="prose prose-sm max-w-none text-muted-foreground whitespace-pre-wrap">
                      {section.content}
                    </div>
                  </CardContent>
                </Card>
              ))}
            </div>
          </div>
        )}

        <div className="grid md:grid-cols-2 gap-6 pt-4">
          {/* Materials */}
          {content?.materials && content.materials.length > 0 && (
            <Card>
              <CardHeader>
                <CardTitle className="flex items-center text-lg">
                  <FileText className="mr-2 h-5 w-5 text-emerald-500" /> Tài liệu cần chuẩn bị
                </CardTitle>
              </CardHeader>
              <CardContent>
                <ul className="list-disc pl-5 space-y-1 text-muted-foreground">
                  {content.materials.map((mat, i) => (
                    <li key={i}>{mat}</li>
                  ))}
                </ul>
              </CardContent>
            </Card>
          )}

          {/* Homework */}
          {content?.homework && (
            <Card className="md:col-span-1 h-full">
              <CardHeader>
                <CardTitle className="flex items-center text-lg">
                  <Layers className="mr-2 h-5 w-5 text-amber-500" /> Bài tập về nhà
                </CardTitle>
              </CardHeader>
              <CardContent>
                <p className="text-muted-foreground whitespace-pre-wrap">
                  {content.homework}
                </p>
              </CardContent>
            </Card>
          )}
        </div>
      </div>
    </div>
  )
}
