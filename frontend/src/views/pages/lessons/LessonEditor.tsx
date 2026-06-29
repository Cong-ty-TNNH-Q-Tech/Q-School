import { useParams, useNavigate } from 'react-router-dom'
import { ChevronLeft, Plus, Trash2, Save, BookOpen } from 'lucide-react'

import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'
import { Textarea } from '@/components/ui/textarea'
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from '@/components/ui/select'
import {
  Card,
  CardContent,
  CardHeader,
  CardTitle,
  CardDescription,
} from '@/components/ui/card'
import { Separator } from '@/components/ui/separator'

import { useLessonForm } from '@/viewmodels/useLessonForm'
import { SUBJECT_OPTIONS, GRADE_OPTIONS } from './lesson.constants'

export default function LessonEditor() {
  const { id } = useParams<{ id: string }>()
  const isEditMode = Boolean(id)
  const navigate = useNavigate()
  
  const form = useLessonForm(id)

  if (isEditMode && form.isLoading && !form.title) {
    return <div className="p-8 text-center text-muted-foreground animate-pulse">Đang tải dữ liệu bài giảng...</div>
  }

  return (
    <div className="space-y-6 max-w-4xl mx-auto pb-10">
      <div className="flex items-center gap-4">
        <Button variant="ghost" size="icon" onClick={() => navigate(-1)}>
          <ChevronLeft className="h-5 w-5" />
        </Button>
        <div>
          <h2 className="text-2xl font-bold tracking-tight">
            {isEditMode ? 'Chỉnh sửa bài giảng' : 'Tạo bài giảng mới'}
          </h2>
          <p className="text-muted-foreground">
            {isEditMode ? 'Cập nhật thông tin và nội dung bài giảng' : 'Thiết kế giáo án với các mục tiêu, phần nội dung và tài liệu'}
          </p>
        </div>
      </div>

      {form.error && (
        <div className="rounded-md bg-destructive/15 p-3 text-sm text-destructive font-medium border border-destructive/20">
          {form.error}
        </div>
      )}

      <form onSubmit={form.handleSubmit} className="space-y-8">
        
        {/* Basic Info */}
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center text-lg">
              <BookOpen className="mr-2 h-5 w-5 text-indigo-500" /> Thông tin cơ bản
            </CardTitle>
            <CardDescription>Tiêu đề, môn học và khối lớp</CardDescription>
          </CardHeader>
          <CardContent className="space-y-4">
            <div className="space-y-2">
              <Label htmlFor="title">Tiêu đề bài giảng <span className="text-destructive">*</span></Label>
              <Input 
                id="title" 
                placeholder="Ví dụ: Định luật bảo toàn năng lượng" 
                value={form.title}
                onChange={(e) => form.setTitle(e.target.value)}
                required
              />
            </div>
            
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div className="space-y-2">
                <Label htmlFor="subject">Môn học</Label>
                <Select value={form.subject} onValueChange={form.setSubject}>
                  <SelectTrigger id="subject">
                    <SelectValue placeholder="Chọn môn học" />
                  </SelectTrigger>
                  <SelectContent>
                    {SUBJECT_OPTIONS.map(opt => (
                      <SelectItem key={opt.value} value={opt.value}>{opt.label}</SelectItem>
                    ))}
                  </SelectContent>
                </Select>
              </div>
              <div className="space-y-2">
                <Label htmlFor="gradeLevel">Khối lớp</Label>
                <Select value={form.gradeLevel} onValueChange={form.setGradeLevel}>
                  <SelectTrigger id="gradeLevel">
                    <SelectValue placeholder="Chọn khối lớp" />
                  </SelectTrigger>
                  <SelectContent>
                    {GRADE_OPTIONS.map(opt => (
                      <SelectItem key={opt.value} value={opt.value}>{opt.label}</SelectItem>
                    ))}
                  </SelectContent>
                </Select>
              </div>
            </div>
          </CardContent>
        </Card>

        {/* Content Builder */}
        <Card>
          <CardHeader>
            <CardTitle className="text-lg">Soạn thảo nội dung bài giảng</CardTitle>
            <CardDescription>Xây dựng cấu trúc chi tiết bài giảng</CardDescription>
          </CardHeader>
          <CardContent className="space-y-8">
            
            {/* Objectives */}
            <div className="space-y-4">
              <div className="flex items-center justify-between">
                <Label className="text-base">Mục tiêu bài học</Label>
                <Button type="button" variant="outline" size="sm" onClick={form.addObjective}>
                  <Plus className="mr-2 h-4 w-4" /> Thêm mục tiêu
                </Button>
              </div>
              <div className="space-y-3">
                {form.objectives.map((obj, i) => (
                  <div key={i} className="flex items-center gap-2">
                    <div className="flex h-8 w-8 shrink-0 items-center justify-center rounded-full bg-muted text-muted-foreground text-xs font-medium">
                      {i + 1}
                    </div>
                    <Input 
                      placeholder="Học sinh hiểu được..." 
                      value={obj}
                      onChange={(e) => form.handleObjectiveChange(i, e.target.value)}
                    />
                    <Button 
                      type="button" 
                      variant="ghost" 
                      size="icon" 
                      onClick={() => form.removeObjective(i)}
                      disabled={form.objectives.length === 1}
                      className="text-muted-foreground hover:text-destructive"
                    >
                      <Trash2 className="h-4 w-4" />
                    </Button>
                  </div>
                ))}
              </div>
            </div>

            <Separator />

            {/* Sections */}
            <div className="space-y-4">
              <div className="flex items-center justify-between">
                <Label className="text-base">Các phần bài học (Sections)</Label>
                <Button type="button" variant="outline" size="sm" onClick={form.addSection}>
                  <Plus className="mr-2 h-4 w-4" /> Thêm phần
                </Button>
              </div>
              <div className="space-y-6">
                {form.sections.map((section, i) => (
                  <div key={i} className="relative rounded-lg border bg-card p-4 shadow-sm">
                    <Button 
                      type="button" 
                      variant="ghost" 
                      size="icon" 
                      onClick={() => form.removeSection(i)}
                      disabled={form.sections.length === 1}
                      className="absolute right-2 top-2 text-muted-foreground hover:text-destructive"
                    >
                      <Trash2 className="h-4 w-4" />
                    </Button>
                    
                    <h4 className="font-medium mb-4">Phần {i + 1}</h4>
                    
                    <div className="space-y-4">
                      <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
                        <div className="md:col-span-3 space-y-2">
                          <Label>Tiêu đề phần</Label>
                          <Input 
                            placeholder="Khởi động, Lý thuyết, Luyện tập..." 
                            value={section.title}
                            onChange={(e) => form.handleSectionChange(i, 'title', e.target.value)}
                          />
                        </div>
                        <div className="space-y-2">
                          <Label>Thời lượng (phút)</Label>
                          <Input 
                            type="number" 
                            min="0"
                            value={section.duration_minutes || ''}
                            onChange={(e) => form.handleSectionChange(i, 'duration_minutes', parseInt(e.target.value) || 0)}
                          />
                        </div>
                      </div>
                      
                      <div className="space-y-2">
                        <Label>Nội dung</Label>
                        <Textarea 
                          placeholder="Chi tiết nội dung phần này..." 
                          className="min-h-[120px]"
                          value={section.content}
                          onChange={(e) => form.handleSectionChange(i, 'content', e.target.value)}
                        />
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            </div>

            <Separator />

            {/* Materials & Homework */}
            <div className="grid grid-cols-1 md:grid-cols-2 gap-8">
              
              <div className="space-y-4">
                <div className="flex items-center justify-between">
                  <Label className="text-base">Tài liệu chuẩn bị</Label>
                  <Button type="button" variant="ghost" size="sm" onClick={form.addMaterial}>
                    <Plus className="h-4 w-4" />
                  </Button>
                </div>
                <div className="space-y-3">
                  {form.materials.map((mat, i) => (
                    <div key={i} className="flex items-center gap-2">
                      <Input 
                        placeholder="SGK, Máy chiếu..." 
                        value={mat}
                        onChange={(e) => form.handleMaterialChange(i, e.target.value)}
                      />
                      <Button 
                        type="button" 
                        variant="ghost" 
                        size="icon" 
                        onClick={() => form.removeMaterial(i)}
                        disabled={form.materials.length === 1}
                      >
                        <Trash2 className="h-4 w-4" />
                      </Button>
                    </div>
                  ))}
                </div>
              </div>

              <div className="space-y-4">
                <Label className="text-base">Bài tập về nhà</Label>
                <Textarea 
                  placeholder="Giao bài tập hoặc hướng dẫn tự học..." 
                  className="min-h-[120px]"
                  value={form.homework}
                  onChange={(e) => form.setHomework(e.target.value)}
                />
              </div>

            </div>
          </CardContent>
        </Card>

        {/* Actions */}
        <div className="flex justify-end gap-3">
          <Button type="button" variant="outline" onClick={() => navigate(-1)}>
            Hủy
          </Button>
          <Button type="submit" disabled={form.isLoading} className="bg-indigo-600 hover:bg-indigo-700">
            <Save className="mr-2 h-4 w-4" /> 
            {form.isLoading ? 'Đang lưu...' : (isEditMode ? 'Cập nhật bài giảng' : 'Tạo bài giảng')}
          </Button>
        </div>

      </form>
    </div>
  )
}
