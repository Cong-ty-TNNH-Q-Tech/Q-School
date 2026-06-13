import { useAuthStore } from '@/stores/useAuthStore'
import { useNavigate } from 'react-router-dom'
import { 
  FileText, 
  Camera, 
  MessageSquare, 
  Users, 
  BookOpen, 
  CheckCircle,
  Clock,
  ArrowRight
} from 'lucide-react'

export default function Dashboard() {
  const user = useAuthStore((state) => state.user)
  const navigate = useNavigate()

  const quickActions = [
    {
      title: "Tạo Phiếu Bài Tập",
      description: "Dùng AI sinh đề kiểm tra, bài tập về nhà bám sát GDPT 2018.",
      icon: FileText,
      color: "text-blue-600",
      bgColor: "bg-blue-100 dark:bg-blue-900/30",
      gradient: "from-blue-500 to-cyan-400",
      link: "/dashboard/worksheet"
    },
    {
      title: "Chấm Điểm Camera (OCR)",
      description: "Chụp ảnh bài thi giấy, bóc tách chữ viết tay và tự động chấm điểm.",
      icon: Camera,
      color: "text-purple-600",
      bgColor: "bg-purple-100 dark:bg-purple-900/30",
      gradient: "from-purple-500 to-pink-400",
      link: "#"
    },
    {
      title: "Nhận Xét Sổ Liên Lạc",
      description: "Sinh tự động lời nhận xét tinh tế, chuyên nghiệp cho từng học sinh.",
      icon: MessageSquare,
      color: "text-emerald-600",
      bgColor: "bg-emerald-100 dark:bg-emerald-900/30",
      gradient: "from-emerald-500 to-teal-400",
      link: "#"
    }
  ]

  const stats = [
    { label: "Tổng số Học sinh", value: "145", icon: Users, trend: "+12%" },
    { label: "Lớp đang phụ trách", value: "4", icon: BookOpen, trend: "Cố định" },
    { label: "Bài tập đã tạo", value: "32", icon: FileText, trend: "+5%" },
    { label: "Bài thi đã chấm", value: "128", icon: CheckCircle, trend: "+24%" }
  ]

  return (
    <div className="space-y-8 animate-in fade-in slide-in-from-bottom-4 duration-500">
      {/* Header Section */}
      <div className="relative overflow-hidden rounded-2xl bg-gradient-to-r from-slate-900 to-slate-800 dark:from-slate-800 dark:to-slate-950 p-8 text-white shadow-xl">
        <div className="absolute top-0 right-0 -mt-4 -mr-4 w-64 h-64 bg-white opacity-5 rounded-full blur-3xl"></div>
        <div className="relative z-10 flex flex-col md:flex-row md:items-center justify-between gap-4">
          <div>
            <h2 className="text-3xl font-bold tracking-tight mb-2">
              Chào mừng trở lại, Thầy/Cô {user?.profile?.full_name || user?.username || ''}! 👋
            </h2>
            <p className="text-slate-300 max-w-2xl text-lg">
              Q-School AI Workspace đã sẵn sàng. Hãy chọn một công cụ bên dưới để bắt đầu tối ưu hóa công việc giảng dạy của bạn hôm nay.
            </p>
          </div>
          <div className="flex items-center gap-2 bg-white/10 px-4 py-2 rounded-full backdrop-blur-sm border border-white/20">
            <span className="flex h-3 w-3 rounded-full bg-emerald-400 animate-pulse"></span>
            <span className="text-sm font-medium">VNPT Smartbot is Online</span>
          </div>
        </div>
      </div>

      {/* Metrics Section */}
      <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-4">
        {stats.map((stat, idx) => (
          <div 
            key={idx} 
            className="group relative overflow-hidden rounded-xl border bg-card p-6 shadow-sm hover:shadow-md transition-all duration-300 hover:-translate-y-1"
          >
            <div className="flex flex-row items-center justify-between space-y-0 pb-2">
              <h3 className="tracking-tight text-sm font-medium text-muted-foreground">{stat.label}</h3>
              <div className="p-2 bg-slate-100 dark:bg-slate-800 rounded-lg group-hover:scale-110 transition-transform duration-300">
                <stat.icon className="h-4 w-4 text-slate-600 dark:text-slate-300" />
              </div>
            </div>
            <div className="pt-2">
              <div className="text-3xl font-bold">{stat.value}</div>
              <p className="text-xs text-emerald-500 font-medium mt-1 flex items-center gap-1">
                {stat.trend.startsWith('+') ? (
                  <svg className="w-3 h-3" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M13 7h8m0 0v8m0-8l-8 8-4-4-6 6"></path></svg>
                ) : null}
                {stat.trend} so với tháng trước
              </p>
            </div>
          </div>
        ))}
      </div>

      {/* Quick Actions (MVP Core Features) */}
      <div>
        <h3 className="text-xl font-bold tracking-tight mb-4 flex items-center gap-2">
          ⚡ Công cụ nổi bật
        </h3>
        <div className="grid gap-6 md:grid-cols-3">
          {quickActions.map((action, idx) => (
            <div 
              key={idx} 
              onClick={() => navigate(action.link)}
              className="group relative flex flex-col justify-between overflow-hidden rounded-2xl border bg-card shadow-sm hover:shadow-xl transition-all duration-300 hover:-translate-y-1 cursor-pointer"
            >
              {/* Top Gradient Bar */}
              <div className={`h-2 w-full bg-gradient-to-r ${action.gradient}`}></div>
              
              <div className="p-6">
                <div className={`mb-4 inline-flex p-3 rounded-xl ${action.bgColor}`}>
                  <action.icon className={`h-6 w-6 ${action.color}`} />
                </div>
                <h4 className="text-xl font-semibold mb-2">{action.title}</h4>
                <p className="text-muted-foreground text-sm line-clamp-2">
                  {action.description}
                </p>
              </div>
              
              <div className="p-6 pt-0 mt-auto">
                <div className="flex items-center text-sm font-medium text-slate-600 dark:text-slate-300 group-hover:text-primary transition-colors">
                  Bắt đầu ngay <ArrowRight className="ml-1 h-4 w-4 transform group-hover:translate-x-1 transition-transform" />
                </div>
              </div>
            </div>
          ))}
        </div>
      </div>

      {/* Recent Activity */}
      <div className="grid gap-6 md:grid-cols-2">
        <div className="rounded-2xl border bg-card shadow-sm p-6">
          <h3 className="text-lg font-bold mb-4">Lịch sử hoạt động</h3>
          <div className="space-y-4">
            {[
              { text: "Đã chấm xong 40 bài kiểm tra lớp 10A1", time: "2 giờ trước", icon: CheckCircle, color: "text-emerald-500" },
              { text: "Tạo phiếu bài tập môn Toán - Hình học không gian", time: "Hôm qua", icon: FileText, color: "text-blue-500" },
              { text: "Sinh nhận xét học bạ lớp 11B3", time: "3 ngày trước", icon: MessageSquare, color: "text-purple-500" },
            ].map((item, idx) => (
              <div key={idx} className="flex items-start gap-4 p-3 rounded-xl hover:bg-slate-50 dark:hover:bg-slate-900/50 transition-colors">
                <div className="mt-0.5">
                  <item.icon className={`h-5 w-5 ${item.color}`} />
                </div>
                <div>
                  <p className="text-sm font-medium">{item.text}</p>
                  <p className="text-xs text-muted-foreground flex items-center gap-1 mt-1">
                    <Clock className="h-3 w-3" /> {item.time}
                  </p>
                </div>
              </div>
            ))}
          </div>
        </div>

        <div className="rounded-2xl border bg-gradient-to-br from-indigo-50 to-purple-50 dark:from-indigo-950/20 dark:to-purple-950/20 shadow-sm p-6 flex flex-col justify-center items-center text-center relative overflow-hidden">
          <div className="absolute top-0 right-0 w-32 h-32 bg-purple-500/10 rounded-full blur-3xl"></div>
          <div className="absolute bottom-0 left-0 w-32 h-32 bg-indigo-500/10 rounded-full blur-3xl"></div>
          
          <div className="relative z-10">
            <div className="mb-4 inline-flex p-4 rounded-full bg-white dark:bg-slate-800 shadow-sm">
              <Camera className="h-8 w-8 text-indigo-600 dark:text-indigo-400" />
            </div>
            <h3 className="text-lg font-bold mb-2">Trải nghiệm chấm thi O2O</h3>
            <p className="text-muted-foreground text-sm mb-6 max-w-[250px] mx-auto">
              Sử dụng camera điện thoại hoặc tải ảnh bài thi lên để AI chấm điểm tự động trong 3 giây.
            </p>
            <button className="bg-indigo-600 hover:bg-indigo-700 text-white px-6 py-2.5 rounded-full text-sm font-medium transition-all hover:shadow-lg hover:-translate-y-0.5">
              Tải ảnh bài thi
            </button>
          </div>
        </div>
      </div>
    </div>
  )
}
