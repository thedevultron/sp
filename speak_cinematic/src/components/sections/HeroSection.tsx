import { useRef } from 'react';
import { ArrowDown, ArrowUpRight, Play } from 'lucide-react';
import WebGPUHero, { VoiceBars } from '../cinematic/WebGPUHero';
import { startDownload } from '../../lib/download';
import { APP_NAME } from '../../site';

export default function HeroSection({ heroScroll, onTour }: { heroScroll: React.RefObject<number>; onTour: () => void }) {
  const ref = useRef<HTMLElement | null>(null);
  return (
    <section id="overview" className="hero" ref={ref} style={{ position: 'relative', minHeight: '108vh', display: 'flex', flexDirection: 'column', justifyContent: 'flex-end', overflow: 'clip' }}>
      <div style={{ position: 'absolute', inset: 0 }}>
        <WebGPUHero scrollRef={heroScroll} />
      </div>
      <div style={{ position: 'relative', zIndex: 2, maxWidth: 1280, margin: '0 auto', padding: '150px 24px 40px', width: '100%' }}>
        <div className="hero-copy">
          <div className="eyebrow" style={{ marginBottom: 22 }}>VOXULA AI {`V2.1`} · NATIVE WINDOWS</div>
          <h1 className="h-display" style={{ fontSize: 'clamp(56px, 10.5vw, 148px)', margin: 0 }}>
            <span className="mask-line"><span>Your Voice.</span></span>
            <span className="mask-line"><span style={{ color: 'transparent', WebkitTextStroke: '1.5px rgba(214,228,250,.85)' }}>Everywhere.</span></span>
          </h1>
          <p style={{ marginTop: 22, fontSize: 'clamp(16px, 2.2vw, 21px)', color: '#b9c1d9', maxWidth: 620, lineHeight: 1.55 }}>
            Press <b style={{ color: '#fff' }}>Ctrl + Space</b> to type into any app. Sub-second, private, free.
            Powered by Gemini Live. Your keys never leave this machine.
          </p>
          <div style={{ display: 'flex', gap: 14, flexWrap: 'wrap', marginTop: 30 }}>
            <button className="btn-primary magnetic" onClick={startDownload}>
              Download for Windows · Free<ArrowUpRight size={17} />
            </button>
            <button className="btn-ghost magnetic" onClick={onTour}>
              <Play size={16} />Watch cinematic tour
            </button>
          </div>
          <div style={{ display: 'flex', gap: 26, flexWrap: 'wrap', marginTop: 30 }} className="font-mono2">
            {['142MS TO CARET', '99.4% ACCURACY', '0 SERVERS IN PATH'].map((s) => (
              <span key={s} style={{ fontSize: 11, letterSpacing: '0.22em', color: '#8b93b0' }}>{s}</span>
            ))}
          </div>
        </div>

        <div className="hero-capsule glass" style={{ marginTop: 44, borderRadius: 22, padding: '20px 22px', display: 'flex', alignItems: 'center', gap: 20, flexWrap: 'wrap' }}>
          <span style={{ width: 10, height: 10, borderRadius: '50%', background: '#3ddc84', boxShadow: '0 0 16px #3ddc84' }} />
          <div>
            <div className="font-display" style={{ fontWeight: 600 }}>{APP_NAME} · Listening</div>
            <div className="font-mono2" style={{ fontSize: 11, color: '#8b93b0', letterSpacing: '0.18em' }}>GEMINI LIVE WS · CONNECTED · 142MS</div>
          </div>
          <div style={{ marginLeft: 'auto' }}><VoiceBars count={28} /></div>
          <div className="font-mono2" style={{ fontSize: 11, color: '#8b93b0' }}>hold <span className="keycap">Ctrl</span> + <span className="keycap">Space</span> — release to commit</div>
        </div>

        <div className="marquee" style={{ marginTop: 34, borderTop: '1px solid rgba(182,217,252,.1)', paddingTop: 18 }}>
          <div className="marquee-track font-mono2" style={{ fontSize: 12, letterSpacing: '0.3em', color: '#69718e' }}>
            {['VS CODE', 'SLACK', 'NOTION', 'WORD', 'FIGMA', 'CHROME', 'TERMINAL', 'DISCORD', 'OBSIDIAN', 'GMAIL', 'VS CODE', 'SLACK', 'NOTION', 'WORD', 'FIGMA', 'CHROME', 'TERMINAL', 'DISCORD', 'OBSIDIAN', 'GMAIL'].map((a, i) => (
              <span key={i}>{a} ·</span>
            ))}
          </div>
          <div style={{ display: 'flex', alignItems: 'center', gap: 10, marginTop: 16, color: '#69718e', fontSize: 12 }}>
            <ArrowDown size={14} /> Scroll — the film begins
          </div>
        </div>
      </div>
    </section>
  );
}
