import { Lock } from 'lucide-react';

const HOTKEYS = [
  ['Ctrl', 'Space', 'Global dictation', 'Your voice, typed wherever your cursor is.'],
  ['Win', 'Shift', 'Screen companion', 'Voice + live screen, together.'],
  ['Ctrl', 'Win', 'Fresh start', 'Purge transcript and token counter.'],
  ['Esc', '', 'Back to focus', 'Clear the canvas and dismiss to tray.'],
];

export default function PrivacySection() {
  return (
    <section id="privacy" className="chapter" style={{ padding: '90px 24px' }}>
      <div style={{ maxWidth: 1280, margin: '0 auto', display: 'grid', gridTemplateColumns: 'repeat(auto-fit,minmax(320px,1fr))', gap: 24 }}>
        <div className="chapter-head glass rise" style={{ borderRadius: 26, padding: 40, textAlign: 'center' }}>
          <div style={{ width: 72, height: 72, borderRadius: '50%', margin: '0 auto', display: 'flex', alignItems: 'center', justifyContent: 'center', background: 'radial-gradient(circle at 35% 30%, #7a52f5, #1a1440)', boxShadow: '0 0 60px rgba(102,58,243,.5)' }}>
            <Lock color="#fff" size={26} />
          </div>
          <div className="font-mono2" style={{ fontSize: 11, letterSpacing: '0.3em', color: '#b6d9fc', marginTop: 22 }}>ON-DEVICE ENCRYPTION</div>
          <div className="font-display" style={{ fontSize: 26, fontWeight: 600, marginTop: 10 }}>Never our data.<br />Always your voice.</div>
          <div style={{ color: '#8b93b0', marginTop: 14, fontSize: 14, lineHeight: 1.6 }}>
            Local DPAPI encryption. Zero telemetry. No compromises.<br />
            Triggers: refine · polish · elaborate.
          </div>
        </div>
        <div>
          <div className="eyebrow">Chapter IV · Privacy + muscle memory</div>
          <h2 className="h-display" style={{ fontSize: 'clamp(34px, 5vw, 60px)', margin: '16px 0 20px' }}>
            <span className="mask-line"><span>Your words are yours.</span></span>
          </h2>
          {HOTKEYS.map(([a, b, t, d]) => (
            <div key={t} className="rise" style={{ display: 'flex', gap: 18, alignItems: 'center', padding: '18px 0', borderTop: '1px solid rgba(182,217,252,.1)' }}>
              <span style={{ display: 'flex', gap: 6 }}>
                <span className="keycap">{a}</span>
                {b ? <span className="keycap">{b}</span> : null}
              </span>
              <span><b>{t}</b><br /><span style={{ color: '#8b93b0', fontSize: 14 }}>{d}</span></span>
            </div>
          ))}
          <div style={{ display: 'grid', gap: 10, marginTop: 18, color: '#aab3cc', fontSize: 14, lineHeight: 1.6 }}>
            <div><b style={{ color: '#fff' }}>Your keys. Under lock.</b> Credential Manager encrypts API keys locally with DPAPI.</div>
            <div><b style={{ color: '#fff' }}>Direct line. No middleman.</b> Encrypted connection straight to the voice service. No tracking.</div>
            <div><b style={{ color: '#fff' }}>Almost invisible.</b> Idles quietly in your tray until inspiration strikes.</div>
          </div>
        </div>
      </div>
    </section>
  );
}
