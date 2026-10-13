import { motion, useTransform } from "framer-motion";
import { ArrowUpRight, Check, Smartphone } from "lucide-react";
import { ChapterMark, Eyebrow, GhostButton, PrimaryButton, Reveal, VoiceBars, WaveLogo, useSectionProgress } from "./ui";
import { AUTHOR, GITHUB_INSTALLER_DOWNLOAD_URL, GITHUB_REPO_URL, INSTALLER_FILE, SITE_VERSION, type ModalKind } from "../site";

export function Showcase({ openModal }: { openModal: (m: ModalKind) => void }) {
  const { ref, progress } = useSectionProgress();
  const scale = useTransform(progress, [0, 0.45, 1], [0.7, 1, 1.04]);
  const op = useTransform(progress, [0, 0.25, 0.85, 1], [0, 1, 1, 0.3]);
  const glow = useTransform(progress, [0, 0.5, 1], [0.2, 1, 0.5]);
  const l1 = useTransform(progress, [0.05, 0.4], ["-12%", "0%"]);
  const l2 = useTransform(progress, [0.05, 0.4], ["12%", "0%"]);
  const sub = useTransform(progress, [0.4, 0.6], [0, 1]);

  return (
    <section id="showcase" className="relative bg-ink">
      <div ref={ref} className="relative h-[260vh]">
        <div className="sticky top-0 flex h-screen items-center justify-center overflow-hidden px-6">
          <motion.div
            style={{ opacity: glow }}
            className="pointer-events-none absolute left-1/2 top-1/2 h-[1000px] w-[1000px] -translate-x-1/2 -translate-y-1/2 rounded-full bg-[radial-gradient(circle,rgba(76,141,255,0.28),rgba(121,159,214,0.06)_45%,transparent_68%)]"
          />
          <motion.div style={{ scale, opacity: op }} className="relative text-center">
            <div className="mb-8 flex justify-center">
              <ChapterMark num="VII" title="Epilogue" />
            </div>
            <div className="mb-6 font-mono text-[11px] tracking-[0.3em] text-clay">VOXULA AI IN ACTION</div>
            <h2 className="font-display text-[clamp(2.2rem,8.5vw,7.5rem)] leading-[0.95] text-cream">
              <motion.span style={{ x: l1 }} className="block">Say it.</motion.span>
              <motion.span style={{ x: l2 }} className="block text-ember italic">
                Consider it done.
              </motion.span>
            </h2>
            <motion.div style={{ opacity: sub }} className="mt-10 flex flex-col items-center gap-8">
              <p className="text-lg text-mute">Dictate raw. Say refine. Ship polished.</p>
              <PrimaryButton onClick={() => openModal("download")} icon={false}>
                Get Voxula AI <ArrowUpRight size={18} />
              </PrimaryButton>
            </motion.div>
          </motion.div>
        </div>
      </div>
    </section>
  );
}

export function DownloadFooter({
  openModal,
  openChat,
}: {
  openModal: (m: ModalKind) => void;
  openChat: () => void;
}) {
  return (
    <section id="download" className="relative overflow-hidden bg-ink px-6 pb-10 pt-24 md:px-16">
      <div className="mx-auto max-w-6xl">
        <Reveal y={60}>
          <div className="relative overflow-hidden rounded-[36px] border border-white/10 bg-gradient-to-br from-panel-2 via-panel to-ink-2 p-6 sm:p-8 md:p-16">
            <div className="pointer-events-none absolute -right-24 -top-24 h-[420px] w-[420px] rounded-full bg-[radial-gradient(circle,rgba(76,141,255,0.35),transparent_65%)]" />
            <div className="pointer-events-none absolute -bottom-32 -left-16 h-[360px] w-[360px] rounded-full bg-[radial-gradient(circle,rgba(121,159,214,0.12),transparent_65%)]" />
            <div className="relative grid items-center gap-12 lg:grid-cols-[1.3fr_0.7fr]">
              <div>
                <WaveLogo size={44} />
                <Eyebrow className="mt-8">100% FREE. ENTIRELY YOURS.</Eyebrow>
                <h2 className="font-display mt-5 text-[clamp(2.1rem,6vw,5.2rem)] leading-[0.98] text-cream">
                  Find your voice. <span className="text-ember italic">Get into flow.</span>
                </h2>
                <p className="mt-6 max-w-lg text-lg text-mute">
                  Less between you and your next great idea. New to Voxula AI? Read the{" "}
                  <a href="#/docs" className="text-cream underline decoration-clay underline-offset-4">
                    Docs
                  </a>{" "}
                  first.
                </p>
                <div className="mt-10 flex flex-col items-start gap-5 sm:flex-row sm:items-center">
                  <PrimaryButton onClick={() => openModal("download")} className="w-full sm:w-auto justify-center">
                    Download Voxula AI for Windows <ArrowUpRight size={17} />
                  </PrimaryButton>
                  <button onClick={openChat} className="text-[14px] text-mute underline decoration-white/20 underline-offset-4 transition hover:text-cream hover:decoration-clay">
                    Questions? Ask about Voxula
                  </button>
                </div>
                <div className="mt-8 font-mono text-[12px] text-mute">
                  {SITE_VERSION} · Native x64 · Windows 10 / 11 · Free forever
                </div>
              </div>
              <ul className="space-y-4 text-[14px] text-cream/85">
                {["Free key supported", "No subscription required", "Unsigned build — if Windows warns, click More info then Run anyway"].map((t) => (
                  <li key={t} className="flex items-start gap-3 rounded-2xl border border-white/10 bg-white/[0.03] p-4">
                    <Check size={16} className="mt-0.5 shrink-0 text-sage" />
                    {t}
                  </li>
                ))}
              </ul>
            </div>
          </div>
        </Reveal>

        <Reveal>
          <div className="mt-6 flex flex-col items-start justify-between gap-6 rounded-[28px] border border-white/10 bg-white/[0.02] p-8 md:flex-row md:items-center md:p-10">
            <div className="flex items-center gap-6">
              <div className="flex h-14 w-14 shrink-0 items-center justify-center rounded-2xl bg-clay/12 text-clay">
                <Smartphone size={24} />
              </div>
              <div>
                <h3 className="font-display text-3xl text-cream">Your flow doesn't stop at your desk.</h3>
                <p className="mt-1 text-mute">Take voice notes on the move with the mobile companion.</p>
              </div>
            </div>
            <GhostButton onClick={() => openModal("guide")}>Explore the companion</GhostButton>
          </div>
        </Reveal>

        <footer className="mt-24">
          <div className="hairline" />
          <div className="mt-10 flex flex-col gap-10 md:flex-row md:items-start md:justify-between">
            <a href="#overview" className="flex items-center gap-3">
              <WaveLogo size={30} />
              <div>
                <div className="font-display text-2xl text-cream">Voxula AI</div>
                <div className="font-mono text-[11px] text-mute">by {AUTHOR}</div>
              </div>
            </a>
            <nav className="flex flex-wrap gap-x-8 gap-y-3 text-[14px] text-mute">
              <a href="#/docs" className="transition hover:text-cream">Documentation</a>
              <a href={GITHUB_REPO_URL} target="_blank" rel="noreferrer" className="flex items-center gap-1 transition hover:text-cream">
                GitHub <ArrowUpRight size={13} />
              </a>
              <a href={GITHUB_INSTALLER_DOWNLOAD_URL} download className="flex items-center gap-1 transition hover:text-cream" title={INSTALLER_FILE}>
                Installer (.exe) <ArrowUpRight size={13} />
              </a>
              <a href="#privacy" className="transition hover:text-cream">Keyboard reference</a>
              <button onClick={() => openModal("support")} className="transition hover:text-cream">Support</button>
            </nav>
          </div>
          <div className="mt-12 flex flex-col items-start justify-between gap-4 border-t border-white/[0.07] pt-6 text-[12.5px] text-mute md:flex-row md:items-center">
            <span>© 2026 {AUTHOR}. Built for speed, privacy, and flow.</span>
            <span className="flex items-center gap-2">
              <span className="h-2 w-2 rounded-full bg-sage" style={{ animation: "pulse-dot 1.6s infinite" }} />
              All systems in flow
              <VoiceBars count={10} height={12} />
            </span>
          </div>
          <p className="mt-4 text-center font-mono text-[11px] text-mute">DirectX 11+ · Windows 10 Build 19041+ or Windows 11 · 64-bit</p>
        </footer>
      </div>
    </section>
  );
}
