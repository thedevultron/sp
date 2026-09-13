import { useRef, type MouseEvent, type ReactNode } from "react";
import { cn } from "../../utils/cn";
import { getQualityTier } from "../../lib/perf";

interface GlassCardProps {
  children: ReactNode;
  className?: string;
  /** Mouse-following luminous spotlight overlay */
  spotlight?: boolean;
  /** Subtle 3D tilt toward the cursor */
  tilt?: boolean;
  /** Backdrop blur budget: sm (10px) default, none for dense grids */
  blur?: "sm" | "none";
  id?: string;
}

export function GlassCard({ children, className, spotlight = true, tilt = false, blur, id }: GlassCardProps) {
  const ref = useRef<HTMLDivElement>(null);
  const raf = useRef(0);

  const handleMove = (e: MouseEvent<HTMLDivElement>) => {
    const el = ref.current;
    if (!el) return;
    if (getQualityTier() === "low") return;
    if (raf.current) return;
    const cx = e.clientX;
    const cy = e.clientY;
    raf.current = requestAnimationFrame(() => {
      raf.current = 0;
      const r = el.getBoundingClientRect();
      const x = cx - r.left;
      const y = cy - r.top;
      el.style.setProperty("--mx", `${x}px`);
      el.style.setProperty("--my", `${y}px`);
      if (tilt && getQualityTier() === "high") {
        const rx = (y / r.height - 0.5) * -2.6;
        const ry = (x / r.width - 0.5) * 2.6;
        el.style.setProperty("--rx", `${rx.toFixed(2)}deg`);
        el.style.setProperty("--ry", `${ry.toFixed(2)}deg`);
      }
    });
  };

  const handleLeave = () => {
    const el = ref.current;
    if (!el) return;
    cancelAnimationFrame(raf.current);
    raf.current = 0;
    el.style.setProperty("--rx", "0deg");
    el.style.setProperty("--ry", "0deg");
  };

  return (
    <div
      id={id}
      ref={ref}
      onMouseMove={tilt || spotlight ? handleMove : undefined}
      onMouseLeave={tilt ? handleLeave : undefined}
      className={cn(
        "spot-card glass-card card-lift",
        tilt && "tilt-card",
        blur === "none" && "glass-flat",
        className
      )}
    >
      {spotlight && <div className="spot-overlay" aria-hidden="true" />}
      {children}
    </div>
  );
}
