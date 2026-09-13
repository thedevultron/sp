import { useEffect, useRef } from "react";
import { gsap } from "gsap";
import { ensureScrollPlugins } from "../../lib/motion";

/** Sticky card stack. CSS sticky for layout, GSAP for depth. */
export function StickyStack({ cards }: { cards: React.ReactNode[] }) {
  const ref = useRef<HTMLDivElement>(null);

  useEffect(() => {
    ensureScrollPlugins();
    const root = ref.current;
    if (!root) return;
    if (window.matchMedia("(prefers-reduced-motion: reduce)").matches) return;
    if (window.innerWidth < 768) return;

    const ctx = gsap.context(() => {
      const els = gsap.utils.toArray<HTMLElement>(".stack-card");
      els.forEach((card, i) => {
        const next = els[i + 1];
        if (!next) return;
        gsap.to(card, {
          scale: 0.92 + i * 0.015,
          autoAlpha: 0.72,
          y: -24,
          ease: "none",
          scrollTrigger: {
            trigger: next,
            start: "top 78%",
            end: "top 24%",
            scrub: true,
            invalidateOnRefresh: true,
          },
        });
      });
    }, root);
    return () => ctx.revert();
  }, [cards.length]);

  return (
    <div ref={ref} className="sticky-stack">
      {cards.map((c, i) => (
        <div key={i} className="stack-card">
          {c}
        </div>
      ))}
    </div>
  );
}
