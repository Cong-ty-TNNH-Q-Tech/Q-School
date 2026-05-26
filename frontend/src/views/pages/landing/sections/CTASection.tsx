import { useNavigate } from 'react-router-dom'

export function CTASection() {
  const navigate = useNavigate()

  return (
    <section className="cta-section">
      <div className="cta-inner">
        <div className="cta-blob cta-blob-1" />
        <div className="cta-blob cta-blob-2" />

        <h2 className="cta-title">
          Sẵn sàng thay đổi cách bạn <span className="text-gradient">dạy & học?</span>
        </h2>
        <p className="cta-desc">
          Tham gia cùng hàng ngàn giáo viên và học sinh đã tin dùng Q-School AI.
          Đăng ký miễn phí — không cần thẻ tín dụng.
        </p>
        <div className="cta-actions">
          <button className="btn-primary-glow btn-lg" onClick={() => navigate('/login')}>
            Bắt đầu miễn phí ngay
            <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><line x1="5" y1="12" x2="19" y2="12" /><polyline points="12 5 19 12 12 19" /></svg>
          </button>
        </div>
      </div>
    </section>
  )
}
