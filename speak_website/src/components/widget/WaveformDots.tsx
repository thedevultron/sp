import { cn } from "../../utils/cn";

interface WaveformDotsProps {
  active: boolean;
  className?: string;
}

const BARS = [
  { h: 7, d: "0s" },
  { h: 12, d: "0.12s" },
  { h: 16, d: "0.24s" },
  { h: 12, d: "0.07s" },
  { h: 7, d: "0.17s" },
];

/**
 * Five Blueprint-Blue audio bars. Pure CSS keyframes (compositor only)
 * instead of 5x framer-motion infinite loops — same dance, ~0 JS cost.
 */
export function WaveformDots({ active, className }: WaveformDotsProps) {
  return (
    <div className={cn("flex h-5 items-center gap-[5px]", className)} aria-hidden="true">
      {BARS.map((b, i) => (
        <span
          key={i}
          className={cn("w-[3px] rounded-full bg-blueprint", active && "wave-bar")}
          style={{
            height: active ? b.h : 4,
            opacity: active ? undefined : 0.3,
            boxShadow: "0 0 8px rgba(182,217,252,0.5)",
            animationDelay: b.d,
          }}
        />
      ))}
      <style>{`@keyframes wave-dance { 0%,100% { transform: scaleY(0.35); opacity: 0.45; } 50% { transform: scaleY(1); opacity: 1; } } .wave-bar { transform-origin: center; animation: wave-dance 0.9s ease-in-out infinite; will-change: transform, opacity; } @media (prefers-reduced-motion: reduce) { .wave-bar { animation: none !important; } }`}</style>
    </div>
  );
}
