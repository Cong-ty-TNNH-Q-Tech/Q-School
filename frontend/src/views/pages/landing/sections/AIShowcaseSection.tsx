export function AIShowcaseSection() {
  return (
    <section className="showcase-section">
      <div className="section-container">
        <div className="showcase-grid">
          {/* Left — text */}
          <div className="showcase-text">
            <span className="section-badge">AI Engine</span>
            <h2 className="section-title">
              Được hỗ trợ bởi <span className="text-gradient">vLLM nội bộ</span>
            </h2>
            <p className="section-desc" style={{ textAlign: 'left' }}>
              Không phụ thuộc dịch vụ bên ngoài. Q-School vận hành mô hình ngôn ngữ lớn (LLM) trên
              máy chủ riêng, đảm bảo tốc độ phản hồi nhanh, bảo mật dữ liệu tuyệt đối và chi phí
              tối ưu.
            </p>

            <ul className="showcase-list">
              {[
                { title: 'Self-hosted vLLM', desc: 'Kiểm soát toàn bộ hạ tầng AI' },
                { title: 'Streaming SSE', desc: 'Phản hồi real-time, không lag' },
                { title: 'RAG Pipeline', desc: 'Tìm kiếm ngữ nghĩa với pgvector HNSW' },
                { title: 'Data Privacy', desc: 'Dữ liệu không rời khỏi hệ thống' },
              ].map((item) => (
                <li key={item.title} className="showcase-item">
                  <div className="showcase-check">
                    <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="3" strokeLinecap="round" strokeLinejoin="round"><polyline points="20 6 9 17 4 12" /></svg>
                  </div>
                  <div>
                    <strong>{item.title}</strong>
                    <span>{item.desc}</span>
                  </div>
                </li>
              ))}
            </ul>
          </div>

          {/* Right — terminal mockup */}
          <div className="showcase-visual">
            <div className="terminal-card">
              <div className="terminal-header">
                <div className="vc-dots"><span /><span /><span /></div>
                <span className="terminal-title">vLLM Server — Running</span>
              </div>
              <div className="terminal-body">
                <code className="t-line"><span className="t-green">$</span> vllm serve Qwen2.5-72B-Instruct</code>
                <code className="t-line t-dim">INFO: Loading model weights...</code>
                <code className="t-line t-dim">INFO: Model loaded in 12.4s</code>
                <code className="t-line"><span className="t-cyan">►</span> Server ready on <span className="t-green">:8000</span></code>
                <code className="t-line t-dim">INFO: Received request chat/completions</code>
                <code className="t-line"><span className="t-purple">✦</span> Generating lesson plan... <span className="t-blink">█</span></code>
                <code className="t-line t-dim">INFO: 1,247 tokens in 2.1s (594 tok/s)</code>
                <code className="t-line"><span className="t-green">✓</span> Response streamed successfully</code>
              </div>
            </div>
          </div>
        </div>
      </div>
    </section>
  )
}
