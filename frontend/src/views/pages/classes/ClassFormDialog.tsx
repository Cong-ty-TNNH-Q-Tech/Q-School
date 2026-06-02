import { useState, useEffect } from 'react'
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
} from '@/components/ui/dialog'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'
import { useClasses } from '@/viewmodels/useClasses'
import { useAuthStore } from '@/stores/useAuthStore'
import type { Class } from '@/models'

interface ClassFormDialogProps {
  open: boolean
  onOpenChange: (open: boolean) => void
  classData?: Class | null
}

export default function ClassFormDialog({ open, onOpenChange, classData }: ClassFormDialogProps) {
  const isEditing = !!classData
  const [name, setName] = useState('')
  const [gradeLevel, setGradeLevel] = useState('')
  const [subject, setSubject] = useState('')
  
  const { createClass, updateClass, isLoading } = useClasses()
  const user = useAuthStore((state) => state.user)

  useEffect(() => {
    if (open) {
      if (classData) {
        setName(classData.name)
        setGradeLevel(classData.grade_level || '')
        setSubject(classData.subject || '')
      } else {
        setName('')
        setGradeLevel('')
        setSubject('')
      }
    }
  }, [open, classData])

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    if (!name || !user) return

    try {
      if (isEditing && classData) {
        await updateClass(classData.id, { name, grade_level: gradeLevel, subject })
      } else {
        await createClass({ name, grade_level: gradeLevel, subject }, user.id)
      }
      onOpenChange(false)
    } catch (error) {
      console.error('Failed to submit class', error)
    }
  }

  return (
    <Dialog open={open} onOpenChange={onOpenChange}>
      <DialogContent className="sm:max-w-[425px]">
        <form onSubmit={handleSubmit}>
          <DialogHeader>
            <DialogTitle>{isEditing ? 'Cập nhật lớp học' : 'Tạo lớp học mới'}</DialogTitle>
            <DialogDescription>
              {isEditing
                ? 'Chỉnh sửa thông tin lớp học hiện tại.'
                : 'Điền thông tin để tạo lớp học mới.'}
            </DialogDescription>
          </DialogHeader>
          <div className="grid gap-4 py-4">
            <div className="grid grid-cols-4 items-center gap-4">
              <Label htmlFor="name" className="text-right">
                Tên lớp <span className="text-red-500">*</span>
              </Label>
              <Input
                id="name"
                value={name}
                onChange={(e) => setName(e.target.value)}
                className="col-span-3"
                placeholder="VD: 10A1 - Toán Nâng Cao"
                required
              />
            </div>
            <div className="grid grid-cols-4 items-center gap-4">
              <Label htmlFor="gradeLevel" className="text-right">
                Khối lớp
              </Label>
              <Input
                id="gradeLevel"
                value={gradeLevel}
                onChange={(e) => setGradeLevel(e.target.value)}
                className="col-span-3"
                placeholder="VD: 10"
              />
            </div>
            <div className="grid grid-cols-4 items-center gap-4">
              <Label htmlFor="subject" className="text-right">
                Môn học
              </Label>
              <Input
                id="subject"
                value={subject}
                onChange={(e) => setSubject(e.target.value)}
                className="col-span-3"
                placeholder="VD: Toán"
              />
            </div>
          </div>
          <DialogFooter>
            <Button type="button" variant="outline" onClick={() => onOpenChange(false)} disabled={isLoading}>
              Hủy
            </Button>
            <Button type="submit" disabled={!name || isLoading}>
              {isLoading ? 'Đang lưu...' : isEditing ? 'Cập nhật' : 'Tạo mới'}
            </Button>
          </DialogFooter>
        </form>
      </DialogContent>
    </Dialog>
  )
}
