import { useCallback, useEffect, useRef, useState } from "react";
import { Activity, AlignLeft, Code2, FileText, Hash, Lock, Sparkles } from "lucide-react";
import { cn } from "../../utils/cn";
import type { AppContent, AppTarget, DictationStatus, TransformMode } from "../../types";
import { KeyCap } from "../ui/KeyCap";
import { GlassCard } from "../ui/GlassCard";
import { SmartTokenBar } from "../widget/SmartTokenBar";
import { AppMockupWindow } from "./AppMockupWindow";

const CONTENT: Record<AppTarget, AppContent> = {
  vscode: {
    lang: "code",
    raw: `// um quick dictation handler
function onSpeech(text) {
let clean = text.trim()
inject(clean)
return true
}`,
    polished: `/** Stream the final transcript into the active caret. */
export async function onSpeech(text: string): Promise<void> {
  const clean = text.trim();
  await caret.inject(clean, { commit: true });
}`,
  },
  slack: {
    lang: "text",
    raw: "hey team um so the new build is out and uh latency is down to like 140 milliseconds so it basically types before you finish talking will post numbers later",
    polished:
      "Hey team — the new build is out. Latency is down to ~140 ms, so SPEAK essentially types before you finish talking. Full benchmarks in the thread.",
  },
  notion: {
    lang: "text",
    raw: "sprint notes um we shipped the token bar and the failover engine uh next up is neon ink on the screen canvas and the mobile handoff",
    polished:
      "What shipped this sprint:\n• Smart Token Context Bar\n• Multi-Key Failover Engine\nNext up: Neon Ink canvas overlays and the mobile companion handoff.",
  },
};

const APP_LABEL: Record<AppTarget, string> = {
  vscode: "VS Code",
  slack: "Slack",
  notion: "Notion",
};

const APP_ICON: Record<AppTarget, typeof Code2> = {
  vscode: Code2,
  slack: Hash,
  notion: FileText,
};

const STATUS_META: Record<DictationStatus, { label: string; dot: string }> = {
  idle: { label: "IDLE", dot: "bg-fog/60" },
  listening: { label: "LISTENING", dot: "anim-ping-soft bg-token-green" },
  refining: { label: "REFINING", dot: "bg-token-amber" },
  done: { label: "COMMITTED", dot: "bg-blueprint" },
};

export function LiveTypingPlayground() {
  const [app, setApp] = useState<AppTarget>("vscode");
  const [mode, setMode] = useState<TransformMode>("polish");
  const [status, setStatus] = useState<DictationStatus>("idle");
  const [budget, setBudget] = useState(0);
  const [refined, setRefined] = useState(false);
  const [latency, setLatency] = useState(142);
  const statusRef = useRef<DictationStatus>("idle");
  statusRef.current = status;

  const content = CONTENT[app];
  const raw = content.raw;

  const toggle = useCallback(() => {
    if (statusRef.current === "listening" || statusRef.current === "refining") {
      setStatus("done");
      return;
    }
    setBudget(0);
    setRefined(false);
    setStatus("listening");
  }, []);

  /* Character stream — batched, throttled, paused offscreen */
  useEffect(() => {
    if (status !== "listening") return;
    if (typeof document !== "undefined" && document.hidden) return;
    const iv = window.setInterval(() => {
      setBudget((b) => (b >= raw.length ? b : b + 2 + (Math.random() < 0.3 ? 1 : 0)));
    }, 32);
    return () => window.clearInterval(iv);
  }, [status, raw.length]);

  /* Completion → optional refine pass */
  useEffect(() => {
    if (status !== "listening" || budget < raw.length) return;
    if (mode === "polish") {
      setStatus("refining");
      const t = window.setTimeout(() => {
        setRefined(true);
        setStatus("done");
      }, 1150);
      return () => window.clearTimeout(t);
    }
    setStatus("done");
  }, [status, budget, raw.length, mode]);

  /* Live latency jitter — slowed, compositor-friendly */
  useEffect(() => {
    if (status !== "listening") return;
    const iv = window.setInterval(() => setLatency(118 + Math.round(Math.random() * 58)), 650);
    return () => window.clearInterval(iv);
  }, [status]);

  /* Real physical Ctrl+Space */
  useEffect(() => {
    const onKey = (e: KeyboardEvent) => {
      if (e.ctrlKey && !e.shiftKey && !e.altKey && !e.metaKey && e.code === "Space") {
        e.preventDefault();
        if (!e.repeat) toggle();
      }
    };
    window.addEventListener("keydown", onKey);
    return () => window.removeEventListener("keydown", onKey);
  }, [toggle]);

  const display = refined ? content.polished : raw;
  const displayBudget = refined ? content.polished.length : Math.min(budget, raw.length);
  const progress = refined ? 0.55 : 0.08 + (displayBudget / raw.length) * 0.44;
  const tokens = 980 + displayBudget * 12;
  const listening = status === "listening";

  return (
    <div className="grid gap-5 lg:grid-cols-[350px_1fr]">
      {/* ── Control panel ── */}
      <GlassCard tilt className="p-6 sm:p-7" spotlight>
        <div className="flex h-full flex-col gap-7">
          <div>
            <SectionLabel index="01" label="Trigger" />
            <button
              type="button"
              onClick={toggle}
              className={cn(
                "mt-3 flex w-full items-center justify-center gap-2.5 rounded-full border py-3.5 transition-all duration-300",
                listening
                  ? "border-[rgba(102,58,243,0.55)] bg-[rgba(102,58,243,0.14)] shadow-[0_0_28px_rgba(102,58,243,0.3)]"
                  : "border-edge bg-[rgba(186,214,247,0.05)] hover:border-[rgba(186,215,247,0.3)] hover:bg-[rgba(186,214,247,0.09)]"
              )}
            >
              <KeyCap active={listening}>Ctrl</KeyCap>
              <KeyCap active={listening}>Space</KeyCap>
              <span className={cn("text-[13px] font-medium", listening ? "text-white" : "text-mist")}>
                {listening ? "Listening — press to stop" : "Press Ctrl + Space to Speak"}
              </span>
            </button>
            <p className="mt-2.5 text-center font-mono text-[10.5px] tracking-wide text-fog/70">
              Works with your physical Ctrl + Space, too
            </p>
          </div>

          <div>
            <SectionLabel index="02" label="Target window" />
            <div className="mt-3 flex rounded-full border border-edge bg-white/[0.02] p-1">
              {(Object.keys(APP_LABEL) as AppTarget[]).map((t) => {
                const Icon = APP_ICON[t];
                return (
                  <button
                    key={t}
                    type="button"
                    onClick={() => {
                      setApp(t);
                      setStatus("idle");
                      setBudget(0);
                      setRefined(false);
                    }}
                    className={cn(
                      "flex flex-1 items-center justify-center gap-1.5 rounded-full py-2 text-[12.5px] font-medium transition-all duration-300",
                      app === t
                        ? "bg-[rgba(186,214,247,0.12)] text-white shadow-[inset_0_1px_0_rgba(255,255,255,0.12)]"
                        : "text-fog hover:text-mist"
                    )}
                  >
                    <Icon size={13} strokeWidth={1.5} />
                    {APP_LABEL[t]}
                  </button>
                );
              })}
            </div>
          </div>

          <div>
            <SectionLabel index="03" label="Transformation" />
            <div className="mt-3 flex rounded-full border border-edge bg-white/[0.02] p-1">
              <button
                type="button"
                onClick={() => setMode("raw")}
                className={cn(
                  "flex flex-1 items-center justify-center gap-1.5 rounded-full py-2 text-[12.5px] font-medium transition-all duration-300",
                  mode === "raw"
                    ? "bg-[rgba(186,214,247,0.12)] text-white shadow-[inset_0_1px_0_rgba(255,255,255,0.12)]"
                    : "text-fog hover:text-mist"
                )}
              >
                <AlignLeft size={13} strokeWidth={1.5} />
                Raw
              </button>
              <button
                type="button"
                onClick={() => setMode("polish")}
                className={cn(
                  "flex flex-1 items-center justify-center gap-1.5 rounded-full py-2 text-[12.5px] font-medium transition-all duration-300",
                  mode === "polish"
                    ? "bg-[rgba(186,214,247,0.12)] text-white shadow-[inset_0_1px_0_rgba(255,255,255,0.12)]"
                    : "text-fog hover:text-mist"
                )}
              >
                <Sparkles size={13} strokeWidth={1.5} />
                Auto-Refine
              </button>
            </div>
          </div>

          {/* Session console */}
          <div className="mt-auto rounded-xl border border-edge bg-[rgba(5,6,15,0.7)] p-4 font-mono text-[11px]">
            <ConsoleRow label="STATUS">
              <span className="flex items-center gap-2">
                <span className={cn("h-1.5 w-1.5 rounded-full", STATUS_META[status].dot)} />
                <span className={status === "listening" ? "text-token-green" : "text-frost"}>
                  {STATUS_META[status].label}
                </span>
              </span>
            </ConsoleRow>
            <ConsoleRow label="TARGET">{APP_LABEL[app].toUpperCase()}</ConsoleRow>
            <ConsoleRow label="MODE">{mode === "polish" ? "AUTO-REFINE" : "RAW TRANSCRIPTION"}</ConsoleRow>
            <ConsoleRow label="SESSION">
              <span className="tabular-nums">{tokens.toLocaleString("en-US")} TOKENS</span>
            </ConsoleRow>
          </div>
        </div>
      </GlassCard>

      {/* ── App window + telemetry ── */}
      <div className="flex flex-col gap-4">
        <div className="flex items-center gap-3 px-1">
          <span className="font-mono text-[10px] uppercase tracking-[0.16em] text-fog">Session context</span>
          <SmartTokenBar progress={progress} tokens={tokens} latency={latency} className="flex-1" />
        </div>

        <AppMockupWindow
          app={app}
          display={display}
          budget={displayBudget}
          streaming={listening}
          refining={status === "refining"}
          lang={content.lang}
        />

        <div className="flex flex-wrap items-center gap-2 px-1">
          <TelemetryPill>
            <span className={cn("h-1.5 w-1.5 rounded-full", listening ? "anim-ping-soft bg-token-green" : "bg-token-green/70")} />
            <span className="tabular-nums">Latency {latency}ms</span>
          </TelemetryPill>
          <TelemetryPill>
            <span className="h-1.5 w-1.5 rounded-full bg-blueprint/80" />
            Accuracy 99.4%
          </TelemetryPill>
          <TelemetryPill>
            <Lock size={11} strokeWidth={1.5} className="text-blueprint" />
            DPAPI Encrypted
          </TelemetryPill>
          <TelemetryPill>
            <Activity size={11} strokeWidth={1.5} className="text-token-green" />
            Gemini Live WS
          </TelemetryPill>
        </div>
      </div>
    </div>
  );
}

function SectionLabel({ index, label }: { index: string; label: string }) {
  return (
    <div className="flex items-center gap-2.5">
      <span className="font-mono text-[11px] tabular-nums text-blueprint">{index}</span>
      <span className="font-mono text-[11px] uppercase tracking-[0.16em] text-fog">{label}</span>
      <span className="h-px flex-1 bg-gradient-to-r from-edge to-transparent" />
    </div>
  );
}

function ConsoleRow({ label, children }: { label: string; children: React.ReactNode }) {
  return (
    <div className="flex items-center justify-between py-1">
      <span className="text-fog/60">{label}</span>
      <span className="text-frost">{children}</span>
    </div>
  );
}

function TelemetryPill({ children }: { children: React.ReactNode }) {
  return (
    <span className="inline-flex items-center gap-2 rounded-full border border-edge bg-white/[0.03] px-3 py-1.5 font-mono text-[10.5px] uppercase tracking-[0.12em] text-mist transition-colors duration-300 hover:border-[rgba(186,215,247,0.28)] hover:text-frost">
      {children}
    </span>
  );
}
