import { ArrowLeft, Sparkles, ArrowRightLeft, ChevronRight } from 'lucide-react';
import { Link } from 'react-router-dom';
import { Button } from '@/components/ui/button';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';
import { TextInputArea, SSEResultDisplay, PaymentRequiredBanner, RateLimitWarning } from '@/views/components/AITools';
import { useAITool } from '@/viewmodels/useAITool';
import { SUPPORTED_LANGUAGES } from '@/services/mockData';

export default function TranslatePage() {
  const {
    inputText,
    result,
    isStreaming,
    error,
    uploadedFile, setUploadedFile,
    sourceLang, setSourceLang,
    targetLang, setTargetLang,
    swapLanguages,
    isPaymentRequired, rateLimitSeconds,
    execute, copyResult, handleInputChange
  } = useAITool('translate');

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
            <span className="text-gray-900">Dịch thuật</span>
          </div>
          <h1 className="text-2xl font-bold text-gray-900 flex items-center gap-2">
            Academic Translator
          </h1>
          <p className="text-gray-500 text-sm mt-1">Dịch thuật tài liệu học thuật với độ chính xác cao.</p>
        </div>
      </div>

      {isPaymentRequired && <PaymentRequiredBanner />}
      <RateLimitWarning secondsLeft={rateLimitSeconds} />

      {/* Language Selection Bar */}
      <div className="flex items-center justify-between bg-white p-3 rounded-xl border border-gray-200 shadow-sm mb-6">
        <div className="flex-1">
          <Select value={sourceLang} onValueChange={setSourceLang} disabled={isStreaming}>
            <SelectTrigger className="border-0 focus:ring-0 shadow-none font-medium bg-gray-50/50 hover:bg-gray-50 transition-colors rounded-lg">
              <SelectValue placeholder="Ngôn ngữ nguồn" />
            </SelectTrigger>
            <SelectContent>
              {SUPPORTED_LANGUAGES.filter(lang => lang.code !== targetLang).map(lang => (
                <SelectItem key={`src-${lang.code}`} value={lang.code}>
                  {lang.native_name} ({lang.name})
                </SelectItem>
              ))}
            </SelectContent>
          </Select>
        </div>
        
        <Button 
          variant="ghost" 
          size="icon" 
          className="rounded-full mx-2 hover:bg-primary/10 hover:text-primary transition-all active:rotate-180 flex-shrink-0 group"
          onClick={swapLanguages}
          disabled={isStreaming}
          title="Hoán đổi ngôn ngữ"
        >
          <ArrowRightLeft className="w-4 h-4 transition-transform group-hover:scale-110" />
        </Button>

        <div className="flex-1">
          <Select value={targetLang} onValueChange={setTargetLang} disabled={isStreaming}>
            <SelectTrigger className="border-0 focus:ring-0 shadow-none font-medium bg-gray-50/50 hover:bg-gray-50 transition-colors rounded-lg">
              <SelectValue placeholder="Ngôn ngữ đích" />
            </SelectTrigger>
            <SelectContent>
              {SUPPORTED_LANGUAGES.filter(lang => lang.code !== sourceLang).map(lang => (
                <SelectItem key={`tgt-${lang.code}`} value={lang.code}>
                  {lang.native_name} ({lang.name})
                </SelectItem>
              ))}
            </SelectContent>
          </Select>
        </div>
        
        <Button 
          className="ml-4 flex-shrink-0" 
          onClick={execute}
          disabled={isStreaming || (!inputText.trim() && !uploadedFile) || isPaymentRequired || rateLimitSeconds > 0}
        >
          <Sparkles className="w-4 h-4 mr-2" />
          {isStreaming ? 'Đang dịch...' : 'Dịch'}
        </Button>
      </div>

      {error && <p className="text-sm text-red-500 mb-4 font-medium px-2">{error}</p>}

      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-2">
          <TextInputArea
            value={inputText}
            onChange={handleInputChange}
            placeholder="Nhập văn bản cần dịch..."
            onFileUpload={setUploadedFile}
            uploadedFile={uploadedFile}
            disabled={isStreaming}
          />
        </div>
        
        <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-2 h-[300px] md:h-auto">
          <SSEResultDisplay 
            result={result} 
            isStreaming={isStreaming} 
            onCopy={copyResult}
          />
        </div>
      </div>
    </div>
  );
}
