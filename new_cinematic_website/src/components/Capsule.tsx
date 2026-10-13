import { useEffect, useState } from "react";
import { AnimatePresence, motion } from "framer-motion";
import { ChevronDown, Eye, EyeOff, Mic, Monitor, Settings2, BookOpen, ArrowUpRight } from "lucide-react";
import { cn } from "../utils/cn";
import type { ModalKind } from "../site";

function Dots({ active }: { active: boolean }) {
  return (
    <div className="flex items-center gap-1">
      {[0, 1, 2, 3, 4].map((i) => (
        <span
          key={i}
          className="h-1.5 w-1.5 rounded-full bg-clay"
          style={{
            opacity: active ? 1 : 0.35,
            animation: active ? `bar ${0.6 + i * 0.13}s ease-in-out ${i * 0.08}s infinite` : "none",
          }}
        />
      ))}
    </div>
  );
}

export function Capsule({
  active,
  text,
  progress,
  openModal,
  className,
  defaultOpen = false,
}: {
  active: boolean;
  text: string;
  progress: number;
  openModal?: (m: ModalKind) => void;
  className?: string;
  defaultOpen?: boolean;
}) {
  const [open, setOpen] = useState(defaultOpen);
  const [vision, setVision] = useState(false);
  const [hidden, setHidden] = useState(false);

  useEffect(() => {
    const onKey = (e: KeyboardEvent) => {
      if (e.key === "Escape") {
        setVision(false);
      }
    };
    window.addEventListener("keydown", onKey);
    return () => window.removeEventListener("keydown", onKey);
  }, []);

  const pct = Math.min(100, Math.max(4, progress));
  const barColor = pct > 90 ? "#eb5757" : pct > 75 ? "#f59e0b" : "#27a644";

  if (hidden) {
    return (
      <button
        onClick={() => setHidden(false)}
        className="mx-auto flex items-center gap-2 rounded-full border border-white/15 bg-white/[0.04] px-5 py-3 text-sm text-cream backdrop-blur transition hover:border-clay/60"
      >
        <Mic size={15} className="text-clay" /> Show Voxula AI capsule <ArrowUpRight size={14} />
      </button>
    );
  }

  return (
    <div
      className={cn(
        "relative w-full max-w-[460px] overflow-hidden rounded-[26px] border border-white/10 bg-[#0f1011]/90 shadow-[0_40px_120px_-30px_rgba(0,0,0,0.9),0_0_0_1px_rgba(255,255,255,0.03)_inset] backdrop-blur-xl",
        className
      )}
    >
      {vision && (
        <div className="pointer-events-none absolute inset-2 z-10">
          {["left-0 top-0 border-l-2 border-t-2", "right-0 top-0 border-r-2 border-t-2", "bottom-0 left-0 border-b-2 border-l-2", "bottom-0 right-0 border-b-2 border-r-2"].map((c) => (
            <span key={c} className={cn("absolute h-4 w-4 rounded-sm border-clay", c)} />
          ))}
        </div>
      )}
      <div className="flex items-center justify-between gap-3 px-5 pt-4">
        <div className="flex items-center gap-2.5">
          <span
            className={cn("h-2 w-2 rounded-full", active ? "bg-sage" : "bg-mute/60")}
            style={active ? { animation: "pulse-dot 1.6s infinite" } : undefined}
          />
          <span className="font-mono text-[11px] tracking-[0.22em] text-cream">VOXULA</span>
          <span
            className={cn(
              "rounded-full px-2 py-0.5 font-mono text-[9px] uppercase tracking-widest",
              active ? "bg-sage/20 text-sage" : "bg-white/[0.06] text-mute"
            )}
          >
            {active ? "Live" : "Ready"}
          </span>
        </div>
        <Dots active={active} />
        <div className="flex items-center gap-1 text-mute">
          <button aria-label="Settings" onClick={() => openModal?.("settings")} className="rounded-md p-1.5 transition hover:bg-white/10 hover:text-cream">
            <Settings2 size={14} />
          </button>
          <button aria-label="Guide" onClick={() => openModal?.("guide")} className="rounded-md p-1.5 transition hover:bg-white/10 hover:text-cream">
            <BookOpen size={14} />
          </button>
          <button aria-label="Hide" onClick={() => setHidden(true)} className="rounded-md p-1.5 transition hover:bg-white/10 hover:text-cream">
            <EyeOff size={14} />
          </button>
        </div>
      </div>

      <div className="group relative mx-5 mt-4" title={`Tokens: ${Math.round(pct * 1280).toLocaleString()} / 128,000 · 180ms`}>
        <div className="h-[3px] overflow-hidden rounded-full bg-white/10">
          <motion.div
            className="h-full rounded-full"
            animate={{ width: `${pct}%`, backgroundColor: barColor }}
            transition={{ type: "spring", stiffness: 90, damping: 20 }}
          />
        </div>
      </div>

      <div className="flex items-center justify-between px-5 py-3.5">
        <button onClick={() => setOpen((o) => !o)} className="flex items-center gap-2 text-left text-[12.5px] text-mute transition hover:text-cream">
          <ChevronDown size={14} className={cn("transition-transform", open && "rotate-180")} />
          {vision ? "Screen vision enabled · demo" : "Your next thought, one shortcut away."}
        </button>
        <button
          aria-label="Toggle screen vision"
          onClick={() => setVision((v) => !v)}
          className={cn("rounded-md p-1.5 transition", vision ? "bg-clay/20 text-clay" : "text-mute hover:text-cream")}
        >
          {vision ? <Monitor size={14} /> : <Eye size={14} />}
        </button>
      </div>

      <AnimatePresence initial={false}>
        {open && (
          <motion.div
            initial={{ height: 0, opacity: 0 }}
            animate={{ height: "auto", opacity: 1 }}
            exit={{ height: 0, opacity: 0 }}
            transition={{ duration: 0.45, ease: [0.16, 1, 0.3, 1] }}
            className="overflow-hidden border-t border-white/[0.07]"
          >
            <div className="px-5 py-4">
              <div className="mb-2 font-mono text-[9.5px] uppercase tracking-[0.25em] text-mute">Live transcript</div>
              <p className="min-h-[3.2rem] whitespace-pre-wrap text-[13.5px] leading-relaxed text-cream/90">
                {text ? (
                  text.slice(-170)
                ) : (
                  <span className="text-mute">
                    Press Ctrl + Space in the simulator below. Your words will appear here, in real time.
                  </span>
                )}
                {active && <span className="caret ml-0.5 inline-block h-3.5 w-[2px] translate-y-0.5 bg-clay" />}
              </p>
            </div>
          </motion.div>
        )}
      </AnimatePresence>
    </div>
  );
}
