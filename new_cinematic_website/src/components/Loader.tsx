import { useEffect, useState } from "react";
import { motion } from "framer-motion";
import { WaveLogo } from "./ui";

export function Loader({ onDone }: { onDone: () => void }) {
  const [pct, setPct] = useState(0);

  useEffect(() => {
    const start = performance.now();
    const dur = 1900;
    let raf = 0;
    const tick = (t: number) => {
      const p = Math.min(1, (t - start) / dur);
      // mic-check stutter in first third
      const eased = p < 0.33 ? Math.floor(p * 12) / 12 * 0.5 + p * 0.1 : 0.2 + (p - 0.33) * 1.2;
      setPct(Math.min(100, Math.round(Math.min(1, eased) * 100)));
      if (p < 1) raf = requestAnimationFrame(tick);
      else {
        setPct(100);
        setTimeout(onDone, 250);
      }
    };
    raf = requestAnimationFrame(tick);
    return () => cancelAnimationFrame(raf);
  }, [onDone]);

  return (
    <motion.div
      className="fixed inset-0 z-[100] flex flex-col items-center justify-center bg-ink"
      exit={{ y: "-100%", transition: { duration: 1, ease: [0.76, 0, 0.24, 1] } }}
    >
      <div className="absolute left-1/2 top-1/2 h-[520px] w-[520px] -translate-x-1/2 -translate-y-1/2 rounded-full bg-clay/10 blur-[110px]" />
      <motion.div
        initial={{ opacity: 0, scale: 0.8 }}
        animate={{ opacity: 1, scale: 1 }}
        transition={{ duration: 0.8, ease: [0.16, 1, 0.3, 1] }}
        className="relative flex flex-col items-center"
      >
        <WaveLogo size={64} />
        <div className="mt-5 font-mono text-xs tracking-[0.5em] text-cream">VOXULA AI</div>
        <div className="mt-10 flex h-12 items-center gap-[3px]">
          {Array.from({ length: 36 }).map((_, i) => {
            const on = i / 36 <= pct / 100;
            return (
              <span
                key={i}
                className="w-[3px] rounded-full transition-colors duration-300"
                style={{
                  height: `${25 + 75 * Math.abs(Math.sin(i * 0.55 + pct * 0.08))}%`,
                  background: on ? "#4c8dff" : "rgba(208,214,224,0.14)",
                }}
              />
            );
          })}
        </div>
        <div className="mt-8 h-px w-64 overflow-hidden bg-white/10">
          <div className="h-full bg-clay transition-[width] duration-150" style={{ width: `${pct}%` }} />
        </div>
        <div className="mt-4 font-mono text-[10px] tracking-[0.35em] text-mute">
          MIC CHECK {String(pct).padStart(3, "0")}%
        </div>
      </motion.div>
    </motion.div>
  );
}
