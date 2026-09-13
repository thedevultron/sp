import { motion } from "framer-motion";
import { cn } from "../../utils/cn";

interface SmartTokenBarProps {
  /** 0..1 */
  progress: number;
  tokens: number;
  latency: number;
  className?: string;
  tooltip?: boolean;
}

function telemetryColor(p: number) {
  if (p < 0.6) return "#22c55e";
  if (p < 0.85) return "#f59e0b";
  return "#ef4444";
}

/** 2px luminous context meter — Green → Amber → Red. */
export function SmartTokenBar({ progress, tokens, latency, className, tooltip = true }: SmartTokenBarProps) {
  const p = Math.min(1, Math.max(0, progress));
  const color = telemetryColor(p);

  return (
    <div className={cn("group/bar relative", className)}>
      <div className="h-[2px] w-full overflow-hidden rounded-full bg-[rgba(186,215,247,0.1)]">
        <motion.div
          className="h-full rounded-full"
          style={{ backgroundColor: color, boxShadow: `0 0 12px ${color}` }}
          animate={{ width: `${p * 100}%` }}
          initial={false}
          transition={{ type: "spring", stiffness: 170, damping: 26 }}
        />
      </div>
      {tooltip && (
        <div className="pointer-events-none absolute -top-9 left-1/2 z-30 -translate-x-1/2 whitespace-nowrap rounded-md border border-edge bg-[rgba(5,6,15,0.96)] px-2.5 py-1 font-mono text-[11px] tabular-nums text-frost opacity-0 shadow-[0_8px_24px_rgba(0,0,0,0.6)] transition-opacity duration-200 group-hover/bar:opacity-100">
          Tokens: {tokens.toLocaleString("en-US")} / 128,000 · {latency}ms
        </div>
      )}
    </div>
  );
}
