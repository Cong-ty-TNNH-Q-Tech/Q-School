import { ArrowLeft, Sparkles } from 'lucide-react';
import { Link } from 'react-router-dom';
import { Button } from '@/components/ui/button';
import { Label } from '@/components/ui/label';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';
import { TextInputArea, SSEResultDisplay } from '@/views/components/AITools';
import { useAITool } from '@/viewmodels/useAITool';
import type { RewriteTone } from '@/models/ai';

export default function RewritePage() {
  const {
    inputText, setInputText,
    result,
    isStreaming,
    error,
    uploadedFile, setUploadedFile,
    rewriteTone, setRewriteTone,
    execute, copyResult
  } = useAITool('rewrite');

  return (
    <div className="container mx-auto px-4 py-8 max-w-5xl">
      <div className="flex items-center gap-4 mb-8">
        <Button variant="ghost" size="icon" asChild className="rounded-full">
          <Link to="/ai/tools">
            <ArrowLeft className="w-5 h-5" />
          </Link>
        </Button>
        <div>
          <h1 className="text-2xl font-bold text-gray-900 flex items-center gap-2">
            Text Rewriter
          </h1>
          <p className="text-gray-500 text-sm mt-1">Viết lại câu văn mượt mà hơn với nhiều phong cách đa dạng.</p>
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        <div className="lg:col-span-1 space-y-6">
          <div className="bg-white p-5 rounded-xl border border-gray-200 shadow-sm">
            <h3 className="font-medium text-gray-900 mb-4">Tuỳ chọn</h3>
            
            <div className="space-y-3">
              <Label>Văn phong (Tone)</Label>
              <Select 
                value={rewriteTone} 
                onValueChange={(val) => setRewriteTone(val as RewriteTone)}
                disabled={isStreaming}
              >
                <SelectTrigger>
                  <SelectValue placeholder="Chọn văn phong" />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="formal">Trang trọng</SelectItem>
                  <SelectItem value="friendly">Thân thiện</SelectItem>
                  <SelectItem value="concise">Súc tích</SelectItem>
                  <SelectItem value="academic">Học thuật</SelectItem>
                  <SelectItem value="creative">Sáng tạo</SelectItem>
                </SelectContent>
              </Select>
            </div>

            <Button 
              className="w-full mt-6" 
              onClick={execute}
              disabled={isStreaming || (!inputText.trim() && !uploadedFile)}
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
            onChange={setInputText}
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
