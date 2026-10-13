import { useEffect, useRef, useState } from "react";
import { motion, useScroll, useTransform } from "framer-motion";
import { Lock, Monitor } from "lucide-react";
import { Capsule } from "./Capsule";
import { GhostButton, KeyCap, PrimaryButton } from "./ui";
import { HERO_PHRASES } from "../data";
import type { DemoState, ModalKind } from "../site";
import { scrollToId } from "../lib/scroll";

function CharLine({ text, delay, ready, italic }: { text: string; delay: number; ready: boolean; italic?: boolean }) {
  return (
    <span className="block overflow-hidden pb-[0.1em]">
      {text.split("").map((c, i) => (
        <motion.span
          key={i}
          className={`inline-block ${italic ? "text-ember italic pr-[0.04em]" : ""}`}
          initial={{ y: "115%", rotate: 8, opacity: 0 }}
          animate={ready ? { y: "0%", rotate: 0, opacity: 1 } : {}}
          transition={{ duration: 1.1, delay: delay + i * 0.045, ease: [0.16, 1, 0.3, 1] }}
        >
          {c === " " ? "\u00A0" : c}
        </motion.span>
      ))}
    </span>
  );
}

const APPS = ["VS Code", "Slack", "Notion", "Word", "Any app"];

export function Hero({
  ready,
  demo,
  openModal,
}: {
  ready: boolean;
  demo: DemoState;
  openModal: (m: ModalKind) => void;
}) {
  // ---------- scroll choreography
  const introRef = useRef<HTMLDivElement>(null);
  const { scrollYProgress: introP } = useScroll({ target: introRef, offset: ["start start", "end start"] });
  const introY = useTransform(introP, [0, 1], [0, -140]);
  const introOpacity = useTransform(introP, [0, 0.7], [1, 0]);
  const glowScale = useTransform(introP, [0, 1], [1, 1.6]);

  const stageRef = useRef<HTMLDivElement>(null);
  const { scrollYProgress: p } = useScroll({ target: stageRef, offset: ["start start", "end end"] });
  const capScale = useTransform(p, [0, 0.35, 1], [0.84, 1, 1]);
  const capY = useTransform(p, [0, 0.35], [160, 0]);
  const capOpacity = useTransform(p, [0, 0.2], [0, 1]);
  const capBlur = useTransform(p, [0, 0.25], ["blur(14px)", "blur(0px)"]);
  const ringScale = useTransform(p, [0, 1], [0.6, 2.8]);
  const ringOpacity = useTransform(p, [0, 0.15, 0.8, 1], [0, 1, 0.8, 0]);
  const leftOp = useTransform(p, [0.3, 0.5], [0, 1]);
  const leftX = useTransform(p, [0.3, 0.5], [-50, 0]);
  const rightOp = useTransform(p, [0.4, 0.6], [0, 1]);
  const rightX = useTransform(p, [0.4, 0.6], [50, 0]);
  const botOp = useTransform(p, [0.5, 0.7], [0, 1]);
  const stageOut = useTransform(p, [0.88, 1], [1, 0]);

  // ---------- idle auto-dictation loop (when simulator isn't being used)
  const [idle, setIdle] = useState("");
  useEffect(() => {
    if (demo.active || demo.text) return;
    let cancelled = false;
    let idx = 0;
    const timers: number[] = [];
    const run = () => {
      if (cancelled) return;
      const phrase = HERO_PHRASES[idx % HERO_PHRASES.length];
      let i = 0;
      const type = () => {
        if (cancelled) return;
        i += 1;
        setIdle(phrase.slice(0, i));
        if (i < phrase.length) timers.push(window.setTimeout(type, 38));
        else {
          timers.push(
            window.setTimeout(() => {
              setIdle("");
              idx += 1;
              timers.push(window.setTimeout(run, 500));
            }, 2200)
          );
        }
      };
      type();
    };
    timers.push(window.setTimeout(run, 1200));
    return () => {
      cancelled = true;
      timers.forEach(clearTimeout);
    };
  }, [demo.active, demo.text]);

  const showDemo = demo.active || !!demo.text;
  const text = showDemo ? demo.text : idle;
  const progress = showDemo ? demo.progress : 12 + idle.length / 12;
  const active = showDemo ? demo.active : idle.length > 0;

  return (
    <section id="overview" className="relative bg-ink">
      {/* ---------- Scene 1: title card */}
      <div ref={introRef} className="relative flex min-h-screen flex-col overflow-hidden">
        <motion.div style={{ scale: glowScale }} className="pointer-events-none absolute inset-0">
          <div className="absolute left-1/2 top-[38%] h-[900px] w-[900px] -translate-x-1/2 -translate-y-1/2 rounded-full bg-[radial-gradient(circle,rgba(76,141,255,0.22),rgba(121,159,214,0.06)_45%,transparent_70%)]" />
          <div className="absolute -left-40 bottom-0 h-[500px] w-[500px] rounded-full bg-[radial-gradient(circle,rgba(121,159,214,0.08),transparent_70%)]" />
        </motion.div>
        <div
          className="pointer-events-none absolute inset-0 opacity-[0.35]"
          style={{
            backgroundImage:
              "linear-gradient(rgba(208,214,224,0.05) 1px, transparent 1px), linear-gradient(90deg, rgba(208,214,224,0.05) 1px, transparent 1px)",
            backgroundSize: "72px 72px",
            maskImage: "radial-gradient(ellipse 70% 60% at 50% 40%, black, transparent)",
            WebkitMaskImage: "radial-gradient(ellipse 70% 60% at 50% 40%, black, transparent)",
          }}
        />

        <motion.div
          style={{ y: introY, opacity: introOpacity }}
          className="relative z-10 mx-auto flex w-full max-w-6xl flex-1 flex-col items-center justify-center px-6 pb-32 pt-36 text-center"
        >
          <motion.div
            initial={{ opacity: 0, y: 14 }}
            animate={ready ? { opacity: 1, y: 0 } : {}}
            transition={{ duration: 1, delay: 0.1 }}
            className="mb-8 flex items-center gap-3 rounded-full border border-white/10 bg-white/[0.03] px-4 py-1.5 font-mono text-[11px] tracking-[0.25em] text-mute backdrop-blur"
          >
            <span className="text-cream">VOXULA AI</span>
            <span className="h-3 w-px bg-white/20" />
            <span className="text-clay">V2.1</span>
          </motion.div>

          <h1 className="font-display text-[clamp(2.4rem,9.5vw,7.5rem)] leading-[0.94] tracking-[-0.03em] text-cream">
            <CharLine text="Your Voice." delay={0.25} ready={ready} />
            <CharLine text="Everywhere." delay={0.75} ready={ready} italic />
          </h1>

          <motion.p
            initial={{ opacity: 0, y: 20, filter: "blur(8px)" }}
            animate={ready ? { opacity: 1, y: 0, filter: "blur(0px)" } : {}}
            transition={{ duration: 1.1, delay: 1.5, ease: [0.16, 1, 0.3, 1] }}
            className="mt-8 max-w-xl text-base leading-relaxed text-mute md:text-xl"
          >
            Press <KeyCap>Ctrl</KeyCap> + <KeyCap>Space</KeyCap> to type into any app. Sub-second, private, free.
          </motion.p>

          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={ready ? { opacity: 1, y: 0 } : {}}
            transition={{ duration: 1, delay: 1.7, ease: [0.16, 1, 0.3, 1] }}
            className="mt-10 flex w-full max-w-md flex-col items-stretch justify-center gap-4 sm:w-auto sm:flex-row sm:items-center"
          >
            <PrimaryButton onClick={() => openModal("download")} className="w-full justify-center sm:w-auto">
              Download for Windows
              <span className="h-4 w-px bg-ink/25" />
              <span className="font-medium text-ink">It's free</span>
            </PrimaryButton>
            <GhostButton onClick={() => scrollToId("simulator")} className="w-full justify-center sm:w-auto">
              Launch web simulator
            </GhostButton>
          </motion.div>

          <motion.div
            initial={{ opacity: 0 }}
            animate={ready ? { opacity: 1 } : {}}
            transition={{ duration: 1.2, delay: 2 }}
            className="mt-10 flex flex-wrap items-center justify-center gap-x-6 gap-y-2 text-[13px] text-mute"
          >
            <span className="flex items-center gap-2">
              <Monitor size={14} className="text-clay" /> Native Windows 11
            </span>
            <span className="hidden h-1 w-1 rounded-full bg-mute/50 sm:block" />
            <span>Free tier included</span>
            <span className="hidden h-1 w-1 rounded-full bg-mute/50 sm:block" />
            <span>Bring your own key</span>
          </motion.div>
        </motion.div>

        {/* compat strip */}
        <div className="relative z-10 border-y border-white/[0.07] bg-ink/60 py-5 backdrop-blur">
          <div className="mx-auto flex max-w-6xl items-center gap-8 px-6">
            <span className="hidden shrink-0 font-mono text-[10.5px] tracking-[0.25em] text-mute md:block">
              WORKS WHERE YOU WORK
            </span>
            <div
              className="relative flex-1 overflow-hidden"
              style={{ maskImage: "linear-gradient(90deg, transparent, black 12%, black 88%, transparent)", WebkitMaskImage: "linear-gradient(90deg, transparent, black 12%, black 88%, transparent)" }}
            >
              <div className="animate-marquee flex w-max gap-14 whitespace-nowrap">
                {[...APPS, ...APPS, ...APPS, ...APPS].map((a, i) => (
                  <span key={i} className="font-display text-2xl italic text-cream/70">
                    {a}
                  </span>
                ))}
              </div>
            </div>
          </div>
        </div>

        <div className="pointer-events-none absolute bottom-24 right-8 z-10 hidden flex-col items-center gap-3 font-mono text-[10px] tracking-[0.3em] text-mute lg:flex">
          <span style={{ writingMode: "vertical-rl" }}>SCROLL</span>
          <motion.span
            className="block h-12 w-px bg-clay/70 origin-top"
            animate={{ scaleY: [0.2, 1, 0.2] }}
            transition={{ duration: 2.2, repeat: Infinity, ease: "easeInOut" }}
          />
        </div>
      </div>

      {/* ---------- Scene 2: the capsule appears */}
      <div ref={stageRef} className="relative h-[240vh]">
        <motion.div
          style={{ opacity: stageOut }}
          className="sticky top-0 flex h-screen items-center justify-center overflow-hidden"
        >
          {/* sound rings */}
          <motion.div style={{ scale: ringScale, opacity: ringOpacity }} className="pointer-events-none absolute left-1/2 top-1/2">
            {[0, 1, 2, 3].map((i) => (
              <span
                key={i}
                className="absolute left-0 top-0 block h-[620px] w-[620px] rounded-full border border-clay/30"
                style={{ animation: `ring 5s ease-out ${i * 1.25}s infinite` }}
              />
            ))}
          </motion.div>
          <div className="pointer-events-none absolute left-1/2 top-1/2 h-[700px] w-[700px] -translate-x-1/2 -translate-y-1/2 rounded-full bg-[radial-gradient(circle,rgba(76,141,255,0.16),transparent_65%)]" />

          <div className="relative z-10 flex w-full max-w-6xl flex-col items-center px-6">
            <motion.div style={{ opacity: capOpacity }} className="mb-6 flex items-center gap-4 font-mono text-[10.5px] tracking-[0.3em] text-mute">
              <span className="h-px w-10 bg-white/20" />
              VOXULA CAPSULE — LIVE
              <span className="h-px w-10 bg-white/20" />
            </motion.div>

            <motion.div style={{ scale: capScale, y: capY, opacity: capOpacity, filter: capBlur }} className="w-full max-w-[min(460px,calc(100vw-3rem))]">
              <Capsule active={active} text={text} progress={progress} openModal={openModal} defaultOpen className="mx-auto" />
            </motion.div>

            {/* orbiting notes */}
            <motion.div
              style={{ opacity: leftOp, x: leftX }}
              className="absolute left-0 top-[18%] hidden max-w-[210px] text-left lg:block"
            >
              <div className="mb-2 flex items-center gap-2 text-sm text-cream">
                <Lock size={14} className="text-clay" /> Private by design
              </div>
              <p className="text-[13px] leading-relaxed text-mute">Keys stay in your vault. Audio only streams while you speak.</p>
            </motion.div>
            <motion.div
              style={{ opacity: rightOp, x: rightX }}
              className="absolute right-0 top-[58%] hidden max-w-[220px] text-right lg:block"
            >
              <div className="mb-2 text-sm text-cream">Sub-second latency</div>
              <p className="text-[13px] leading-relaxed text-mute">Words land at your cursor before the thought cools.</p>
            </motion.div>
            <motion.div style={{ opacity: botOp }} className="mt-10 flex items-center gap-3 text-sm text-mute">
              <KeyCap>ctrl</KeyCap> + <KeyCap>space</KeyCap>
              <span>and you're in flow</span>
            </motion.div>
          </div>
        </motion.div>
      </div>
    </section>
  );
}
