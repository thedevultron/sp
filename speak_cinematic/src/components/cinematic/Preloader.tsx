import { useEffect, useState } from 'react';
import { VoiceBars } from './WebGPUHero';
import { APP_NAME } from '../../site';

export default function Preloader({ onDone }: { onDone: () => void }) {
  const [pct, setPct] = useState(0);
  useEffect(() => {
    let v = 0;
    const id = window.setInterval(() => {
      v += Math.random() * 16 + 6;
      if (v >= 100) { v = 100; window.clearInterval(id); window.setTimeout(onDone, 450); }
      setPct(Math.floor(v));
    }, 110);
    return () => window.clearInterval(id);
  }, [onDone]);

  return (
    <div style={{ position: 'fixed', inset: 0, zIndex: 100, background: '#05060f', display: 'flex', alignItems: 'center', justifyContent: 'center', flexDirection: 'column', gap: 26 }}>
      <div className="font-mono2" style={{ fontSize: 11, letterSpacing: '0.5em', color: '#8b93b0' }}>{APP_NAME} · MIC CHECK</div>
      <VoiceBars count={42} />
      <div className="font-display" style={{ fontSize: 'clamp(56px, 10vw, 120px)', fontWeight: 700, letterSpacing: '-0.05em', lineHeight: 1 }}>
        {String(pct).padStart(3, '0')}<span style={{ fontSize: '0.35em', color: '#8b93b0' }}>%</span>
      </div>
      <div style={{ width: 220, height: 2, background: 'rgba(182,217,252,0.12)', borderRadius: 2, overflow: 'hidden' }}>
        <div style={{ width: `${pct}%`, height: '100%', background: 'linear-gradient(90deg,#663af3,#b6d9fc)', transition: 'width .2s' }} />
      </div>
      <div className="font-mono2" style={{ fontSize: 11, letterSpacing: '0.25em', color: '#5c6584' }}>
        {pct < 40 ? 'BINDING CTRL + SPACE' : pct < 80 ? 'LINKING GEMINI LIVE' : 'WARMING VOICE PIPELINE'}
      </div>
    </div>
  );
}
