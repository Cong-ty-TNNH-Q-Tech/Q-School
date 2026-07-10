import { type ReactNode } from 'react';
import { FileText, Languages, PenLine, Video, Wand2 } from 'lucide-react';
import { ToolCard } from '@/views/components/AITools';

// [FIX #2] Dùng explicit type thay vì `as const` (as const không có giá trị với JSX elements)
interface ToolConfig {
  title: string;
  description: string;
  icon: ReactNode;
  to: string;
  gradientClass: string;
  iconColorClass: string;
  badge: string;
}

// Module-level constant — khởi tạo 1 lần, stable reference, không re-create mỗi render
const TOOLS: ToolConfig[] = [
  {
    title: 'Tóm tắt văn bản',
    description: 'Tóm tắt tài liệu dài thành các ý chính, phù hợp cho ôn tập và nghiên cứu.',
    icon: <FileText className="w-6 h-6" />,
    to: '/ai/tools/summarize',
    gradientClass: 'from-blue-500/15 to-cyan-500/15',
    iconColorClass: 'text-blue-600',
    badge: 'Streaming',
  },
  {
    title: 'Dịch thuật học thuật',
    description: 'Dịch văn bản, tài liệu với độ chính xác cao. Hỗ trợ 20 ngôn ngữ phổ biến.',
    icon: <Languages className="w-6 h-6" />,
    to: '/ai/tools/translate',
    gradientClass: 'from-violet-500/15 to-pink-500/15',
    iconColorClass: 'text-violet-600',
    badge: 'Streaming',
  },
  {
    title: 'Viết lại văn bản',
    description: 'Viết lại câu văn theo 5 văn phong: Trang trọng, Thân thiện, Súc tích, Học thuật, Sáng tạo.',
    icon: <PenLine className="w-6 h-6" />,
    to: '/ai/tools/rewrite',
    gradientClass: 'from-orange-500/15 to-yellow-500/15',
    iconColorClass: 'text-orange-600',
    badge: 'Streaming',
  },
  {
    title: 'Câu hỏi từ YouTube',
    description: 'Nhập link video YouTube, hệ thống tự trích xuất nội dung và sinh câu hỏi MCQ + tự luận kèm timestamp.',
    icon: <Video className="w-6 h-6" />,
    to: '/ai/tools/youtube-qa',
    gradientClass: 'from-red-500/15 to-rose-500/15',
    iconColorClass: 'text-red-600',
    badge: 'AI',
  },
];

export default function AIToolsHubPage() {
  return (
    <div className="container mx-auto px-4 py-8 max-w-5xl">
      {/* Page Header */}
      <div className="mb-10 flex items-start gap-4">
        <div className="flex h-12 w-12 shrink-0 items-center justify-center rounded-xl bg-gradient-to-br from-primary/20 to-primary/10 shadow-inner">
          <Wand2 className="h-6 w-6 text-primary" />
        </div>
        <div>
          <h1 className="text-3xl font-bold tracking-tight text-gray-900">
            AI Tools Hub
          </h1>
          <p className="mt-1.5 text-base text-gray-500 max-w-2xl">
            Bộ công cụ AI hỗ trợ giảng dạy và học tập. Tóm tắt, dịch thuật, viết lại văn bản và sinh câu hỏi từ video YouTube chỉ trong vài giây.
          </p>
        </div>
      </div>

      {/* Tool Cards Grid */}
      <div className="grid grid-cols-1 sm:grid-cols-2 gap-5">
        {TOOLS.map((tool, index) => (
          <div
            key={tool.to}
            // [FIX #3] Thêm duration-500 — bắt buộc để animation có thời gian chạy
            // Convention dự án: FlashcardStudy dùng duration-300, EssaySubmission dùng duration-500
            className="animate-in fade-in slide-in-from-bottom-4 duration-500"
            style={{ animationDelay: `${index * 80}ms`, animationFillMode: 'both' }}
          >
            <ToolCard
              title={tool.title}
              description={tool.description}
              icon={tool.icon}
              to={tool.to}
              gradientClass={tool.gradientClass}
              iconColorClass={tool.iconColorClass}
              badge={tool.badge}
            />
          </div>
        ))}
      </div>

      {/* Footer note */}
      <p className="mt-8 text-center text-xs text-gray-400">
        Tất cả công cụ đang chạy ở chế độ mô phỏng (Mock). Kết quả thực sẽ được kết nối sau khi Backend hoàn thiện.
      </p>
    </div>
  );
}
