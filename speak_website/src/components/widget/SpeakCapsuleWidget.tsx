import { useEffect, useRef, useState } from "react";
import { AnimatePresence, motion, useMotionValue, useReducedMotion, useSpring, useTransform } from "framer-motion";
import { BookOpen, ChevronDown, Monitor, Settings, X } from "lucide-react";
import { cn } from "../../utils/cn";
import { WaveformDots } from "./WaveformDots";
import { SmartTokenBar } from "./SmartTokenBar";
import { useInViewport, getQualityTier } from "../../lib/perf";
import { TranscriptDrawer } from "./TranscriptDrawer";

const TRANSCRIPT =
  "Press control-space and SPEAK types straight into whatever window you are in. Sub-second latency, zero focus stolen, and your API keys never leave this machine.";

const BASE_TOKENS = 1420;

interface SpeakCapsuleWidgetProps {
  className?: string;
}

/** The cropped SPEAK glass capsule — faithful to the native product UI. */
export function SpeakCapsuleWidget({ className }: SpeakCapsuleWidgetProps) {
  const reduce = useReducedMotion();
  const [listening, setListening] = useState(false);
  const [minimized, setMinimized] = useState(false);
  const [drawerOpen, setDrawerOpen] = useState(true);
  const [vision, setVision] = useState(false);
  const [charCount, setCharCount] = useState(0);
  const [tokens, setTokens] = useState(BASE_TOKENS);
  const [latency, setLatency] = useState(180);
  const wrapRef = useRef<HTMLDivElement>(null);
  const { ref: viewRef, inView } = useInViewport<HTMLDivElement>(0.05);
  const tiltAllowed =
    !reduce && getQualityTier() === "high" && typeof window !== "undefined" && window.innerWidth >= 1280;

  /* Cursor-driven 3D tilt — high-tier desktops only, rAF-throttled */
  const mx = useMotionValue(0);
  const my = useMotionValue(0);
  const rotateX = useSpring(useTransform(my, [-0.5, 0.5], [3.2, -3.2]), { stiffness: 140, damping: 18 });
  const rotateY = useSpring(useTransform(mx, [-0.5, 0.5], [-4, 4]), { stiffness: 140, damping: 18 });
  const moveRaf = useRef(0);

  const handleMove = (e: React.MouseEvent) => {
    if (!tiltAllowed || !wrapRef.current) return;
    if (moveRaf.current) return;
    const cx = e.clientX;
    const cy = e.clientY;
    moveRaf.current = requestAnimationFrame(() => {
      moveRaf.current = 0;
      const r = wrapRef.current?.getBoundingClientRect();
      if (!r) return;
      mx.set((cx - r.left) / r.width - 0.5);
      my.set((cy - r.top) / r.height - 0.5);
    });
  };
  const handleLeave = () => {
    cancelAnimationFrame(moveRaf.current);
    moveRaf.current = 0;
    mx.set(0);
    my.set(0);
  };

  /* Dictation engine */
  const startDictation = () => {
    setCharCount(0);
    setTokens(BASE_TOKENS);
    setListening(true);
    setDrawerOpen(true);
  };

  useEffect(() => {
    if (!listening || !inView) return;
    const iv = window.setInterval(() => {
      setCharCount((c) => Math.min(TRANSCRIPT.length, c + 2));
      setTokens((t) => t + 6);
    }, 34);
    return () => window.clearInterval(iv);
  }, [listening, inView]);

  useEffect(() => {
    if (!listening || !inView) return;
    const iv = window.setInterval(() => setLatency(118 + Math.round(Math.random() * 58)), 700);
    return () => window.clearInterval(iv);
  }, [listening, inView]);

  useEffect(() => {
    if (listening && charCount >= TRANSCRIPT.length) {
      const t = window.setTimeout(() => setListening(false), 900);
      return () => window.clearTimeout(t);
    }
  }, [listening, charCount]);

  const progress = 0.06 + (charCount / TRANSCRIPT.length) * 0.42;
  const statusLive = listening || charCount > 0;

  if (minimized) {
    return (
      <div className={className}>
        <button
          type="button"
          onClick={() => setMinimized(false)}
          className="group flex items-center gap-3 rounded-full border border-edge bg-[rgba(5,6,15,0.9)] py-2.5 pl-4 pr-5 shadow-[var(--shadow-widget)] transition-all duration-300 hover:border-[rgba(186,215,247,0.3)]"
        >
          <span className="h-2 w-2 rounded-full bg-token-green" />
          <span className="font-mono text-[11px] uppercase tracking-[0.14em] text-mist">SPEAK · resting in tray</span>
          <span className="font-mono text-[10px] text-fog transition-colors group-hover:text-blueprint">restore</span>
        </button>
      </div>
    );
  }

  return (
    <div
      ref={(el) => {
        (wrapRef as React.MutableRefObject<HTMLDivElement | null>).current = el;
        viewRef(el);
      }}
      onMouseMove={handleMove}
      onMouseLeave={handleLeave}
      className={cn("relative", className)}
      style={{ perspective: "1400px" }}
    >
      {/* Screen-Vision neon bounding box */}
      <AnimatePresence>
        {vision && (
          <motion.div
            key="vision-box"
            initial={{ opacity: 0, scale: 1.04 }}
            animate={{ opacity: 1, scale: 1 }}
            exit={{ opacity: 0, scale: 1.04 }}
            transition={{ duration: 0.35, ease: "easeOut" }}
            className="anim-pulse-border pointer-events-none absolute -inset-3 rounded-[26px] border border-blueprint/70"
            style={{ boxShadow: "0 0 24px rgba(182,217,252,0.18), inset 0 0 24px rgba(182,217,252,0.06)" }}
            aria-hidden="true"
          >
            <span className="absolute -left-px -top-px h-4 w-4 rounded-tl-[26px] border-l-2 border-t-2 border-blueprint" />
            <span className="absolute -right-px -top-px h-4 w-4 rounded-tr-[26px] border-r-2 border-t-2 border-blueprint" />
            <span className="absolute -bottom-px -left-px h-4 w-4 rounded-bl-[26px] border-b-2 border-l-2 border-blueprint" />
            <span className="absolute -bottom-px -right-px h-4 w-4 rounded-br-[26px] border-b-2 border-r-2 border-blueprint" />
            <span className="absolute -top-3 right-6 rounded-sm border border-blueprint/40 bg-[rgba(5,6,15,0.92)] px-2 py-0.5 font-mono text-[9px] uppercase tracking-[0.18em] text-blueprint">
              Screen vision live
            </span>
          </motion.div>
        )}
      </AnimatePresence>

      <motion.div
        className="glass-widget p-4 sm:p-5"
        style={tiltAllowed ? { rotateX, rotateY, transformStyle: "preserve-3d" } : undefined}
      >
        {/* ── Row 1 · status / waveform / actions ── */}
        <div className="flex items-center gap-3">
          <button
            type="button"
            onClick={() => (listening ? setListening(false) : startDictation())}
            className="group flex min-w-0 items-center gap-2.5 rounded-full py-1 pl-1 pr-1 transition-colors hover:bg-white/[0.04]"
            title={listening ? "Stop dictation" : "Start dictation"}
          >
            <span className={cn("h-2 w-2 shrink-0 rounded-full", statusLive ? "anim-ping-soft bg-token-green" : "bg-token-green/80")} />
            <span className="truncate text-[13px] font-medium text-frost">
              {listening ? "SPEAK Listening" : "SPEAK Ready"}
            </span>
            <span
              className={cn(
                "rounded-[6px] px-1.5 py-0.5 font-mono text-[10px] uppercase tracking-[0.1em]",
                listening ? "bg-[rgba(34,197,94,0.16)] text-token-green" : "bg-[rgba(199,211,234,0.12)] text-mist"
              )}
            >
              {listening ? "Live" : "Ready"}
            </span>
          </button>

          <button
            type="button"
            onClick={() => (listening ? setListening(false) : startDictation())}
            className="ml-auto rounded-full px-2 py-1.5 transition-transform hover:scale-105 active:scale-95"
            aria-label="Toggle dictation"
          >
            <WaveformDots active={listening} />
          </button>

          <div className="flex items-center gap-1.5">
            <CapsuleIconButton label="Settings">
              <Settings size={15} strokeWidth={1.5} />
            </CapsuleIconButton>
            <CapsuleIconButton label="Guide">
              <BookOpen size={15} strokeWidth={1.5} />
            </CapsuleIconButton>
            <CapsuleIconButton label="Hide to tray" danger onClick={() => setMinimized(true)}>
              <X size={15} strokeWidth={1.5} />
            </CapsuleIconButton>
          </div>
        </div>

        {/* ── Row 2 · Smart Token Context Meter ── */}
        <div className="mt-4">
          <SmartTokenBar progress={progress} tokens={tokens} latency={latency} />
        </div>

        {/* ── Row 3 · bottom tray ── */}
        <div className="mt-4 flex items-center justify-between">
          <button
            type="button"
            onClick={() => setDrawerOpen((v) => !v)}
            className="group flex items-center gap-1.5 rounded-full border border-edge bg-[rgba(186,214,247,0.05)] py-1.5 pl-3 pr-2.5 text-[12px] font-medium text-mist transition-all duration-300 hover:border-[rgba(186,215,247,0.3)] hover:text-frost"
          >
            Transcript
            <ChevronDown
              size={14}
              strokeWidth={1.5}
              className={cn("text-fog transition-transform duration-300", drawerOpen && "rotate-180 text-blueprint")}
            />
          </button>

          <button
            type="button"
            onClick={() => setVision((v) => !v)}
            aria-pressed={vision}
            className={cn(
              "grid h-9 w-9 place-items-center rounded-[10px] border transition-all duration-300",
              vision
                ? "border-blueprint/60 bg-[rgba(182,217,252,0.1)] text-blueprint shadow-[0_0_18px_rgba(182,217,252,0.25)]"
                : "border-edge bg-[rgba(186,214,247,0.05)] text-mist hover:border-[rgba(186,215,247,0.3)] hover:text-frost"
            )}
            title="Screen Vision — stream your viewport with your voice (Win+Shift)"
          >
            <Monitor size={16} strokeWidth={1.5} />
          </button>
        </div>

        <TranscriptDrawer open={drawerOpen} text={TRANSCRIPT.slice(0, charCount)} streaming={listening} />
      </motion.div>
    </div>
  );
}

function CapsuleIconButton({
  children,
  label,
  danger,
  onClick,
}: {
  children: React.ReactNode;
  label: string;
  danger?: boolean;
  onClick?: () => void;
}) {
  return (
    <button
      type="button"
      onClick={onClick}
      title={label}
      aria-label={label}
      className={cn(
        "grid h-7 w-7 place-items-center rounded-lg border border-transparent text-mist transition-all duration-200",
        danger
          ? "hover:border-[rgba(239,68,68,0.35)] hover:bg-[rgba(239,68,68,0.08)] hover:text-token-red hover:shadow-[0_0_14px_rgba(239,68,68,0.25)]"
          : "hover:border-edge hover:bg-white/[0.05] hover:text-frost"
      )}
    >
      {children}
    </button>
  );
}
