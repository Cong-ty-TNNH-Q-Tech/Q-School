import { useState } from 'react'
import { 
  Camera, 
  UploadCloud, 
  FileText, 
  CheckCircle, 
  AlertCircle,
  ScanLine,
  RefreshCcw,
  Save
} from 'lucide-react'

interface ErrorDetail {
  error: string;
  correction: string;
  type: string;
}

interface Feedback {
  positive: string;
  errors: ErrorDetail[];
  advice: string;
}

interface GradingResult {
  score: number;
  ocrText: string;
  feedback: Feedback;
}

export default function CameraGrading() {
  const [imagePreview, setImagePreview] = useState<string | null>(null)
  const [isProcessing, setIsProcessing] = useState(false)
  const [result, setResult] = useState<GradingResult | null>(null)
  const [activeTab, setActiveTab] = useState<'ocr' | 'grading'>('grading')

  const handleFileUpload = (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0]
    if (file) {
      const url = URL.createObjectURL(file)
      setImagePreview(url)
      
      // Simulate API call to VNPT SmartReader
      setIsProcessing(true)
      setResult(null)
      
      setTimeout(() => {
        setIsProcessing(false)
        setResult({
          score: 8.5,
          ocrText: "Em thấy người nông dân rất vất vả. Họ phải thức khuya dậy sớm để ra đồng. Tuy cực nhọc nhưng trên môi họ luôn nở nụ cười tươi tắn vì một vụ mùa bọi thu...",
          feedback: {
            positive: "Bài viết có cảm xúc chân thật, dùng từ tượng hình khá tốt ('thức khuya dậy sớm', 'nụ cười tươi tắn').",
            errors: [
              { error: "bọi thu", correction: "bội thu", type: "Chính tả" }
            ],
            advice: "Em cần cẩn thận hơn về lỗi chính tả (dấu hỏi/ngã, lỗi âm vực). Tiếp tục phát huy cách viết giàu cảm xúc này nhé!"
          }
        })
      }, 3000)
    }
  }

  const resetUpload = () => {
    setImagePreview(null)
    setResult(null)
    setIsProcessing(false)
  }

  return (
    <div className="flex flex-col lg:flex-row h-full min-h-[calc(100vh-4rem)] bg-slate-50 border rounded-2xl overflow-hidden shadow-sm animate-in fade-in duration-500">
      
      {/* LEFT PANE: Upload & Image View */}
      <div className="w-full lg:w-[45%] flex flex-col bg-white border-r border-slate-200 z-10 shadow-[2px_0_10px_rgba(0,0,0,0.02)] relative">
        <div className="p-6 border-b border-slate-100 flex justify-between items-center bg-white/80 backdrop-blur-md sticky top-0 z-20">
          <div>
            <h2 className="text-2xl font-bold tracking-tight text-slate-800">Chấm Điểm O2O</h2>
            <p className="text-sm text-slate-500 mt-1">Dùng VNPT SmartReader bóc tách ảnh chụp bài thi.</p>
          </div>
          {imagePreview && (
            <button 
              onClick={resetUpload}
              className="flex items-center gap-2 px-3 py-1.5 text-sm font-medium text-slate-600 bg-slate-100 hover:bg-slate-200 rounded-lg transition-colors"
            >
              <RefreshCcw className="w-4 h-4" /> Bỏ ảnh
            </button>
          )}
        </div>

        <div className="flex-1 p-6 flex flex-col relative overflow-hidden bg-slate-50/50">
          {!imagePreview ? (
            <div className="flex-1 border-2 border-dashed border-indigo-200 bg-indigo-50/30 hover:bg-indigo-50/50 hover:border-indigo-400 transition-all rounded-2xl flex flex-col items-center justify-center text-center p-8 relative">
              <input 
                type="file" 
                accept="image/*" 
                className="absolute inset-0 w-full h-full opacity-0 cursor-pointer"
                onChange={handleFileUpload}
              />
              <div className="w-20 h-20 bg-white shadow-sm rounded-full flex items-center justify-center mb-6">
                <UploadCloud className="w-10 h-10 text-indigo-500" />
              </div>
              <h3 className="text-xl font-semibold text-slate-800 mb-2">Tải ảnh bài thi lên đây</h3>
              <p className="text-slate-500 text-sm max-w-sm mb-6">
                Hỗ trợ định dạng JPG, PNG. Chụp thẳng từ trên xuống để VNPT SmartReader đọc chữ viết tay chính xác nhất.
              </p>
              <div className="flex items-center gap-4">
                <span className="text-sm font-medium text-slate-400">hoặc</span>
                <button className="flex items-center gap-2 bg-indigo-600 hover:bg-indigo-700 text-white px-5 py-2.5 rounded-full text-sm font-medium transition-all shadow-md">
                  <Camera className="w-4 h-4" />
                  Mở Camera (Mobile)
                </button>
              </div>
            </div>
          ) : (
            <div className="relative flex-1 rounded-2xl overflow-hidden bg-slate-900 shadow-inner group">
              <img 
                src={imagePreview} 
                alt="Scanned Exam" 
                className={`w-full h-full object-contain transition-all duration-700 ${isProcessing ? 'opacity-50 grayscale blur-sm' : 'opacity-100'}`}
              />
              {isProcessing && (
                <div className="absolute inset-0 flex flex-col items-center justify-center z-10">
                  <div className="w-full max-w-xs h-1 bg-indigo-500/20 rounded-full overflow-hidden mb-4 relative">
                    <div className="absolute top-0 left-0 h-full w-1/2 bg-indigo-400 animate-[ping-pong_1.5s_ease-in-out_infinite]"></div>
                  </div>
                  <ScanLine className="w-12 h-12 text-white animate-pulse mb-3" />
                  <p className="text-white font-medium">Đang gọi API VNPT SmartReader...</p>
                  <p className="text-slate-300 text-xs mt-1">Đang bóc tách chữ viết tay (OCR)</p>
                </div>
              )}
            </div>
          )}
        </div>
        
        {/* Rubric selector if uploaded */}
        <div className={`p-6 border-t border-slate-200 transition-all duration-500 ${imagePreview ? 'opacity-100 translate-y-0' : 'opacity-0 translate-y-4 hidden'}`}>
          <label className="text-sm font-semibold text-slate-700 block mb-2">Tiêu chí chấm (Rubric)</label>
          <select className="w-full p-3 text-sm border border-slate-200 rounded-xl focus:ring-2 focus:ring-indigo-500/20 bg-white">
            <option>Tự luận Ngữ Văn Lớp 6 (Cơ bản)</option>
            <option>Tự luận Ngữ Văn Lớp 6 (Nâng cao)</option>
            <option>Viết đoạn văn Tiếng Anh (CEFR A2)</option>
          </select>
        </div>
      </div>

      {/* RIGHT PANE: Analysis Results */}
      <div className="flex-1 bg-slate-100 relative flex flex-col h-full">
        {/* Tabs */}
        <div className="flex items-center gap-1 p-4 border-b border-slate-200 bg-white/50 backdrop-blur-sm z-10">
          <button 
            onClick={() => setActiveTab('ocr')}
            className={`px-5 py-2.5 rounded-lg text-sm font-medium flex items-center gap-2 transition-all ${activeTab === 'ocr' ? 'bg-white shadow-sm text-indigo-700' : 'text-slate-500 hover:text-slate-700 hover:bg-slate-200/50'}`}
          >
            <FileText className="w-4 h-4" /> Bản gốc (OCR)
          </button>
          <button 
            onClick={() => setActiveTab('grading')}
            className={`px-5 py-2.5 rounded-lg text-sm font-medium flex items-center gap-2 transition-all ${activeTab === 'grading' ? 'bg-white shadow-sm text-indigo-700' : 'text-slate-500 hover:text-slate-700 hover:bg-slate-200/50'}`}
          >
            <CheckCircle className="w-4 h-4" /> AI Đánh giá & Điểm
          </button>
        </div>

        {/* Content Area */}
        <div className="flex-1 overflow-y-auto p-6 custom-scrollbar">
          {!result && !isProcessing && (
            <div className="h-full flex flex-col items-center justify-center text-slate-400">
              <img src="https://illustrations.popsy.co/amber/student-going-to-school.svg" alt="Empty state" className="w-64 h-64 opacity-50 mb-4" />
              <p>Chưa có dữ liệu. Hãy tải ảnh bài thi lên để bắt đầu chấm.</p>
            </div>
          )}

          {isProcessing && (
            <div className="space-y-6 animate-pulse">
              <div className="h-32 bg-slate-200 rounded-2xl w-full"></div>
              <div className="grid grid-cols-2 gap-4">
                <div className="h-24 bg-slate-200 rounded-xl"></div>
                <div className="h-24 bg-slate-200 rounded-xl"></div>
              </div>
              <div className="h-64 bg-slate-200 rounded-2xl w-full"></div>
            </div>
          )}

          {result && !isProcessing && activeTab === 'ocr' && (
            <div className="bg-white p-6 rounded-2xl shadow-sm border border-slate-200 animate-in fade-in slide-in-from-bottom-4">
              <h3 className="text-lg font-bold mb-4 flex items-center gap-2">
                <FileText className="w-5 h-5 text-blue-500" /> Kết quả bóc tách từ ảnh
              </h3>
              <div className="p-4 bg-slate-50 border border-slate-100 rounded-xl font-mono text-sm leading-relaxed text-slate-700 whitespace-pre-wrap">
                {result.ocrText}
              </div>
              <p className="text-xs text-slate-400 mt-4 text-right">Powered by VNPT SmartReader</p>
            </div>
          )}

          {result && !isProcessing && activeTab === 'grading' && (
            <div className="space-y-6 animate-in fade-in slide-in-from-bottom-4">
              
              {/* Score Card */}
              <div className="bg-gradient-to-br from-indigo-600 to-purple-600 rounded-2xl p-8 text-white shadow-lg relative overflow-hidden">
                <div className="absolute top-0 right-0 w-48 h-48 bg-white opacity-10 rounded-full blur-3xl transform translate-x-1/2 -translate-y-1/2"></div>
                <div className="relative z-10 flex items-center justify-between">
                  <div>
                    <h3 className="text-indigo-100 font-medium mb-1">Điểm đánh giá bởi VNPT Smartbot</h3>
                    <p className="text-sm text-indigo-200">Độ tin cậy: 98.5%</p>
                  </div>
                  <div className="text-6xl font-bold tracking-tighter">
                    {result.score}<span className="text-3xl text-indigo-300">/10</span>
                  </div>
                </div>
              </div>

              {/* Error Highlights */}
              <div className="bg-white p-6 rounded-2xl shadow-sm border border-slate-200">
                <h3 className="text-lg font-bold mb-4 flex items-center gap-2 text-slate-800">
                  <AlertCircle className="w-5 h-5 text-rose-500" /> Lỗi phát hiện
                </h3>
                <div className="space-y-3">
                  {result.feedback.errors.map((err: ErrorDetail, idx: number) => (
                    <div key={idx} className="flex items-start gap-4 p-3 bg-rose-50 border border-rose-100 rounded-xl">
                      <div className="px-2 py-1 bg-rose-200 text-rose-700 text-xs font-bold rounded">
                        {err.type}
                      </div>
                      <div>
                        <p className="text-sm text-slate-700">
                          Ghi sai: <span className="text-rose-600 font-medium line-through">"{err.error}"</span>
                        </p>
                        <p className="text-sm text-slate-700 mt-1">
                          Sửa lại: <span className="text-emerald-600 font-medium">"{err.correction}"</span>
                        </p>
                      </div>
                    </div>
                  ))}
                </div>
              </div>

              {/* Sandwich Feedback */}
              <div className="bg-white p-6 rounded-2xl shadow-sm border border-slate-200">
                <h3 className="text-lg font-bold mb-4 flex items-center gap-2 text-slate-800">
                  <MessageSquare className="w-5 h-5 text-emerald-500" /> Nhận xét Sư phạm (Sandwich Feedback)
                </h3>
                <div className="space-y-4">
                  <div className="p-4 bg-emerald-50 border-l-4 border-emerald-400 rounded-r-xl">
                    <p className="text-sm font-medium text-emerald-800 mb-1">Ưu điểm:</p>
                    <p className="text-sm text-slate-700">{result.feedback.positive}</p>
                  </div>
                  <div className="p-4 bg-amber-50 border-l-4 border-amber-400 rounded-r-xl">
                    <p className="text-sm font-medium text-amber-800 mb-1">Lời khuyên cải thiện:</p>
                    <p className="text-sm text-slate-700">{result.feedback.advice}</p>
                  </div>
                </div>
              </div>

            </div>
          )}
        </div>

        {/* Bottom Action */}
        <div className={`p-4 bg-white/80 backdrop-blur-md border-t border-slate-200 flex justify-end gap-3 transition-all duration-300 ${result && !isProcessing ? 'translate-y-0 opacity-100' : 'translate-y-full opacity-0 absolute bottom-0'}`}>
          <button className="px-6 py-2.5 bg-slate-100 hover:bg-slate-200 text-slate-700 rounded-xl text-sm font-semibold transition-colors">
            Chấm lại
          </button>
          <button className="flex items-center gap-2 px-8 py-2.5 bg-indigo-600 hover:bg-indigo-700 text-white rounded-xl text-sm font-bold shadow-md hover:shadow-lg transition-all hover:-translate-y-0.5">
            <Save className="w-4 h-4" />
            Lưu vào Bảng điểm
          </button>
        </div>
      </div>
    </div>
  )
}

function MessageSquare(props: React.SVGProps<SVGSVGElement>) {
  return (
    <svg
      {...props}
      xmlns="http://www.w3.org/2000/svg"
      width="24"
      height="24"
      viewBox="0 0 24 24"
      fill="none"
      stroke="currentColor"
      strokeWidth="2"
      strokeLinecap="round"
      strokeLinejoin="round"
    >
      <path d="M21 15a2 2 0 0 1-2 2H7l-4 4V5a2 2 0 0 1 2-2h14a2 2 0 0 1 2 2z" />
    </svg>
  )
}
