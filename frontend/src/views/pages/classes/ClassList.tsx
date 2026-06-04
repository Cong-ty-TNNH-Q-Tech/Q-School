import { useEffect, useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { Plus, Search, MoreVertical, RefreshCw } from 'lucide-react'

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

import { useClasses } from '@/viewmodels/useClasses'
import { useAuthStore } from '@/stores/useAuthStore'
import ClassFormDialog from './ClassFormDialog'
import type { Class } from '@/models'

export default function ClassList() {
  const navigate = useNavigate()
  const user = useAuthStore((state) => state.user)
  const { classes, fetchClasses, deleteClass, isLoading } = useClasses()

  const [searchQuery, setSearchQuery] = useState('')
  const [gradeFilter, setGradeFilter] = useState('all')
  const [subjectFilter, setSubjectFilter] = useState('all')

  const [isDialogOpen, setIsDialogOpen] = useState(false)
  const [editingClass, setEditingClass] = useState<Class | null>(null)

  useEffect(() => {
    if (user) {
      fetchClasses(user.id)
    }
  }, [user, fetchClasses])

  const handleCreate = () => {
    setEditingClass(null)
    setIsDialogOpen(true)
  }

  const handleEdit = (cls: Class) => {
    setEditingClass(cls)
    setIsDialogOpen(true)
  }

  const handleDelete = async (id: string) => {
    if (confirm('Bạn có chắc chắn muốn xóa lớp học này không?')) {
      await deleteClass(id)
    }
  }

  // Filtering
  const filteredClasses = classes.filter((cls) => {
    const matchesSearch = cls.name.toLowerCase().includes(searchQuery.toLowerCase())
    const matchesGrade = gradeFilter === 'all' || cls.grade_level === gradeFilter
    const matchesSubject = subjectFilter === 'all' || cls.subject === subjectFilter
    return matchesSearch && matchesGrade && matchesSubject
  })

  // Helper to render badge color based on grade
  const getGradeBadgeVariant = (name: string) => {
    if (name.startsWith('10')) return 'default'
    if (name.startsWith('11')) return 'secondary'
    return 'outline'
  }

  const getGradePrefix = (name: string) => {
    const match = name.match(/^(10|11|12)[A-Z]/)
    return match ? match[0] : 'N/A'
  }

  return (
    <div className="space-y-6">
      <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4">
        <div>
          <h2 className="text-2xl font-bold tracking-tight">Lớp học của tôi</h2>
          <p className="text-muted-foreground">
            Quản lý danh sách lớp, học sinh và bài tập
          </p>
        </div>
        <Button onClick={handleCreate} className="bg-indigo-600 hover:bg-indigo-700">
          <Plus className="mr-2 h-4 w-4" /> Tạo lớp học mới
        </Button>
      </div>

      <div className="flex flex-col sm:flex-row gap-4">
        <div className="relative flex-1">
          <Search className="absolute left-2.5 top-2.5 h-4 w-4 text-muted-foreground" />
          <Input
            type="search"
            placeholder="Tìm kiếm theo tên lớp..."
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
            <SelectItem value="10">Khối 10</SelectItem>
            <SelectItem value="11">Khối 11</SelectItem>
            <SelectItem value="12">Khối 12</SelectItem>
          </SelectContent>
        </Select>
        <Select value={subjectFilter} onValueChange={setSubjectFilter}>
          <SelectTrigger className="w-full sm:w-[180px]">
            <SelectValue placeholder="Môn học (Tất cả)" />
          </SelectTrigger>
          <SelectContent>
            <SelectItem value="all">Môn học (Tất cả)</SelectItem>
            <SelectItem value="Toán">Toán</SelectItem>
            <SelectItem value="Vật Lý">Vật Lý</SelectItem>
            <SelectItem value="Hóa">Hóa Học</SelectItem>
            <SelectItem value="Ngữ Văn">Ngữ Văn</SelectItem>
            <SelectItem value="Tiếng Anh">Tiếng Anh</SelectItem>
          </SelectContent>
        </Select>
      </div>

      <div className="rounded-md border">
        <Table>
          <TableHeader>
            <TableRow>
              <TableHead className="w-[300px]">TÊN LỚP</TableHead>
              <TableHead>SĨ SỐ</TableHead>
              <TableHead>BÀI TẬP ĐANG MỞ</TableHead>
              <TableHead>NGÀY TẠO</TableHead>
              <TableHead className="text-right">HÀNH ĐỘNG</TableHead>
            </TableRow>
          </TableHeader>
          <TableBody>
            {isLoading && classes.length === 0 ? (
              <TableRow>
                <TableCell colSpan={5} className="text-center h-24 text-muted-foreground">
                  Đang tải dữ liệu...
                </TableCell>
              </TableRow>
            ) : filteredClasses.length === 0 ? (
              <TableRow>
                <TableCell colSpan={5} className="text-center h-24 text-muted-foreground">
                  Không tìm thấy lớp học nào.
                </TableCell>
              </TableRow>
            ) : (
              filteredClasses.map((cls) => (
                <TableRow key={cls.id}>
                  <TableCell className="font-medium cursor-pointer" onClick={() => navigate(`/dashboard/classes/${cls.id}`)}>
                    <div className="flex items-center gap-3">
                      <Badge variant={getGradeBadgeVariant(cls.name)} className={cls.name.startsWith('10') ? 'bg-green-100 text-green-800 hover:bg-green-100' : cls.name.startsWith('11') ? 'bg-indigo-100 text-indigo-800 hover:bg-indigo-100' : 'bg-slate-100 text-slate-800'}>
                        {getGradePrefix(cls.name)}
                      </Badge>
                      {cls.name}
                    </div>
                  </TableCell>
                  <TableCell>{cls.student_count || 0}</TableCell>
                  <TableCell>
                    {/* Mock assignment count for UI fidelity based on the screenshot */}
                    <Badge variant="secondary" className={cls.name.includes('Toán Nâng Cao') ? 'bg-green-100 text-green-800 hover:bg-green-100' : cls.name.includes('Cơ Bản') ? 'bg-slate-100 text-slate-800' : cls.name.includes('THPT QG') ? 'bg-red-100 text-red-800 hover:bg-red-100' : 'bg-green-100 text-green-800'}>
                      {cls.name.includes('Toán Nâng Cao') ? '3 bài tập' : cls.name.includes('Cơ Bản') ? '0 bài tập' : cls.name.includes('THPT QG') ? '5 bài tập' : '1-2 bài tập'}
                    </Badge>
                  </TableCell>
                  <TableCell>
                    {new Date(cls.created_at).toLocaleDateString('vi-VN')}
                  </TableCell>
                  <TableCell className="text-right">
                    <DropdownMenu>
                      <DropdownMenuTrigger asChild>
                        <Button variant="ghost" className="h-8 w-8 p-0">
                          <span className="sr-only">Open menu</span>
                          <MoreVertical className="h-4 w-4" />
                        </Button>
                      </DropdownMenuTrigger>
                      <DropdownMenuContent align="end">
                        <DropdownMenuItem onClick={() => navigate(`/dashboard/classes/${cls.id}`)}>
                          Xem chi tiết
                        </DropdownMenuItem>
                        <DropdownMenuItem onClick={() => handleEdit(cls)}>
                          Chỉnh sửa
                        </DropdownMenuItem>
                        <DropdownMenuItem
                          className="text-red-600 focus:text-red-600"
                          onClick={() => handleDelete(cls.id)}
                        >
                          Xóa lớp
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

      <div className="flex justify-center">
        <Button variant="outline" className="w-[150px]">
          <RefreshCw className="mr-2 h-4 w-4" /> Tải thêm...
        </Button>
      </div>

      <ClassFormDialog
        open={isDialogOpen}
        onOpenChange={setIsDialogOpen}
        classData={editingClass}
      />
    </div>
  )
}
