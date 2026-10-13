import { useEffect, useRef, useState } from 'react';
import { X } from 'lucide-react';
import { CHAPTERS } from '../../site';

export default function TourOverlay({ index, onStop, onJump }: { index: number; onStop: () => void; onJump: (i: number) => void }) {
  const c = CHAPTERS[Math.min(index, CHAPTERS.length - 1)];
  return (
    <div style={{ position: 'fixed', left: 0, right: 0, bottom: 0, zIndex: 85, padding: '0 24px calc(7vh + 20px)', display: 'flex', justifyContent: 'center', pointerEvents: 'none' }}>
      <div className="glass" style={{ pointerEvents: 'auto', borderRadius: 18, padding: '14px 16px', display: 'flex', alignItems: 'center', gap: 16, maxWidth: 720, width: '100%' }}>
        <span className="font-mono2" style={{ fontSize: 10, letterSpacing: '0.3em', color: '#7a52f5', whiteSpace: 'nowrap' }}>
          {String(index + 1).padStart(2, '0')} / {String(CHAPTERS.length).padStart(2, '0')} · {c.label.toUpperCase()}
        </span>
        <span className="font-display" style={{ fontWeight: 600, whiteSpace: 'nowrap', overflow: 'hidden', textOverflow: 'ellipsis' }}>{c.title}</span>
        <span style={{ display: 'flex', gap: 6, marginLeft: 'auto' }}>
          {CHAPTERS.map((ch: { id: string; title: string }, i: number) => (
            <button key={ch.id} onClick={() => onJump(i)} aria-label={ch.title}
              style={{ width: i === index ? 26 : 8, height: 8, borderRadius: 99, border: 'none', cursor: 'pointer', background: i === index ? '#b6d9fc' : 'rgba(182,217,252,.25)', transition: 'all .4s' }} />
          ))}
        </span>
        <button onClick={onStop} aria-label="Stop tour" style={{ background: 'rgba(255,255,255,.06)', border: '1px solid rgba(182,217,252,.2)', color: '#fff', borderRadius: '50%', width: 32, height: 32, display: 'flex', alignItems: 'center', justifyContent: 'center', cursor: 'pointer' }}>
          <X size={15} />
        </button>
      </div>
    </div>
  );
}
