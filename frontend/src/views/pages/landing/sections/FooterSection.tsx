export function FooterSection() {
  return (
    <footer className="footer-section">
      <div className="section-container">
        <div className="footer-grid">
          <div className="footer-brand">
            <div className="nav-brand">
              <div className="brand-icon">Q</div>
              <span className="brand-text">Q-School <span className="brand-ai">AI</span></span>
            </div>
            <p className="footer-tagline">
              Nền tảng Giáo dục Thông minh tích hợp AI, giúp nâng cao chất lượng dạy và học
              cho giáo viên và học sinh Việt Nam.
            </p>
          </div>

          <div className="footer-col">
            <h4>Sản phẩm</h4>
            <ul>
              <li><a href="#features">Tính năng</a></li>
              <li><a href="#pricing">Bảng giá</a></li>
              <li><a href="#testimonials">Đánh giá</a></li>
            </ul>
          </div>

          <div className="footer-col">
            <h4>Hỗ trợ</h4>
            <ul>
              <li><span>Trung tâm trợ giúp</span></li>
              <li><span>Tài liệu API</span></li>
              <li><span>Liên hệ</span></li>
            </ul>
          </div>

          <div className="footer-col">
            <h4>Pháp lý</h4>
            <ul>
              <li><span>Điều khoản sử dụng</span></li>
              <li><span>Chính sách bảo mật</span></li>
            </ul>
          </div>
        </div>

        <div className="footer-bottom">
          <span>© 2026 Q-Tech. All rights reserved.</span>
          <span>
            Made with{' '}
            <svg
              aria-label="love"
              viewBox="0 0 24 24"
              width="16"
              height="16"
              fill="currentColor"
              role="img"
            >
              <path d="M12 21.35l-1.45-1.32C5.4 15.36 2 12.28 2 8.5 2 5.42 4.42 3 7.5 3c1.74 0 3.41.81 4.5 2.09C13.09 3.81 14.76 3 16.5 3 19.58 3 22 5.42 22 8.5c0 3.78-3.4 6.86-8.55 11.54L12 21.35z" />
            </svg>{' '}
            in Vietnam
          </span>
        </div>
      </div>
    </footer>
  )
}
