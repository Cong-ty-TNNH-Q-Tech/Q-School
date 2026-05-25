import { useState, useEffect } from 'react'
import { useNavigate } from 'react-router-dom'
import { HeroSection } from './sections/HeroSection'
import { FeaturesSection } from './sections/FeaturesSection'
import { StatsSection } from './sections/StatsSection'
import { AIShowcaseSection } from './sections/AIShowcaseSection'
import { PricingSection } from './sections/PricingSection'
import { TestimonialsSection } from './sections/TestimonialsSection'
import { CTASection } from './sections/CTASection'
import { FooterSection } from './sections/FooterSection'
import './landing.css'

export default function LandingPage() {
  const navigate = useNavigate()
  const [scrolled, setScrolled] = useState(false)

  useEffect(() => {
    const onScroll = () => setScrolled(window.scrollY > 40)
    window.addEventListener('scroll', onScroll)
    return () => window.removeEventListener('scroll', onScroll)
  }, [])

  return (
    <div className="landing-root">
      {/* ── Navbar ── */}
      <nav className={`landing-nav ${scrolled ? 'nav-scrolled' : ''}`}>
        <div className="nav-inner">
          <div className="nav-brand">
            <div className="brand-icon">Q</div>
            <span className="brand-text">Q-School <span className="brand-ai">AI</span></span>
          </div>
          <div className="nav-links">
            <a href="#features">Tính năng</a>
            <a href="#pricing">Bảng giá</a>
            <a href="#testimonials">Đánh giá</a>
          </div>
          <div className="nav-actions">
            <button className="btn-ghost" onClick={() => navigate('/login')}>Đăng nhập</button>
            <button className="btn-primary-glow" onClick={() => navigate('/login')}>
              Dùng thử miễn phí
            </button>
          </div>
        </div>
      </nav>

      {/* ── Page Sections ── */}
      <HeroSection />
      <StatsSection />
      <FeaturesSection />
      <AIShowcaseSection />
      <PricingSection />
      <TestimonialsSection />
      <CTASection />
      <FooterSection />
    </div>
  )
}
