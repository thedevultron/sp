import { Keyboard, Eye, Layers, Gauge, Wand2, Sparkles } from 'lucide-react';

const FEATURES = [
  { icon: Keyboard, k: 'CTRL + SPACE', t: 'Instant Dictation', d: 'Live dictation streamed at 16 kHz and typed at your cursor — any app, sub-second, multilingual auto-detect.' },
  { icon: Eye, k: 'WIN + SHIFT', t: 'Multimodal Companion', d: 'An AI that sees — and acts. Optional screen share plus voice desktop control, narrated step by step.' },
  { icon: Layers, k: 'ALWAYS CONNECTED', t: 'Multi-Key Engine', d: 'Primary + backup keys in Windows Credential Manager. On rate limits Voxula rotates keys and reconnects.' },
  { icon: Gauge, k: 'CTRL + WIN', t: 'Smart Context', d: 'Live token bar: green 0–60%, orange 61–85%, red 86–100%. Hover for exact tokens. Purge anytime.' },
  { icon: Wand2, k: 'SETTINGS → REFINE', t: 'Custom Actions', d: 'Teach it your own words. Up to 3 custom refine actions — say "summarize" and the whole session obeys.' },
  { icon: Sparkles, k: 'SAY "REFINE"', t: 'Refine & Polish', d: 'Say refine, polish, or elaborate and the whole session is deleted and retyped, cleaner. Self-correction aware.' },
];

export default function FeaturesSection() {
  return (
    <section id="features" className="chapter" style={{ padding: '90px 24px' }}>
      <div className="chapter-head" style={{ maxWidth: 1280, margin: '0 auto' }}>
        <div className="eyebrow">Chapter II · Features</div>
        <h2 className="h-display" style={{ fontSize: 'clamp(38px, 6vw, 76px)', margin: '18px 0 12px' }}>
          <span className="mask-line"><span>Quietly powerful.</span></span>
        </h2>
        <p style={{ color: '#aab3cc', maxWidth: 600, lineHeight: 1.6 }}>Six capabilities. One shortcut. Say refine, polish, or elaborate — the session rewrites itself.</p>
      </div>
      <div style={{ maxWidth: 1280, margin: '46px auto 0', display: 'grid', gridTemplateColumns: 'repeat(auto-fit,minmax(320px,1fr))', gap: 18 }}>
        {FEATURES.map((f) => (
          <div key={f.t} className="feature-card rise glass" style={{ padding: 30, minHeight: 250 }}>
            <div className="spotlight" />
            <f.icon size={22} color="#b6d9fc" />
            <div className="font-mono2" style={{ fontSize: 10.5, letterSpacing: '0.28em', color: '#7a52f5', marginTop: 18 }}>{f.k}</div>
            <div className="font-display" style={{ fontSize: 25, fontWeight: 600, margin: '10px 0' }}>{f.t}</div>
            <p style={{ color: '#aab3cc', fontSize: 14.5, lineHeight: 1.65 }}>{f.d}</p>
          </div>
        ))}
      </div>
    </section>
  );
}
