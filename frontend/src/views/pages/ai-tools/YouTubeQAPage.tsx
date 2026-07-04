import { ArrowLeft, Sparkles, PlayCircle, Clock, CheckCircle2, ChevronRight } from 'lucide-react';
import { Link } from 'react-router-dom';
import { cn } from '@/lib/utils';
import { Button } from '@/components/ui/button';
import { Label } from '@/components/ui/label';
import { Input } from '@/components/ui/input';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';
import { PaymentRequiredBanner, RateLimitWarning } from '@/views/components/AITools';
import { useYouTubeQuestions } from '@/viewmodels/useYouTubeQuestions';
import type { YouTubeQuestionType } from '@/models/ai';

export default function YouTubeQAPage() {
  const {
    youtubeUrl,
    handleUrlChange,
    questionCount, setQuestionCount,
    questionType, setQuestionType,
    questions,
    videoInfo,
    isLoading,
    error,
    isPaymentRequired,
    rateLimitSeconds,
    generate,
    validateUrl,
  } = useYouTubeQuestions();

  // [FIX #1] Bỏ React.ChangeEvent (React chưa được import trong file này) → dùng inline handler
  // [FIX #2] Tách rõ 2 biến logic để tránh duplicate call và inconsistency
  const hasUrl = youtubeUrl.trim().length > 0;
  const isUrlValid = !hasUrl || validateUrl(youtubeUrl); // empty = valid (chưa nhập thì không show lỗi)

  return (
    <div className="container mx-auto px-4 py-8 max-w-5xl">
      <div className="flex items-center gap-4 mb-6">
        <Button variant="ghost" size="icon" asChild className="rounded-full shrink-0">
          <Link to="/ai/tools">
            <ArrowLeft className="w-5 h-5" />
          </Link>
        </Button>
        <div>
          <div className="flex items-center text-sm font-medium text-gray-500 mb-1">
            <Link to="/ai/tools" className="hover:text-primary transition-colors">AI Tools</Link>
            <ChevronRight className="w-4 h-4 mx-1" />
            <span className="text-gray-900">YouTube Q&A</span>
          </div>
          <h1 className="text-2xl font-bold text-gray-900 flex items-center gap-2">
            YouTube Q&A Generator
          </h1>
          <p className="text-gray-500 text-sm mt-1">Tự động trích xuất nội dung và sinh câu hỏi từ video YouTube.</p>
        </div>
      </div>

      {isPaymentRequired && <PaymentRequiredBanner />}
      <RateLimitWarning secondsLeft={rateLimitSeconds} />

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        <div className="lg:col-span-1 space-y-6">
          <div className="bg-white p-5 rounded-xl border border-gray-200 shadow-sm">
            <h3 className="font-medium text-gray-900 mb-4">Cấu hình</h3>
            
            <div className="space-y-4">
              <div className="space-y-2">
                <Label>Link Video YouTube</Label>
                <div className="relative">
                  <PlayCircle className="absolute left-3 top-2.5 h-4 w-4 text-gray-400" />
                  <Input
                    placeholder="https://youtube.com/watch?v=..."
                    value={youtubeUrl}
                    onChange={(e) => handleUrlChange(e.target.value)}
                    disabled={isLoading}
                    className="pl-9"
                    aria-label="Đường dẫn YouTube"
                  />
                </div>
                {!isUrlValid && <p className="text-xs text-red-500">Đường dẫn không hợp lệ</p>}
              </div>

              <div className="space-y-2">
                <Label>Số lượng câu hỏi (5–20)</Label>
                <Input
                  type="number"
                  min={5}
                  max={20}
                  value={questionCount}
                  onChange={(e) => {
                    // [FIX #3] Clamp giá trị trong state để đồng bộ với validation của hook
                    const val = Number(e.target.value);
                    if (!isNaN(val)) setQuestionCount(Math.min(20, Math.max(5, val)));
                  }}
                  disabled={isLoading}
                />
              </div>

              <div className="space-y-2">
                <Label>Loại câu hỏi</Label>
                <Select 
                  value={questionType} 
                  onValueChange={(val) => setQuestionType(val as YouTubeQuestionType)}
                  disabled={isLoading}
                >
                  <SelectTrigger>
                    <SelectValue placeholder="Chọn loại" />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value="mcq">Trắc nghiệm</SelectItem>
                    <SelectItem value="open">Tự luận</SelectItem>
                    <SelectItem value="mix">Hỗn hợp</SelectItem>
                  </SelectContent>
                </Select>
              </div>
            </div>

            <Button
              className="w-full mt-6"
              onClick={generate}
              disabled={isLoading || !hasUrl || !isUrlValid || isPaymentRequired || rateLimitSeconds > 0}
            >
              <Sparkles className="w-4 h-4 mr-2" />
              {isLoading ? 'Đang xử lý...' : 'Tạo câu hỏi'}
            </Button>
            
            {error && <p className="text-sm text-red-500 mt-3 font-medium">{error}</p>}
          </div>

          {videoInfo && (
            <div className="bg-white rounded-xl border border-gray-200 shadow-sm overflow-hidden animate-in fade-in slide-in-from-bottom-2">
              <img 
                src={videoInfo.thumbnail_url} 
                alt="Video thumbnail" 
                className="w-full h-auto aspect-video object-cover bg-gray-100"
              />
              <div className="p-4">
                <h4 className="font-medium text-gray-900 line-clamp-2 text-sm leading-snug" title={videoInfo.title}>
                  {videoInfo.title}
                </h4>
                <div className="flex items-center text-xs text-gray-500 mt-2">
                  <Clock className="w-3.5 h-3.5 mr-1.5" />
                  {videoInfo.duration}
                </div>
              </div>
            </div>
          )}
        </div>

        <div className="lg:col-span-2">
          <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-6 min-h-[400px] h-full flex flex-col">
            <div className="flex items-center justify-between mb-6 pb-4 border-b border-gray-100">
              <h3 className="font-medium text-gray-900">
                Danh sách câu hỏi {questions.length > 0 && <span className="text-primary">({questions.length})</span>}
              </h3>
            </div>

            {isLoading && !questions.length ? (
              <div className="flex flex-col items-center justify-center flex-1 text-gray-400 space-y-4">
                <div className="w-8 h-8 rounded-full border-2 border-primary border-t-transparent animate-spin"></div>
                <p className="text-sm">Đang trích xuất nội dung và phân tích video...</p>
              </div>
            ) : questions.length === 0 ? (
              <div className="flex items-center justify-center flex-1 text-gray-400 text-sm italic">
                Kết quả sẽ hiển thị tại đây...
              </div>
            ) : (
              <div className="space-y-4 overflow-y-auto pr-2 pb-4">
                {questions.map((q, index) => (
                  <div key={q.id} className="p-5 rounded-xl border border-gray-100 bg-gray-50/50 hover:bg-gray-50 hover:border-primary/20 transition-all">
                    <div className="flex items-start justify-between gap-4 mb-4">
                      <h4 className="text-[15px] font-medium text-gray-900 leading-relaxed">
                        <span className="text-primary mr-2 font-semibold">Câu {index + 1}:</span>
                        {q.question_text}
                      </h4>
                      <span className="shrink-0 inline-flex items-center rounded-full bg-blue-50 px-2.5 py-1 text-[11px] font-medium text-blue-700 ring-1 ring-inset ring-blue-700/10">
                        {q.timestamp}
                      </span>
                    </div>

                    {q.type === 'mcq' && q.options && (
                      <div className="space-y-2.5 mt-4 ml-1">
                        {q.options.map((opt, i) => {
                          const isCorrect = opt === q.correct_answer;
                          return (
                            <div 
                              key={i} 
                              className={cn(
                                "flex items-start gap-3 text-[14px] p-2.5 rounded-lg border",
                                isCorrect ? "bg-green-50/50 border-green-200/60 text-green-800" : "bg-white border-gray-200 text-gray-600"
                              )}
                            >
                              <span className={cn(
                                "flex items-center justify-center w-5 h-5 rounded-full border text-[11px] font-medium shrink-0 mt-0.5",
                                isCorrect ? "border-green-500 bg-green-500 text-white" : "border-gray-300 bg-gray-50 text-gray-500"
                              )}>
                                {String.fromCharCode(65 + i)}
                              </span>
                              <span className={cn("leading-relaxed", isCorrect && "font-medium")}>
                                {opt}
                              </span>
                              {isCorrect && <CheckCircle2 className="w-4 h-4 ml-auto text-green-500 shrink-0 mt-0.5" />}
                            </div>
                          );
                        })}
                      </div>
                    )}

                    {q.type === 'open' && q.correct_answer && (
                      <div className="mt-4 ml-1 p-3.5 bg-white rounded-lg border border-gray-200 text-[14px] text-gray-600 leading-relaxed shadow-sm">
                        <div className="font-medium text-gray-900 mb-1 flex items-center gap-1.5">
                          <CheckCircle2 className="w-4 h-4 text-green-500" />
                          Gợi ý đáp án:
                        </div>
                        {q.correct_answer}
                      </div>
                    )}
                  </div>
                ))}
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  );
}
