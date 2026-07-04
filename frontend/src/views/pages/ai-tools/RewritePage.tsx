import { ArrowLeft, Sparkles, ChevronRight, Crown, Heart, Zap, GraduationCap } from 'lucide-react';
import { Link } from 'react-router-dom';
import { cn } from '@/lib/utils';
import { Button } from '@/components/ui/button';
import { Label } from '@/components/ui/label';
import { TextInputArea, SSEResultDisplay, PaymentRequiredBanner, RateLimitWarning } from '@/views/components/AITools';
import { useAITool } from '@/viewmodels/useAITool';
import type { RewriteTone } from '@/models/ai';

const TONE_OPTIONS = [
  { value: 'formal', label: 'Trang trọng', icon: Crown },
  { value: 'friendly', label: 'Thân thiện', icon: Heart },
  { value: 'concise', label: 'Súc tích', icon: Zap },
  { value: 'academic', label: 'Học thuật', icon: GraduationCap },
  { value: 'creative', label: 'Sáng tạo', icon: Sparkles },
] as const;

export default function RewritePage() {
  const {
    inputText,
    result,
    isStreaming,
    error,
    uploadedFile, setUploadedFile,
    rewriteTone, setRewriteTone,
    isPaymentRequired, rateLimitSeconds,
    execute, copyResult, handleInputChange
  } = useAITool('rewrite');

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
            <span className="text-gray-900">Viết lại văn bản</span>
          </div>
          <h1 className="text-2xl font-bold text-gray-900 flex items-center gap-2">
            Text Rewriter
          </h1>
          <p className="text-gray-500 text-sm mt-1">Viết lại câu văn mượt mà hơn với nhiều phong cách đa dạng.</p>
        </div>
      </div>

      {isPaymentRequired && <PaymentRequiredBanner />}
      <RateLimitWarning secondsLeft={rateLimitSeconds} />

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        <div className="lg:col-span-1 space-y-6">
          <div className="bg-white p-5 rounded-xl border border-gray-200 shadow-sm">
            <h3 className="font-medium text-gray-900 mb-4">Tuỳ chọn</h3>
            
            <div className="space-y-3">
              <Label>Văn phong (Tone)</Label>
              <div className="flex flex-wrap gap-2">
                {TONE_OPTIONS.map((tone) => {
                  const Icon = tone.icon;
                  const isActive = rewriteTone === tone.value;
                  return (
                    <button
                      key={tone.value}
                      type="button"
                      onClick={() => setRewriteTone(tone.value as RewriteTone)}
                      disabled={isStreaming}
                      aria-pressed={isActive}
                      aria-label={`Văn phong ${tone.label}`}
                      className={cn(
                        "flex items-center gap-1.5 px-3 py-1.5 rounded-full text-sm font-medium transition-all duration-200 border",
                        isActive 
                          ? "bg-primary text-primary-foreground border-primary shadow-sm" 
                          : "bg-gray-50 text-gray-600 border-gray-200 hover:border-primary/50 hover:bg-primary/5",
                        isStreaming && "opacity-50 cursor-not-allowed"
                      )}
                    >
                      <Icon className={cn("w-4 h-4", isActive ? "text-primary-foreground" : "text-gray-500")} />
                      {tone.label}
                    </button>
                  );
                })}
              </div>
            </div>

            <Button 
              className="w-full mt-6" 
              onClick={execute}
              disabled={isStreaming || (!inputText.trim() && !uploadedFile) || isPaymentRequired || rateLimitSeconds > 0}
            >
              <Sparkles className="w-4 h-4 mr-2" />
              {isStreaming ? 'Đang xử lý...' : 'Viết lại ngay'}
            </Button>
            
            {error && <p className="text-sm text-red-500 mt-3 font-medium">{error}</p>}
          </div>
        </div>

        <div className="lg:col-span-2 flex flex-col gap-6">
          <TextInputArea
            value={inputText}
            onChange={handleInputChange}
            placeholder="Dán nội dung cần viết lại..."
            onFileUpload={setUploadedFile}
            uploadedFile={uploadedFile}
            disabled={isStreaming}
          />

          <div className="flex-1 min-h-[280px] bg-white rounded-xl shadow-sm border border-gray-200 p-2">
            <SSEResultDisplay
              result={result}
              isStreaming={isStreaming}
              onCopy={copyResult}
            />
          </div>
        </div>
      </div>
    </div>
  );
}
