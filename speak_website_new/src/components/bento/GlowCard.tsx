import { useRef, type CSSProperties, type ReactNode } from 'react';
import { useReducedMotion } from 'motion/react';
import { cn } from '../../utils/cn';

/**
 * GlowCard — border-glow, isolated. The card owns its cursor-local glow;
 * a grid-level tracker (BentoGrid) feeds --bridge-x/--bridge-y/--grid-glow
 * so light bleeds across card gaps from neighboring pointers.
 */
type GlowCardProps = {
  children: ReactNode;
  className?: string;
  glowColor?: string; // "r, g, b"
  glowRadius?: number;
};

const IDLE = 0;

export default function GlowCard({ children, className, glowColor = '76, 141, 255', glowRadius = 260 }: GlowCardProps) {
  const ref = useRef<HTMLDivElement>(null);
  const reduced = useReducedMotion();

  const setGlow = (xPct: number, yPct: number, intensity: number) => {
    const el = ref.current;
    if (!el) return;
    el.style.setProperty('--glow-x', `${xPct}%`);
    el.style.setProperty('--glow-y', `${yPct}%`);
    el.style.setProperty('--glow-intensity', intensity.toString());
  };

  return (
    <div
      ref={ref}
      onPointerMove={(e) => {
        if (reduced || !ref.current) return;
        const r = ref.current.getBoundingClientRect();
        setGlow(((e.clientX - r.left) / r.width) * 100, ((e.clientY - r.top) / r.height) * 100, 1);
      }}
      onPointerLeave={() => setGlow(50, 0, IDLE)}
      className={cn('vox-glow-card', className)}
      style={{ '--glow-radius': `${glowRadius}px`, '--vox-glow': glowColor } as CSSProperties}
    >
      <div className="vox-glow-inner">{children}</div>
    </div>
  );
}
