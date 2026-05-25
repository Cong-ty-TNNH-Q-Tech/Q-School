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
              <li><a href="#">Trung tâm trợ giúp</a></li>
              <li><a href="#">Tài liệu API</a></li>
              <li><a href="#">Liên hệ</a></li>
            </ul>
          </div>

          <div className="footer-col">
            <h4>Pháp lý</h4>
            <ul>
              <li><a href="#">Điều khoản sử dụng</a></li>
              <li><a href="#">Chính sách bảo mật</a></li>
            </ul>
          </div>
        </div>

        <div className="footer-bottom">
          <span>© 2026 Q-Tech. All rights reserved.</span>
          <span>Made with ♥ in Vietnam</span>
        </div>
      </div>
    </footer>
  )
}
