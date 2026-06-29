import { useEffect, useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { Plus, Search, MoreVertical, BookOpen, Pencil, Eye, Trash2 } from 'lucide-react'

import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from '@/components/ui/table'
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuTrigger,
} from '@/components/ui/dropdown-menu'
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from '@/components/ui/select'
import { Badge } from '@/components/ui/badge'
import {
  AlertDialog,
  AlertDialogAction,
  AlertDialogCancel,
  AlertDialogContent,
  AlertDialogDescription,
  AlertDialogFooter,
  AlertDialogHeader,
  AlertDialogTitle,
} from '@/components/ui/alert-dialog'

import { useLessons } from '@/viewmodels/useLessons'
import { useAuthStore } from '@/stores/useAuthStore'
import { SUBJECT_OPTIONS, GRADE_OPTIONS } from './lesson.constants'

export default function LessonList() {
  const navigate = useNavigate()
  const user = useAuthStore((state) => state.user)
  const { lessons, fetchLessons, deleteLesson, isLoading } = useLessons()

  const [searchQuery, setSearchQuery] = useState('')
  const [gradeFilter, setGradeFilter] = useState('all')
  const [subjectFilter, setSubjectFilter] = useState('all')

  const [deletingLessonId, setDeletingLessonId] = useState<string | null>(null)

  useEffect(() => {
    if (user) {
      fetchLessons(user.id)
    }
  }, [user, fetchLessons])

  const handleDelete = async () => {
    if (deletingLessonId) {
      await deleteLesson(deletingLessonId)
      setDeletingLessonId(null)
    }
  }

  // Filtering
  const filteredLessons = lessons.filter((lesson) => {
    const matchesSearch = lesson.title.toLowerCase().includes(searchQuery.toLowerCase())
    const matchesGrade = gradeFilter === 'all' || lesson.grade_level === gradeFilter
    const matchesSubject = subjectFilter === 'all' || lesson.subject === subjectFilter
    return matchesSearch && matchesGrade && matchesSubject
  })

  // Helper for grade badge colors
  const getGradeBadgeVariant = (grade: string | null) => {
    if (grade === '10') return 'default'
    if (grade === '11') return 'secondary'
    return 'outline'
  }

  return (
    <div className="space-y-6">
      <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4">
        <div>
          <h2 className="text-2xl font-bold tracking-tight">Bài giảng của tôi</h2>
          <p className="text-muted-foreground">
            Quản lý và soạn thảo nội dung giáo án điện tử
          </p>
        </div>
        <Button onClick={() => navigate('/lessons/new')} className="bg-indigo-600 hover:bg-indigo-700">
          <Plus className="mr-2 h-4 w-4" /> Tạo bài giảng mới
        </Button>
      </div>

      <div className="flex flex-col sm:flex-row gap-4">
        <div className="relative flex-1">
          <Search className="absolute left-2.5 top-2.5 h-4 w-4 text-muted-foreground" />
          <Input
            type="search"
            placeholder="Tìm kiếm theo tiêu đề..."
            className="pl-8"
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
          />
        </div>
        <Select value={gradeFilter} onValueChange={setGradeFilter}>
          <SelectTrigger className="w-full sm:w-[180px]">
            <SelectValue placeholder="Khối lớp (Tất cả)" />
          </SelectTrigger>
          <SelectContent>
            <SelectItem value="all">Khối lớp (Tất cả)</SelectItem>
            {GRADE_OPTIONS.map(opt => (
              <SelectItem key={opt.value} value={opt.value}>{opt.label}</SelectItem>
            ))}
          </SelectContent>
        </Select>
        <Select value={subjectFilter} onValueChange={setSubjectFilter}>
          <SelectTrigger className="w-full sm:w-[180px]">
            <SelectValue placeholder="Môn học (Tất cả)" />
          </SelectTrigger>
          <SelectContent>
            <SelectItem value="all">Môn học (Tất cả)</SelectItem>
            {SUBJECT_OPTIONS.map(opt => (
              <SelectItem key={opt.value} value={opt.value}>{opt.label}</SelectItem>
            ))}
          </SelectContent>
        </Select>
      </div>

      <div className="rounded-md border bg-card">
        <Table>
          <TableHeader>
            <TableRow>
              <TableHead className="w-[300px]">TIÊU ĐỀ BÀI GIẢNG</TableHead>
              <TableHead>MÔN HỌC</TableHead>
              <TableHead>KHỐI LỚP</TableHead>
              <TableHead>NGÀY TẠO</TableHead>
              <TableHead className="text-right">HÀNH ĐỘNG</TableHead>
            </TableRow>
          </TableHeader>
          <TableBody>
            {isLoading && lessons.length === 0 ? (
              <TableRow>
                <TableCell colSpan={5} className="text-center h-24 text-muted-foreground">
                  Đang tải dữ liệu...
                </TableCell>
              </TableRow>
            ) : filteredLessons.length === 0 ? (
              <TableRow>
                <TableCell colSpan={5} className="text-center h-24 text-muted-foreground">
                  Không tìm thấy bài giảng nào.
                </TableCell>
              </TableRow>
            ) : (
              filteredLessons.map((lesson) => (
                <TableRow key={lesson.id}>
                  <TableCell className="font-medium cursor-pointer" onClick={() => navigate(`/lessons/${lesson.id}`)}>
                    <div className="flex items-center gap-3">
                      <div className="bg-primary/10 p-2 rounded-md">
                        <BookOpen className="h-4 w-4 text-primary" />
                      </div>
                      <span className="truncate max-w-[200px] sm:max-w-xs">{lesson.title}</span>
                    </div>
                  </TableCell>
                  <TableCell>
                    {lesson.subject || '—'}
                  </TableCell>
                  <TableCell>
                    {lesson.grade_level ? (
                      <Badge variant={getGradeBadgeVariant(lesson.grade_level)} className={lesson.grade_level === '10' ? 'bg-green-100 text-green-800 hover:bg-green-100' : lesson.grade_level === '11' ? 'bg-indigo-100 text-indigo-800 hover:bg-indigo-100' : 'bg-slate-100 text-slate-800'}>
                        Khối {lesson.grade_level}
                      </Badge>
                    ) : (
                      '—'
                    )}
                  </TableCell>
                  <TableCell>
                    {new Date(lesson.created_at).toLocaleDateString('vi-VN')}
                  </TableCell>
                  <TableCell className="text-right">
                    <DropdownMenu>
                      <DropdownMenuTrigger asChild>
                        <Button variant="ghost" className="h-8 w-8 p-0">
                          <span className="sr-only">Mở menu</span>
                          <MoreVertical className="h-4 w-4" />
                        </Button>
                      </DropdownMenuTrigger>
                      <DropdownMenuContent align="end">
                        <DropdownMenuItem onClick={() => navigate(`/lessons/${lesson.id}`)}>
                          <Eye className="mr-2 h-4 w-4" /> Xem chi tiết
                        </DropdownMenuItem>
                        <DropdownMenuItem onClick={() => navigate(`/lessons/${lesson.id}/edit`)}>
                          <Pencil className="mr-2 h-4 w-4" /> Chỉnh sửa
                        </DropdownMenuItem>
                        <DropdownMenuItem
                          className="text-red-600 focus:text-red-600"
                          onClick={() => setDeletingLessonId(lesson.id)}
                        >
                          <Trash2 className="mr-2 h-4 w-4" /> Xóa bài giảng
                        </DropdownMenuItem>
                      </DropdownMenuContent>
                    </DropdownMenu>
                  </TableCell>
                </TableRow>
              ))
            )}
          </TableBody>
        </Table>
      </div>

      {/* TODO: Thêm Cursor Pagination khi tích hợp Backend API (AGENTS.md §5) */}

      <AlertDialog open={!!deletingLessonId} onOpenChange={(open: boolean) => !open && setDeletingLessonId(null)}>
        <AlertDialogContent>
          <AlertDialogHeader>
            <AlertDialogTitle>Xác nhận xóa bài giảng</AlertDialogTitle>
            <AlertDialogDescription>
              Hành động này không thể hoàn tác. Bạn có chắc chắn muốn xóa bài giảng này khỏi hệ thống không?
            </AlertDialogDescription>
          </AlertDialogHeader>
          <AlertDialogFooter>
            <AlertDialogCancel>Hủy</AlertDialogCancel>
            <AlertDialogAction onClick={handleDelete} className="bg-destructive text-destructive-foreground hover:bg-destructive/90">
              Xóa bài giảng
            </AlertDialogAction>
          </AlertDialogFooter>
        </AlertDialogContent>
      </AlertDialog>

    </div>
  )
}
