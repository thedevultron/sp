import { useEffect, useState } from "react";
import { AnimatePresence, motion, useReducedMotion } from "framer-motion";
import { Gauge, KeyRound, Mic, Monitor, PenTool, Sparkles } from "lucide-react";
import { cn } from "../../utils/cn";
import { GlassCard } from "../ui/GlassCard";
import { Reveal } from "../ui/Reveal";
import { KeyCap } from "../ui/KeyCap";
import { WaveformDots } from "../widget/WaveformDots";
import { SmartTokenBar } from "../widget/SmartTokenBar";
import { ScrollFloat } from "../cinematic/TextMotion";
import FoldText from "../FoldText";

export function BentoPillarsSection() {
  return (
    <section id="pillars" className="relative py-24 sm:py-32">
      <div className="mx-auto max-w-[1200px] px-6">
        <ScrollFloat>
          <Reveal>
            <p className="text-center font-mono text-[11px] uppercase tracking-[0.22em] text-fog/60">
              02 — Under the hood
            </p>
          </Reveal>
          <h2 className="mx-auto mt-5 max-w-[18ch] text-center font-display text-4xl font-medium tracking-tight sm:text-5xl">
            <FoldText
              text="You stay in flow. SPEAK handles the rest."
              splitBy="word"
              hinge="top"
              trigger="scroll"
              duration={0.6}
              stagger={0.03}
              ease="power3.out"
              fontSize="1em"
              fontWeight={500}
              color="#d1e4fa"
              style={{ lineHeight: "1.14", letterSpacing: "-0.01em" }}
            />
          </h2>
          <Reveal delay={0.14}>
            <p className="mx-auto mt-5 max-w-[54ch] text-center text-[15px] leading-relaxed text-fog">
              Six parts work as one. You speak once. Text, vision and keys move where you point.
            </p>
          </Reveal>
        </ScrollFloat>

        <div className="mt-16 grid gap-5 md:grid-cols-6">
          <Reveal className="md:col-span-3" delay={0.05}>
            <PillarCard
              index="01"
              icon={Mic}
              title="Instant Dictation"
              copy="You speak into the local mic. SPEAK streams to Gemini Live. Characters land at the caret in under a second. Focus never leaves the window."
              demo={
                <div>
                  <div className="flex w-full items-center gap-4 rounded-xl border border-edge bg-white/[0.02] px-4 py-3">
                    <WaveformDots active />
                    <div className="min-w-0 flex-1">
                      <p className="font-mono text-[10px] uppercase tracking-[0.16em] text-blueprint">ctrl + space held</p>
                      <p className="truncate text-[12.5px] text-mist">streaming to caret</p>
                    </div>
                    <span className="rounded-full border border-edge px-2.5 py-1 font-mono text-[10px] tabular-nums text-token-green">
                      142MS
                    </span>
                  </div>
                  <div className="mt-3 flex items-center gap-1.5 px-1">
                    <KeyCap>Ctrl</KeyCap>
                    <KeyCap>Space</KeyCap>
                    <span className="ml-2 font-mono text-[10px] uppercase tracking-[0.14em] text-fog/70">global toggle</span>
                  </div>
                </div>
              }
            />
          </Reveal>

          <Reveal className="md:col-span-3" delay={0.12}>
            <PillarCard
              index="02"
              icon={Monitor}
              title="Live Screen Companion"
              copy="You hold Win+Shift. SPEAK streams mic plus viewport. You talk through code. SPEAK reads what you see."
              demo={
                <div className="relative h-24 overflow-hidden rounded-xl border border-edge bg-[#070812]">
                  <div className="absolute inset-x-5 top-4 space-y-2.5" aria-hidden="true">
                    <div className="h-1.5 w-3/4 rounded-full bg-[rgba(152,192,239,0.16)]" />
                    <div className="ml-5 h-1.5 w-1/2 rounded-full bg-[rgba(186,215,247,0.1)]" />
                    <div className="ml-5 h-1.5 w-2/3 rounded-full bg-[rgba(186,215,247,0.08)]" />
                    <div className="h-1.5 w-1/3 rounded-full bg-[rgba(152,192,239,0.13)]" />
                  </div>
                  <div className="anim-scan absolute inset-x-0 h-10 bg-gradient-to-b from-transparent via-[rgba(182,217,252,0.09)] to-transparent" />
                  <span className="absolute left-2 top-2 h-3 w-3 border-l border-t border-blueprint/80" />
                  <span className="absolute right-2 top-2 h-3 w-3 border-r border-t border-blueprint/80" />
                  <span className="absolute bottom-2 left-2 h-3 w-3 border-b border-l border-blueprint/80" />
                  <span className="absolute bottom-2 right-2 h-3 w-3 border-b border-r border-blueprint/80" />
                  <span className="absolute bottom-2 left-1/2 -translate-x-1/2 rounded-sm border border-blueprint/40 bg-[rgba(5,6,15,0.9)] px-2 py-0.5 font-mono text-[9px] uppercase tracking-[0.16em] text-blueprint">
                    Win + Shift · viewport live
                  </span>
                </div>
              }
            />
          </Reveal>

          <Reveal className="md:col-span-2" delay={0.05}>
            <PillarCard
              index="03"
              blur="none"
              icon={KeyRound}
              title="Multi-Key Failover"
              copy="You add backup keys. SPEAK swaps on rate limit in 0 ms. Dictation never stalls."
              demo={<FailoverDemo />}
            />
          </Reveal>

          <Reveal className="md:col-span-2" delay={0.12}>
            <PillarCard
              index="04"
              blur="none"
              icon={Gauge}
              title="Smart Token Bar"
              copy="You see green to amber to red. You purge with Ctrl+Win before limits hit."
              demo={<TokenCycleDemo />}
            />
          </Reveal>

          <Reveal className="md:col-span-2" delay={0.19}>
            <PillarCard
              index="05"
              blur="none"
              icon={PenTool}
              title="Screen Canvas"
              copy="You draw neon ink over any window. You point at the bug. Esc clears the layer."
              demo={<NeonInkDemo />}
            />
          </Reveal>

          <Reveal className="md:col-span-6" delay={0.1}>
            <GlassCard tilt className="h-full p-7 sm:p-8">
              <div className="grid items-center gap-7 md:grid-cols-[1fr_1.1fr]">
                <div>
                  <CardHeader index="06" icon={Sparkles} title="One-Tap Refine" />
                  <p className="mt-3 text-[14px] leading-relaxed text-fog">
                    You say <span className="font-mono text-[12.5px] text-mist">“refine this”</span>. Messy speech
                    turns crisp before it hits the wire. Docs, mail and commits read clean.
                  </p>
                </div>
                <RefineDemo />
              </div>
            </GlassCard>
          </Reveal>
        </div>
      </div>
    </section>
  );
}

/* ── Explicit composition. No magic child splitting. ── */

function PillarCard({
  index,
  icon,
  title,
  copy,
  demo,
  className,
  blur,
}: {
  index: string;
  icon: typeof Mic;
  title: string;
  copy: string;
  demo: React.ReactNode;
  className?: string;
  blur?: "sm" | "none";
}) {
  return (
    <GlassCard tilt blur={blur} className={cn("flex h-full flex-col p-7", className)}>
      <PillarInner index={index} icon={icon} title={title} copy={copy} demo={demo} />
    </GlassCard>
  );
}

function PillarInner({
  index,
  icon,
  title,
  copy,
  demo,
}: {
  index: string;
  icon: typeof Mic;
  title: string;
  copy: string;
  demo: React.ReactNode;
}) {
  return (
    <>
      <CardHeader index={index} icon={icon} title={title} />
      <p className="mt-3 text-[14px] leading-relaxed text-fog">{copy}</p>
      <div className="mt-auto pt-6">{demo}</div>
    </>
  );
}

function CardHeader({ index, icon: Icon, title }: { index: string; icon: typeof Mic; title: string }) {
  return (
    <div>
      <div className="flex items-start justify-between">
        <div className="grid h-11 w-11 place-items-center rounded-full border border-edge bg-white/[0.04] shadow-[inset_0_1px_0_rgba(255,255,255,0.12)]">
          <Icon size={18} strokeWidth={1.5} className="text-frost" />
        </div>
        <span className="font-mono text-[11px] tabular-nums text-fog/50">{index}</span>
      </div>
      <h3 className="mt-4 font-display text-xl font-medium leading-snug text-frost">{title}</h3>
    </div>
  );
}

/* ── Live micro-demos ── */

function FailoverDemo() {
  const reduce = useReducedMotion();
  const [active, setActive] = useState(0);
  useEffect(() => {
    if (reduce) return;
    const iv = window.setInterval(() => setActive((a) => (a + 1) % 2), 1700);
    return () => window.clearInterval(iv);
  }, [reduce]);
  return (
    <div className="rounded-xl border border-edge bg-white/[0.02] px-4 py-3.5">
      <div className="flex items-center gap-2.5">
        {["GEMINI_KEY_A", "GEMINI_KEY_B"].map((k, i) => (
          <span
            key={k}
            className={cn(
              "rounded-md border px-2.5 py-1.5 font-mono text-[10.5px] tracking-wide transition-all duration-500",
              active === i
                ? "border-[rgba(34,197,94,0.5)] bg-[rgba(34,197,94,0.1)] text-token-green shadow-[0_0_16px_rgba(34,197,94,0.18)]"
                : "border-edge text-fog/60"
            )}
          >
            {k}
          </span>
        ))}
      </div>
      <p className="mt-2.5 font-mono text-[10px] uppercase tracking-[0.14em] text-fog/70">
        rate limit hits. swap runs in 0ms
      </p>
    </div>
  );
}

function TokenCycleDemo() {
  const reduce = useReducedMotion();
  const phases = [0.24, 0.52, 0.74, 0.93];
  const [phase, setPhase] = useState(0);
  useEffect(() => {
    if (reduce) return;
    const iv = window.setInterval(() => setPhase((p) => (p + 1) % phases.length), 1500);
    return () => window.clearInterval(iv);
  }, [reduce, phases.length]);
  const p = reduce ? 0.42 : phases[phase];
  return (
    <div className="rounded-xl border border-edge bg-white/[0.02] px-4 py-3.5">
      <SmartTokenBar progress={p} tokens={Math.round(128000 * p)} latency={142} tooltip={false} />
      <p className="mt-3 font-mono text-[10px] uppercase tracking-[0.14em] text-fog/70">
        green to amber to red. ctrl+win purges
      </p>
    </div>
  );
}

function NeonInkDemo() {
  return (
    <div className="relative overflow-hidden rounded-xl border border-edge bg-[#070812] px-3 py-2">
      <svg viewBox="0 0 220 64" className="h-16 w-full" aria-hidden="true">
        <motion.path
          d="M8 44 C 34 10, 52 58, 78 30 S 118 8, 138 34 S 186 54, 212 18"
          fill="none"
          stroke="#b6d9fc"
          strokeWidth="2.5"
          strokeLinecap="round"
          style={{ filter: "drop-shadow(0 0 6px rgba(182,217,252,0.7))" }}
          initial={{ pathLength: 0, opacity: 0 }}
          whileInView={{ pathLength: 1, opacity: 1 }}
          viewport={{ once: true, margin: "-40px" }}
          transition={{ duration: 1.6, ease: "easeInOut", delay: 0.25 }}
        />
        <motion.circle
          cx="212"
          cy="18"
          r="4"
          fill="#b6d9fc"
          initial={{ opacity: 0, scale: 0 }}
          whileInView={{ opacity: 1, scale: 1 }}
          viewport={{ once: true }}
          transition={{ delay: 1.7, type: "spring", stiffness: 300, damping: 14 }}
          style={{ filter: "drop-shadow(0 0 8px rgba(182,217,252,0.9))" }}
        />
      </svg>
      <p className="pb-1 text-center font-mono text-[10px] uppercase tracking-[0.14em] text-fog/70">
        freehand over any window. esc clears
      </p>
    </div>
  );
}

const MESSY = "so um the deploy failed because the env var was missing i think, can someone uh check staging";
const CLEAN = "The deploy failed. The env var was missing. Please check staging.";

function RefineDemo() {
  const reduce = useReducedMotion();
  const [polished, setPolished] = useState(false);
  useEffect(() => {
    if (reduce) return;
    const iv = window.setInterval(() => setPolished((v) => !v), 3400);
    return () => window.clearInterval(iv);
  }, [reduce]);
  const show = reduce ? true : polished;
  return (
    <div className="relative h-full min-h-[110px] overflow-hidden rounded-xl border border-edge bg-white/[0.02] p-4">
      <AnimatePresence mode="wait" initial={false}>
        <motion.div
          key={show ? "clean" : "messy"}
          initial={{ opacity: 0, y: 10, filter: "blur(4px)" }}
          animate={{ opacity: 1, y: 0, filter: "blur(0px)" }}
          exit={{ opacity: 0, y: -10, filter: "blur(4px)" }}
          transition={{ duration: 0.45, ease: [0.22, 1, 0.36, 1] }}
        >
          <p className="flex items-center gap-2 font-mono text-[10px] uppercase tracking-[0.16em]">
            {show ? (
              <>
                <Sparkles size={11} strokeWidth={1.5} className="text-blueprint" />
                <span className="text-blueprint">refined output</span>
              </>
            ) : (
              <>
                <Mic size={11} strokeWidth={1.5} className="text-fog" />
                <span className="text-fog">raw speech</span>
              </>
            )}
          </p>
          <p className={cn("mt-2 text-[13.5px] leading-relaxed", show ? "text-frost" : "text-fog")}>{show ? CLEAN : MESSY}</p>
        </motion.div>
      </AnimatePresence>
    </div>
  );
}
