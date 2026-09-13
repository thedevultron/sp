import { useMemo, type ReactNode } from "react";
import { AnimatePresence, motion } from "framer-motion";
import { Code2, FileText, Hash, Minus, Sparkles, Square, X } from "lucide-react";
import type { AppTarget, ContentToken } from "../../types";

/* ── Syntax highlighting (icy, palette-locked) ── */

const CODE_RE =
  /(\/\/[^\n]*)|("(?:[^"\\\n]|\\.)*"|'(?:[^'\\\n]|\\.)*'|`(?:[^`\\]|\\.)*`)|\b(const|let|var|function|return|await|async|export|import|from|if|else|new|type|interface|Promise|void|string|number|true|false|null|undefined)\b|\b(\d+(?:\.\d+)?)\b/g;

function highlightCode(code: string): ContentToken[] {
  const tokens: ContentToken[] = [];
  let last = 0;
  let m: RegExpExecArray | null;
  CODE_RE.lastIndex = 0;
  while ((m = CODE_RE.exec(code)) !== null) {
    if (m.index > last) tokens.push({ text: code.slice(last, m.index), cls: "text-[rgba(209,228,250,0.85)]" });
    const cls = m[1]
      ? "italic text-[#78879e]"
      : m[2]
        ? "text-[#8fd6a5]"
        : m[3]
          ? "text-[#98c0ef]"
          : "text-blueprint";
    tokens.push({ text: m[0], cls });
    last = m.index + m[0].length;
  }
  if (last < code.length) tokens.push({ text: code.slice(last), cls: "text-[rgba(209,228,250,0.85)]" });
  return tokens;
}

function TypedText({
  content,
  budget,
  lang,
  streaming,
}: {
  content: string;
  budget: number;
  lang: "code" | "text";
  streaming: boolean;
}) {
  const tokens = useMemo<ContentToken[]>(
    () => (lang === "code" ? highlightCode(content) : [{ text: content, cls: "text-mist" }]),
    [content, lang]
  );
  const nodes: ReactNode[] = [];
  let remaining = budget;
  for (let i = 0; i < tokens.length && remaining > 0; i++) {
    const take = tokens[i].text.slice(0, remaining);
    if (take.length > 0) {
      nodes.push(
        <span key={i} className={tokens[i].cls}>
          {take}
        </span>
      );
    }
    remaining -= tokens[i].text.length;
  }
  return (
    <>
      {nodes}
      {streaming && <span className="type-caret" />}
    </>
  );
}

/* ── Window chrome meta ── */

const WINDOW_META: Record<AppTarget, { icon: typeof Code2; title: string }> = {
  vscode: { icon: Code2, title: "main.ts — speak" },
  slack: { icon: Hash, title: "# voice-eng — Slack" },
  notion: { icon: FileText, title: "Sprint Notes — Notion" },
};

interface AppMockupWindowProps {
  app: AppTarget;
  display: string;
  budget: number;
  streaming: boolean;
  refining: boolean;
  lang: "code" | "text";
}

export function AppMockupWindow({ app, display, budget, streaming, refining, lang }: AppMockupWindowProps) {
  const Meta = WINDOW_META[app];
  const lineCount = display.slice(0, budget).split("\n").length;

  return (
    <div className="glass-widget flex h-[380px] flex-col overflow-hidden sm:h-[420px]" style={{ borderRadius: 16 }}>
      {/* Title bar */}
      <div className="flex h-10 shrink-0 items-center justify-between border-b border-edge bg-[rgba(186,214,247,0.03)] px-4">
        <div className="flex items-center gap-2.5">
          <Meta.icon size={14} strokeWidth={1.5} className="text-blueprint" />
          <span className="font-mono text-[11px] text-fog">{Meta.title}</span>
        </div>
        <div className="flex items-center gap-3 text-fog/70">
          <Minus size={13} strokeWidth={1.5} />
          <Square size={11} strokeWidth={1.5} />
          <X size={13} strokeWidth={1.5} className="transition-colors hover:text-token-red" />
        </div>
      </div>

      {/* Body */}
      <div className="relative flex-1 overflow-hidden">
        {app === "vscode" && (
          <div className="flex h-full">
            {/* Tab strip + gutter handled inline */}
            <div className="flex h-full w-full flex-col">
              <div className="flex shrink-0 items-center gap-1 border-b border-edge bg-[rgba(5,6,15,0.6)] px-2 pt-1.5">
                <span className="rounded-t-md border border-b-0 border-edge bg-[rgba(186,214,247,0.06)] px-3 py-1.5 font-mono text-[11px] text-frost">
                  main.ts
                </span>
                <span className="px-3 py-1.5 font-mono text-[11px] text-fog/50">token-bar.ts</span>
              </div>
              <div className="flex flex-1 overflow-hidden py-4 pl-4 pr-6">
                <div className="w-9 shrink-0 select-none pr-3 text-right font-mono text-[12px] leading-[1.75] text-fog/35">
                  {Array.from({ length: lineCount }, (_, i) => (
                    <div key={i}>{i + 1}</div>
                  ))}
                </div>
                <pre className="flex-1 whitespace-pre-wrap break-words font-mono text-[12.5px] leading-[1.75]">
                  <TypedText content={display} budget={budget} lang={lang} streaming={streaming} />
                </pre>
              </div>
              <div className="flex h-7 shrink-0 items-center justify-between border-t border-edge bg-[rgba(186,214,247,0.03)] px-3 font-mono text-[10px] text-fog/70">
                <span>TypeScript · UTF-8</span>
                <span className="tabular-nums">Ln {lineCount}, Col 1 · Spaces: 2</span>
              </div>
            </div>
          </div>
        )}

        {app === "slack" && (
          <div className="flex h-full flex-col">
            <div className="flex shrink-0 items-center gap-2 border-b border-edge px-4 py-2.5">
              <Hash size={13} strokeWidth={1.5} className="text-fog" />
              <span className="text-[13px] font-semibold text-frost">voice-eng</span>
              <span className="hidden truncate text-[12px] text-fog/70 sm:block">SPEAK v2 rollout · latency results</span>
            </div>
            <div className="flex-1 space-y-5 overflow-hidden px-4 py-4">
              <div className="flex gap-3 opacity-70">
                <span className="grid h-8 w-8 shrink-0 place-items-center rounded-lg bg-[rgba(186,214,247,0.08)] font-mono text-[11px] font-semibold text-blueprint">
                  AB
                </span>
                <div>
                  <div className="flex items-baseline gap-2">
                    <span className="text-[13px] font-semibold text-frost">amir</span>
                    <span className="font-mono text-[10px] text-fog/60">10:42</span>
                  </div>
                  <p className="text-[13px] leading-relaxed text-mist">
                    Shipping the v2 build tonight — dictation latency results below.
                  </p>
                </div>
              </div>
              <div className="flex gap-3">
                <span className="grid h-8 w-8 shrink-0 place-items-center rounded-lg bg-[rgba(102,58,243,0.25)] font-mono text-[11px] font-semibold text-white">
                  AB
                </span>
                <div className="min-w-0">
                  <div className="flex items-baseline gap-2">
                    <span className="text-[13px] font-semibold text-frost">amir</span>
                    <span className="rounded-sm bg-[rgba(186,214,247,0.08)] px-1 font-mono text-[9px] uppercase tracking-wide text-mist">
                      via SPEAK
                    </span>
                  </div>
                  <p className="whitespace-pre-wrap text-[13px] leading-relaxed">
                    <TypedText content={display} budget={budget} lang={lang} streaming={streaming} />
                  </p>
                </div>
              </div>
            </div>
            <div className="mx-4 mb-4 shrink-0 rounded-lg border border-edge bg-white/[0.03] px-3 py-2 text-[12.5px] text-fog/50">
              Message #voice-eng
            </div>
          </div>
        )}

        {app === "notion" && (
          <div className="h-full overflow-hidden px-8 py-5 sm:px-12">
            <p className="font-mono text-[10px] uppercase tracking-[0.14em] text-fog/60">Workspace / Engineering</p>
            <h3 className="mt-2 font-display text-[22px] font-medium text-frost">Sprint Notes</h3>
            <div className="mt-1 mb-4 h-px w-16 bg-edge" />
            <p className="whitespace-pre-wrap text-[13.5px] leading-[1.8]">
              <TypedText content={display} budget={budget} lang={lang} streaming={streaming} />
            </p>
          </div>
        )}

        {/* Refining overlay */}
        <AnimatePresence>
          {refining && (
            <motion.div
              key="refining"
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              exit={{ opacity: 0 }}
              transition={{ duration: 0.3 }}
              className="absolute inset-0 z-10 grid place-items-center bg-[rgba(5,6,15,0.6)] backdrop-blur-[3px]"
            >
              <div className="relative overflow-hidden rounded-full border border-edge bg-[rgba(5,6,15,0.9)] px-5 py-2.5 shadow-[var(--shadow-widget)]">
                <span className="pointer-events-none absolute inset-y-0 w-1/3 bg-gradient-to-r from-transparent via-[rgba(186,215,247,0.14)] to-transparent [animation:refine-sweep_1.1s_linear_infinite]" />
                <span className="relative flex items-center gap-2.5 font-mono text-[11px] uppercase tracking-[0.16em] text-mist">
                  <Sparkles size={13} strokeWidth={1.5} className="animate-pulse text-blueprint" />
                  Refining transcript
                </span>
              </div>
            </motion.div>
          )}
        </AnimatePresence>
      </div>
    </div>
  );
}
