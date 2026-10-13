import { useEffect, useRef } from 'react';

// Bulletproof scroll-triggered number ticker. Trigger uses a scroll
// listener + getBoundingClientRect (never IntersectionObserver threshold
// edge cases), animation is a plain rAF ease-out loop writing textContent.
// Deterministic in every browser, StrictMode-safe.
export default function TickerNumber({ to, from = 0 }: {
  to: number; from?: number;
}) {
  const ref = useRef<HTMLSpanElement>(null);
  const played = useRef(false);
  useEffect(() => {
    const el = ref.current;
    if (!el) return;
    let raf = 0;
    let dead = false;
    const fmt = (v: number) => String(Math.round(v));
    const reduce = window.matchMedia('(prefers-reduced-motion: reduce)').matches;
    const animate = (startVal: number, goal: number) => {
      if (reduce || startVal === goal) {
        el.textContent = fmt(goal);
        return;
      }
      const t0 = performance.now();
      const dur = 900;
      const tick = (t: number) => {
        if (dead) return;
        const p = Math.min(1, (t - t0) / dur);
        const eased = 1 - Math.pow(1 - p, 3);
        el.textContent = fmt(startVal + (goal - startVal) * eased);
        if (p < 1) raf = requestAnimationFrame(tick);
      };
      raf = requestAnimationFrame(tick);
    };
    const inView = () => {
      const r = el.getBoundingClientRect();
      return r.top < window.innerHeight * 0.92 && r.bottom > 0;
    };
    if (played.current) {
      const current = Number.parseInt(el.textContent || '', 10);
      animate(Number.isFinite(current) ? current : from, to);
      return;
    }
    el.textContent = fmt(from);
    const onScroll = () => {
      if (played.current) return;
      if (inView()) {
        played.current = true;
        window.removeEventListener('scroll', onScroll);
        animate(from, to);
      }
    };
    onScroll();
    window.addEventListener('scroll', onScroll, { passive: true });
    return () => {
      dead = true;
      window.removeEventListener('scroll', onScroll);
      cancelAnimationFrame(raf);
    };
  }, [to, from]);
  return <span ref={ref} />;
}
