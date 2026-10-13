import { useState } from "react";
import { AnimatePresence, motion, useMotionValueEvent, useTransform } from "framer-motion";
import { Check, KeyRound, ShieldCheck, Sparkles } from "lucide-react";
import { ChapterMark, Eyebrow, KeyCap, VoiceBars, useSectionProgress } from "./ui";
import { cn } from "../utils/cn";

const STEPS = [
  {
    n: "01",
    tag: "CONNECT",
    title: "Bring a key. We'll find it.",
    body: "Auto-detects GEMINI_API_KEY or your saved vault key, with a free-tier fallback. Keys stay on your device.",
  },
  {
    n: "02",
    tag: "SUMMON",
    title: "One shortcut. Any app.",
    body: "Press Ctrl + Space. Voxula appears over your active window with a live transcript — without stealing focus.",
  },
  {
    n: "03",
    tag: "FLOW",
    title: "Speak at the speed of thought.",
    body: 'Words stream to your cursor sub-second. Say "refine" and the session rewrites itself in place.',
  },
];

function WindowChrome({ title, children, className }: { title: string; children: React.ReactNode; className?: string }) {
  return (
    <div className={cn("overflow-hidden rounded-2xl border border-white/10 bg-panel shadow-[0_50px_100px_-40px_rgba(0,0,0,0.9)]", className)}>
      <div className="flex items-center gap-2 border-b border-white/[0.07] bg-ink-2 px-4 py-3">
        <span className="h-2.5 w-2.5 rounded-full bg-[#4c8dff]/70" />
        <span className="h-2.5 w-2.5 rounded-full bg-[#799fd6]/70" />
        <span className="h-2.5 w-2.5 rounded-full bg-[#27a644]/70" />
        <span className="ml-3 font-mono text-[11px] text-mute">{title}</span>
      </div>
      {children}
    </div>
  );
}

function ConnectVisual({ sp }: { sp: number }) {
  const env = "GEMINI_API_KEY";
  const n = Math.floor(Math.min(1, sp / 0.45) * env.length);
  const found = sp > 0.5;
  const keyChars = Math.floor(Math.max(0, (sp - 0.5) / 0.4) * 22);
  return (
    <WindowChrome title="voxula — vault" className="w-full">
      <div className="space-y-5 p-6 font-mono text-[13px]">
        <div className="flex items-center gap-3 text-mute">
          <KeyRound size={15} className="text-clay" /> scanning environment…
        </div>
        <div className="rounded-xl border border-white/10 bg-ink/70 p-4">
          <div className="text-cream">
            <span className="text-mute">$ </span>
            {env.slice(0, n)}
            {!found && <span className="caret text-clay">▍</span>}
          </div>
          <div className="mt-3 flex items-center gap-2 text-sage" style={{ opacity: found ? 1 : 0 }}>
            <Check size={14} /> detected
          </div>
          <div className="mt-2 break-all text-cream/80" style={{ opacity: found ? 1 : 0 }}>
            AIza{"•".repeat(keyChars)}
          </div>
        </div>
        <div className="flex items-center gap-3 rounded-xl bg-sage/10 p-3 text-sage transition-opacity duration-500" style={{ opacity: sp > 0.88 ? 1 : 0.7 }}>
          <ShieldCheck size={16} /> Encrypted with DPAPI · stays on this device
        </div>
      </div>
    </WindowChrome>
  );
}

function SummonVisual({ sp }: { sp: number }) {
  const pressed = sp > 0.3;
  const capY = Math.max(0, 1 - Math.min(1, (sp - 0.3) / 0.35)) * 120;
  return (
    <div className="relative w-full">
      <WindowChrome title="Notes.docx — Word" className="w-full">
        <div className="h-[320px] space-y-3 p-8">
          <div className="h-3 w-1/3 rounded bg-white/15" />
          <div className="h-2 w-full rounded bg-white/[0.07]" />
          <div className="h-2 w-[92%] rounded bg-white/[0.07]" />
          <div className="h-2 w-[70%] rounded bg-white/[0.07]" />
          <div className="pt-4 text-[15px] text-cream/70">
            Meeting notes<span className="caret ml-0.5 inline-block h-4 w-[2px] translate-y-0.5 bg-clay" />
          </div>
        </div>
      </WindowChrome>
      <div
        className="absolute -bottom-6 left-1/2 w-[82%] -translate-x-1/2 rounded-2xl border border-white/10 bg-[#0f1011]/95 p-4 shadow-2xl backdrop-blur transition-opacity"
        style={{ transform: `translate(-50%, ${capY}px)`, opacity: pressed ? 1 : 0 }}
      >
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-2 font-mono text-[11px] tracking-[0.2em] text-cream">
            <span className="h-2 w-2 rounded-full bg-sage" style={{ animation: "pulse-dot 1.6s infinite" }} /> VOXULA
          </div>
          <VoiceBars count={12} height={20} />
        </div>
        <div className="mt-3 text-[13px] text-mute">Listening… live transcript appears here.</div>
      </div>
      <div className="absolute -top-5 right-4 flex items-center gap-1.5 rounded-xl border border-white/10 bg-ink px-3 py-2 shadow-xl">
        <span className={cn("transition-transform duration-200", pressed && "translate-y-[2px]")}>
          <KeyCap className={pressed ? "border-clay text-clay" : ""}>Ctrl</KeyCap>
        </span>
        +
        <span className={cn("transition-transform duration-200", pressed && "translate-y-[2px]")}>
          <KeyCap className={pressed ? "border-clay text-clay" : ""}>Space</KeyCap>
        </span>
      </div>
    </div>
  );
}

function FlowVisual({ sp }: { sp: number }) {
  const raw = "hey maya the draft is ready, um I moved our sync to 5pm ping me if that works";
  const polish = "Hi Maya — the draft is ready. I've moved our sync to 5:00 PM. Ping me if that works.";
  const typed = Math.floor(Math.min(1, sp / 0.55) * raw.length);
  const refined = sp > 0.8;
  const text = refined ? polish : raw.slice(0, typed);
  return (
    <WindowChrome title="Messages — Slack" className="w-full">
      <div className="min-h-[320px] p-6">
        <div className="mb-4 flex items-center gap-3">
          <div className="flex h-8 w-8 items-center justify-center rounded-lg bg-clay text-xs font-semibold text-ink">AB</div>
          <div className="text-sm text-cream">
            Amir <span className="ml-2 text-xs text-mute">Just now</span>
          </div>
        </div>
        <p className="min-h-[96px] text-[17px] leading-relaxed text-cream">
          {text}
          <span className="caret ml-0.5 inline-block h-4 w-[2px] translate-y-0.5 bg-clay" />
        </p>
        <div className="mt-6 flex items-center justify-between">
          <VoiceBars count={20} height={24} active={!refined && sp > 0.02} />
          <motion.div
            animate={{ opacity: sp > 0.62 ? 1 : 0, y: sp > 0.62 ? 0 : 8 }}
            className="flex items-center gap-2 rounded-full border border-clay/40 bg-clay/10 px-3 py-1.5 font-mono text-xs text-clay"
          >
            <Sparkles size={13} /> {refined ? "refined in place" : 'say "refine"'}
          </motion.div>
        </div>
      </div>
    </WindowChrome>
  );
}

export function Pipeline() {
  const { ref, progress } = useSectionProgress();
  const [state, setState] = useState({ step: 0, sp: 0 });
  const [mobileStep, setMobileStep] = useState(0);

  useMotionValueEvent(progress, "change", (v) => {
    const clamped = Math.min(0.9999, Math.max(0, (v - 0.08) / 0.84));
    const raw = clamped * 3;
    const step = Math.floor(raw);
    setState({ step, sp: raw - step });
  });
  const railH = useTransform(progress, [0.08, 0.92], ["0%", "100%"]);
  const { step, sp } = state;
  const s = STEPS[step];

  return (
    <section id="how-it-works" className="relative bg-ink-2">
      {/* Mobile view (< lg): Clean, fully visible, interactive step presentation */}
      <div className="px-6 py-24 lg:hidden">
        <div className="mx-auto max-w-xl">
          <ChapterMark num="II" title="The shortcut" />
          <Eyebrow className="mt-8">HOW IT WORKS</Eyebrow>
          <h2 className="font-display mt-4 text-[clamp(2.2rem,7vw,3.6rem)] leading-[1.04] text-cream">
            Instant execution. <span className="text-ember italic">Zero friction.</span>
          </h2>
          <p className="mt-3 text-base text-mute">From a thought to the page, in less than a second.</p>

          {/* Interactive Step Switcher for Mobile */}
          <div className="mt-8 flex gap-2 rounded-full border border-white/10 bg-white/[0.04] p-1.5">
            {STEPS.map((st, i) => (
              <button
                key={st.n}
                onClick={() => setMobileStep(i)}
                className={cn(
                  "flex-1 rounded-full py-2.5 font-mono text-xs transition-all",
                  mobileStep === i ? "bg-clay font-medium text-ink shadow-md" : "text-mute hover:text-cream"
                )}
              >
                {st.n} {st.tag}
              </button>
            ))}
          </div>

          <div className="mt-7">
            <div className="font-mono text-xs tracking-widest text-clay">{STEPS[mobileStep].n} / {STEPS[mobileStep].tag}</div>
            <h3 className="font-display mt-2 text-3xl text-cream">{STEPS[mobileStep].title}</h3>
            <p className="mt-3 text-sm leading-relaxed text-mute">{STEPS[mobileStep].body}</p>
          </div>

          <div className="mt-8 overflow-hidden rounded-2xl">
            <AnimatePresence mode="wait">
              <motion.div
                key={mobileStep}
                initial={{ opacity: 0, y: 16 }}
                animate={{ opacity: 1, y: 0 }}
                exit={{ opacity: 0, y: -16 }}
                transition={{ duration: 0.35 }}
              >
                {mobileStep === 0 && <ConnectVisual sp={0.8} />}
                {mobileStep === 1 && <SummonVisual sp={0.7} />}
                {mobileStep === 2 && <FlowVisual sp={0.7} />}
              </motion.div>
            </AnimatePresence>
          </div>
        </div>
      </div>

      {/* Desktop view (lg:block): Cinematic sticky scrub choreography */}
      <div ref={ref} className="relative hidden h-[420vh] lg:block">
        <div className="sticky top-0 flex h-screen items-center overflow-hidden">
          <div className="pointer-events-none absolute -left-40 top-1/4 h-[600px] w-[600px] rounded-full bg-[radial-gradient(circle,rgba(76,141,255,0.1),transparent_65%)]" />
          <div className="mx-auto grid w-full max-w-6xl items-center gap-12 px-6 md:px-16 lg:grid-cols-[0.9fr_1.1fr]">
            <div>
              <ChapterMark num="II" title="The shortcut" />
              <Eyebrow className="mt-8">HOW IT WORKS</Eyebrow>
              <h2 className="font-display mt-4 text-[clamp(2rem,4.6vw,4rem)] leading-[1.02] text-cream">
                Instant execution. <span className="text-ember italic">Zero friction.</span>
              </h2>
              <p className="mt-4 text-mute">From a thought to the page, in less than a second.</p>

              <div className="relative mt-10 flex gap-6">
                <div className="relative w-px shrink-0 bg-white/10">
                  <motion.div style={{ height: railH }} className="absolute left-0 top-0 w-px bg-clay" />
                </div>
                <div className="min-h-[190px] flex-1">
                  <AnimatePresence mode="wait">
                    <motion.div
                      key={step}
                      initial={{ opacity: 0, y: 24, filter: "blur(8px)" }}
                      animate={{ opacity: 1, y: 0, filter: "blur(0px)" }}
                      exit={{ opacity: 0, y: -24, filter: "blur(8px)" }}
                      transition={{ duration: 0.5, ease: [0.16, 1, 0.3, 1] }}
                    >
                      <div className="font-mono text-[11px] tracking-[0.25em] text-clay">
                        {s.n} / {s.tag}
                      </div>
                      <h3 className="font-display mt-3 text-4xl text-cream md:text-5xl">{s.title}</h3>
                      <p className="mt-4 max-w-md text-[16px] leading-relaxed text-mute">{s.body}</p>
                    </motion.div>
                  </AnimatePresence>
                </div>
              </div>
              <div className="mt-8 flex gap-2">
                {STEPS.map((_, i) => (
                  <span key={i} className={cn("h-1 rounded-full transition-all duration-500", i === step ? "w-10 bg-clay" : "w-4 bg-white/15")} />
                ))}
              </div>
            </div>

            <div className="relative mx-auto w-full max-w-[560px]">
              <div className="absolute -inset-10 rounded-full bg-clay/[0.07] blur-3xl" />
              <AnimatePresence mode="wait">
                <motion.div
                  key={step}
                  initial={{ opacity: 0, scale: 0.94, rotateX: 8, y: 30 }}
                  animate={{ opacity: 1, scale: 1, rotateX: 0, y: 0 }}
                  exit={{ opacity: 0, scale: 1.03, y: -20 }}
                  transition={{ duration: 0.55, ease: [0.16, 1, 0.3, 1] }}
                  className="relative"
                  style={{ perspective: 1200 }}
                >
                  {step === 0 && <ConnectVisual sp={sp} />}
                  {step === 1 && <SummonVisual sp={sp} />}
                  {step === 2 && <FlowVisual sp={sp} />}
                </motion.div>
              </AnimatePresence>
            </div>
          </div>
        </div>
      </div>
    </section>
  );
}
