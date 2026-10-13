import { motion, useTransform } from "framer-motion";
import { Combine, Cpu, Wallet } from "lucide-react";
import { ChapterMark, Eyebrow, Reveal, RiseText, ScrollWords, useSectionProgress } from "./ui";

function Strike({ label, price, delay }: { label: string; price: string; delay: number }) {
  return (
    <div className="relative flex items-center justify-between gap-4 border-b border-white/10 py-4 sm:py-5">
      <span className="text-sm sm:text-lg text-cream/80">{label}</span>
      <span className="relative font-display text-2xl sm:text-3xl text-mute">
        {price}
        <motion.span
          initial={{ scaleX: 0 }}
          whileInView={{ scaleX: 1 }}
          viewport={{ once: true, margin: "-20%" }}
          transition={{ duration: 0.7, delay, ease: [0.76, 0, 0.24, 1] }}
          className="absolute left-[-6%] top-1/2 h-[2px] w-[112%] origin-left bg-clay"
        />
      </span>
    </div>
  );
}

export function Manifesto() {
  const { ref, progress } = useSectionProgress();
  const typeW = useTransform(progress, [0.25, 0.75], ["0%", "27%"]);
  const speakW = useTransform(progress, [0.3, 0.85], ["0%", "100%"]);
  const barsOp = useTransform(progress, [0.2, 0.35], [0, 1]);
  const lineH = useTransform(progress, [0, 1], ["0%", "100%"]);

  return (
    <div className="relative bg-ink">
      {/* Mobile view (< lg) */}
      <div className="px-6 py-24 lg:hidden">
        <div className="mx-auto max-w-xl">
          <ChapterMark num="I" title="The weight of typing" />
          <p className="font-display mt-8 text-[clamp(1.9rem,6.5vw,3.2rem)] leading-[1.12] text-cream">
            Thoughts move at the speed of <span className="text-clay">speech</span>. Fingers don't. Voice tools charge you <span className="text-amber">monthly</span>, or melt your <span className="text-clay">CPU</span> running local models. We wanted something <span className="text-ember italic">quieter</span>.
          </p>
          <div className="mt-12 space-y-5">
            <div>
              <div className="mb-2 flex justify-between font-mono text-[11px] tracking-[0.2em] text-mute">
                <span>TYPING</span>
                <span>~40 WPM</span>
              </div>
              <div className="h-2 overflow-hidden rounded-full bg-white/[0.07]">
                <div style={{ width: "27%" }} className="h-full rounded-full bg-mute/60" />
              </div>
            </div>
            <div>
              <div className="mb-2 flex justify-between font-mono text-[11px] tracking-[0.2em] text-clay">
                <span>SPEAKING</span>
                <span>~150 WPM</span>
              </div>
              <div className="h-2 overflow-hidden rounded-full bg-white/[0.07]">
                <div style={{ width: "100%" }} className="h-full rounded-full bg-gradient-to-r from-clay to-amber" />
              </div>
            </div>
            <p className="pt-2 text-xs text-mute">Typical averages. Illustrative.</p>
          </div>
        </div>
      </div>

      {/* Desktop view (lg:block): Cinematic scroll scrubber */}
      <div ref={ref} className="relative hidden h-[320vh] lg:block">
        <div className="sticky top-0 flex h-screen flex-col justify-center overflow-hidden">
          <div className="pointer-events-none absolute right-0 top-1/2 h-[700px] w-[700px] -translate-y-1/2 translate-x-1/3 rounded-full bg-[radial-gradient(circle,rgba(76,141,255,0.12),transparent_65%)]" />
          <motion.div style={{ height: lineH }} className="absolute left-6 top-0 w-px bg-gradient-to-b from-clay/0 via-clay/60 to-clay/0 md:left-12" />
          <div className="mx-auto w-full max-w-6xl px-6 md:px-16">
            <ChapterMark num="I" title="The weight of typing" />
            <ScrollWords
              progress={progress}
              start={0.02}
              end={0.6}
              highlights={["speech", "quieter", "monthly", "cpu"]}
              className="font-display mt-10 text-[clamp(2rem,5.2vw,4.6rem)] leading-[1.08] text-cream"
              text="Thoughts move at the speed of speech. Fingers don't. Voice tools charge you monthly, or melt your CPU running local models. We wanted something quieter."
            />
            <motion.div style={{ opacity: barsOp }} className="mt-14 max-w-2xl space-y-5">
              <div>
                <div className="mb-2 flex justify-between font-mono text-[11px] tracking-[0.2em] text-mute">
                  <span>TYPING</span>
                  <span>~40 WPM</span>
                </div>
                <div className="h-2 overflow-hidden rounded-full bg-white/[0.07]">
                  <motion.div style={{ width: typeW }} className="h-full rounded-full bg-mute/60" />
                </div>
              </div>
              <div>
                <div className="mb-2 flex justify-between font-mono text-[11px] tracking-[0.2em] text-clay">
                  <span>SPEAKING</span>
                  <span>~150 WPM</span>
                </div>
                <div className="h-2 overflow-hidden rounded-full bg-white/[0.07]">
                  <motion.div style={{ width: speakW }} className="h-full rounded-full bg-gradient-to-r from-clay to-amber" />
                </div>
              </div>
              <p className="pt-2 text-xs text-mute">Typical averages. Illustrative.</p>
            </motion.div>
          </div>
        </div>
      </div>
    </div>
  );
}


const POINTS = [
  { icon: Wallet, title: "No subscriptions.", body: "Voice should not cost monthly. Free tier included." },
  { icon: Cpu, title: "Sips CPU.", body: "No heavy local models. Cloud transcription, tray-idle footprint." },
  { icon: Combine, title: "Copilot plus dictation.", body: "A screen-seeing assistant and instant typer in one flow." },
];

export function About() {
  return (
    <section id="about" className="relative bg-ink px-6 pb-40 pt-20 md:px-16">
      <div className="hairline mx-auto mb-24 max-w-6xl" />
      <div className="mx-auto grid max-w-6xl gap-16 lg:grid-cols-[1.1fr_0.9fr]">
        <div>
          <Reveal>
            <Eyebrow>WHY VOXULA EXISTS</Eyebrow>
          </Reveal>
          <h2 className="font-display mt-6 text-[clamp(2.1rem,6vw,5rem)] leading-[1.02] text-cream">
            <RiseText text="Built because the alternatives cost too much." />
          </h2>
          <Reveal delay={0.1}>
            <p className="mt-6 max-w-lg text-lg text-mute">
              Subscription voice tools or CPU-hungry local models. Voxula is neither — one free, featherweight Windows app.
            </p>
          </Reveal>
          <Reveal delay={0.15}>
            <p className="mt-10 max-w-xl border-l-2 border-clay/60 pl-6 text-[17px] leading-relaxed text-cream/85">
              Great voice tools either charge monthly or hog the CPU running local models. Voxula AI is an always-on voice
              copilot and sub-second dictation in one tray app that idles quietly until you call it. Bring a free key. That is
              the whole business model.
            </p>
          </Reveal>
        </div>

        <Reveal delay={0.1} className="self-center">
          <div className="rounded-3xl border border-white/10 bg-panel/70 p-8 backdrop-blur">
            <div className="mb-2 font-mono text-[10.5px] tracking-[0.25em] text-mute">THE MONTHLY BILL</div>
            <Strike label="Voice dictation subscription" price="$12/mo" delay={0.3} />
            <Strike label="Local model, 8 GB of RAM" price="100% CPU" delay={0.7} />
            <div className="flex items-center justify-between pt-6">
              <span className="text-lg text-cream">Voxula AI</span>
              <motion.span
                initial={{ opacity: 0, scale: 0.7 }}
                whileInView={{ opacity: 1, scale: 1 }}
                viewport={{ once: true }}
                transition={{ duration: 0.8, delay: 1.2, ease: [0.16, 1, 0.3, 1] }}
                className="font-display text-ember text-5xl"
              >
                $0 · idle
              </motion.span>
            </div>
          </div>
        </Reveal>
      </div>

      <div className="mx-auto mt-24 grid max-w-6xl gap-5 md:grid-cols-3">
        {POINTS.map((p, i) => (
          <Reveal key={p.title} delay={i * 0.12}>
            <div className="group h-full rounded-3xl border border-white/10 bg-gradient-to-b from-white/[0.04] to-transparent p-8 transition-colors duration-500 hover:border-clay/40">
              <div className="mb-8 flex h-12 w-12 items-center justify-center rounded-2xl bg-clay/12 text-clay transition-transform duration-500 group-hover:-rotate-6 group-hover:scale-110">
                <p.icon size={22} />
              </div>
              <h3 className="font-display text-3xl text-cream">{p.title}</h3>
              <p className="mt-3 text-[15px] leading-relaxed text-mute">{p.body}</p>
            </div>
          </Reveal>
        ))}
      </div>
    </section>
  );
}
