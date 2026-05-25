import { useEffect, useRef } from 'react'
import { useNavigate } from 'react-router-dom'

export function HeroSection() {
  const navigate = useNavigate()
  const canvasRef = useRef<HTMLCanvasElement>(null)

  /* ── Animated particle network background ── */
  useEffect(() => {
    const cvs = canvasRef.current
    if (!cvs) return
    const ctx = cvs.getContext('2d')!
    let raf: number
    let w = (cvs.width = cvs.offsetWidth)
    let h = (cvs.height = cvs.offsetHeight)

    const particles: { x: number; y: number; vx: number; vy: number; r: number }[] = []
    const COUNT = 60
    for (let i = 0; i < COUNT; i++) {
      particles.push({
        x: Math.random() * w,
        y: Math.random() * h,
        vx: (Math.random() - 0.5) * 0.4,
        vy: (Math.random() - 0.5) * 0.4,
        r: Math.random() * 2 + 1,
      })
    }

    function draw() {
      ctx.clearRect(0, 0, w, h)
      for (const p of particles) {
        p.x += p.vx
        p.y += p.vy
        if (p.x < 0 || p.x > w) p.vx *= -1
        if (p.y < 0 || p.y > h) p.vy *= -1
        ctx.beginPath()
        ctx.arc(p.x, p.y, p.r, 0, Math.PI * 2)
        ctx.fillStyle = 'rgba(139,92,246,0.5)'
        ctx.fill()
      }
      for (let i = 0; i < particles.length; i++) {
        for (let j = i + 1; j < particles.length; j++) {
          const dx = particles[i].x - particles[j].x
          const dy = particles[i].y - particles[j].y
          const dist = Math.sqrt(dx * dx + dy * dy)
          if (dist < 150) {
            ctx.beginPath()
            ctx.moveTo(particles[i].x, particles[i].y)
            ctx.lineTo(particles[j].x, particles[j].y)
            ctx.strokeStyle = `rgba(139,92,246,${0.15 * (1 - dist / 150)})`
            ctx.lineWidth = 0.6
            ctx.stroke()
          }
        }
      }
      raf = requestAnimationFrame(draw)
    }
    draw()

    const onResize = () => {
      w = cvs.width = cvs.offsetWidth
      h = cvs.height = cvs.offsetHeight
    }
    window.addEventListener('resize', onResize)
    return () => {
      cancelAnimationFrame(raf)
      window.removeEventListener('resize', onResize)
    }
  }, [])

  return (
    <section className="hero-section" id="hero">
      <canvas ref={canvasRef} className="hero-canvas" />

      {/* Decorative blobs */}
      <div className="hero-blob hero-blob-1" />
      <div className="hero-blob hero-blob-2" />
      <div className="hero-blob hero-blob-3" />

      <div className="hero-content">
        <div className="hero-badge">
          <span className="badge-dot" />
          Nền tảng EdTech #1 tích hợp AI
        </div>

        <h1 className="hero-title">
          Giáo dục <span className="text-gradient">Thông minh</span>
          <br />
          Dẫn lối <span className="text-gradient-alt">Tương lai</span>
        </h1>

        <p className="hero-subtitle">
          Q-School AI kết hợp trí tuệ nhân tạo với hệ thống LMS hiện đại, giúp giáo viên
          tiết kiệm 70% thời gian soạn giáo án và học sinh cá nhân hóa lộ trình học tập.
        </p>

        <div className="hero-actions">
          <button className="btn-primary-glow btn-lg" onClick={() => navigate('/login')}>
            <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><polygon points="13 2 3 14 12 14 11 22 21 10 12 10 13 2" /></svg>
            Bắt đầu miễn phí
          </button>
          <button className="btn-outline-glow btn-lg" onClick={() => { document.getElementById('features')?.scrollIntoView({ behavior: 'smooth' }) }}>
            Khám phá tính năng
            <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><path d="m6 9 6 6 6-6" /></svg>
          </button>
        </div>

        {/* Floating UI mockup */}
        <div className="hero-visual">
          <div className="visual-card visual-card-main">
            <div className="vc-header">
              <div className="vc-dots"><span /><span /><span /></div>
              <span className="vc-title">AI Workspace</span>
            </div>
            <div className="vc-body">
              <div className="vc-chat-bubble vc-user">Tạo giáo án Toán lớp 10 chương Hàm số</div>
              <div className="vc-chat-bubble vc-ai">
                <span className="vc-ai-icon" aria-hidden="true">
                  <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                    <path d="M12 3l1.8 5.2L19 10l-5.2 1.8L12 17l-1.8-5.2L5 10l5.2-1.8L12 3z" />
                  </svg>
                </span>
                <div>
                  <div className="vc-typing">Đang tạo giáo án chi tiết...</div>
                  <div className="vc-progress"><div className="vc-progress-bar" /></div>
                </div>
              </div>
            </div>
          </div>
          <div className="visual-card visual-card-float visual-float-1">
            <div className="vf-icon vf-icon-quiz">
              <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2"><path d="M12 22c5.523 0 10-4.477 10-10S17.523 2 12 2 2 6.477 2 12s4.477 10 10 10z"/><path d="M9.09 9a3 3 0 0 1 5.83 1c0 2-3 3-3 3"/><line x1="12" y1="17" x2="12.01" y2="17"/></svg>
            </div>
            <span>Quiz thông minh</span>
          </div>
          <div className="visual-card visual-card-float visual-float-2">
            <div className="vf-icon vf-icon-flash">
              <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2"><rect x="2" y="3" width="20" height="14" rx="2"/><line x1="8" y1="21" x2="16" y2="21"/><line x1="12" y1="17" x2="12" y2="21"/></svg>
            </div>
            <span>Flashcard AI</span>
          </div>
          <div className="visual-card visual-card-float visual-float-3">
            <div className="vf-icon vf-icon-chart">
              <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2"><line x1="18" y1="20" x2="18" y2="10"/><line x1="12" y1="20" x2="12" y2="4"/><line x1="6" y1="20" x2="6" y2="14"/></svg>
            </div>
            <span>Analytics</span>
          </div>
        </div>
      </div>
    </section>
  )
}
