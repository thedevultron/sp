import { useEffect, useRef, useState } from "react";
import { useReducedMotion, AnimatePresence, motion } from "framer-motion";
import { gsap } from "gsap";
import { ensureScrollPlugins } from "../../lib/motion";
import { cn } from "../../utils/cn";

/** Scroll-linked lift for section headings. Transform/opacity only — no filter scrub. */
export function ScrollFloat({
  children,
  className,
}: {
  children: React.ReactNode;
  className?: string;
}) {
  const ref = useRef<HTMLDivElement>(null);

  useEffect(() => {
    ensureScrollPlugins();
    const el = ref.current;
    if (!el) return;
    if (window.matchMedia("(prefers-reduced-motion: reduce)").matches) return;
    if (window.innerWidth < 768) return;
    const tween = gsap.fromTo(
      el,
      { y: 28, autoAlpha: 0.35 },
      {
        y: 0,
        autoAlpha: 1,
        ease: "none",
        scrollTrigger: { trigger: el, start: "top 88%", end: "top 48%", scrub: 1 },
      }
    );
    return () => {
      tween.scrollTrigger?.kill();
      tween.kill();
    };
  }, []);

  return (
    <div ref={ref} className={cn("will-change-transform", className)}>
      {children}
    </div>
  );
}

/** Dynamic headline looper. Active voice, short phrases. */
export function TextLoop({
  phrases,
  className,
  interval = 2400,
}: {
  phrases: string[];
  className?: string;
  interval?: number;
}) {
  const reduce = useReducedMotion();
  const [i, setI] = useState(0);

  useEffect(() => {
    if (reduce) return;
    const id = window.setInterval(() => setI((v) => (v + 1) % phrases.length), interval);
    return () => window.clearInterval(id);
  }, [reduce, phrases.length, interval]);

  return (
    <span className={cn("inline-flex min-h-[1.2em] items-center", className)} aria-live="polite">
      <AnimatePresence mode="wait" initial={false}>
        <motion.span
          key={i}
          initial={{ y: 14, opacity: 0, filter: "blur(4px)" }}
          animate={{ y: 0, opacity: 1, filter: "blur(0px)" }}
          exit={{ y: -14, opacity: 0, filter: "blur(4px)" }}
          transition={{ duration: 0.45, ease: [0.22, 1, 0.36, 1] }}
          className="inline-block"
        >
          {phrases[i]}
        </motion.span>
      </AnimatePresence>
    </span>
  );
}
