import { ArrowLeft, Sparkles, ArrowRightLeft } from 'lucide-react';
import { Link } from 'react-router-dom';
import { Button } from '@/components/ui/button';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';
import { TextInputArea, SSEResultDisplay } from '@/views/components/AITools';
import { useAITool } from '@/viewmodels/useAITool';
import { SUPPORTED_LANGUAGES } from '@/services/mockData';

export default function TranslatePage() {
  const {
    inputText, setInputText,
    result,
    isStreaming,
    error,
    uploadedFile, setUploadedFile,
    sourceLang, setSourceLang,
    targetLang, setTargetLang,
    swapLanguages,
    execute, copyResult
  } = useAITool('translate');

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
            Academic Translator
          </h1>
          <p className="text-gray-500 text-sm mt-1">Dịch thuật tài liệu học thuật với độ chính xác cao.</p>
        </div>
      </div>

      {/* Language Selection Bar */}
      <div className="flex items-center justify-between bg-white p-3 rounded-xl border border-gray-200 shadow-sm mb-6">
        <div className="flex-1">
          <Select value={sourceLang} onValueChange={setSourceLang} disabled={isStreaming}>
            <SelectTrigger className="border-0 focus:ring-0 shadow-none font-medium bg-gray-50/50 hover:bg-gray-50 transition-colors rounded-lg">
              <SelectValue placeholder="Ngôn ngữ nguồn" />
            </SelectTrigger>
            <SelectContent>
              {SUPPORTED_LANGUAGES.map(lang => (
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
          className="rounded-full mx-2 hover:bg-primary/10 hover:text-primary transition-colors flex-shrink-0"
          onClick={swapLanguages}
          disabled={isStreaming}
          title="Hoán đổi ngôn ngữ"
        >
          <ArrowRightLeft className="w-4 h-4" />
        </Button>

        <div className="flex-1">
          <Select value={targetLang} onValueChange={setTargetLang} disabled={isStreaming}>
            <SelectTrigger className="border-0 focus:ring-0 shadow-none font-medium bg-gray-50/50 hover:bg-gray-50 transition-colors rounded-lg">
              <SelectValue placeholder="Ngôn ngữ đích" />
            </SelectTrigger>
            <SelectContent>
              {SUPPORTED_LANGUAGES.map(lang => (
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
          disabled={isStreaming || (!inputText.trim() && !uploadedFile)}
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
            onChange={setInputText}
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
