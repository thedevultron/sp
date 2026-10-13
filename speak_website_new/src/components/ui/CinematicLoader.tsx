import { useEffect, useState } from 'react';
import { motion, useReducedMotion } from 'motion/react';
import VoiceLines from './VoiceLines';
import { WaveLogo } from './Primitives';

/**
 * CinematicLoader — midnight booth intro.
 * Voice lines tune up like a mic check while a hairline progress bar
 * draws across. Exits with rise + de-blur. Skipped under reduced motion.
 */
export default function CinematicLoader({ onDone }: { onDone: () => void }) {
  const reduced = useReducedMotion();
  const [pct, setPct] = useState(0);

  useEffect(() => {
    if (reduced) {
      onDone();
      return;
    }
    const t0 = performance.now();
    const dur = 1700;
    let raf = 0;
    const tick = (t: number) => {
      const p = Math.min(1, (t - t0) / dur);
      // ease-out with a mic-check stutter in the first third
      const eased = p < 0.35 ? p * 0.55 + Math.sin(p * 40) * 0.008 : 0.19 + (p - 0.35) * 1.25;
      setPct(Math.round(Math.min(1, Math.max(0, eased)) * 100));
      if (p < 1) raf = requestAnimationFrame(tick);
      else window.setTimeout(onDone, 220);
    };
    raf = requestAnimationFrame(tick);
    return () => cancelAnimationFrame(raf);
  }, [onDone, reduced]);

  if (reduced) return null;

  return (
    <motion.div
      className="cine-loader"
      role="status"
      aria-label="Loading Voxula AI"
      initial={{ opacity: 1 }}
      exit={{ opacity: 0, filter: 'blur(10px)', scale: 1.04 }}
      transition={{ duration: 0.7, ease: [0.22, 1, 0.36, 1] }}
    >
      <motion.div
        className="cine-loader-inner"
        initial={{ opacity: 0, y: 24, filter: 'blur(8px)' }}
        animate={{ opacity: 1, y: 0, filter: 'blur(0px)' }}
        transition={{ duration: 0.8, ease: [0.22, 1, 0.36, 1] }}
      >
        <WaveLogo />
        <p className="cine-loader-brand">VOXULA AI</p>
        <VoiceLines bars={36} height={56} label="Tuning microphone" />
        <div className="cine-loader-track" aria-hidden="true">
          <i style={{ transform: `scaleX(${pct / 100})` }} />
        </div>
        <p className="cine-loader-meta">
          <span>MIC CHECK</span>
          <span>{String(pct).padStart(3, '0')}%</span>
        </p>
      </motion.div>
    </motion.div>
  );
}
