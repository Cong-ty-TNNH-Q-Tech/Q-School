import { useState } from 'react'
import { 
  Sparkles, 
  Copy, 
  Save, 
  Languages, 
  Plus, 
  X,
  User,
  GraduationCap,
  MessageSquareText,
  ChevronDown,
  CheckCircle2,
  Circle
} from 'lucide-react'

export default function ReportComments() {
  const [isGenerating, setIsGenerating] = useState(false)
  const [tone, setTone] = useState('khich_le')
  
  const strengths = ['Hòa đồng', 'Nhiệt tình tham gia phong trào', 'Thể lực tốt']
  const improvements = ['Mất gốc Toán', 'Hay nói chuyện riêng', 'Chưa làm bài tập về nhà']

  const [commentText, setCommentText] = useState(
    "Lê Hoàng Long là một học sinh rất hòa đồng và nhiệt tình tham gia các phong trào của lớp, em luôn thể hiện thể lực tốt và tinh thần đồng đội cao trong các hoạt động thể thao. Học kỳ này, em có thành tích học tập nhìn chung xuất sắc, đạt danh hiệu Học sinh Giỏi (ĐTB: 9.2).\n\n" +
    "Tuy nhiên, để phát huy tối đa tiềm năng, Long cần đặc biệt chú ý hơn trong các giờ học Toán để nắm vững lại các kiến thức cơ bản đang bị hổng. Em cũng cần khắc phục tình trạng hay nói chuyện riêng trong lớp làm ảnh hưởng đến các bạn xung quanh, đồng thời rèn luyện thói quen tự giác hoàn thành đầy đủ bài tập về nhà trước khi đến lớp.\n\n" +
    "Thầy/Cô tin rằng với sự năng động và nền tảng tốt hiện có, nếu Long quyết tâm tập trung và kỷ luật hơn trong học tập, em chắc chắn sẽ đạt được những bước tiến vượt bậc và những kết quả còn tuyệt vời hơn nữa trong thời gian tới!"
  )

  const handleGenerate = () => {
    setIsGenerating(true)
    setTimeout(() => setIsGenerating(false), 2000)
  }

  return (
    <div className="flex flex-col h-full min-h-[calc(100vh-4rem)] animate-in fade-in duration-500">
      
      <div className="mb-6 flex items-center gap-3">
        <div className="w-10 h-10 rounded-xl bg-indigo-100 flex items-center justify-center text-indigo-600">
          <MessageSquareText className="w-5 h-5" />
        </div>
        <div>
          <h1 className="text-2xl font-bold text-slate-800">Tạo Lời Phê Tự Động</h1>
          <p className="text-sm text-slate-500">Sinh nhận xét sổ liên lạc được cá nhân hóa bằng AI.</p>
        </div>
      </div>

      <div className="flex flex-col lg:flex-row gap-6 h-full flex-1">
        
        {/* LEFT PANE: Configuration Form */}
        <div className="w-full lg:w-[420px] flex flex-col bg-white border border-slate-200 rounded-2xl shadow-sm overflow-hidden flex-shrink-0">
          <div className="p-5 flex-1 overflow-y-auto custom-scrollbar space-y-6">
            
            {/* Student Selector */}
            <div className="space-y-2">
              <label className="text-xs font-bold text-slate-500 uppercase tracking-wider">Học sinh</label>
              <div className="flex items-center justify-between p-3 border border-slate-200 rounded-xl bg-slate-50 cursor-pointer hover:bg-slate-100 transition-colors">
                <div className="flex items-center gap-3">
                  <div className="w-10 h-10 rounded-full bg-slate-200 flex items-center justify-center text-slate-600 font-bold text-sm">
                    LL
                  </div>
                  <div>
                    <p className="text-sm font-bold text-slate-800">Lê Hoàng Long</p>
                    <p className="text-xs text-slate-500">- 10A1</p>
                  </div>
                </div>
                <div className="flex items-center gap-3">
                  <span className="px-2 py-1 bg-emerald-100 text-emerald-700 text-xs font-bold rounded-md flex items-center gap-1">
                    <GraduationCap className="w-3 h-3" /> Học lực: Giỏi
                  </span>
                  <ChevronDown className="w-4 h-4 text-slate-400" />
                </div>
              </div>
            </div>

            {/* Strengths */}
            <div className="space-y-3">
              <label className="text-xs font-bold text-slate-500 uppercase tracking-wider">Điểm mạnh / Khen ngợi</label>
              <div className="flex flex-wrap gap-2">
                {strengths.map((s, i) => (
                  <div key={i} className="flex items-center gap-1.5 px-3 py-1.5 bg-blue-50 border border-blue-100 text-blue-700 rounded-lg text-sm transition-all hover:bg-blue-100">
                    <span>{s}</span>
                    <X className="w-3.5 h-3.5 cursor-pointer hover:text-blue-900 opacity-70" />
                  </div>
                ))}
                <button className="flex items-center gap-1 px-3 py-1.5 border border-dashed border-slate-300 text-slate-500 rounded-lg text-sm hover:bg-slate-50 transition-colors">
                  <Plus className="w-3.5 h-3.5" /> Thêm
                </button>
              </div>
            </div>

            {/* Improvements */}
            <div className="space-y-3">
              <label className="text-xs font-bold text-slate-500 uppercase tracking-wider">Cần cải thiện</label>
              <div className="flex flex-wrap gap-2">
                {improvements.map((s, i) => (
                  <div key={i} className="flex items-center gap-1.5 px-3 py-1.5 bg-rose-50 border border-rose-100 text-rose-700 rounded-lg text-sm transition-all hover:bg-rose-100">
                    <span>{s}</span>
                    <X className="w-3.5 h-3.5 cursor-pointer hover:text-rose-900 opacity-70" />
                  </div>
                ))}
                <button className="flex items-center gap-1 px-3 py-1.5 border border-dashed border-slate-300 text-slate-500 rounded-lg text-sm hover:bg-slate-50 transition-colors">
                  <Plus className="w-3.5 h-3.5" /> Thêm
                </button>
              </div>
            </div>

            {/* Tone */}
            <div className="space-y-3">
              <label className="text-xs font-bold text-slate-500 uppercase tracking-wider">Giọng điệu</label>
              <div className="space-y-2">
                {[
                  { id: 'khich_le', label: 'Khích lệ & Động viên' },
                  { id: 'nghiem_khac', label: 'Nghiêm khắc & Chuyên nghiệp' },
                  { id: 'ngan_gon', label: 'Ngắn gọn' },
                ].map((t) => (
                  <div 
                    key={t.id}
                    onClick={() => setTone(t.id)}
                    className={`flex items-center gap-3 p-3 rounded-xl border cursor-pointer transition-all ${
                      tone === t.id 
                      ? 'border-indigo-600 bg-indigo-50/50 text-indigo-700 shadow-sm' 
                      : 'border-slate-200 hover:border-slate-300 text-slate-600'
                    }`}
                  >
                    {tone === t.id ? (
                      <CheckCircle2 className="w-5 h-5 text-indigo-600" />
                    ) : (
                      <Circle className="w-5 h-5 text-slate-300" />
                    )}
                    <span className="text-sm font-medium">{t.label}</span>
                  </div>
                ))}
              </div>
            </div>

          </div>
          
          <div className="p-5 border-t border-slate-100 bg-slate-50/50">
            <button 
              onClick={handleGenerate}
              disabled={isGenerating}
              className="w-full flex items-center justify-center gap-2 bg-indigo-600 hover:bg-indigo-700 text-white font-semibold py-3.5 rounded-xl shadow-md transition-all hover:shadow-lg disabled:opacity-70"
            >
              <Sparkles className={`w-5 h-5 ${isGenerating ? 'animate-spin' : ''}`} />
              {isGenerating ? 'Đang phân tích...' : 'Sinh Lời Phê AI'}
            </button>
          </div>
        </div>

        {/* RIGHT PANE: Output */}
        <div className="flex-1 flex flex-col gap-4">
          
          {/* Editor Area */}
          <div className="flex-1 bg-white border border-slate-200 rounded-2xl shadow-sm flex flex-col overflow-hidden relative">
            <div className="flex justify-between items-center p-4 border-b border-slate-100 bg-slate-50/50">
              <div className="flex items-center gap-2 text-indigo-600">
                <MessageSquareText className="w-4 h-4" />
                <span className="text-sm font-bold uppercase tracking-wider">Bản Thảo Lời Phê</span>
              </div>
              <div className="text-xs text-slate-400 italic">
                Nhấn vào để chỉnh sửa nội dung
              </div>
            </div>
            
            <div className="flex-1 p-6 relative">
              {isGenerating ? (
                <div className="absolute inset-0 flex items-center justify-center bg-white/80 backdrop-blur-sm z-10">
                  <div className="flex flex-col items-center gap-3">
                    <div className="w-8 h-8 border-4 border-indigo-200 border-t-indigo-600 rounded-full animate-spin"></div>
                    <p className="text-sm font-medium text-indigo-600 animate-pulse">AI đang tổng hợp lời phê...</p>
                  </div>
                </div>
              ) : null}
              
              <textarea 
                className="w-full h-full resize-none text-slate-700 text-base leading-relaxed focus:outline-none placeholder:text-slate-300"
                value={commentText}
                onChange={(e) => setCommentText(e.target.value)}
                placeholder="Lời phê sẽ xuất hiện ở đây..."
              />
            </div>
          </div>

          {/* Action Bar */}
          <div className="flex justify-end gap-3 items-center">
            <button className="flex items-center gap-2 px-5 py-2.5 bg-white border border-slate-200 hover:bg-slate-50 text-slate-700 rounded-xl text-sm font-medium transition-all shadow-sm">
              <Languages className="w-4 h-4" /> Dịch sang Tiếng Anh
            </button>
            <button className="flex items-center gap-2 px-5 py-2.5 bg-white border border-slate-200 hover:bg-slate-50 text-slate-700 rounded-xl text-sm font-medium transition-all shadow-sm">
              <Save className="w-4 h-4" /> Lưu vào Hồ sơ
            </button>
            <button className="flex items-center gap-2 px-8 py-2.5 bg-indigo-600 hover:bg-indigo-700 text-white rounded-xl text-sm font-bold shadow-md hover:shadow-lg transition-all hover:-translate-y-0.5 ml-2">
              <Copy className="w-4 h-4" /> Sao chép
            </button>
          </div>

        </div>

      </div>
    </div>
  )
}
