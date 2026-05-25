const testimonials = [
  {
    name: 'Nguyễn Thị Hương',
    role: 'Giáo viên Toán — THPT Chuyên Hà Nội',
    avatar: 'NH',
    text: 'Q-School AI giúp tôi tiết kiệm hơn 3 tiếng mỗi ngày trong việc soạn giáo án. AI tạo nội dung chất lượng cao và tôi chỉ cần chỉnh sửa nhẹ.',
    rating: 5,
  },
  {
    name: 'Trần Minh Đức',
    role: 'Phó Hiệu trưởng — THCS Nguyễn Du',
    avatar: 'TD',
    text: 'Hệ thống quản lý lớp học và phân tích học tập cho chúng tôi cái nhìn toàn diện về tiến độ từng học sinh. Đặc biệt tính năng IEP rất hữu ích.',
    rating: 5,
  },
  {
    name: 'Phạm Quỳnh Anh',
    role: 'Học sinh lớp 12 — THPT Chu Văn An',
    avatar: 'PA',
    text: 'Flashcard và Quiz AI giúp mình ôn thi hiệu quả gấp đôi. Mình thích tính năng phân tích điểm yếu để biết cần tập trung vào phần nào.',
    rating: 5,
  },
]

export function TestimonialsSection() {
  return (
    <section className="testimonials-section" id="testimonials">
      <div className="section-container">
        <div className="section-header">
          <span className="section-badge">Đánh giá</span>
          <h2 className="section-title">
            Được tin dùng bởi <span className="text-gradient">hàng ngàn người</span>
          </h2>
        </div>

        <div className="testimonials-grid">
          {testimonials.map((t) => (
            <div className="testimonial-card" key={t.name}>
              <div className="testimonial-stars">
                {Array.from({ length: t.rating }).map((_, i) => (
                  <svg key={i} width="16" height="16" viewBox="0 0 24 24" fill="currentColor"><polygon points="12 2 15.09 8.26 22 9.27 17 14.14 18.18 21.02 12 17.77 5.82 21.02 7 14.14 2 9.27 8.91 8.26 12 2" /></svg>
                ))}
              </div>
              <p className="testimonial-text">"{t.text}"</p>
              <div className="testimonial-author">
                <div className="testimonial-avatar">{t.avatar}</div>
                <div>
                  <strong>{t.name}</strong>
                  <span>{t.role}</span>
                </div>
              </div>
            </div>
          ))}
        </div>
      </div>
    </section>
  )
}
