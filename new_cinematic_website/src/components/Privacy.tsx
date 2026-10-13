import { motion, useScroll, useTransform } from "framer-motion";
import { useRef } from "react";
import { Keyboard, Layers, LockKeyhole, ShieldCheck } from "lucide-react";
import { ChapterMark, Eyebrow, KeyCap, Reveal, RiseText } from "./ui";
import { SHORTCUTS } from "../data";

const PILLARS = [
  { icon: LockKeyhole, title: "Your keys. Under lock.", body: "Windows Credential Manager encrypts API keys locally with DPAPI." },
  { icon: ShieldCheck, title: "Direct line. No middleman.", body: "Encrypted connection straight to the voice service. No tracking." },
  { icon: Layers, title: "Almost invisible.", body: "Idles quietly in your tray until inspiration strikes." },
];

export function Privacy() {
  const ref = useRef<HTMLDivElement>(null);
  const { scrollYProgress } = useScroll({ target: ref, offset: ["start end", "end start"] });
  const rot = useTransform(scrollYProgress, [0, 1], [0, 220]);
  const rotBack = useTransform(scrollYProgress, [0, 1], [0, -160]);
  const lockScale = useTransform(scrollYProgress, [0.1, 0.4], [0.8, 1]);

  return (
    <section id="privacy" ref={ref} className="relative overflow-hidden bg-paper px-6 py-32 text-ink md:px-16 md:py-44">
      <div className="relative mx-auto max-w-6xl">
        <Reveal>
          <ChapterMark num="VI" title="The vault" tone="light" />
        </Reveal>
        <Reveal delay={0.05} className="mt-8">
          <Eyebrow tone="light">PRIVACY</Eyebrow>
        </Reveal>
        <h2 className="font-display mt-5 text-[clamp(2.6rem,7vw,6rem)] leading-[0.98]">
          <RiseText text="Your words" /> <RiseText text="are yours." className="italic text-clay-deep" delay={0.15} />
        </h2>
        <Reveal delay={0.15}>
          <p className="mt-6 max-w-xl text-lg text-mute-dark">Local DPAPI encryption. Zero telemetry. No compromises.</p>
        </Reveal>

        <div className="mt-20 grid items-center gap-14 lg:grid-cols-[0.9fr_1.1fr]">
          <Reveal>
            <div className="relative mx-auto flex aspect-square w-full max-w-[280px] sm:max-w-[420px] items-center justify-center">
              <motion.div style={{ rotate: rot }} className="absolute inset-0 rounded-full border border-dashed border-ink/25" />
              <motion.div style={{ rotate: rotBack }} className="absolute inset-[12%] rounded-full border border-ink/15">
                <span className="absolute left-1/2 top-0 h-2.5 w-2.5 -translate-x-1/2 -translate-y-1/2 rounded-full bg-clay" />
                <span className="absolute bottom-0 left-1/2 h-2 w-2 -translate-x-1/2 translate-y-1/2 rounded-full bg-ink/40" />
              </motion.div>
              <div className="absolute inset-[26%] rounded-full bg-[radial-gradient(circle,rgba(76,141,255,0.3),transparent_70%)]" />
              <motion.div
                style={{ scale: lockScale }}
                className="relative flex h-24 w-24 sm:h-32 sm:w-32 items-center justify-center rounded-full bg-ink text-clay shadow-[0_30px_60px_-20px_rgba(0,0,0,0.6)]"
              >
                <LockKeyhole size={34} className="sm:hidden" />
                <LockKeyhole size={44} className="hidden sm:block" />
              </motion.div>
              <div className="absolute bottom-[6%] left-1/2 flex -translate-x-1/2 items-center gap-2 whitespace-nowrap rounded-full bg-ink px-4 py-2 font-mono text-[10px] tracking-[0.2em] text-cream">
                <ShieldCheck size={13} className="text-sage" /> ON-DEVICE ENCRYPTION
              </div>
            </div>
            <p className="mt-10 text-center font-display text-2xl italic text-mute-dark">Never our data. Always your voice.</p>
          </Reveal>

          <div>
            <div className="mb-5 flex items-center gap-2 font-mono text-[10.5px] tracking-[0.25em] text-mute-dark">
              <Keyboard size={14} /> BUILT INTO MUSCLE MEMORY
            </div>
            <div className="divide-y divide-ink/10 rounded-3xl border border-ink/10 bg-cream/60 backdrop-blur">
              {SHORTCUTS.map((s, i) => (
                <motion.div
                  key={s.title}
                  initial={{ opacity: 0, x: 40 }}
                  whileInView={{ opacity: 1, x: 0 }}
                  viewport={{ once: true, margin: "-10%" }}
                  transition={{ duration: 0.9, delay: i * 0.12, ease: [0.16, 1, 0.3, 1] }}
                  className="group flex flex-col sm:flex-row items-start sm:items-center justify-between gap-4 px-5 sm:px-6 py-5 transition-colors hover:bg-white/50"
                >
                  <div>
                    <div className="font-display text-2xl">{s.title}</div>
                    <div className="mt-1 text-[14px] text-mute-dark">{s.body}</div>
                  </div>
                  <div className="flex shrink-0 items-center gap-1.5 transition-transform duration-300 group-hover:translate-y-0.5">
                    {s.keys.map((k, j) => (
                      <span key={k} className="flex items-center gap-1.5">
                        {j > 0 && <span className="text-mute-dark">+</span>}
                        <KeyCap tone="light" className="px-2.5 py-1.5 text-xs">{k}</KeyCap>
                      </span>
                    ))}
                  </div>
                </motion.div>
              ))}
            </div>
          </div>
        </div>

        <div className="mt-20 grid gap-5 md:grid-cols-3">
          {PILLARS.map((p, i) => (
            <Reveal key={p.title} delay={i * 0.12}>
              <div className="h-full rounded-3xl bg-ink p-8 text-cream transition-transform duration-500 hover:-translate-y-1.5">
                <p.icon size={24} className="text-clay" />
                <h3 className="font-display mt-8 text-3xl">{p.title}</h3>
                <p className="mt-3 text-[15px] leading-relaxed text-mute">{p.body}</p>
              </div>
            </Reveal>
          ))}
        </div>
        <Reveal>
          <p className="mt-12 text-center font-mono text-[11.5px] leading-relaxed text-mute-dark">
            Voice refine triggers: refine · polish · elaborate (plus expand alias and up to 3 custom actions in Settings → Refine).
          </p>
        </Reveal>
      </div>
    </section>
  );
}
