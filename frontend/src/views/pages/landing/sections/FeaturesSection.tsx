import { useNavigate } from 'react-router-dom'

const features = [
  {
    icon: (
      <svg width="28" height="28" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.8" strokeLinecap="round" strokeLinejoin="round">
        <path d="M21 15a2 2 0 0 1-2 2H7l-4 4V5a2 2 0 0 1 2-2h14a2 2 0 0 1 2 2z" />
      </svg>
    ),
    color: 'var(--feat-violet)',
    title: 'Trợ lý AI Chat',
    desc: 'Hỏi đáp tức thì với AI được tinh chỉnh riêng cho giáo dục Việt Nam. Hỗ trợ SSE streaming, phản hồi mượt mà như đang chat với giáo viên thật.',
    link: '/dashboard',
  },
  {
    icon: (
      <svg width="28" height="28" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.8" strokeLinecap="round" strokeLinejoin="round">
        <path d="M14.5 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V7.5L14.5 2z" />
        <polyline points="14 2 14 8 20 8" />
        <line x1="16" y1="13" x2="8" y2="13" /><line x1="16" y1="17" x2="8" y2="17" /><line x1="10" y1="9" x2="8" y2="9" />
      </svg>
    ),
    color: 'var(--feat-blue)',
    title: 'Sinh giáo án tự động',
    desc: 'AI tạo giáo án chi tiết theo chuẩn MOET chỉ trong vài giây. Tùy chỉnh theo môn học, khối lớp và phương pháp giảng dạy.',
    link: '/dashboard',
  },
  {
    icon: (
      <svg width="28" height="28" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.8" strokeLinecap="round" strokeLinejoin="round">
        <path d="M12 22c5.523 0 10-4.477 10-10S17.523 2 12 2 2 6.477 2 12s4.477 10 10 10z" />
        <path d="M9.09 9a3 3 0 0 1 5.83 1c0 2-3 3-3 3" /><line x1="12" y1="17" x2="12.01" y2="17" />
      </svg>
    ),
    color: 'var(--feat-cyan)',
    title: 'Quiz thông minh',
    desc: 'Hệ thống đề thi đa dạng: trắc nghiệm, tự luận, ghép cặp. AI tự động chấm điểm và phân tích điểm yếu từng học sinh.',
    link: '/dashboard',
  },
  {
    icon: (
      <svg width="28" height="28" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.8" strokeLinecap="round" strokeLinejoin="round">
        <rect x="2" y="3" width="20" height="14" rx="2" />
        <line x1="8" y1="21" x2="16" y2="21" /><line x1="12" y1="17" x2="12" y2="21" />
      </svg>
    ),
    color: 'var(--feat-emerald)',
    title: 'Flashcard & Ôn tập',
    desc: 'Thuật toán lặp lại cách quãng (Spaced Repetition) giúp ghi nhớ bền vững. AI tự tạo bộ flashcard từ nội dung bài học.',
    link: '/dashboard/flashcards',
  },
  {
    icon: (
      <svg width="28" height="28" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.8" strokeLinecap="round" strokeLinejoin="round">
        <line x1="18" y1="20" x2="18" y2="10" /><line x1="12" y1="20" x2="12" y2="4" /><line x1="6" y1="20" x2="6" y2="14" />
      </svg>
    ),
    color: 'var(--feat-amber)',
    title: 'Phân tích học tập',
    desc: 'Dashboard trực quan hiển thị tiến độ, điểm mạnh — yếu và đề xuất cải thiện. Giáo viên quản lý lớp học dễ dàng hơn bao giờ hết.',
    link: '/dashboard',
  },
  {
    icon: (
      <svg width="28" height="28" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.8" strokeLinecap="round" strokeLinejoin="round">
        <path d="M17 21v-2a4 4 0 0 0-4-4H5a4 4 0 0 0-4 4v2" /><circle cx="9" cy="7" r="4" />
        <path d="M23 21v-2a4 4 0 0 0-3-3.87" /><path d="M16 3.13a4 4 0 0 1 0 7.75" />
      </svg>
    ),
    color: 'var(--feat-rose)',
    title: 'Quản lý lớp học',
    desc: 'Hệ thống quản lý học sinh, giáo viên, phụ huynh toàn diện. Tích hợp giao bài tập, thông báo và IEP cho học sinh đặc biệt.',
    link: '/dashboard',
  },
]

export function FeaturesSection() {
  const navigate = useNavigate()

  return (
    <section className="features-section" id="features">
      <div className="section-container">
        <div className="section-header">
          <span className="section-badge">Tính năng</span>
          <h2 className="section-title">
            Mọi thứ bạn cần, <span className="text-gradient">một nền tảng duy nhất</span>
          </h2>
          <p className="section-desc">
            Q-School AI tích hợp đầy đủ công cụ từ giảng dạy, kiểm tra đến phân tích — tất cả
            được tăng cường bởi AI tiên tiến nhất.
          </p>
        </div>

        <div className="features-grid">
          {features.map((f) => (
            <div
              className="feature-card"
              key={f.title}
              onClick={() => navigate(f.link)}
              style={{ cursor: 'pointer' }}
            >
              <div className="feature-icon" style={{ '--fc': f.color } as React.CSSProperties}>
                {f.icon}
              </div>
              <h3 className="feature-title">{f.title}</h3>
              <p className="feature-desc">{f.desc}</p>
            </div>
          ))}
        </div>
      </div>
    </section>
  )
}
