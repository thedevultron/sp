import { useEffect, useState, type ReactNode } from "react";
import { motion } from "framer-motion";
import { BookOpen, Download, Monitor, ShieldCheck } from "lucide-react";
import { Eyebrow, GhostButton, KeyCap, PrimaryButton, Reveal, RiseText } from "./ui";
import {
  GEMINI_KEY_URL,
  GITHUB_INSTALLER_DOWNLOAD_URL,
  GITHUB_REPO_URL,
  INSTALLER_FILE,
  INSTALLER_SIZE,
  type ModalKind,
} from "../site";
import { scrollToId } from "../lib/scroll";
import { cn } from "../utils/cn";

const NAV = [
  ["docs-start", "Get started"],
  ["docs-dictation", "Dictation"],
  ["docs-companion", "Companion"],
  ["docs-refine", "Refine"],
  ["docs-context", "Context"],
  ["docs-canvas", "Canvas & tray"],
  ["docs-settings", "Settings"],
  ["docs-models", "AI Engine"],
  ["docs-security", "Security & privacy"],
  ["docs-troubleshooting", "Troubleshooting"],
] as const;

function Sec({
  id,
  num,
  tag,
  title,
  hotkey,
  children,
}: {
  id: string;
  num: string;
  tag: string;
  title: ReactNode;
  hotkey?: ReactNode;
  children: ReactNode;
}) {
  return (
    <section id={id} className="scroll-mt-24 border-t border-white/[0.08] py-16 first:border-t-0">
      <Reveal>
        <div className="flex flex-wrap items-center justify-between gap-4">
          <div className="flex items-center gap-4 font-mono text-[11px] tracking-[0.25em] text-clay">
            <span className="font-display text-4xl italic tracking-normal">{num}</span>
            {tag}
          </div>
          {hotkey && <div className="flex items-center gap-1.5 text-sm text-mute">{hotkey}</div>}
        </div>
        <h2 className="font-display mt-5 text-[clamp(2.2rem,4.6vw,3.8rem)] leading-[1.02] text-cream">{title}</h2>
      </Reveal>
      <Reveal delay={0.08}>
        <div className="mt-8 space-y-5 text-[16px] leading-relaxed text-mute">{children}</div>
      </Reveal>
    </section>
  );
}

function List({ items }: { items: ReactNode[] }) {
  return (
    <ul className="space-y-3">
      {items.map((it, i) => (
        <li key={i} className="flex gap-4">
          <span className="mt-[0.7em] h-1.5 w-1.5 shrink-0 rounded-full bg-clay" />
          <span>{it}</span>
        </li>
      ))}
    </ul>
  );
}

function Note({ icon, children }: { icon: ReactNode; children: ReactNode }) {
  return (
    <div className="flex gap-3 rounded-2xl border border-clay/25 bg-clay/[0.06] p-5 text-[15px] text-cream/90">
      <span className="mt-0.5 shrink-0 text-clay">{icon}</span>
      <div>{children}</div>
    </div>
  );
}

function Table({ head, rows }: { head: string[]; rows: ReactNode[][] }) {
  return (
    <div className="overflow-x-auto rounded-2xl border border-white/10">
      <table className="w-full min-w-[480px] text-left text-[14.5px]">
        <thead className="bg-white/[0.04] font-mono text-[11px] uppercase tracking-widest text-mute">
          <tr>
            {head.map((h) => (
              <th key={h} className="px-5 py-3 font-normal">{h}</th>
            ))}
          </tr>
        </thead>
        <tbody className="divide-y divide-white/[0.07]">
          {rows.map((r, i) => (
            <tr key={i}>
              {r.map((c, j) => (
                <td key={j} className={cn("px-5 py-3.5 align-top", j === 0 ? "text-cream" : "text-mute")}>{c}</td>
              ))}
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}

const code = (s: string) => <code className="rounded-md bg-white/[0.07] px-1.5 py-0.5 font-mono text-[0.88em] text-amber">{s}</code>;
const strong = (s: string) => <strong className="font-medium text-cream">{s}</strong>;
const Keys = ({ k }: { k: string[] }) => (
  <>
    {k.map((x, i) => (
      <span key={x} className="flex items-center gap-1.5">
        {i > 0 && "+"}
        <KeyCap>{x}</KeyCap>
      </span>
    ))}
  </>
);

export function Docs({ openModal }: { openModal: (m: ModalKind) => void }) {
  const [active, setActive] = useState("docs-start");

  useEffect(() => {
    const obs = new IntersectionObserver(
      (entries) => {
        entries.forEach((e) => e.isIntersecting && setActive(e.target.id));
      },
      { rootMargin: "-25% 0px -65% 0px" }
    );
    NAV.forEach(([id]) => {
      const el = document.getElementById(id);
      if (el) obs.observe(el);
    });
    return () => obs.disconnect();
  }, []);

  return (
    <div id="docs-top" className="relative bg-ink pt-32">
      <div className="pointer-events-none absolute left-1/2 top-0 h-[500px] w-[900px] -translate-x-1/2 bg-[radial-gradient(ellipse,rgba(76,141,255,0.14),transparent_70%)]" />
      <div className="relative mx-auto max-w-6xl px-6 md:px-16">
        <Eyebrow>DOCS · VOXULA AI V2.1</Eyebrow>
        <h1 className="font-display mt-6 text-[clamp(3rem,8vw,7rem)] leading-[0.95] text-cream">
          <RiseText text="How to use" /> <RiseText text="Voxula AI." className="text-ember italic" delay={0.2} />
        </h1>
        <Reveal delay={0.2}>
          <p className="mt-6 max-w-2xl text-lg text-mute">
            Setup, dictation, companion, refine, context, canvas, settings, security — everything the app does, on one page.
          </p>
        </Reveal>
        <Reveal delay={0.25}>
          <div className="mt-8 max-w-2xl">
            <Note icon={<BookOpen size={18} />}>
              <strong className="font-medium text-cream">New here? Start with the installer, then the 3-step flow.</strong> Install → add an API key → focus any app and press Ctrl + Space. The simulator on the home page mirrors this flow, including refine.
            </Note>
          </div>
        </Reveal>

        <div className="mt-16 grid gap-12 lg:grid-cols-[250px_1fr]">
          <aside className="hidden lg:block">
            <div className="sticky top-28">
              <div className="font-mono text-[10.5px] tracking-[0.25em] text-clay">INSTALLATION GUIDE</div>
              <div className="mt-1 text-xs text-mute">v2.1 · 10 sections</div>
              <nav className="relative mt-6 space-y-0.5 border-l border-white/10">
                {NAV.map(([id, label], i) => (
                  <button
                    key={id}
                    onClick={() => scrollToId(id)}
                    className={cn(
                      "relative -ml-px flex w-full items-center gap-3 border-l py-2 pl-4 text-left text-[14px] transition-colors",
                      active === id ? "border-clay text-cream" : "border-transparent text-mute hover:text-cream"
                    )}
                  >
                    <span className="font-mono text-[10px] text-clay/80">{String(i + 1).padStart(2, "0")}</span>
                    {label}
                  </button>
                ))}
              </nav>
              <button
                onClick={() => openModal("download")}
                className="mt-8 flex w-full items-center justify-center gap-2 rounded-full bg-clay px-5 py-3 text-sm font-medium text-ink transition hover:-translate-y-0.5"
              >
                <Download size={15} /> Get the installer
              </button>
            </div>
          </aside>

          <main className="min-w-0">
            <Sec id="docs-start" num="01" tag="GET STARTED" title="Install and connect.">
              <ol className="space-y-8">
                <li className="flex gap-5">
                  <span className="font-display text-3xl italic text-clay">1</span>
                  <div>
                    <div className="text-cream">Install Voxula AI for Windows.</div>
                    <p className="mt-2">
                      Run the installer {code(INSTALLER_FILE)} ({INSTALLER_SIZE}, Windows 10 Build 19041+ or Windows 11, 64-bit, DirectX 11+). Hosted on GitHub (voxula_ai_installer). No admin rights needed. Optional desktop/startup shortcuts, uninstaller included.{" "}
                      <a href={GITHUB_INSTALLER_DOWNLOAD_URL} download className="text-clay underline underline-offset-4">Direct download .exe</a>
                    </p>
                  </div>
                </li>
                <li className="flex gap-5">
                  <span className="font-display text-3xl italic text-clay">2</span>
                  <div>
                    <div className="text-cream">Bring an API key.</div>
                    <p className="mt-2">
                      Voxula AI auto-detects {code("GEMINI_API_KEY")}, or open Settings → Setup to paste a primary + backup key. Keys live in Windows Credential Manager, never in plain files.{" "}
                      <a href={GEMINI_KEY_URL} target="_blank" rel="noreferrer" className="text-clay underline underline-offset-4">Get a free key</a>
                    </p>
                  </div>
                </li>
                <li className="flex gap-5">
                  <span className="font-display text-3xl italic text-clay">3</span>
                  <div>
                    <div className="text-cream">Focus any app and speak.</div>
                    <p className="mt-2">
                      Put your cursor in Notepad, Word, VS Code, Slack, Discord, or a browser field. Press <KeyCap>Ctrl</KeyCap>+<KeyCap>Space</KeyCap> and talk — words type at your cursor, sub-second.
                    </p>
                  </div>
                </li>
              </ol>
              <div className="flex flex-wrap gap-3 pt-2">
                <PrimaryButton onClick={() => openModal("download")}>Get the installer</PrimaryButton>
                <GhostButton href={GITHUB_REPO_URL} target="_blank">GitHub Repo</GhostButton>
              </div>
            </Sec>

            <Sec id="docs-dictation" num="02" tag="DICTATION" title="Live voice dictation." hotkey={<><Keys k={["Ctrl", "Space"]} /><span className="ml-2">toggle on/off</span></>}>
              <List
                items={[
                  "Streams mic audio (16 kHz mono) to live transcription.",
                  "Types directly at the cursor in whatever app is focused — multilingual auto-detect, sub-second.",
                  "The capsule shows live status, a sound-wave visualizer (mic vs. voice), an interim preview, and the token bar.",
                  "Press Ctrl+Space again to stop. The capsule hides to the tray.",
                ]}
              />
            </Sec>

            <Sec id="docs-companion" num="03" tag="COMPANION" title="Multimodal live companion." hotkey={<><Keys k={["Win", "Shift"]} /><span className="ml-2">voice + optional screen share</span></>}>
              <List
                items={[
                  "Real-time voice conversation (replies play through speakers; the capsule shows Speaking… / Listening… / Working…).",
                  "Optional live screen sharing (~1 fps JPEG) so the assistant sees your desktop. Toggle anytime via the capsule monitor button or Settings → Live Screen — mid-session, audio keeps running.",
                  <>Voice desktop control, powered by the AI Engine — tell it {strong('"click Send"')}, {strong('"scroll down"')}, {strong('"press Ctrl+S"')}. It acts on what it sees, one step at a time, narrating as it goes. Say stop to halt instantly.</>,
                  "Screen-off mode = voice-only companion.",
                ]}
              />
              <Note icon={<Monitor size={18} />}>Screen frames stream only while a session is active, and only to Google's AI service.</Note>
            </Sec>

            <Sec id="docs-refine" num="04" tag="REFINE" title={<>Say “refine” — it <span className="text-ember italic">refines.</span></>} hotkey="refine · polish · elaborate (+ expand alias)">
              <p>Say a trigger word, use the capsule buttons, or pick tray → Refine.</p>
              <List
                items={[
                  "Rewrites everything typed this session (since purge or dictation start).",
                  "Delete-and-replace: the original is removed with measured Backspaces and the rewrite is typed in place — no clipboard, no Ctrl+A, no Enter presses.",
                  <>Self-correction aware: {strong('"could you set meeting at 9pm actually 5pm"')} → {strong('"Could we schedule the meeting for 5:00 PM?"')} (obsolete info dropped, times normalized).</>,
                  "If Voxula AI has focus, refine asks you to click your document first, then say the word again — history is kept so a retry works.",
                ]}
              />
              <Table
                head={["Trigger", "Does", "Best for"]}
                rows={[
                  [code("refine"), "Clean rewrite", "Grammar, clarity, structure"],
                  [code("polish"), "Tighten tone", "Emails, messages, notes"],
                  [code("elaborate"), "Expand idea", "Detail, examples, formatting"],
                ]}
              />
              <Note icon={<BookOpen size={18} />}>Tip: dictate messy in the home simulator, then Say "refine" and watch delete + retype.</Note>
              <p>
                <span className="text-cream">Custom refine actions (up to 3):</span> Settings → Refine tab. Edit the Refine/Polish/Elaborate prompts and triggers, or add your own (e.g. name Summarize, trigger {code("summarize")}, custom prompt). They appear immediately in the capsule, the tray Refine menu and voice triggers after Save. Trigger words: a–z 0–9 -, 2–24 chars, must be unique.
              </p>
            </Sec>

            <Sec id="docs-context" num="05" tag="CONTEXT" title="Token bar and purge.">
              <List
                items={[
                  "A 3px bar under the capsule: green 0–60%, orange 61–85%, red 86–100%.",
                  "Hover reveals exact token counts, session time, and remaining buffer.",
                  <><KeyCap>Ctrl</KeyCap>+<KeyCap>Win</KeyCap> instantly stops the session, clears transcript + typed history + token counter, and hard-resets the connection.</>,
                ]}
              />
            </Sec>

            <Sec id="docs-canvas" num="06" tag="CANVAS & TRAY" title="Draw, then dismiss.">
              <List
                items={[
                  "Screen canvas: a fullscreen transparent ink layer — B / 1–3 color keys, right-click clears, Esc exits. Mark your screen while talking to the companion.",
                  "System tray: show/hide capsule, Dictation, Companion, Purge, Refine submenu, Guide, Settings, Exit — with notifications for save/refine/speaker/screen events.",
                  "Capsule hidden? By design (hotkey-only): press Ctrl+Space or tray → Show capsule.",
                ]}
              />
            </Sec>

            <Sec id="docs-settings" num="07" tag="SETTINGS" title="Four tabs, full control.">
              <div className="grid gap-4 sm:grid-cols-2">
                {[
                  ["S", "Setup", "Primary + backup API keys (masked), Test button, free-tier status."],
                  ["G", "Guide", "Shortcut reference, always one click away."],
                  ["P", "Preferences", "Microphone select/refresh, custom vocabulary + signature mark, system prompt, creativity slider, live-screen toggle + frame detail, agent reasoning depth (Low/Medium/High), Windows startup."],
                  ["R", "Refine", "Prompts, trigger words, up to 3 custom actions."],
                ].map(([l, t, b]) => (
                  <div key={l} className="rounded-2xl border border-white/10 bg-white/[0.02] p-5">
                    <div className="flex items-center gap-3">
                      <span className="flex h-8 w-8 items-center justify-center rounded-lg bg-clay/15 font-mono text-sm text-clay">{l}</span>
                      <span className="text-cream">{t}</span>
                    </div>
                    <p className="mt-3 text-[14.5px]">{b}</p>
                  </div>
                ))}
              </div>
            </Sec>

            <Sec id="docs-models" num="08" tag="AI ENGINE" title="What runs where.">
              <Table
                head={["Use", "Engine"]}
                rows={[
                  ["Dictation", "AI Engine (speech-to-text)"],
                  ["Companion (live audio + screen + PC control)", "AI Engine with automatic fallback"],
                  ["Refine (one-shot edit)", "AI Engine with automatic fallback"],
                ]}
              />
              <p>Stored configs with retired IDs self-repair on load. On a connection failure the client rotates keys and retries — after 3 failures in 30s it stops loudly instead of hot-looping.</p>
            </Sec>

            <Sec id="docs-security" num="09" tag="SECURITY & PRIVACY" title={<>Your words are <span className="text-ember italic">yours.</span></>}>
              <List
                items={[
                  <>Keys live in Windows Credential Manager (target {code("SPEAK_AI_App")}), never in plain files. The UI masks them; logs mask them.</>,
                  "A free-tier fallback key ships obfuscated and is used only when the vault is empty — your keys always win.",
                  <>Config writes are atomic to {code("%APPDATA%\\SPEAK_AI\\config.json")}, ACL-restricted to your user; all values are sanitized on load.</>,
                  "Typing uses SendInput unicode (multilingual-safe). The clipboard is never used for injection; no Enter is synthesized. Single-instance lock, debounced hotkeys, bounded queues.",
                  "Mic + screen stream only during an active session, only to Google's AI service. Transcript history resets every launch (no restore). No analytics, no accounts.",
                ]}
              />
            </Sec>

            <Sec id="docs-troubleshooting" num="10" tag="TROUBLESHOOTING" title="Back to flow, fast.">
              <Table
                head={["You see", "What it means / do this"]}
                rows={[
                  ['Companion shows "Model unavailable, trying next…" then "Live connect failed"', "Keys invalid/quota or network. Settings → Setup → Test key; add a backup key."],
                  ['"Speaker error / reply dropped", no voice', "Output device busy/missing. Check your speaker, restart the companion."],
                  ['"Mic silent / Mic Error"', "Wrong input device. Preferences → Microphone → Refresh."],
                  ['Refine says "Click your document, then <word>"', "The capsule had focus. Click the target app and say the trigger again (hands-free works best)."],
                  ["Capsule hidden", "By design (hotkey-only). Ctrl+Space, or tray → Show capsule."],
                  ["Live connect keeps failing", "Bad stored engine IDs self-repair on load; otherwise check keys/network."],
                ]}
              />
              <Note icon={<ShieldCheck size={18} />}>This site is a preview: the simulator uses sample text and never touches your mic, screen, or keys.</Note>
            </Sec>
          </main>
        </div>
      </div>
      <motion.div className="h-24" />
    </div>
  );
}
