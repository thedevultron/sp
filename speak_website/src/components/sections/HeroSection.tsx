import { Download, Terminal } from "lucide-react";
import { EyebrowLabel } from "../ui/EyebrowLabel";
import { VoidVioletButton } from "../ui/VoidVioletButton";
import { GhostPillButton } from "../ui/GhostPillButton";
import { KeyCap } from "../ui/KeyCap";
import { Reveal } from "../ui/Reveal";
import { SpeakCapsuleWidget } from "../widget/SpeakCapsuleWidget";
import { AdaptiveRays } from "../cinematic/AdaptiveRays";
import { TextLoop } from "../cinematic/TextMotion";
import { ProofMetric } from "../cinematic/ProofMetric";
import Magnet from "../Magnet";
import { ScrollVelocity } from "../ScrollVelocity";
import FoldText from "../FoldText";
import { getQualityTier, useInViewport } from "../../lib/perf";
import { INSTALLER_FILE, INSTALLER_URL, INSTALLER_VERSION } from "../../lib/download";

interface HeroSectionProps {
  onNavigate: (id: string) => void;
}

const MARQUEE_APPS = [
  "VS Code",
  "Slack",
  "Notion",
  "Word",
  "Figma",
  "Chrome",
  "Windows Terminal",
  "Discord",
  "Obsidian",
  "Gmail",
];

export function HeroSection({ onNavigate }: HeroSectionProps) {
  const velocityMarquee = getQualityTier() !== "low";
  // Magnet attaches a window mousemove listener — skip it on touch / weak GPUs.
  const magnetOff =
    getQualityTier() === "low" ||
    (typeof window !== "undefined" && window.matchMedia("(pointer: coarse)").matches);
  const { ref: mqRef, inView: mqInView } = useInViewport<HTMLDivElement>(0);

  return (
    <section id="top" className="relative overflow-hidden pt-20 pb-10 sm:pt-24">
      {/* WebGPU light rays — quarter-res, 30fps, low-power adapter */}
      <AdaptiveRays
        className="absolute inset-0"
        raysColor="#b6d9fc"
        raysSpeed={0.55}
        intensity={0.9}
        opacity={0.9}
      />
      {/* Jaw-drop ice beam accents */}
      <div
        aria-hidden="true"
        className="pointer-events-none absolute left-1/2 top-[-220px] z-0 h-[480px] w-[820px] -translate-x-1/2 rounded-full bg-[radial-gradient(closest-side,rgba(102,58,243,0.22),transparent_70%)]"
      />
      <div
        aria-hidden="true"
        className="pointer-events-none absolute left-1/2 top-[-140px] z-0 h-[300px] w-[560px] -translate-x-1/2 rounded-full bg-[radial-gradient(closest-side,rgba(216,236,248,0.12),transparent_70%)]"
      />
      <div className="relative z-[1] mx-auto max-w-[1200px] px-6">
        <div className="grid items-center gap-14 lg:grid-cols-[1.04fr_0.96fr]">
          {/* ── Copy column ── */}
          <div>
            <Reveal>
              <EyebrowLabel align="left">SPEAK v{INSTALLER_VERSION} for Windows</EyebrowLabel>
            </Reveal>

            <h1 className="mt-7 font-display text-[clamp(2.9rem,6.2vw,5.2rem)] font-medium leading-[1.06] tracking-[-0.02em] text-frost">
              <FoldText
                text="Your Voice."
                splitBy="word"
                hinge="top"
                trigger="mount"
                duration={0.7}
                stagger={0.09}
                ease="power3.out"
                fontSize="1em"
                fontWeight={500}
                color="#d1e4fa"
              />
              <br />
              <TextLoop
                phrases={["Everywhere.", "In every app.", "At the caret."]}
                interval={2600}
                className="font-display font-medium text-blueprint"
              />
            </h1>

            <Reveal delay={0.16}>
              <p className="mt-5 max-w-[54ch] text-[16.5px] leading-relaxed text-fog">
                Hold <KeyCap>Ctrl</KeyCap> <KeyCap>Space</KeyCap>. You speak. SPEAK types
                into VS Code, Slack, Notion and Word in 142 ms through{" "}
                <span className="text-mist">Gemini Live</span>.
              </p>
            </Reveal>

            <Reveal delay={0.24}>
              <div className="mt-9 flex flex-wrap items-center gap-3.5">
                <Magnet magnetStrength={3} padding={60} disabled={magnetOff}>
                  <VoidVioletButton
                    size="lg"
                    href={INSTALLER_URL}
                    download={INSTALLER_FILE}
                    icon={<Download size={17} strokeWidth={2} />}
                  >
                    Download for Windows
                  </VoidVioletButton>
                </Magnet>
                <Magnet magnetStrength={4} padding={60} disabled={magnetOff}>
                  <GhostPillButton onClick={() => onNavigate("simulator")} icon={<Terminal size={16} strokeWidth={1.5} />}>
                    Try live simulator
                  </GhostPillButton>
                </Magnet>
              </div>
            </Reveal>

            <Reveal delay={0.3}>
              <p className="mt-8 flex flex-wrap gap-x-7 gap-y-2 font-mono text-[12px] uppercase tracking-[0.14em] text-fog/80">
                <span>
                  <ProofMetric to={142} suffix="ms" className="text-frost" /> to caret
                </span>
                <span>
                  <ProofMetric to={99.4} suffix="%" className="text-frost" /> accuracy
                </span>
                <span>
                  <ProofMetric to={0} className="text-frost" /> servers in path
                </span>
              </p>
            </Reveal>
          </div>

          {/* ── Capsule scene ── */}
          <Reveal delay={0.2} y={40}>
            <div className="relative mx-auto w-full max-w-[620px] lg:ml-auto">
              {/* Static halos — zero filter cost */}
              <div
                aria-hidden="true"
                className="halo-static halo-ice absolute -inset-14"
              />
              <div
                aria-hidden="true"
                className="halo-static halo-violet absolute -right-8 -bottom-10 h-56 w-56"
              />

              <div className="anim-float relative">
                <SpeakCapsuleWidget />
              </div>

              {/* Floating telemetry chips */}
              <div className="anim-float-late absolute -top-5 left-2 hidden items-center gap-2 rounded-full border border-edge bg-[rgba(5,6,15,0.88)] px-3.5 py-2 shadow-[var(--shadow-widget)] sm:flex">
                <span className="anim-ping-soft h-1.5 w-1.5 rounded-full bg-token-green" />
                <span className="font-mono text-[10px] uppercase tracking-[0.14em] text-mist">
                  Gemini Live WS · Connected
                </span>
              </div>
              <div className="anim-float absolute -bottom-6 right-2 hidden rounded-full border border-edge bg-[rgba(5,6,15,0.88)] px-3.5 py-2 shadow-[var(--shadow-widget)] sm:block">
                <span className="font-mono text-[10px] uppercase tracking-[0.14em] text-blueprint tabular-nums">
                  142ms to caret
                </span>
              </div>
            </div>
          </Reveal>
        </div>

        <div className="relative mt-20">
          <div ref={mqRef} className="velocity-mask relative overflow-hidden border-y border-edge/60 py-4">
            {velocityMarquee && mqInView ? (
              <ScrollVelocity
                texts={[
                  <span key="apps" className="flex items-center">
                    {MARQUEE_APPS.map((name) => (
                      <span key={name} className="flex items-center">
                        <span className="px-6 font-mono text-[12px] font-normal uppercase tracking-[0.2em] text-fog/80">
                          {name}
                        </span>
                        <span aria-hidden="true" className="h-1.5 w-1.5 rotate-45 border border-[rgba(186,215,247,0.3)]" />
                      </span>
                    ))}
                  </span>,
                ]}
                velocity={42}
                numCopies={4}
                damping={60}
                stiffness={260}
                className="font-mono"
                scrollerClassName="flex whitespace-nowrap items-center"
              />
            ) : (
              <div className="anim-marquee flex w-max items-center">
                {[...MARQUEE_APPS, ...MARQUEE_APPS].map((name, i) => (
                  <span key={`${name}-${i}`} className="flex items-center">
                    <span className="px-6 font-mono text-[12px] uppercase tracking-[0.2em] text-fog/80">
                      {name}
                    </span>
                    <span aria-hidden="true" className="h-1.5 w-1.5 rotate-45 border border-[rgba(186,215,247,0.3)]" />
                  </span>
                ))}
              </div>
            )}
          </div>
          <p className="mt-3 text-center font-mono text-[10px] uppercase tracking-[0.22em] text-fog/50">
            You type in any window with a caret
          </p>
        </div>
      </div>
    </section>
  );
}
