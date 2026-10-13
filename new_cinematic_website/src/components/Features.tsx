import { useRef, type ReactNode } from "react";
import { motion } from "framer-motion";
import { Check, Mic, Sparkles } from "lucide-react";
import { ChapterMark, Eyebrow, KeyCap, Reveal, RiseText } from "./ui";
import { cn } from "../utils/cn";

function GlowCard({ children, className, delay = 0 }: { children: ReactNode; className?: string; delay?: number }) {
  const ref = useRef<HTMLDivElement>(null);
  const onMove = (e: React.MouseEvent) => {
    const r = ref.current!.getBoundingClientRect();
    ref.current!.style.setProperty("--mx", `${e.clientX - r.left}px`);
    ref.current!.style.setProperty("--my", `${e.clientY - r.top}px`);
  };
  return (
    <motion.div
      initial={{ opacity: 0, y: 70, scale: 0.96 }}
      whileInView={{ opacity: 1, y: 0, scale: 1 }}
      viewport={{ once: true, margin: "-8%" }}
      transition={{ duration: 1.1, delay, ease: [0.16, 1, 0.3, 1] }}
      className={className}
    >
      <div
        ref={ref}
        onMouseMove={onMove}
        className="group relative h-full overflow-hidden rounded-[28px] border border-white/10 bg-panel/80 p-7 transition-colors duration-500 hover:border-clay/30 md:p-9"
        style={{ ["--mx" as string]: "50%", ["--my" as string]: "0%" }}
      >
        <div
          className="pointer-events-none absolute inset-0 opacity-0 transition-opacity duration-500 group-hover:opacity-100"
          style={{ background: "radial-gradient(420px circle at var(--mx) var(--my), rgba(76,141,255,0.14), transparent 60%)" }}
        />
        <div className="relative flex h-full flex-col">{children}</div>
      </div>
    </motion.div>
  );
}

function CardHead({ tag, title, body }: { tag: string; title: string; body: string }) {
  return (
    <div>
      <div className="font-mono text-[10.5px] tracking-[0.25em] text-clay">{tag}</div>
      <h3 className="font-display mt-3 text-[clamp(1.8rem,3vw,2.6rem)] leading-[1.05] text-cream">{title}</h3>
      <p className="mt-3 max-w-md text-[15px] leading-relaxed text-mute">{body}</p>
    </div>
  );
}

function Foot({ children }: { children: ReactNode }) {
  return <div className="mt-auto flex items-center pt-8 font-mono text-[11.5px] text-mute">{children}</div>;
}

const WAVE = [10, 18, 30, 44, 34, 22, 40, 26, 34, 20, 30, 16, 26, 14, 24, 12, 22, 12, 20, 11, 18, 10, 16, 10, 14, 9, 12];

export function Features() {
  return (
    <section id="features" className="relative bg-ink px-6 py-32 md:px-16 md:py-44">
      <div className="pointer-events-none absolute left-1/2 top-0 h-[500px] w-[900px] -translate-x-1/2 bg-[radial-gradient(ellipse,rgba(76,141,255,0.09),transparent_70%)]" />
      <div className="relative mx-auto max-w-6xl">
        <Reveal>
          <ChapterMark num="IV" title="The toolkit" />
        </Reveal>
        <Reveal delay={0.05} className="mt-8">
          <Eyebrow>FEATURES</Eyebrow>
        </Reveal>
        <h2 className="font-display mt-5 text-[clamp(2.6rem,7vw,6rem)] leading-[0.98] text-cream">
          <RiseText text="Quietly" /> <RiseText text="powerful." className="text-ember italic" delay={0.15} />
        </h2>
        <Reveal delay={0.15}>
          <p className="mt-6 max-w-xl text-lg text-mute">
            Six capabilities. One shortcut. Say refine, polish, or elaborate — the session rewrites itself. Full guide in{" "}
            <a href="#/docs" className="text-cream underline decoration-clay/60 underline-offset-4 hover:decoration-clay">
              Docs
            </a>
            .
          </p>
        </Reveal>

        <div className="mt-20 grid grid-cols-1 gap-5 md:grid-cols-6">
          {/* 1 voice */}
          <GlowCard className="md:col-span-4">
            <CardHead
              tag="INSTANT DICTATION"
              title="Your voice. Direct to cursor."
              body="Live dictation streamed at 16 kHz and typed at your cursor — any app, sub-second, multilingual auto-detect."
            />
            <div className="mt-8 flex items-center gap-6">
              <div className="relative flex h-20 w-20 shrink-0 items-center justify-center rounded-full border border-clay/40 bg-clay/10 text-clay">
                <span className="absolute inset-0 rounded-full border border-clay/40" style={{ animation: "ring 2.4s ease-out infinite", left: "50%", top: "50%", width: "100%", height: "100%" }} />
                <Mic size={26} />
              </div>
              <div className="flex h-20 flex-1 items-center gap-[3px] overflow-hidden">
                {WAVE.concat([...WAVE].reverse()).map((h, i) => (
                  <span
                    key={i}
                    className="w-[3px] shrink-0 rounded-full bg-gradient-to-t from-clay to-amber"
                    style={{ height: `${h * 1.6}%`, animation: `bar ${1 + (i % 6) * 0.2}s ease-in-out ${i * 0.04}s infinite`, opacity: 0.35 + h / 80 }}
                  />
                ))}
              </div>
            </div>
            <Foot>
              <KeyCap>Ctrl</KeyCap>
              <span className="mx-1.5">+</span>
              <KeyCap>Space</KeyCap>
            </Foot>
          </GlowCard>

          {/* 2 vision */}
          <GlowCard className="md:col-span-2" delay={0.1}>
            <CardHead
              tag="MULTIMODAL COMPANION"
              title="An AI that sees — and acts."
              body={`A voice companion on the AI Engine: optional ~1 fps screen share plus voice desktop control — "click Send", "scroll down" — narrated step by step.`}
            />
            <div className="relative mt-6 overflow-hidden rounded-xl border border-white/10 bg-ink/70">
              <div className="flex gap-1.5 border-b border-white/[0.07] px-3 py-2">
                {[0, 1, 2].map((i) => <span key={i} className="h-1.5 w-1.5 rounded-full bg-white/20" />)}
              </div>
              <div className="relative space-y-2 p-4">
                <div className="h-2 w-2/3 rounded bg-white/10" />
                <div className="h-2 w-full rounded bg-white/[0.06]" />
                <div className="relative mt-3 inline-flex rounded-lg bg-clay px-4 py-1.5 text-xs font-medium text-ink">
                  Send
                  <motion.span
                    animate={{ scale: [1, 1.15, 1] }}
                    transition={{ duration: 2, repeat: Infinity }}
                    className="absolute -inset-1.5 rounded-xl border border-clay"
                  />
                </div>
                <span className="absolute right-3 top-3 flex items-center gap-1 rounded-full bg-sage/15 px-2 py-0.5 font-mono text-[9px] text-sage">
                  <span className="h-1 w-1 rounded-full bg-sage" /> Live
                </span>
                <span className="absolute bottom-2 left-3 font-mono text-[9px] tracking-widest text-clay">AI VISION</span>
              </div>
            </div>
            <Foot>
              <KeyCap>Win</KeyCap>
              <span className="mx-1.5">+</span>
              <KeyCap>Shift</KeyCap>
            </Foot>
          </GlowCard>

          {/* 3 keys */}
          <GlowCard className="md:col-span-2" delay={0.05}>
            <CardHead
              tag="MULTI-KEY ENGINE"
              title="Stay in flow. Never in a queue."
              body="Primary + backup keys in Windows Credential Manager. On rate limits or drops, Voxula AI rotates keys and reconnects."
            />
            <div className="mt-6 space-y-2.5">
              <div className="flex items-center justify-between rounded-xl border border-white/10 bg-ink/60 px-4 py-3 text-sm">
                <span className="flex items-center gap-2.5 text-cream">
                  <span className="h-2 w-2 rounded-full bg-sage" style={{ animation: "pulse-dot 1.6s infinite" }} /> Primary key
                </span>
                <span className="font-mono text-xs text-mute">AIza••••</span>
              </div>
              <div className="flex items-center justify-between rounded-xl border border-white/10 bg-ink/60 px-4 py-3 text-sm">
                <span className="flex items-center gap-2.5 text-cream">
                  <Check size={14} className="text-sage" /> Backup key
                </span>
                <span className="font-mono text-xs text-mute">standby</span>
              </div>
            </div>
            <Foot>Always connected</Foot>
          </GlowCard>

          {/* 4 context */}
          <GlowCard className="md:col-span-4" delay={0.1}>
            <CardHead
              tag="SMART CONTEXT"
              title="Full context. Full control."
              body="Live token bar: green 0–60%, orange 61–85%, red 86–100%. Hover for exact tokens and session time. Purge anytime."
            />
            <div className="mt-8 rounded-2xl border border-white/10 bg-ink/60 p-5">
              <div className="mb-3 flex items-baseline justify-between font-mono text-[11px] text-mute">
                <span>Session context</span>
                <span>
                  <span className="text-cream">18,420</span> /128k
                </span>
              </div>
              <div className="flex gap-1">
                {Array.from({ length: 28 }).map((_, i) => (
                  <motion.span
                    key={i}
                    initial={{ scaleY: 0.4, opacity: 0.2 }}
                    whileInView={{ scaleY: 1, opacity: 1 }}
                    viewport={{ once: true }}
                    transition={{ delay: 0.4 + i * 0.03, duration: 0.5 }}
                    className={cn("h-6 flex-1 rounded-[3px]", i < 8 ? "bg-sage" : "bg-white/[0.08]")}
                  />
                ))}
              </div>
              <div className="mt-4 flex items-center gap-2 text-[13px] text-mute">
                <span className="h-2 w-2 rounded-full bg-sage" /> Plenty of room to think
              </div>
            </div>
            <Foot>
              <KeyCap>Ctrl</KeyCap>
              <span className="mx-1.5">+</span>
              <KeyCap>Win</KeyCap>
            </Foot>
          </GlowCard>

          {/* 5 custom */}
          <GlowCard className="md:col-span-3">
            <CardHead
              tag="CUSTOM ACTIONS"
              title="Teach it your own words."
              body={`Up to 3 custom refine actions with your own trigger words — say "summarize" and the whole session obeys. Craft them in Settings → Refine.`}
            />
            <div className="mt-8 flex flex-wrap gap-2.5">
              <motion.span
                animate={{ boxShadow: ["0 0 0 0 rgba(76,141,255,0.5)", "0 0 0 10px rgba(76,141,255,0)"] }}
                transition={{ duration: 1.8, repeat: Infinity }}
                className="rounded-full border border-clay bg-clay/15 px-4 py-1.5 font-mono text-sm text-clay"
              >
                summarize
              </motion.span>
              <span className="rounded-full border border-white/10 px-4 py-1.5 font-mono text-sm text-mute">elaborate</span>
              <span className="rounded-full border border-white/10 px-4 py-1.5 font-mono text-sm text-mute">polish</span>
            </div>
            <Foot>Settings → Refine</Foot>
          </GlowCard>

          {/* 6 refine */}
          <GlowCard className="md:col-span-3" delay={0.1}>
            <CardHead
              tag="REFINE & POLISH"
              title="Say “refine” — it refines."
              body="Say refine, polish, or elaborate and the whole session is deleted and retyped, cleaner. Self-correction aware, plus 3 custom actions."
            />
            <div className="mt-6 space-y-2">
              <div className="rounded-xl border border-white/10 bg-ink/60 px-4 py-3 text-[13px] italic text-mute line-through decoration-clay/50">
                um, so here's what I'm thinking...
              </div>
              <div className="flex items-center gap-3 rounded-xl border border-clay/40 bg-clay/10 px-4 py-3 text-[14px] text-cream">
                <Sparkles size={15} className="shrink-0 text-clay" /> A clear idea. Beautifully expressed.
              </div>
            </div>
            <Foot>Say “refine”</Foot>
          </GlowCard>
        </div>
      </div>
    </section>
  );
}
