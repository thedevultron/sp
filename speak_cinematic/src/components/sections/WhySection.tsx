export default function WhySection() {
  return (
    <section id="why" className="chapter" style={{ padding: '90px 24px' }}>
      <div style={{ maxWidth: 1280, margin: '0 auto', display: 'grid', gridTemplateColumns: 'repeat(auto-fit,minmax(300px,1fr))', gap: 40, alignItems: 'end' }}>
        <div className="chapter-head">
          <div className="eyebrow">Chapter III · Why Voxula exists</div>
          <h2 className="h-display" style={{ fontSize: 'clamp(36px, 5.4vw, 68px)', margin: '18px 0 12px' }}>
            <span className="mask-line"><span>Built because the</span></span>
            <span className="mask-line"><span style={{ color: '#8b93b0' }}>alternatives cost too much.</span></span>
          </h2>
        </div>
        <p style={{ color: '#aab3cc', lineHeight: 1.7, fontSize: 16 }}>
          Great voice tools either charge monthly or hog the CPU running local models.
          Voxula AI is an always-on voice copilot and sub-second dictation in one tray app
          that idles quietly until you call it. Bring a free key. That is the whole business model.
        </p>
      </div>
      <div style={{ maxWidth: 1280, margin: '40px auto 0', display: 'grid', gridTemplateColumns: 'repeat(auto-fit,minmax(280px,1fr))', gap: 18 }}>
        {[
          ['No subscriptions.', 'Voice should not cost monthly. Free tier included.'],
          ['Sips CPU.', 'No heavy local models. Cloud transcription, tray-idle footprint.'],
          ['Copilot + dictation.', 'A screen-seeing assistant and instant typer in one flow.'],
        ].map(([t, d]) => (
          <div key={t} className="rise" style={{ borderTop: '1px solid rgba(182,217,252,.16)', paddingTop: 22 }}>
            <div className="font-display" style={{ fontSize: 21, fontWeight: 600 }}>{t}</div>
            <div style={{ color: '#8b93b0', marginTop: 8, lineHeight: 1.6 }}>{d}</div>
          </div>
        ))}
      </div>
    </section>
  );
}
