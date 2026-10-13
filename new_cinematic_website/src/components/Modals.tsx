import { useEffect, useRef, useState, type ReactNode } from "react";
import { AnimatePresence, motion } from "framer-motion";
import {
  ArrowUpRight,
  BookOpen,
  Check,
  ChevronDown,
  Download,
  Eye,
  EyeOff,
  KeyRound,
  Lock,
  Mail,
  Monitor,
  ShieldCheck,
  Sparkles,
  X,
} from "lucide-react";
import { GhostButton, KeyCap, VoiceBars, WaveLogo } from "./ui";
import {
  GEMINI_KEY_URL,
  GITHUB_INSTALLER_DOWNLOAD_URL,
  GITHUB_REPO_URL,
  INSTALLER_FILE,
  INSTALLER_SIZE,
  QUICK_START_TEXT,
  type ModalKind,
} from "../site";
import { FAQ } from "../data";
import { getLenis, scrollToId } from "../lib/scroll";
import { cn } from "../utils/cn";

const META: Record<Exclude<ModalKind, null>, { eyebrow: string; title: string }> = {
  settings: { eyebrow: "PREFERENCES", title: "Make yourself at home." },
  download: { eyebrow: "YOUR NEXT CHAPTER", title: "Meet Voxula AI v2.1." },
  support: { eyebrow: "HERE TO HELP", title: "Let's keep you in flow." },
  guide: { eyebrow: "FIELD GUIDE", title: "A little guidance. Zero friction." },
};

function InfoBox({ icon, children }: { icon: ReactNode; children: ReactNode }) {
  return (
    <div className="flex gap-3 rounded-2xl border border-white/10 bg-white/[0.03] p-4 text-[13.5px] leading-relaxed text-mute">
      <span className="mt-0.5 shrink-0 text-clay">{icon}</span>
      <div>{children}</div>
    </div>
  );
}

/* ---------------- Settings */
function SettingsBody({ keyValue, setKeyValue }: { keyValue: string; setKeyValue: (k: string) => void }) {
  const [draft, setDraft] = useState(keyValue);
  const [show, setShow] = useState(false);
  const [error, setError] = useState(false);
  const [saved, setSaved] = useState(!!keyValue);

  const submit = (e: React.FormEvent) => {
    e.preventDefault();
    if (draft.trim().length < 20) {
      setError(true);
      setSaved(false);
      return;
    }
    setError(false);
    setKeyValue(draft.trim());
    setSaved(true);
  };

  return (
    <div>
      <p className="text-mute">Explore native app preferences. This preview never sends your key to a server.</p>
      <form onSubmit={submit} className="mt-8 space-y-5">
        <div>
          <div className="mb-2 flex items-center justify-between">
            <label htmlFor="apikey" className="flex items-center gap-2 text-sm text-cream">
              <KeyRound size={15} className="text-clay" /> API key
            </label>
            <span className="font-mono text-[10px] tracking-widest text-mute">SESSION ONLY</span>
          </div>
          <div className="relative">
            <input
              id="apikey"
              type={show ? "text" : "password"}
              value={draft}
              onChange={(e) => {
                setDraft(e.target.value);
                setError(false);
              }}
              placeholder="Paste your API key"
              className={cn(
                "w-full rounded-2xl border bg-ink px-4 py-3.5 pr-12 font-mono text-sm text-cream outline-none transition placeholder:text-mute/50 focus:border-clay",
                error ? "border-red-400/60" : "border-white/10"
              )}
            />
            <button type="button" onClick={() => setShow((s) => !s)} aria-label="Show or hide key" className="absolute right-3 top-1/2 -translate-y-1/2 text-mute hover:text-cream">
              {show ? <EyeOff size={17} /> : <Eye size={17} />}
            </button>
          </div>
          {error && <p className="mt-2 text-[13px] text-red-300">Please enter an API key of at least 20 characters.</p>}
          <a href={GEMINI_KEY_URL} target="_blank" rel="noreferrer" className="mt-3 inline-flex items-center gap-1 text-[13px] text-clay underline-offset-4 hover:underline">
            Get a free API key <ArrowUpRight size={13} />
          </a>
        </div>
        <InfoBox icon={<ShieldCheck size={16} />}>
          The native app stores keys in Windows Credential Manager with DPAPI encryption. This browser preview keeps the key in memory only and does not connect to any AI service.
        </InfoBox>
        <div className="flex flex-wrap items-center gap-4">
          <button type="submit" className="rounded-full bg-clay px-6 py-3 text-sm font-medium text-ink transition hover:-translate-y-0.5">
            Save preview preference
          </button>
          {saved && (
            <span className="flex items-center gap-2 text-[13px] text-sage">
              <Check size={15} /> Saved for this preview session
            </span>
          )}
        </div>
        {saved && (
          <button
            type="button"
            onClick={() => {
              setKeyValue("");
              setDraft("");
              setSaved(false);
            }}
            className="text-[13px] text-mute underline underline-offset-4 hover:text-cream"
          >
            Remove saved key
          </button>
        )}
      </form>
    </div>
  );
}

/* ---------------- Guide */
function GuideBody({ close }: { close: () => void }) {
  const [tab, setTab] = useState<"start" | "shortcuts" | "refine">("start");
  const tabs = [
    { k: "start", l: "Get started" },
    { k: "shortcuts", l: "Shortcuts" },
    { k: "refine", l: "Refine" },
  ] as const;
  return (
    <div>
      <div className="flex gap-1 rounded-full border border-white/10 bg-ink p-1">
        {tabs.map((t) => (
          <button
            key={t.k}
            onClick={() => setTab(t.k)}
            className={cn("relative flex-1 rounded-full py-2 text-[13px] transition-colors", tab === t.k ? "text-ink" : "text-mute hover:text-cream")}
          >
            {tab === t.k && <motion.span layoutId="guideTab" className="absolute inset-0 rounded-full bg-cream" transition={{ type: "spring", stiffness: 400, damping: 34 }} />}
            <span className="relative">{t.l}</span>
          </button>
        ))}
      </div>
      <AnimatePresence mode="wait">
        <motion.div key={tab} initial={{ opacity: 0, y: 12 }} animate={{ opacity: 1, y: 0 }} exit={{ opacity: 0, y: -8 }} transition={{ duration: 0.25 }} className="mt-7">
          {tab === "start" && (
            <div className="space-y-5">
              {[
                { n: "01", t: "Bring your own API key", b: (<>Create a key in <a href={GEMINI_KEY_URL} target="_blank" rel="noreferrer" className="text-clay underline">Google AI Studio</a>. The native app auto-detects GEMINI_API_KEY or your saved vault key.</>) },
                { n: "02", t: "Make any app your workspace", b: "Put your cursor in VS Code, Slack, Notion, Word, or any other text field." },
                { n: "03", t: "Press Ctrl+Space. Speak freely.", b: "Toggle dictation, or try the sample-text simulator. No mic permission needed for the demo." },
              ].map((s) => (
                <div key={s.n} className="flex gap-5">
                  <span className="font-display text-3xl italic text-clay">{s.n}</span>
                  <div>
                    <div className="text-cream">{s.t}</div>
                    <p className="mt-1 text-[14px] leading-relaxed text-mute">{s.b}</p>
                  </div>
                </div>
              ))}
              <a href="#/docs" onClick={close} className="inline-flex items-center gap-1 text-[14px] text-clay underline-offset-4 hover:underline">
                Open the full Docs — setup, refine, security <ArrowUpRight size={14} />
              </a>
            </div>
          )}
          {tab === "shortcuts" && (
            <div>
              <div className="divide-y divide-white/[0.07] rounded-2xl border border-white/10">
                {[
                  { k: ["Ctrl", "Space"], d: "Toggle global dictation" },
                  { k: ["Win", "Shift"], d: "Multimodal screen companion (toggle vision mid-session)" },
                  { k: ["Ctrl", "Win"], d: "Purge session and flush memory" },
                  { k: ["Esc"], d: "Clear canvas and dismiss" },
                ].map((r) => (
                  <div key={r.d} className="flex items-center justify-between gap-4 px-5 py-4">
                    <span className="text-[14px] text-cream/90">{r.d}</span>
                    <span className="flex shrink-0 items-center gap-1">
                      {r.k.map((k, i) => (
                        <span key={k} className="flex items-center gap-1">
                          {i > 0 && <span className="text-mute">+</span>}
                          <KeyCap>{k}</KeyCap>
                        </span>
                      ))}
                    </span>
                  </div>
                ))}
              </div>
              <p className="mt-4 text-[13px] leading-relaxed text-mute">
                Browser preview supports Ctrl+Space and Esc. System shortcuts live in the native app. Voice triggers (refine · polish · elaborate) live in the Refine tab.
              </p>
            </div>
          )}
          {tab === "refine" && (
            <div className="space-y-5">
              <div className="flex gap-4">
                <Sparkles size={22} className="mt-1 shrink-0 text-clay" />
                <div>
                  <div className="font-display text-2xl text-cream">Say “refine” — it refines.</div>
                  <p className="mt-1 text-[14px] leading-relaxed text-mute">
                    Say refine, polish, or elaborate, or tap the capsule buttons. The whole session is deleted and retyped, cleaner — no clipboard, no Ctrl+A.
                  </p>
                </div>
              </div>
              <div className="flex gap-5">
                <span className="font-display text-3xl italic text-clay">02</span>
                <div>
                  <div className="text-cream">Try it in the simulator</div>
                  <p className="mt-1 text-[14px] leading-relaxed text-mute">
                    Dictate messy with Raw on, press Say "refine" — or type the word refine — and watch delete-and-replace.
                  </p>
                </div>
              </div>
              <a href="#/docs#docs-refine" onClick={close} className="inline-flex items-center gap-1 text-[14px] text-clay underline-offset-4 hover:underline">
                Refine + custom actions, explained in Docs <ArrowUpRight size={14} />
              </a>
            </div>
          )}
        </motion.div>
      </AnimatePresence>
    </div>
  );
}

/* ---------------- Download */
function DownloadBtn({ onGo }: { onGo: () => void }) {
  const [sparks, setSparks] = useState(0);
  return (
    <a
      href={GITHUB_INSTALLER_DOWNLOAD_URL}
      download
      onClick={() => {
        setSparks((s) => s + 1);
        setTimeout(onGo, 650);
      }}
      className="group relative block overflow-hidden rounded-full p-[1.5px]"
    >
      <span className="absolute inset-[-100%] animate-[spin-slow_3.5s_linear_infinite] bg-[conic-gradient(from_0deg,transparent_0_70%,#799fd6_85%,#fff_100%)]" />
      <span className="relative flex items-center justify-center gap-3 rounded-full bg-clay px-6 py-4 text-[15px] font-medium text-ink transition-colors group-hover:bg-[#e98860]">
        <Download size={18} /> Download Windows Installer (v2.1)
      </span>
      <span key={sparks} className="pointer-events-none absolute inset-0">
        {sparks > 0 &&
          Array.from({ length: 10 }).map((_, i) => {
            const a = (i / 10) * Math.PI * 2;
            return (
              <motion.span
                key={i}
                className="absolute left-1/2 top-1/2 h-1.5 w-1.5 rounded-full bg-amber"
                initial={{ x: 0, y: 0, opacity: 1, scale: 1 }}
                animate={{ x: Math.cos(a) * 120, y: Math.sin(a) * 40, opacity: 0, scale: 0 }}
                transition={{ duration: 0.65, ease: "easeOut" }}
              />
            );
          })}
      </span>
    </a>
  );
}

function DownloadBody({ close }: { close: () => void }) {
  const [thanks, setThanks] = useState(false);
  const [guideSaved, setGuideSaved] = useState(false);

  const saveGuide = () => {
    const blob = new Blob([QUICK_START_TEXT], { type: "text/plain" });
    const url = URL.createObjectURL(blob);
    const a = document.createElement("a");
    a.href = url;
    a.download = "Voxula-AI-2.1-Quick-Start.txt";
    a.click();
    URL.revokeObjectURL(url);
    setGuideSaved(true);
  };

  if (thanks)
    return (
      <motion.div initial={{ opacity: 0, scale: 0.96 }} animate={{ opacity: 1, scale: 1 }} className="text-center">
        <div className="mx-auto flex h-16 w-16 items-center justify-center rounded-full bg-sage/15 text-sage">
          <Check size={30} />
        </div>
        <h3 className="font-display mt-6 text-5xl text-cream">Thank you.</h3>
        <p className="mx-auto mt-3 max-w-sm text-mute">
          Your download has started. Run the installer, grab a free API key, and press Ctrl+Space in any app.
        </p>
        <div className="mt-8 flex justify-center">
          <VoiceBars count={24} height={36} />
        </div>
        <div className="mt-8 grid gap-3 text-left sm:grid-cols-3">
          {["Run setup wizard", "Paste free API key", "Speak anywhere"].map((s, i) => (
            <div key={s} className="rounded-2xl border border-white/10 bg-white/[0.03] p-4">
              <span className="font-display text-2xl italic text-clay">{i + 1}</span>
              <div className="mt-1 text-[14px] text-cream">{s}</div>
            </div>
          ))}
        </div>
        <button onClick={close} className="mt-8 text-[13px] text-mute underline underline-offset-4 hover:text-cream">
          Close
        </button>
      </motion.div>
    );

  return (
    <div>
      <p className="text-mute">A native Windows companion, built for speed, privacy, and your next great idea.</p>
      <div className="mt-7 flex items-center gap-4 rounded-2xl border border-white/10 bg-gradient-to-br from-white/[0.05] to-transparent p-5">
        <div className="flex h-12 w-12 shrink-0 items-center justify-center rounded-xl bg-clay/15 text-clay">
          <Monitor size={22} />
        </div>
        <div className="flex-1">
          <div className="text-cream">Voxula AI for Windows v2.1</div>
          <div className="text-[13px] text-mute">Native x64 · Windows 10 / 11 · Free forever</div>
        </div>
        <span className="font-mono text-xs text-mute">{INSTALLER_SIZE}</span>
      </div>
      <div className="mt-4">
        <InfoBox icon={<Download size={16} />}>
          <span className="text-cream">{INSTALLER_FILE} ({INSTALLER_SIZE})</span>
          <br />
          Official setup wizard hosted on GitHub. 64-bit · No admin rights required · Uninstaller included.
        </InfoBox>
      </div>
      <div className="mt-6 space-y-3">
        <DownloadBtn onGo={() => setThanks(true)} />
        <GhostButton href={GITHUB_REPO_URL} target="_blank" className="w-full justify-center">
          View GitHub Repository (Source & Release)
        </GhostButton>
        <GhostButton onClick={saveGuide} arrow={false} className="w-full justify-center">
          {guideSaved ? <Check size={15} className="text-sage" /> : <BookOpen size={15} />}
          {guideSaved ? "Quick-start guide downloaded" : "Save the quick-start guide"}
        </GhostButton>
        <GhostButton
          onClick={() => {
            close();
            setTimeout(() => scrollToId("simulator"), 350);
          }}
          className="w-full justify-center"
        >
          Try the web simulator
        </GhostButton>
      </div>
      <p className="mt-6 flex items-center justify-center gap-2 text-[12.5px] text-mute">
        <Lock size={13} /> No account. No subscription. Your key, your control.
      </p>
    </div>
  );
}

/* ---------------- Support */
function SupportBody() {
  const [open, setOpen] = useState<number | null>(0);
  return (
    <div>
      <p className="text-mute">Start with a few quick checks to get back to your workflow.</p>
      <div className="mt-7 divide-y divide-white/[0.07] rounded-2xl border border-white/10">
        {FAQ.map((f, i) => (
          <div key={f.q}>
            <button onClick={() => setOpen(open === i ? null : i)} className="flex w-full items-center justify-between gap-4 px-5 py-4 text-left text-[15px] text-cream">
              {f.q}
              <ChevronDown size={16} className={cn("shrink-0 text-mute transition-transform", open === i && "rotate-180 text-clay")} />
            </button>
            <AnimatePresence initial={false}>
              {open === i && (
                <motion.div initial={{ height: 0, opacity: 0 }} animate={{ height: "auto", opacity: 1 }} exit={{ height: 0, opacity: 0 }} className="overflow-hidden">
                  <p className="px-5 pb-5 text-[14px] leading-relaxed text-mute">{f.a}</p>
                </motion.div>
              )}
            </AnimatePresence>
          </div>
        ))}
      </div>
      <div className="mt-5">
        <InfoBox icon={<Mail size={16} />}>
          Most answers live in{" "}
          <a href="#/docs#docs-troubleshooting" className="text-clay underline">Docs</a>, including the full troubleshooting table. For release-specific help, use the support info bundled with the native app.
        </InfoBox>
      </div>
    </div>
  );
}

/* ---------------- Shell */
export function ProductModal({
  kind,
  onClose,
  keyValue,
  setKeyValue,
}: {
  kind: ModalKind;
  onClose: () => void;
  keyValue: string;
  setKeyValue: (k: string) => void;
}) {
  const panelRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    if (!kind) return;
    const lenis = getLenis();
    lenis?.stop();
    const prevOverflow = document.body.style.overflow;
    document.body.style.overflow = "hidden";
    const prevFocus = document.activeElement as HTMLElement | null;
    setTimeout(() => panelRef.current?.focus(), 30);

    const onKey = (e: KeyboardEvent) => {
      if (e.key === "Escape") {
        e.stopPropagation();
        onClose();
      }
      if (e.key === "Tab" && panelRef.current) {
        const f = panelRef.current.querySelectorAll<HTMLElement>('a[href], button, input, [tabindex]:not([tabindex="-1"])');
        if (!f.length) return;
        const first = f[0];
        const last = f[f.length - 1];
        if (e.shiftKey && document.activeElement === first) {
          e.preventDefault();
          last.focus();
        } else if (!e.shiftKey && document.activeElement === last) {
          e.preventDefault();
          first.focus();
        }
      }
    };
    window.addEventListener("keydown", onKey, true);
    return () => {
      window.removeEventListener("keydown", onKey, true);
      document.body.style.overflow = prevOverflow;
      lenis?.start();
      prevFocus?.focus?.();
    };
  }, [kind, onClose]);

  return (
    <AnimatePresence>
      {kind && (
        <motion.div
          key="backdrop"
          className="fixed inset-0 z-[90] flex items-center justify-center bg-black/70 p-4 backdrop-blur-md"
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          exit={{ opacity: 0 }}
          onMouseDown={(e) => e.target === e.currentTarget && onClose()}
        >
          <motion.div
            ref={panelRef}
            tabIndex={-1}
            role="dialog"
            aria-modal="true"
            data-lenis-prevent
            initial={{ opacity: 0, y: 40, scale: 0.96, filter: "blur(8px)" }}
            animate={{ opacity: 1, y: 0, scale: 1, filter: "blur(0px)" }}
            exit={{ opacity: 0, y: 20, scale: 0.97 }}
            transition={{ duration: 0.45, ease: [0.16, 1, 0.3, 1] }}
            className="relative max-h-[92vh] w-full max-w-[560px] overflow-y-auto rounded-[32px] border border-white/10 bg-panel p-7 shadow-[0_60px_160px_-40px_rgba(0,0,0,1)] outline-none md:p-10"
          >
            <div className="pointer-events-none absolute -right-20 -top-20 h-60 w-60 rounded-full bg-[radial-gradient(circle,rgba(76,141,255,0.25),transparent_70%)]" />
            <button onClick={onClose} aria-label="Close" className="absolute right-5 top-5 rounded-full border border-white/10 p-2 text-mute transition hover:border-clay/50 hover:text-cream">
              <X size={16} />
            </button>
            <div className="relative">
              <div className="mb-6 flex items-center gap-3">
                <WaveLogo size={26} />
                <span className="font-mono text-[10.5px] tracking-[0.25em] text-clay">
                  VOXULA AI / {META[kind].eyebrow}
                </span>
              </div>
              <h2 className="font-display mb-6 text-[clamp(2rem,4.5vw,3rem)] leading-[1.02] text-cream">{META[kind].title}</h2>
              {kind === "settings" && <SettingsBody keyValue={keyValue} setKeyValue={setKeyValue} />}
              {kind === "guide" && <GuideBody close={onClose} />}
              {kind === "download" && <DownloadBody close={onClose} />}
              {kind === "support" && <SupportBody />}
            </div>
          </motion.div>
        </motion.div>
      )}
    </AnimatePresence>
  );
}
