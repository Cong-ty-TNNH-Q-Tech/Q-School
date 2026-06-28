import { useEffect, useState } from 'react'
import { Link } from 'react-router-dom'
import { ChevronRight, Loader2, CheckCircle2, XCircle } from 'lucide-react'
import { Button } from '@/components/ui/button'
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from '@/components/ui/card'
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select'
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs'
import { Textarea } from '@/components/ui/textarea'
import { useEssaySubmission } from '@/viewmodels/useEssaySubmission'
import ImageDropzone from './ImageDropzone'

export default function EssaySubmissionPage() {
  const {
    rubrics,
    loadingRubrics,
    fetchRubrics,
    uploadedImageUrl,
    uploading,
    uploadProgress,
    uploadImage,
    removeImage,
    submission,
    submitting,
    submitEssay,
    error,
    resetForm
  } = useEssaySubmission()

  const [selectedRubricId, setSelectedRubricId] = useState<string>('')
  const [textContent, setTextContent] = useState('')
  const [activeTab, setActiveTab] = useState('text')
  const [formError, setFormError] = useState<string | null>(null)

  useEffect(() => {
    fetchRubrics()
  }, [fetchRubrics])

  const handleSubmit = async () => {
    setFormError(null)
    
    if (!selectedRubricId) {
      setFormError('Vui lòng chọn Tiêu chí đánh giá')
      return
    }

    if (activeTab === 'text' && !textContent.trim()) {
      setFormError('Vui lòng nhập nội dung bài viết')
      return
    }

    if (activeTab === 'image' && !uploadedImageUrl) {
      setFormError('Vui lòng tải lên ảnh bài thi')
      return
    }

    await submitEssay({
      rubric_id: selectedRubricId,
      content: activeTab === 'text' ? textContent : undefined,
      image_url: activeTab === 'image' ? (uploadedImageUrl || undefined) : undefined
    })
  }

  // Render Status Panel if submitted
  if (submission) {
    return (
      <div className="flex-1 space-y-4 p-4 md:p-8 pt-6 max-w-4xl mx-auto w-full">
        <div className="flex items-center space-x-2 text-sm text-muted-foreground mb-4">
          <Link to="/quizzes" className="hover:text-foreground">Bài tập</Link>
          <ChevronRight className="h-4 w-4" />
          <span className="text-foreground font-medium">Kết quả nộp bài</span>
        </div>

        <Card className="border-none shadow-md">
          <CardHeader className="bg-muted/30 pb-4 border-b">
            <CardTitle className="text-2xl font-bold">Trạng thái chấm bài</CardTitle>
            <CardDescription>Mã nộp bài: {submission.id}</CardDescription>
          </CardHeader>
          <CardContent className="pt-8">
            <div className="flex flex-col items-center justify-center space-y-6 py-8">
              {submission.status === 'pending' && (
                <>
                  <Loader2 className="h-16 w-16 text-primary animate-spin" />
                  <div className="text-center">
                    <h3 className="text-xl font-semibold mb-2">Đang xếp hàng chờ AI chấm...</h3>
                    <p className="text-muted-foreground">Hệ thống đã ghi nhận bài làm của bạn.</p>
                  </div>
                </>
              )}

              {submission.status === 'processing' && (
                <>
                  <div className="relative">
                    <div className="absolute inset-0 bg-primary/20 rounded-full animate-ping"></div>
                    <Loader2 className="h-16 w-16 text-primary animate-spin relative z-10" />
                  </div>
                  <div className="text-center">
                    <h3 className="text-xl font-semibold mb-2">AI đang phân tích bài viết...</h3>
                    <p className="text-muted-foreground">Quá trình này có thể mất vài phút. Vui lòng không đóng trang này.</p>
                  </div>
                </>
              )}

              {submission.status === 'graded' && (
                <div className="w-full animate-in fade-in slide-in-from-bottom-4 duration-500">
                  <div className="flex flex-col items-center justify-center mb-8">
                    <CheckCircle2 className="h-16 w-16 text-green-500 mb-4" />
                    <h3 className="text-2xl font-bold text-green-600">Đã chấm xong!</h3>
                    <div className="mt-4 text-4xl font-extrabold text-primary bg-primary/10 px-8 py-4 rounded-2xl">
                      {submission.score} / 10
                    </div>
                  </div>

                  {submission.ai_feedback && (
                    <div className="space-y-6 text-left w-full">
                      <div className="bg-muted/30 rounded-lg p-6 border">
                        <h4 className="font-semibold text-lg mb-2">Nhận xét tổng quan</h4>
                        <p className="text-foreground/80">{(submission.ai_feedback as any).summary}</p>
                      </div>

                      <div className="grid md:grid-cols-2 gap-4">
                        <div className="bg-green-500/5 border border-green-500/20 rounded-lg p-5">
                          <h4 className="font-semibold text-green-700 mb-3 flex items-center">
                            Điểm mạnh
                          </h4>
                          <ul className="list-disc pl-5 space-y-1 text-green-800/80">
                            {(submission.ai_feedback as any).strengths?.map((s: string, i: number) => (
                              <li key={i}>{s}</li>
                            ))}
                          </ul>
                        </div>
                        <div className="bg-orange-500/5 border border-orange-500/20 rounded-lg p-5">
                          <h4 className="font-semibold text-orange-700 mb-3 flex items-center">
                            Cần cải thiện
                          </h4>
                          <ul className="list-disc pl-5 space-y-1 text-orange-800/80">
                            {(submission.ai_feedback as any).weaknesses?.map((w: string, i: number) => (
                              <li key={i}>{w}</li>
                            ))}
                          </ul>
                        </div>
                      </div>
                    </div>
                  )}

                  <div className="mt-8 text-center">
                    <Button onClick={resetForm} variant="outline">Nộp bài khác</Button>
                  </div>
                </div>
              )}

              {submission.status === 'failed' && (
                <div className="text-center animate-in fade-in">
                  <XCircle className="h-16 w-16 text-destructive mx-auto mb-4" />
                  <h3 className="text-xl font-semibold text-destructive mb-2">Chấm điểm thất bại</h3>
                  <p className="text-muted-foreground mb-6">Đã xảy ra lỗi trong quá trình AI phân tích. Vui lòng thử lại.</p>
                  <Button onClick={resetForm}>Thử lại</Button>
                </div>
              )}
            </div>
          </CardContent>
        </Card>
      </div>
    )
  }

  return (
    <div className="flex-1 space-y-4 p-4 md:p-8 pt-6 max-w-4xl mx-auto w-full">
      <div className="flex items-center space-x-2 text-sm text-muted-foreground mb-4">
        <span className="hover:text-foreground cursor-pointer">Bài tự luận</span>
        <ChevronRight className="h-4 w-4" />
        <span className="text-foreground font-medium">Nộp bài</span>
      </div>

      <div className="flex items-center justify-between mb-6">
        <h2 className="text-3xl font-bold tracking-tight">Nộp bài tự luận</h2>
      </div>

      <Card className="border-none shadow-md">
        <CardContent className="pt-6 space-y-8">
          
          <div className="space-y-3">
            <label className="text-sm font-semibold">
              Tiêu chí đánh giá (Rubric) <span className="text-destructive">*</span>
            </label>
            <Select 
              value={selectedRubricId} 
              onValueChange={setSelectedRubricId}
              disabled={loadingRubrics || submitting}
            >
              <SelectTrigger className="w-full md:w-[400px]">
                <SelectValue placeholder={loadingRubrics ? "Đang tải..." : "Chọn tiêu chí đánh giá..."} />
              </SelectTrigger>
              <SelectContent>
                {rubrics.map(rubric => (
                  <SelectItem key={rubric.id} value={rubric.id}>
                    {rubric.title}
                  </SelectItem>
                ))}
              </SelectContent>
            </Select>
            <p className="text-xs text-muted-foreground">Giáo viên sẽ sử dụng tiêu chí này để AI chấm điểm bài làm của bạn.</p>
          </div>

          <Tabs value={activeTab} onValueChange={setActiveTab} className="w-full">
            <TabsList className="grid w-full grid-cols-2 mb-6">
              <TabsTrigger value="text" disabled={submitting || uploading}>Nhập văn bản</TabsTrigger>
              <TabsTrigger value="image" disabled={submitting}>Tải ảnh bài thi</TabsTrigger>
            </TabsList>
            
            <TabsContent value="text" className="space-y-4">
              <div className="space-y-2">
                <Textarea 
                  placeholder="Nhập nội dung bài làm của bạn vào đây..." 
                  className="min-h-[300px] resize-y text-base p-4 leading-relaxed"
                  value={textContent}
                  onChange={(e) => setTextContent(e.target.value)}
                  disabled={submitting}
                />
                <div className="text-right text-xs text-muted-foreground">
                  {textContent.length} ký tự
                </div>
              </div>
            </TabsContent>
            
            <TabsContent value="image" className="space-y-4">
              <div className="bg-muted/10 p-6 rounded-lg border">
                <div className="mb-4">
                  <h3 className="text-sm font-semibold mb-1">Chụp ảnh bài làm trên giấy</h3>
                  <p className="text-xs text-muted-foreground">Hệ thống AI sẽ tự động đọc chữ viết tay (OCR) để chấm điểm.</p>
                </div>
                <ImageDropzone 
                  onFileSelect={uploadImage}
                  uploading={uploading}
                  uploadProgress={uploadProgress}
                  imageUrl={uploadedImageUrl}
                  onRemove={removeImage}
                />
              </div>
            </TabsContent>
          </Tabs>

          {(error || formError) && (
            <div className="p-3 bg-destructive/10 border border-destructive/20 rounded-md text-destructive text-sm font-medium">
              {error || formError}
            </div>
          )}

          <div className="pt-4 flex justify-end">
            <Button 
              size="lg" 
              onClick={handleSubmit} 
              disabled={submitting || uploading}
              className="w-full sm:w-auto min-w-[200px]"
            >
              {submitting ? (
                <>
                  <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                  Đang xử lý...
                </>
              ) : (
                'Nộp bài'
              )}
            </Button>
          </div>
        </CardContent>
      </Card>
    </div>
  )
}
