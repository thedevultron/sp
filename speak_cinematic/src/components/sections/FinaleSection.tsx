import { ArrowUpRight } from 'lucide-react';
import { useState } from 'react';
import { startDownload } from '../../lib/download';
import { APP_NAME, SITE_VERSION, GITHUB_REPO_URL, GEMINI_KEY_URL, INSTALLER_SIZE } from '../../site';

export default function FinaleSection() {
  const [done, setDone] = useState(false);
  const dl = () => { startDownload(); setDone(true); };
  return (
    <section id="finale" className="chapter finale" style={{ padding: '110px 24px 40px' }}>
      <div style={{ maxWidth: 1280, margin: '0 auto', textAlign: 'center', padding: '30px 0 60px' }}>
        <div className="eyebrow" style={{ justifyContent: 'center' }}>Finale · Say it. Consider it done.</div>
        <div className="h-display" style={{ fontSize: 'clamp(40px, 7vw, 92px)', marginTop: 16 }}>
          <span className="mask-line"><span>Dictate raw.</span></span>
          <span className="mask-line"><span>Say refine. Ship polished.</span></span>
        </div>
      </div>
      <div className="finale-card glass" style={{ maxWidth: 980, margin: '0 auto', borderRadius: 30, padding: 'clamp(32px,5vw,64px)', textAlign: 'center', position: 'relative', overflow: 'hidden' }}>
        <div style={{ position: 'absolute', inset: 0, background: 'radial-gradient(60% 50% at 50% 0%, rgba(102,58,243,.28), transparent 70%)', pointerEvents: 'none' }} />
        <div className="font-mono2" style={{ fontSize: 11, letterSpacing: '0.4em', color: '#b6d9fc' }}>100% FREE · ENTIRELY YOURS</div>
        <h3 className="font-display" style={{ fontSize: 'clamp(34px, 5vw, 58px)', margin: '14px 0', letterSpacing: '-0.03em' }}>Find your voice. Get into flow.</h3>
        <p style={{ color: '#aab3cc', maxWidth: 560, margin: '0 auto', lineHeight: 1.65 }}>
          Less between you and your next great idea. {SITE_VERSION} · Native x64 · Windows 10/11 · {INSTALLER_SIZE} · Free forever.
          Unsigned build — if Windows warns, click More info then Run anyway.
        </p>
        <div style={{ display: 'flex', gap: 14, justifyContent: 'center', flexWrap: 'wrap', marginTop: 30, position: 'relative' }}>
          <button className="btn-primary magnetic" onClick={dl}>Download {APP_NAME} for Windows<ArrowUpRight size={17} /></button>
          <a className="btn-ghost magnetic" href={GEMINI_KEY_URL} target="_blank" rel="noreferrer">Get a free Gemini key</a>
        </div>
        {done && <div className="font-mono2" style={{ marginTop: 18, fontSize: 12, color: '#3ddc84' }}>THANK YOU — CHECK YOUR DOWNLOADS · RUN → PASTE KEY → PRESS CTRL+SPACE</div>}
        <div className="font-mono2" style={{ marginTop: 22, fontSize: 11, color: '#69718e', letterSpacing: '0.15em' }}>
          NO SUBSCRIPTION · FREE KEY SUPPORTED · <a href={GITHUB_REPO_URL} target="_blank" rel="noreferrer" style={{ color: '#b6d9fc' }}>GITHUB</a>
        </div>
      </div>
      <footer style={{ maxWidth: 1280, margin: '70px auto 0', borderTop: '1px solid rgba(182,217,252,.1)', paddingTop: 26, display: 'flex', gap: 18, flexWrap: 'wrap', justifyContent: 'space-between', color: '#69718e', fontSize: 13 }}>
        <span>{APP_NAME} by Amir Bagawan · © 2026 · Built for speed, privacy, and flow.</span>
        <span className="font-mono2" style={{ fontSize: 11 }}>DIRECTX 11+ · WIN 10 19041+ / WIN 11 64-BIT · ALL SYSTEMS IN FLOW</span>
      </footer>
    </section>
  );
}
