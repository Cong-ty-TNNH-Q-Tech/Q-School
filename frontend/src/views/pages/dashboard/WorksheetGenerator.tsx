import { useState } from 'react'
import { 
  Sparkles, 
  Edit3, 
  Save, 
  Download, 
  CheckSquare, 
  Square,
  ChevronDown
} from 'lucide-react'

export default function WorksheetGenerator() {
  const [topic, setTopic] = useState("Phép cộng trừ số thập phân, có các bài toán đố thực tế...")
  const [questionTypes, setQuestionTypes] = useState({
    multipleChoice: true,
    fillInBlank: true,
    trueFalse: false,
    matching: false
  })
  const [questionCount, setQuestionCount] = useState(15)
  const [difficulty, setDifficulty] = useState("Trung bình")
  const [includeAnswers, setIncludeAnswers] = useState(true)

  const toggleQuestionType = (type: keyof typeof questionTypes) => {
    setQuestionTypes(prev => ({ ...prev, [type]: !prev[type] }))
  }

  return (
    <div className="flex flex-col md:flex-row h-full min-h-[calc(100vh-4rem)] bg-slate-50 border rounded-2xl overflow-hidden shadow-sm animate-in fade-in duration-500">
      
      {/* LEFT PANE: Configuration Form */}
      <div className="w-full md:w-[400px] flex flex-col bg-white border-r border-slate-200 z-10 shadow-[2px_0_10px_rgba(0,0,0,0.02)]">
        <div className="p-6 border-b border-slate-100">
          <h2 className="text-2xl font-bold tracking-tight text-slate-800">Tạo Phiếu Bài Tập</h2>
          <p className="text-sm text-slate-500 mt-1">Cấu hình nội dung và định dạng cho bài tập.</p>
        </div>

        <div className="flex-1 overflow-y-auto p-6 space-y-6 custom-scrollbar">
          
          {/* Topic Input */}
          <div className="space-y-2">
            <label className="text-sm font-semibold text-slate-700">Chủ đề / Nội dung chính</label>
            <textarea 
              className="w-full h-32 p-3 text-sm border border-slate-200 rounded-xl focus:ring-2 focus:ring-indigo-500/20 focus:border-indigo-500 transition-all resize-none bg-slate-50/50"
              placeholder="VD: Phép cộng trừ số thập phân..."
              value={topic}
              onChange={(e) => setTopic(e.target.value)}
            />
          </div>

          {/* Question Types */}
          <div className="space-y-3">
            <label className="text-sm font-semibold text-slate-700">Loại câu hỏi</label>
            <div className="grid grid-cols-2 gap-3">
              {[
                { id: 'multipleChoice', label: 'Trắc nghiệm' },
                { id: 'fillInBlank', label: 'Điền vào chỗ trống' },
                { id: 'trueFalse', label: 'Đúng / Sai' },
                { id: 'matching', label: 'Nối từ' },
              ].map((type) => (
                <div 
                  key={type.id}
                  onClick={() => toggleQuestionType(type.id as keyof typeof questionTypes)}
                  className={`flex items-center gap-2 p-3 rounded-xl border cursor-pointer transition-all ${
                    questionTypes[type.id as keyof typeof questionTypes] 
                    ? 'border-indigo-500 bg-indigo-50/50 text-indigo-700' 
                    : 'border-slate-200 hover:border-slate-300 text-slate-600'
                  }`}
                >
                  {questionTypes[type.id as keyof typeof questionTypes] ? (
                    <CheckSquare className="w-4 h-4 text-indigo-600" />
                  ) : (
                    <Square className="w-4 h-4 text-slate-400" />
                  )}
                  <span className="text-sm font-medium">{type.label}</span>
                </div>
              ))}
            </div>
          </div>

          {/* Count and Difficulty */}
          <div className="grid grid-cols-2 gap-4">
            <div className="space-y-2">
              <label className="text-sm font-semibold text-slate-700">Số lượng câu hỏi</label>
              <input 
                type="number" 
                className="w-full p-3 text-sm border border-slate-200 rounded-xl focus:ring-2 focus:ring-indigo-500/20 focus:border-indigo-500 transition-all bg-slate-50/50"
                value={questionCount}
                onChange={(e) => setQuestionCount(parseInt(e.target.value) || 0)}
              />
            </div>
            <div className="space-y-2">
              <label className="text-sm font-semibold text-slate-700">Độ khó</label>
              <div className="relative">
                <select 
                  className="w-full p-3 text-sm border border-slate-200 rounded-xl appearance-none focus:ring-2 focus:ring-indigo-500/20 focus:border-indigo-500 transition-all bg-slate-50/50"
                  value={difficulty}
                  onChange={(e) => setDifficulty(e.target.value)}
                >
                  <option>Dễ</option>
                  <option>Trung bình</option>
                  <option>Khó</option>
                </select>
                <ChevronDown className="absolute right-3 top-3.5 w-4 h-4 text-slate-400 pointer-events-none" />
              </div>
            </div>
          </div>
        </div>

        {/* Action Button */}
        <div className="p-6 border-t border-slate-100 bg-slate-50/50">
          <button className="w-full flex items-center justify-center gap-2 bg-gradient-to-r from-indigo-600 to-violet-600 hover:from-indigo-700 hover:to-violet-700 text-white font-medium py-3.5 rounded-xl shadow-md hover:shadow-lg transition-all hover:-translate-y-0.5">
            <Sparkles className="w-5 h-5 text-indigo-200" />
            Tạo Bài Tập Bằng AI
          </button>
        </div>
      </div>

      {/* RIGHT PANE: Preview Area */}
      <div className="flex-1 bg-slate-100 relative flex flex-col h-full overflow-hidden">
        
        {/* Document Preview Scrollable Area */}
        <div className="flex-1 overflow-y-auto p-4 md:p-8 custom-scrollbar relative">
          
          {/* Mock A4 Paper */}
          <div className="bg-white mx-auto max-w-[800px] min-h-[1056px] shadow-sm ring-1 ring-slate-900/5 mb-24 rounded-sm relative group transition-all">
            
            <div className="p-12 md:p-16 text-slate-800">
              {/* Header Info */}
              <div className="flex justify-between items-end border-b-2 border-slate-800 pb-6 mb-8">
                <div className="space-y-4 flex-1 pr-8">
                  <div className="flex items-end gap-2">
                    <span className="font-semibold w-16">Họ tên:</span>
                    <div className="flex-1 border-b border-dotted border-slate-400 pb-1"></div>
                  </div>
                  <div className="flex items-end gap-2">
                    <span className="font-semibold w-16">Lớp:</span>
                    <div className="w-32 border-b border-dotted border-slate-400 pb-1"></div>
                    <span className="font-semibold ml-4">Ngày:</span>
                    <div className="flex-1 border-b border-dotted border-slate-400 pb-1"></div>
                  </div>
                </div>
                <div className="w-32 h-32 border-2 border-slate-300 rounded flex items-center justify-center text-slate-300 text-sm font-medium">
                  Điểm số
                </div>
              </div>

              {/* Title */}
              <h1 className="text-2xl font-bold text-center mb-10 text-slate-900">
                BÀI TẬP: PHÉP CỘNG TRỪ SỐ THẬP PHÂN
              </h1>

              {/* Content Mock */}
              <div className="space-y-8">
                {/* Q1 */}
                <div>
                  <h3 className="font-bold mb-4">Câu 1: Đặt tính rồi tính</h3>
                  <div className="grid grid-cols-2 gap-8">
                    <div>
                      <p className="mb-2">a) 45.6 + 23.8</p>
                      <div className="h-24 border border-slate-200 rounded-lg bg-[url('data:image/svg+xml;base64,PHN2ZyB4bWxucz0iaHR0cDovL3d3dy53My5vcmcvMjAwMC9zdmciIHdpZHRoPSIyMCIgaGVpZ2h0PSIyMCI+CjxyZWN0IHdpZHRoPSIyMCIgaGVpZ2h0PSIyMCIgZmlsbD0ibm9uZSIgc3Ryb2tlPSIjZTJlOGYwIiBzdHJva2Utd2lkdGg9IjEiLz4KPC9zdmc+')]"></div>
                    </div>
                    <div>
                      <p className="mb-2">b) 89.4 - 36.7</p>
                      <div className="h-24 border border-slate-200 rounded-lg bg-[url('data:image/svg+xml;base64,PHN2ZyB4bWxucz0iaHR0cDovL3d3dy53My5vcmcvMjAwMC9zdmciIHdpZHRoPSIyMCIgaGVpZ2h0PSIyMCI+CjxyZWN0IHdpZHRoPSIyMCIgaGVpZ2h0PSIyMCIgZmlsbD0ibm9uZSIgc3Ryb2tlPSIjZTJlOGYwIiBzdHJva2Utd2lkdGg9IjEiLz4KPC9zdmc+')]"></div>
                    </div>
                  </div>
                </div>

                {/* Q2 */}
                <div>
                  <h3 className="font-bold mb-4">Câu 2: Điền số thích hợp vào chỗ chấm</h3>
                  <div className="space-y-4 ml-4">
                    <p>a) 12.5 + ............................ = 20</p>
                    <p>b) ............................ - 5.4 = 10.6</p>
                  </div>
                </div>

                {/* Q3 */}
                <div>
                  <h3 className="font-bold mb-4">Câu 3: Bài toán đố</h3>
                  <p className="mb-4 leading-relaxed">
                    Một sợi dây dài 15.5m. Lần thứ nhất người ta cắt đi 3.2m, lần thứ hai cắt đi 4.5m. 
                    Hỏi sợi dây còn lại dài bao nhiêu mét?
                  </p>
                  <div className="h-32 border border-slate-200 rounded-lg bg-[url('data:image/svg+xml;base64,PHN2ZyB4bWxucz0iaHR0cDovL3d3dy53My5vcmcvMjAwMC9zdmciIHdpZHRoPSIyMCIgaGVpZ2h0PSIyMCI+CjxyZWN0IHdpZHRoPSIyMCIgaGVpZ2h0PSIyMCIgZmlsbD0ibm9uZSIgc3Ryb2tlPSIjZTJlOGYwIiBzdHJva2Utd2lkdGg9IjEiLz4KPC9zdmc+')]"></div>
                </div>
              </div>
              
              <div className="absolute bottom-8 w-full text-center text-xs text-slate-400 left-0">
                Trang 1/1 - Tạo bởi Q-School AI
              </div>
            </div>
          </div>
        </div>

        {/* Bottom Floating Action Bar */}
        <div className="absolute bottom-0 left-0 w-full bg-white/80 backdrop-blur-md border-t border-slate-200 p-4 shadow-[0_-4px_20px_rgba(0,0,0,0.05)] z-20 flex flex-col sm:flex-row items-center justify-between gap-4">
          <div className="flex items-center gap-3 w-full sm:w-auto">
            <button className="flex items-center gap-2 px-4 py-2.5 text-sm font-medium text-slate-700 bg-white border border-slate-300 rounded-lg hover:bg-slate-50 transition-colors">
              <Edit3 className="w-4 h-4" />
              Chỉnh sửa nội dung
            </button>
            <button className="flex items-center gap-2 px-4 py-2.5 text-sm font-medium text-slate-700 bg-white border border-slate-300 rounded-lg hover:bg-slate-50 transition-colors">
              <Save className="w-4 h-4" />
              Lưu bản nháp
            </button>
          </div>

          <div className="flex items-center gap-4 w-full sm:w-auto">
            <label className="flex items-center gap-2 cursor-pointer">
              <div className={`relative w-10 h-5 rounded-full transition-colors ${includeAnswers ? 'bg-indigo-600' : 'bg-slate-300'}`}>
                <div className={`absolute top-0.5 left-0.5 bg-white w-4 h-4 rounded-full transition-transform ${includeAnswers ? 'translate-x-5' : 'translate-x-0'}`}></div>
              </div>
              <span className="text-sm font-medium text-slate-700">Kèm trang Đáp Án</span>
              <input 
                type="checkbox" 
                className="hidden" 
                checked={includeAnswers}
                onChange={() => setIncludeAnswers(!includeAnswers)}
              />
            </label>

            <button className="flex items-center gap-2 bg-[#d32f2f] hover:bg-[#b71c1c] text-white px-6 py-2.5 rounded-lg text-sm font-bold shadow-md hover:shadow-lg transition-all">
              <Download className="w-4 h-4" />
              Xuất ra PDF để in
            </button>
          </div>
        </div>
      </div>

    </div>
  )
}
