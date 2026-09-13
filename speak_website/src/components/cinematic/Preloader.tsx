import { useEffect, useRef, useState } from "react";
import { gsap } from "gsap";
import { ensureScrollPlugins } from "../../lib/motion";
import { cn } from "../../utils/cn";

const PHASES = ["Voice pipeline warming up", "Binding Ctrl + Space", "Linking Gemini Live"];

export function Preloader({ onDone }: { onDone: () => void }) {
  const root = useRef<HTMLDivElement>(null);
  const bar = useRef<HTMLDivElement>(null);
  const num = useRef<HTMLSpanElement>(null);
  const [gone, setGone] = useState(false);
  const [phase, setPhase] = useState(0);

  useEffect(() => {
    const timers: number[] = [window.setTimeout(() => setPhase(1), 380), window.setTimeout(() => setPhase(2), 760)];
    return () => timers.forEach((t) => window.clearTimeout(t));
  }, []);

  useEffect(() => {
    ensureScrollPlugins();
    const reduce = window.matchMedia("(prefers-reduced-motion: reduce)").matches;
    if (reduce) {
      setGone(true);
      onDone();
      return;
    }
    const counter = { v: 0 };
    const ctx = gsap.context(() => {
      const tl = gsap.timeline({
        defaults: { ease: "power3.out" },
        onComplete: () => {
          setGone(true);
          onDone();
        },
      });
      tl.fromTo(bar.current, { scaleX: 0 }, { scaleX: 1, duration: 1.05 }, 0)
        .to(
          counter,
          {
            v: 100,
            duration: 1.05,
            ease: "power2.inOut",
            onUpdate: () => {
              if (num.current) num.current.textContent = `${Math.round(counter.v)}`;
            },
          },
          0
        )
        .to(".preloader-word", { y: 0, autoAlpha: 1, duration: 0.7, stagger: 0.07 }, 0.1)
        .to(".preloader-ring", { scale: 1, autoAlpha: 1, duration: 0.9, ease: "power2.out" }, 0)
        .to(root.current, { yPercent: -100, duration: 0.85, ease: "power4.inOut" }, "+=0.15");
    }, root);
    return () => ctx.revert();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  if (gone) return null;

  return (
    <div
      ref={root}
      className={cn("fixed inset-0 z-[100] flex flex-col items-center justify-center bg-[#05060f]")}
      aria-hidden="true"
    >
      {/* Ice halo ring */}
      <div
        className="preloader-ring pointer-events-none absolute h-[300px] w-[300px] rounded-full bg-[radial-gradient(closest-side,rgba(102,58,243,0.16),transparent_70%)]"
        style={{ transform: "scale(0.8)", opacity: 0 }}
      />
      <div className="flex overflow-hidden">
        {["S", "P", "E", "A", "K"].map((l) => (
          <span
            key={l}
            className="preloader-word font-display text-[13px] font-semibold tracking-[0.5em] text-[#d1e4fa]"
            style={{ transform: "translateY(110%)", opacity: 0 }}
          >
            {l}
          </span>
        ))}
      </div>
      <div className="mt-6 h-px w-[200px] overflow-hidden rounded-full bg-white/10">
        <div
          ref={bar}
          className="h-full w-full origin-left"
          style={{ transform: "scaleX(0)", backgroundImage: "linear-gradient(90deg, #663af3 0%, #b6d9fc 60%, #d8ecf8 100%)" }}
        />
      </div>
      <p className="mt-4 font-mono text-[10px] uppercase tracking-[0.22em] text-[#9da7ba]/80">
        <span ref={num} className="tabular-nums text-[#d8ecf8]">0</span>
        <span className="text-[#9da7ba]/50"> / 100 · </span>
        {PHASES[phase]}
      </p>
    </div>
  );
}
