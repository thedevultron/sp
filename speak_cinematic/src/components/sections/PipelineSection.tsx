const STEPS = [
  { n: '01', t: 'Connect', d: 'Bring a free Gemini key. Voxula auto-detects GEMINI_API_KEY or your saved vault key. Keys stay on your device — DPAPI sealed, never uploaded.' },
  { n: '02', t: 'Summon', d: 'Press Ctrl + Space. Voxula appears over your active window with a live transcript — without stealing focus.' },
  { n: '03', t: 'Flow', d: 'Speak at the speed of thought. Words stream to your cursor sub-second. Say "refine" and the session rewrites itself in place.' },
];

export default function PipelineSection() {
  return (
    <section id="how-it-works" className="chapter" style={{ position: 'relative', padding: '140px 24px 60px' }}>
      <div className="chapter-head" style={{ maxWidth: 1280, margin: '0 auto' }}>
        <div className="eyebrow">Chapter I · How it works</div>
        <h2 className="h-display" style={{ fontSize: 'clamp(38px, 6vw, 76px)', margin: '18px 0 12px' }}>
          <span className="mask-line"><span>Instant execution.</span></span>
          <span className="mask-line"><span style={{ color: '#8b93b0' }}>Zero friction.</span></span>
        </h2>
        <p style={{ color: '#aab3cc', maxWidth: 560, lineHeight: 1.6 }}>From a thought to the page, in less than a second. Three moves take you from install to dictation.</p>
      </div>
      <div style={{ maxWidth: 1280, margin: '48px auto 0', display: 'grid', gridTemplateColumns: 'repeat(auto-fit,minmax(280px,1fr))', gap: 18 }}>
        {STEPS.map((s) => (
          <div key={s.n} className="rise glass" style={{ borderRadius: 22, padding: 30, position: 'relative', overflow: 'hidden' }}>
            <div className="font-mono2" style={{ fontSize: 12, letterSpacing: '0.3em', color: '#663af3' }}>{s.n}</div>
            <div className="font-display" style={{ fontSize: 30, fontWeight: 600, margin: '12px 0' }}>{s.t}</div>
            <p style={{ color: '#aab3cc', lineHeight: 1.65, fontSize: 15 }}>{s.d}</p>
            <div style={{ position: 'absolute', bottom: 0, left: 0, right: 0, height: 2, background: 'linear-gradient(90deg,#663af3,transparent)' }} />
          </div>
        ))}
      </div>
    </section>
  );
}
