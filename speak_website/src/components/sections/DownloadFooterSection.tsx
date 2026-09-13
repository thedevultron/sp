import { useState } from "react";
import { AnimatePresence, motion } from "framer-motion";
import { CheckCircle2, Download, Smartphone } from "lucide-react";
import { EyebrowLabel } from "../ui/EyebrowLabel";
import { Reveal } from "../ui/Reveal";
import { VoidVioletButton } from "../ui/VoidVioletButton";
import { ScrollFloat } from "../cinematic/TextMotion";
import { ProofMetric } from "../cinematic/ProofMetric";
import { AdaptiveRays } from "../cinematic/AdaptiveRays";
import BlurText from "../BlurText";
import Magnet from "../Magnet";
import GradualBlur from "../GradualBlur";
import { getQualityTier } from "../../lib/perf";
import { INSTALLER_FILE, INSTALLER_SIZE_MB, INSTALLER_URL, INSTALLER_VERSION } from "../../lib/download";

interface DownloadFooterSectionProps {
  onNavigate: (id: string) => void;
}

const SPECS = [`Version ${INSTALLER_VERSION}`, "Native x64", "Windows 10/11", "Free Gemini key"];

const FOOTER_LINKS: { label: string; target: string }[] = [
  { label: "Documentation", target: "pillars" },
  { label: "Keyboard Reference", target: "security" },
  { label: "Support", target: "mailto:support@speakvoice.app" },
];

export function DownloadFooterSection({ onNavigate }: DownloadFooterSectionProps) {
  const [started, setStarted] = useState(false);
  // GradualBlur stacks several backdrop-blur layers — CSS hairline on weak GPUs.
  const richBlur =
    getQualityTier() !== "low" &&
    (typeof window === "undefined" || !window.matchMedia("(pointer: coarse)").matches);
  const magnetOff =
    getQualityTier() === "low" ||
    (typeof window !== "undefined" && window.matchMedia("(pointer: coarse)").matches);

  return (
    <section id="download" className="relative pt-10 pb-14 sm:pt-16">
      <div className="mx-auto max-w-[1200px] px-6">
        <ScrollFloat>
          <Reveal>
            <EyebrowLabel>Free for builders</EyebrowLabel>
          </Reveal>
          <h2 className="mx-auto mt-6 text-center font-display text-4xl font-medium tracking-tight text-frost sm:text-6xl">
            <BlurText
              text={`Download SPEAK v${INSTALLER_VERSION}`}
              delay={90}
              animateBy="words"
              direction="top"
              stepDuration={0.4}
              className="justify-center"
            />
          </h2>
          <Reveal delay={0.14}>
            <p className="mx-auto mt-6 max-w-[56ch] text-center text-[15.5px] leading-relaxed text-fog">
              You bring a free Gemini key. You install in under a minute. You dictate in any app from the first press.
            </p>
          </Reveal>
          <Reveal delay={0.18}>
            <p className="mt-5 text-center font-mono text-[11px] uppercase tracking-[0.18em] text-fog/70">
              <ProofMetric to={INSTALLER_SIZE_MB} suffix=" MB" className="text-mist" /> · SHA-256 verified · <ProofMetric to={0} className="text-mist" /> trackers
            </p>
          </Reveal>
        </ScrollFloat>

        {/* Download terminal */}
        <Reveal delay={0.2} y={36}>
          <div
            className="glass-widget relative mx-auto mt-12 max-w-[760px] overflow-hidden px-7 py-12 text-center sm:px-12"
            style={{ borderRadius: 16 }}
          >
            <AdaptiveRays className="absolute inset-0 opacity-70" webgpu={false} />
            {/* Static top halos — no blur filter cost */}
            <div
              aria-hidden="true"
              className="pointer-events-none absolute -top-28 left-1/2 h-56 w-[460px] -translate-x-1/2 rounded-full bg-[radial-gradient(closest-side,rgba(152,192,239,0.17),transparent)]"
            />
            <div
              aria-hidden="true"
              className="pointer-events-none absolute -top-20 left-1/2 h-40 w-[260px] -translate-x-1/2 rounded-full bg-[radial-gradient(closest-side,rgba(102,58,243,0.22),transparent)]"
            />

            <div className="relative">
              <Magnet magnetStrength={2.5} padding={80} disabled={magnetOff}>
                <VoidVioletButton
                  size="lg"
                  href={INSTALLER_URL}
                  download={INSTALLER_FILE}
                  onClick={() => setStarted(true)}
                  icon={
                    started ? (
                      <CheckCircle2 size={17} strokeWidth={2} />
                    ) : (
                      <Download size={17} strokeWidth={2} />
                    )
                  }
                >
                  {started ? `${INSTALLER_FILE} · Downloading` : "Download for Windows · Free"}
                </VoidVioletButton>
              </Magnet>

              <div className="mt-4 h-6">
                <AnimatePresence>
                  {started && (
                    <motion.p
                      key="verified"
                      initial={{ opacity: 0, y: 6, filter: "blur(4px)" }}
                      animate={{ opacity: 1, y: 0, filter: "blur(0px)" }}
                      exit={{ opacity: 0 }}
                      transition={{ duration: 0.35 }}
                      className="font-mono text-[11px] tabular-nums text-token-green"
                    >
                      {INSTALLER_SIZE_MB} MB · SHA-256 verified · no telemetry · check your downloads folder
                    </motion.p>
                  )}
                </AnimatePresence>
              </div>

              <ul className="mt-7 flex flex-wrap items-center justify-center gap-x-3 gap-y-2">
                {SPECS.map((s, i) => (
                  <li key={s} className="flex items-center gap-3">
                    {i > 0 && <span aria-hidden="true" className="text-fog/40">·</span>}
                    <span className="font-mono text-[11px] uppercase tracking-[0.12em] text-mist/90">{s}</span>
                  </li>
                ))}
              </ul>

              <div className="mx-auto mt-9 flex max-w-[460px] items-center gap-4 rounded-xl border border-edge bg-white/[0.02] px-5 py-4 text-left transition-all duration-300 hover:border-[rgba(216,236,248,0.26)]">
                <span className="grid h-10 w-10 shrink-0 place-items-center rounded-full border border-edge bg-white/[0.04]">
                  <Smartphone size={17} strokeWidth={1.5} className="text-blueprint" />
                </span>
                <div>
                  <p className="text-[13.5px] font-medium text-frost">Mobile companion</p>
                  <p className="text-[12.5px] leading-snug text-fog">
                    You hand voice notes to mobile and keep moving.
                  </p>
                </div>
              </div>
            </div>
          </div>
        </Reveal>

        {/* Footer */}
        <footer className="relative mt-24 border-t border-edge pt-10">
          {richBlur ? (
            <GradualBlur
              position="top"
              height="5rem"
              strength={1.6}
              divCount={4}
              exponential
              opacity={0.9}
              className="pointer-events-none absolute -top-20 inset-x-0"
            />
          ) : (
            <div
              aria-hidden="true"
              className="pointer-events-none absolute -top-16 inset-x-0 h-16 bg-gradient-to-b from-transparent to-[rgba(5,6,15,0.6)]"
            />
          )}
          <div className="grid gap-10 md:grid-cols-3">
            <div>
              <div className="flex items-center gap-2.5">
                <svg viewBox="0 0 24 24" className="h-5 w-5" aria-hidden="true">
                  <rect x="1" y="1" width="22" height="22" rx="7" fill="rgba(186,214,247,0.06)" stroke="rgba(186,215,247,0.22)" strokeWidth="1" />
                  <rect x="5.5" y="10" width="2" height="4" rx="1" fill="#b6d9fc" />
                  <rect x="9.25" y="7" width="2" height="10" rx="1" fill="#663af3" />
                  <rect x="13" y="9" width="2" height="6" rx="1" fill="#b6d9fc" />
                  <rect x="16.75" y="11" width="2" height="3" rx="1" fill="#b6d9fc" opacity="0.7" />
                </svg>
                <span className="font-display text-[13px] font-semibold tracking-[0.24em] text-frost">SPEAK</span>
              </div>
              <p className="mt-4 max-w-[30ch] text-[13px] leading-relaxed text-fog">
                © 2026 Amir Bagawan. You speak. SPEAK types.
              </p>
            </div>

            <div className="md:justify-self-center">
              <p className="font-mono text-[10px] uppercase tracking-[0.18em] text-fog/60">System requirements</p>
              <p className="mt-4 max-w-[34ch] font-mono text-[11px] leading-relaxed text-fog">
                DirectX 11+ · Windows 10 Build 19041+ or Windows 11 · 64-bit
              </p>
            </div>

            <nav className="flex flex-row gap-6 md:flex-col md:items-end md:gap-3.5" aria-label="Footer">
              {FOOTER_LINKS.map((l) =>
                l.target.startsWith("mailto:") ? (
                  <a
                    key={l.label}
                    href={l.target}
                    className="text-[13px] font-medium text-mist underline-offset-4 transition-colors duration-200 hover:text-white hover:underline"
                  >
                    {l.label}
                  </a>
                ) : (
                  <button
                    key={l.label}
                    type="button"
                    onClick={() => onNavigate(l.target)}
                    className="text-left text-[13px] font-medium text-mist underline-offset-4 transition-colors duration-200 hover:text-white hover:underline md:text-right"
                  >
                    {l.label}
                  </button>
                )
              )}
            </nav>
          </div>

          <p className="mt-12 border-t border-edge/60 pt-6 text-center font-mono text-[10px] uppercase tracking-[0.18em] text-fog/50">
            Powered by Gemini Live · Your voice, your keys, your machine
          </p>
        </footer>
      </div>
    </section>
  );
}
