import { useCallback, useRef, useState } from 'react';
import { useReducedMotion } from 'motion/react';

type Spark = { id: number; x: number; y: number; angle: number };

let sparkId = 0;

/**
 * DownloadButton — React-Bits-style microinteraction, hand-rolled.
 * StarBorder beam (a conic highlight that orbits the button edge) plus
 * ClickSpark burst (tiny sparks fly from the exact click point).
 * Transform/opacity only; plain button under reduced motion.
 */
export default function DownloadButton({
  href,
  download,
  onClick,
  children,
}: {
  href: string;
  download?: string;
  onClick?: () => void;
  children: React.ReactNode;
}) {
  const reduced = useReducedMotion();
  const [sparks, setSparks] = useState<Spark[]>([]);
  const ref = useRef<HTMLAnchorElement>(null);

  const burst = useCallback(
    (e: React.MouseEvent) => {
      onClick?.();
      if (reduced || !ref.current) return;
      const r = ref.current.getBoundingClientRect();
      const x = e.clientX - r.left;
      const y = e.clientY - r.top;
      const batch = Array.from({ length: 10 }, () => {
        const angle = Math.random() * Math.PI * 2;
        return { id: ++sparkId, x, y, angle };
      });
      setSparks((prev) => [...prev, ...batch]);
      window.setTimeout(() => {
        setSparks((prev) => prev.filter((s) => !batch.some((b) => b.id === s.id)));
      }, 650);
    },
    [onClick, reduced]
  );

  return (
    <span className={`dl-star${reduced ? ' is-static' : ''}`}>
      <a ref={ref} className="button primary full-width dl-beam" href={href} download={download} onClick={burst}>
        {children}
      </a>
      {!reduced &&
        sparks.map((s) => (
          <i
            key={s.id}
            className="dl-spark"
            aria-hidden="true"
            style={{
              left: s.x,
              top: s.y,
              ['--tx' as string]: `${Math.cos(s.angle) * (26 + Math.random() * 26)}px`,
              ['--ty' as string]: `${Math.sin(s.angle) * (26 + Math.random() * 26)}px`,
            }}
          />
        ))}
    </span>
  );
}
