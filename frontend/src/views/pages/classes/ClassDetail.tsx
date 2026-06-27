import { useEffect, useState } from 'react'
import { useParams, useNavigate } from 'react-router-dom'
import { ArrowLeft, UserPlus, Trash2 } from 'lucide-react'

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
  Dialog,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
} from '@/components/ui/dialog'
import { Label } from '@/components/ui/label'

import { useClasses } from '@/viewmodels/useClasses'
import type { ClassStudent } from '@/models'

export default function ClassDetail() {
  const { id } = useParams<{ id: string }>()
  const navigate = useNavigate()
  
  const { 
    selectedClass, 
    classStudents, 
    fetchClassDetail, 
    fetchClassStudents, 
    addStudent, 
    removeStudent, 
    isLoading 
  } = useClasses()

  const [isAddStudentOpen, setIsAddStudentOpen] = useState(false)
  const [newStudentId, setNewStudentId] = useState('')

  useEffect(() => {
    if (id) {
      fetchClassDetail(id)
      fetchClassStudents(id)
    }
  }, [id, fetchClassDetail, fetchClassStudents])

  const handleAddStudent = async (e: React.FormEvent) => {
    e.preventDefault()
    if (!id || !newStudentId) return
    try {
      await addStudent(id, newStudentId)
      setIsAddStudentOpen(false)
      setNewStudentId('')
    } catch {
      alert('Không thể thêm học sinh này. ID có thể đã tồn tại.')
    }
  }

  const handleRemoveStudent = async (studentId: string) => {
    if (!id) return
    if (confirm('Xóa học sinh này khỏi lớp?')) {
      await removeStudent(id, studentId)
    }
  }

  if (isLoading && !selectedClass) {
    return <div className="p-8 text-center text-muted-foreground">Đang tải thông tin lớp...</div>
  }

  if (!selectedClass) {
    return <div className="p-8 text-center text-red-500">Không tìm thấy lớp học.</div>
  }

  return (
    <div className="space-y-6">
      <div className="flex items-center gap-4">
        <Button variant="outline" size="icon" onClick={() => navigate('/dashboard/classes')}>
          <ArrowLeft className="h-4 w-4" />
        </Button>
        <div>
          <h2 className="text-2xl font-bold tracking-tight">{selectedClass.name}</h2>
          <p className="text-muted-foreground">
            Khối: {selectedClass.grade_level || 'N/A'} | Môn: {selectedClass.subject || 'N/A'} | Tạo lúc: {new Date(selectedClass.created_at).toLocaleDateString('vi-VN')}
          </p>
        </div>
      </div>

      <div className="flex items-center justify-between">
        <h3 className="text-lg font-medium">Danh sách học sinh ({selectedClass.student_count || 0})</h3>
        <Button onClick={() => setIsAddStudentOpen(true)} className="bg-indigo-600 hover:bg-indigo-700">
          <UserPlus className="mr-2 h-4 w-4" /> Thêm học sinh
        </Button>
      </div>

      <div className="rounded-md border bg-card">
        <Table>
          <TableHeader>
            <TableRow>
              <TableHead>MÃ HỌC SINH</TableHead>
              <TableHead>NGÀY GIA NHẬP</TableHead>
              <TableHead className="text-right">HÀNH ĐỘNG</TableHead>
            </TableRow>
          </TableHeader>
          <TableBody>
            {classStudents.length === 0 ? (
              <TableRow>
                <TableCell colSpan={3} className="text-center h-24 text-muted-foreground">
                  Lớp học chưa có học sinh nào.
                </TableCell>
              </TableRow>
            ) : (
              classStudents.map((student: ClassStudent) => (
                <TableRow key={student.student_id}>
                  <TableCell className="font-medium">{student.student_id}</TableCell>
                  <TableCell>{new Date(student.joined_at).toLocaleDateString('vi-VN')}</TableCell>
                  <TableCell className="text-right">
                    <Button
                      variant="ghost"
                      size="icon"
                      className="text-red-500 hover:text-red-700"
                      onClick={() => handleRemoveStudent(student.student_id)}
                    >
                      <Trash2 className="h-4 w-4" />
                    </Button>
                  </TableCell>
                </TableRow>
              ))
            )}
          </TableBody>
        </Table>
      </div>

      <Dialog open={isAddStudentOpen} onOpenChange={setIsAddStudentOpen}>
        <DialogContent className="sm:max-w-[425px]">
          <form onSubmit={handleAddStudent}>
            <DialogHeader>
              <DialogTitle>Thêm học sinh vào lớp</DialogTitle>
              <DialogDescription>
                Nhập ID của học sinh để thêm vào lớp này.
              </DialogDescription>
            </DialogHeader>
            <div className="grid gap-4 py-4">
              <div className="grid grid-cols-4 items-center gap-4">
                <Label htmlFor="studentId" className="text-right">
                  Mã học sinh
                </Label>
                <Input
                  id="studentId"
                  value={newStudentId}
                  onChange={(e) => setNewStudentId(e.target.value)}
                  className="col-span-3"
                  placeholder="VD: 22222222-..."
                  required
                />
              </div>
            </div>
            <DialogFooter>
              <Button type="button" variant="outline" onClick={() => setIsAddStudentOpen(false)}>
                Hủy
              </Button>
              <Button type="submit" disabled={!newStudentId || isLoading}>
                Thêm vào lớp
              </Button>
            </DialogFooter>
          </form>
        </DialogContent>
      </Dialog>
    </div>
  )
}
