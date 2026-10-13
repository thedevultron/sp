import { useEffect, useState } from "react";
import { motion, useMotionValueEvent, useTransform } from "framer-motion";
import { Check, Mic } from "lucide-react";
import { ChapterMark, Eyebrow, VoiceBars, useSectionProgress } from "./ui";
import { cn } from "../utils/cn";

const RAW = "could you set meeting at 9pm actually 5pm";
const POLISH = "Could we schedule the meeting for 5:00 PM?";

const TRIGGERS = [
  { word: "refine", what: "Clean rewrite", sub: "grammar, clarity, structure" },
  { word: "polish", what: "Tighten tone", sub: "emails, messages, notes" },
  { word: "elaborate", what: "Expand idea", sub: "detail, examples, formatting" },
];

function OutlookCard({ phase, text }: { phase: "typing" | "speak" | "delete" | "retype" | "done"; text: string }) {
  return (
    <div className="overflow-hidden rounded-3xl border border-white/10 bg-panel shadow-[0_60px_120px_-40px_rgba(0,0,0,0.9)]">
      <div className="flex items-center justify-between border-b border-white/[0.07] bg-ink-2 px-5 py-3">
        <div className="flex items-center gap-2">
          <span className="h-2.5 w-2.5 rounded-full bg-clay/70" />
          <span className="h-2.5 w-2.5 rounded-full bg-amber/70" />
          <span className="h-2.5 w-2.5 rounded-full bg-sage/70" />
          <span className="ml-3 font-mono text-[11px] text-mute">Calendar invite — Outlook</span>
        </div>
        <span className="font-mono text-[10px] tracking-widest text-mute">
          {phase === "typing" && "DICTATING"}
          {phase === "speak" && "LISTENING"}
          {phase === "delete" && "DELETING"}
          {phase === "retype" && "RETYPING"}
          {phase === "done" && "DONE"}
        </span>
      </div>
      <div className="space-y-2 px-5 sm:px-8 pb-2 pt-6 sm:pt-8">
        <div className="flex gap-3 border-b border-white/[0.07] pb-3 text-sm">
          <span className="text-mute">To</span>
          <span className="text-cream/80">maya@acme.co</span>
        </div>
        <div className="flex gap-3 border-b border-white/[0.07] pb-3 text-sm">
          <span className="text-mute">Re</span>
          <span className="text-cream/80">Sync</span>
        </div>
      </div>
      <div className="min-h-[170px] sm:min-h-[190px] px-5 sm:px-8 py-5 sm:py-6">
        <p
          className={cn(
            "font-display text-[clamp(1.4rem,3.2vw,2.5rem)] leading-[1.2] transition-colors duration-300",
            phase === "delete" ? "text-clay/90" : "text-cream"
          )}
        >
          {text}
          <span className="caret ml-0.5 inline-block h-[0.9em] w-[3px] translate-y-1 bg-clay" />
        </p>
      </div>
      <div className="flex items-center justify-between border-t border-white/[0.07] bg-ink-2 px-5 py-3.5">
        <div className="flex items-center gap-3">
          <span
            className={cn(
              "flex h-8 w-8 items-center justify-center rounded-full transition-colors",
              phase === "speak" ? "bg-clay text-ink" : "bg-white/[0.06] text-mute"
            )}
          >
            <Mic size={14} />
          </span>
          {phase === "speak" ? (
            <motion.span initial={{ opacity: 0, x: -8 }} animate={{ opacity: 1, x: 0 }} className="font-mono text-sm text-clay">
              “refine”
            </motion.span>
          ) : (
            <VoiceBars count={14} height={18} active={phase === "typing"} color={phase === "typing" ? "#4c8dff" : "#8a8f98"} />
          )}
        </div>
        {phase === "done" ? (
          <motion.span initial={{ opacity: 0, scale: 0.8 }} animate={{ opacity: 1, scale: 1 }} className="flex items-center gap-1.5 text-[13px] text-sage">
            <Check size={14} /> Refined in place
          </motion.span>
        ) : (
          <span className="font-mono text-[10.5px] text-mute">9pm → 5:00 PM</span>
        )}
      </div>
    </div>
  );
}

function computeRefineState(val: number) {
  let text = "";
  let phase: "typing" | "speak" | "delete" | "retype" | "done" = "typing";
  if (val < 0.26) {
    text = RAW.slice(0, Math.floor((Math.max(0, val - 0.04) / 0.22) * RAW.length));
  } else if (val < 0.42) {
    text = RAW;
    phase = "speak";
  } else if (val < 0.62) {
    phase = "delete";
    const k = (val - 0.42) / 0.2;
    text = RAW.slice(0, Math.ceil((1 - k) * RAW.length));
  } else if (val < 0.9) {
    phase = "retype";
    const k = (val - 0.62) / 0.28;
    text = POLISH.slice(0, Math.floor(k * POLISH.length));
  } else {
    phase = "done";
    text = POLISH;
  }
  return { text, phase };
}

export function Refine() {
  const { ref, progress } = useSectionProgress();
  const [p, setP] = useState(0);
  const [mobileP, setMobileP] = useState(0);

  useMotionValueEvent(progress, "change", (v) => setP(v));
  const glow = useTransform(progress, [0.25, 0.45, 0.7, 0.95], [0.3, 1, 0.8, 0.4]);

  // Mobile auto-loop cycle
  useEffect(() => {
    let t = 0;
    const interval = setInterval(() => {
      t = (t + 0.015) % 1;
      setMobileP(t);
    }, 70);
    return () => clearInterval(interval);
  }, []);

  const desktopState = computeRefineState(p);
  const mobileState = computeRefineState(mobileP);
  const activeTrigger = desktopState.phase === "speak" || desktopState.phase === "delete" ? 0 : -1;
  const activeMobileTrigger = mobileState.phase === "speak" || mobileState.phase === "delete" ? 0 : -1;

  return (
    <section id="refine" className="relative bg-ink-2">
      {/* Mobile view (< lg): Clean, responsive layout */}
      <div className="px-6 py-24 lg:hidden">
        <div className="mx-auto max-w-xl">
          <ChapterMark num="V" title="The rewrite" />
          <Eyebrow className="mt-8">REFINE & POLISH</Eyebrow>
          <h2 className="font-display mt-4 text-[clamp(2.2rem,7vw,3.6rem)] leading-[1.04] text-cream">
            Say <span className="text-ember italic">“refine”</span> — it refines.
          </h2>
          <p className="mt-4 text-base leading-relaxed text-mute">
            Everything you typed this session is removed with measured Backspaces and rewritten in place. No clipboard. No Ctrl+A.
            Self-correction aware — obsolete info is dropped, times normalized.
          </p>

          <div className="mt-8 overflow-hidden rounded-2xl">
            <OutlookCard phase={mobileState.phase} text={mobileState.text} />
            <p className="mt-3 text-center text-xs text-mute">
              “could you set meeting at 9pm actually 5pm” → “Could we schedule the meeting for 5:00 PM?”
            </p>
          </div>

          <div className="mt-8 space-y-2.5">
            {TRIGGERS.map((t, i) => (
              <div
                key={t.word}
                className={cn(
                  "flex items-center justify-between rounded-2xl border px-4 py-3 transition-all duration-300",
                  activeMobileTrigger === i ? "border-clay bg-clay/10" : "border-white/10 bg-white/[0.02]"
                )}
              >
                <span className={cn("font-mono text-sm", activeMobileTrigger === i ? "text-clay" : "text-cream")}>{t.word}</span>
                <span className="text-right text-[12.5px] text-mute">
                  <span className="text-cream/90">{t.what}</span>
                  <span className="hidden sm:inline"> · {t.sub}</span>
                </span>
              </div>
            ))}
          </div>
          <p className="mt-4 text-[13px] text-mute">
            Plus up to 3 custom actions, with your own trigger words — Settings → Refine.
          </p>
        </div>
      </div>

      {/* Desktop view (lg:block): Cinematic sticky scrub choreography */}
      <div ref={ref} className="relative hidden h-[380vh] lg:block">
        <div className="sticky top-0 flex h-screen items-center overflow-hidden">
          <motion.div
            style={{ opacity: glow }}
            className="pointer-events-none absolute left-1/2 top-1/2 h-[900px] w-[900px] -translate-x-1/2 -translate-y-1/2 rounded-full bg-[radial-gradient(circle,rgba(76,141,255,0.2),transparent_62%)]"
          />
          <div className="relative mx-auto grid w-full max-w-6xl items-center gap-12 px-6 md:px-16 lg:grid-cols-[1fr_1.1fr]">
            <div>
              <ChapterMark num="V" title="The rewrite" />
              <Eyebrow className="mt-8">REFINE & POLISH</Eyebrow>
              <h2 className="font-display mt-4 text-[clamp(2.4rem,5.4vw,4.8rem)] leading-[1] text-cream">
                Say <span className="text-ember italic">“refine”</span> — it refines.
              </h2>
              <p className="mt-5 max-w-md text-[16px] leading-relaxed text-mute">
                Everything you typed this session is removed with measured Backspaces and rewritten in place. No clipboard. No Ctrl+A.
                No Enter presses. Self-correction aware — obsolete info is dropped, times normalized.
              </p>
              <div className="mt-8 space-y-2.5">
                {TRIGGERS.map((t, i) => (
                  <div
                    key={t.word}
                    className={cn(
                      "flex items-center justify-between rounded-2xl border px-5 py-3.5 transition-all duration-500",
                      activeTrigger === i ? "border-clay bg-clay/10" : "border-white/10 bg-white/[0.02]"
                    )}
                  >
                    <span className={cn("font-mono text-sm", activeTrigger === i ? "text-clay" : "text-cream")}>{t.word}</span>
                    <span className="text-right text-[13px] text-mute">
                      <span className="text-cream/90">{t.what}</span>
                      <span className="hidden sm:inline"> · {t.sub}</span>
                    </span>
                  </div>
                ))}
              </div>
              <p className="mt-4 text-[13px] text-mute">
                Plus up to 3 custom actions, with your own trigger words — Settings → Refine.
              </p>
            </div>

            <div className="relative">
              <OutlookCard phase={desktopState.phase} text={desktopState.text} />
              <p className="mt-4 text-center text-xs text-mute">
                “could you set meeting at 9pm actually 5pm” → “Could we schedule the meeting for 5:00 PM?”
              </p>
            </div>
          </div>
        </div>
      </div>
    </section>
  );
}
