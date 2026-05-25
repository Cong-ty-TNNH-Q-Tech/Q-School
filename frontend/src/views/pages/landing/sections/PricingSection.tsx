import { useNavigate } from 'react-router-dom'

const plans = [
  {
    name: 'Miễn phí',
    price: '0₫',
    period: '/tháng',
    desc: 'Bắt đầu trải nghiệm ngay',
    features: ['5 lượt AI Chat/ngày', 'Tạo 3 bài Quiz/tháng', 'Flashcard cơ bản', 'Quản lý 1 lớp học'],
    cta: 'Đăng ký miễn phí',
    popular: false,
  },
  {
    name: 'Pro',
    price: '199.000₫',
    period: '/tháng',
    desc: 'Dành cho giáo viên chuyên nghiệp',
    features: [
      'Không giới hạn AI Chat',
      'Sinh giáo án tự động',
      'Quiz & tự luận AI chấm',
      'Flashcard thông minh',
      'Phân tích học tập nâng cao',
      'Quản lý 10 lớp học',
      'Hỗ trợ ưu tiên 24/7',
    ],
    cta: 'Bắt đầu dùng thử',
    popular: true,
  },
  {
    name: 'Enterprise',
    price: 'Liên hệ',
    period: '',
    desc: 'Giải pháp cho trường học & tổ chức',
    features: [
      'Tất cả tính năng Pro',
      'Không giới hạn lớp học',
      'API tích hợp riêng',
      'Triển khai On-premise',
      'Đào tạo & hỗ trợ chuyên biệt',
      'SLA 99.9% uptime',
    ],
    cta: 'Liên hệ tư vấn',
    popular: false,
  },
]

export function PricingSection() {
  const navigate = useNavigate()

  return (
    <section className="pricing-section" id="pricing">
      <div className="section-container">
        <div className="section-header">
          <span className="section-badge">Bảng giá</span>
          <h2 className="section-title">
            Chọn gói phù hợp với <span className="text-gradient">nhu cầu của bạn</span>
          </h2>
          <p className="section-desc">
            Bắt đầu miễn phí, nâng cấp khi cần. Không ràng buộc hợp đồng dài hạn.
          </p>
        </div>

        <div className="pricing-grid">
          {plans.map((p) => (
            <div className={`pricing-card ${p.popular ? 'pricing-popular' : ''}`} key={p.name}>
              {p.popular && <div className="pricing-badge-pop">Phổ biến nhất</div>}
              <h3 className="pricing-name">{p.name}</h3>
              <p className="pricing-desc">{p.desc}</p>
              <div className="pricing-price">
                <span className="pricing-amount">{p.price}</span>
                <span className="pricing-period">{p.period}</span>
              </div>
              <ul className="pricing-features">
                {p.features.map((f) => (
                  <li key={f}>
                    <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round"><polyline points="20 6 9 17 4 12" /></svg>
                    {f}
                  </li>
                ))}
              </ul>
              <button
                className={p.popular ? 'btn-primary-glow' : 'btn-outline-glow'}
                onClick={() => navigate('/login')}
              >
                {p.cta}
              </button>
            </div>
          ))}
        </div>
      </div>
    </section>
  )
}
