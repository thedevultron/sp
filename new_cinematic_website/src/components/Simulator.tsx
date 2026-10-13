import { useCallback, useEffect, useRef, useState } from "react";
import { motion, useScroll, useTransform } from "framer-motion";
import { Check, Code2, FileText, Hash, Mic, RotateCcw, ShieldCheck, Sparkles, Square, Terminal, Zap } from "lucide-react";
import { ChapterMark, Eyebrow, KeyCap, Reveal, RiseText, VoiceBars } from "./ui";
import { SCRIPTS, type AppKey } from "../data";
import type { DemoState } from "../site";
import { scrollToId } from "../lib/scroll";
import { cn } from "../utils/cn";

type Phase = "idle" | "listening" | "typing" | "done" | "deleting" | "retyping" | "refined";
const sleep = (ms: number) => new Promise((r) => setTimeout(r, ms));

const APPS: { key: AppKey; label: string }[] = [
  { key: "vscode", label: "VS Code" },
  { key: "slack", label: "Slack" },
  { key: "notion", label: "Notion" },
];

function Highlight({ line }: { line: string }) {
  if (/^\s*\/\//.test(line)) return <span className="italic text-sage/80">{line}</span>;
  const parts = line.split(/(\bconst\b|\breturn\b|=>|\buser\b|\bUser\b|\.\w+(?=\())/g);
  return (
    <>
      {parts.map((p, i) => {
        if (/^(const|return|=>)$/.test(p)) return <span key={i} className="text-clay">{p}</span>;
        if (/^User$/.test(p)) return <span key={i} className="text-amber">{p}</span>;
        if (/^\.\w+$/.test(p)) return <span key={i} className="text-amber">{p}</span>;
        return <span key={i}>{p}</span>;
      })}
    </>
  );
}

function Caret() {
  return <span className="caret ml-px inline-block h-[1.05em] w-[2px] translate-y-[3px] bg-clay" />;
}

function Ticker({ value }: { value: number }) {
  const [v, setV] = useState(value);
  useEffect(() => {
    const id = setInterval(() => {
      setV((cur) => {
        if (cur === value) return cur;
        const d = value - cur;
        return Math.abs(d) < 2 ? value : cur + Math.round(d * 0.25);
      });
    }, 40);
    return () => clearInterval(id);
  }, [value]);
  return <span className="tabular-nums">{v}</span>;
}

function VSCodeWindow({ text, showCaret }: { text: string; showCaret: boolean }) {
  const lines = text.split("\n");
  const total = Math.max(11, lines.length);
  return (
    <div className="flex min-h-[380px] flex-col">
      <div className="flex border-b border-white/[0.07] bg-ink-2">
        <div className="flex flex-col items-center gap-4 border-r border-white/[0.07] px-3 py-4 text-mute">
          <FileText size={15} /> <Code2 size={15} /> <Hash size={15} /> <Terminal size={15} />
        </div>
        <div className="flex items-center gap-2 border-r border-white/[0.07] bg-panel px-4 py-2.5 font-mono text-[11px] text-cream">
          <span className="text-amber">TS</span> utils.ts
        </div>
      </div>
      <div className="flex-1 bg-panel px-0 py-4 font-mono text-[13px] leading-[1.7]">
        {Array.from({ length: total }).map((_, i) => (
          <div key={i} className="flex">
            <span aria-hidden="true" className="w-12 shrink-0 select-none pr-4 text-right text-mute">{i + 1}</span>
            <span className="whitespace-pre text-cream/90">
              {lines[i] !== undefined && <Highlight line={lines[i]} />}
              {showCaret && i === lines.length - 1 && <Caret />}
              {!text && i === 0 && <span className="text-mute">// Your next great idea starts with your voice.</span>}
            </span>
          </div>
        ))}
      </div>
    </div>
  );
}

function SlackWindow({ text, showCaret }: { text: string; showCaret: boolean }) {
  return (
    <div className="flex min-h-[380px] flex-col bg-panel">
      <div className="border-b border-white/[0.07] bg-ink-2 px-5 py-3 font-mono text-[11px] text-cream">
        <Hash size={11} className="mr-1 inline text-mute" />
        engineering
      </div>
      <div className="flex-1 p-6">
        {text ? (
          <div className="flex gap-3">
            <div className="flex h-9 w-9 shrink-0 items-center justify-center rounded-lg bg-clay text-xs font-semibold text-ink">AB</div>
            <div>
              <div className="text-sm font-medium text-cream">
                Amir <span className="ml-2 text-xs font-normal text-mute">Just now</span>
              </div>
              <p className="mt-1 whitespace-pre-wrap text-[15px] leading-relaxed text-cream/90">
                {text}
                {showCaret && <Caret />}
              </p>
            </div>
          </div>
        ) : (
          <p className="text-[15px] text-mute">Your team is one thought away. Speak to start your message…</p>
        )}
      </div>
      <div className="border-t border-white/[0.07] px-5 py-2.5 font-mono text-[10.5px] text-mute">All changes saved</div>
    </div>
  );
}

function NotionWindow({ text, showCaret }: { text: string; showCaret: boolean }) {
  const lines = text.split("\n");
  return (
    <div className="flex min-h-[380px] flex-col bg-panel">
      <div className="border-b border-white/[0.07] bg-ink-2 px-5 py-3 font-mono text-[11px] text-cream">
        Personal / <span className="text-mute">Product ideas</span>
      </div>
      <div className="flex-1 p-8">
        {text ? (
          <div className="space-y-1.5 text-[15px] text-cream/90">
            {lines.map((l, i) => {
              const last = i === lines.length - 1;
              const c = showCaret && last ? <Caret /> : null;
              if (l.startsWith("## ")) return <h4 key={i} className="font-display pt-3 text-2xl text-cream">{l.slice(3)}{c}</h4>;
              if (l.startsWith("# ")) return <h3 key={i} className="font-display text-4xl text-cream">{l.slice(2)}{c}</h3>;
              if (l.startsWith("•")) return <div key={i} className="pl-3 text-cream/90"><span className="mr-2 text-clay">•</span>{l.slice(1).trim()}{c}</div>;
              return <p key={i} className="min-h-[1.4em] leading-relaxed">{l}{c}</p>;
            })}
          </div>
        ) : (
          <div>
            <h3 className="font-display text-4xl text-cream/70"># Your next big idea</h3>
            <p className="mt-2 text-mute">Speak to bring it to life…</p>
          </div>
        )}
      </div>
    </div>
  );
}

export function Simulator({ onDemo }: { onDemo: (d: DemoState) => void }) {
  const [app, setApp] = useState<AppKey>("vscode");
  const [auto, setAuto] = useState(false);
  const [phase, setPhase] = useState<Phase>("idle");
  const [text, setText] = useState("");
  const run = useRef(0);
  const textRef = useRef("");
  const phaseRef = useRef<Phase>("idle");
  const bufRef = useRef("");

  const setT = (t: string) => {
    textRef.current = t;
    setText(t);
  };
  const setP = (p: Phase) => {
    phaseRef.current = p;
    setPhase(p);
  };

  const doRefine = useCallback(
    async (id: number, key: AppKey) => {
      const polish = SCRIPTS[key].polish;
      const cur = textRef.current;
      setP("deleting");
      for (let i = cur.length; i > 0; i -= 7) {
        setT(cur.slice(0, i));
        await sleep(14);
        if (run.current !== id) return;
      }
      setT("");
      setP("retyping");
      for (let i = 0; i <= polish.length; i += 3) {
        setT(polish.slice(0, i));
        await sleep(16);
        if (run.current !== id) return;
      }
      setT(polish);
      setP("refined");
    },
    []
  );

  const start = useCallback(async () => {
    const id = ++run.current;
    const raw = SCRIPTS[app].raw;
    setT("");
    setP("listening");
    await sleep(650);
    if (run.current !== id) return;
    setP("typing");
    for (let i = 0; i <= raw.length; i += 2) {
      setT(raw.slice(0, i));
      await sleep(22);
      if (run.current !== id) return;
    }
    setT(raw);
    if (auto) {
      await sleep(700);
      if (run.current !== id) return;
      await doRefine(id, app);
    } else setP("done");
  }, [app, auto, doRefine]);

  const stop = useCallback(() => {
    run.current++;
    const ph = phaseRef.current;
    if (ph === "deleting" || ph === "retyping") {
      setT(SCRIPTS[app].polish);
      setP("refined");
    } else setP(textRef.current ? "done" : "idle");
  }, [app]);

  const refine = useCallback(() => {
    const id = ++run.current;
    doRefine(id, app);
  }, [app, doRefine]);

  const reset = useCallback(() => {
    run.current++;
    setT("");
    setP("idle");
  }, []);

  const busy = phase === "listening" || phase === "typing" || phase === "deleting" || phase === "retyping";

  // keyboard
  useEffect(() => {
    const onKey = (e: KeyboardEvent) => {
      if (e.ctrlKey && e.code === "Space") {
        e.preventDefault();
        scrollToId("simulator");
        start();
        return;
      }
      if (e.key === "Escape") {
        if (busy) stop();
        return;
      }
      if (e.ctrlKey && e.key === "Meta") {
        reset();
        return;
      }
      const t = e.target as HTMLElement;
      if (t && (t.tagName === "INPUT" || t.tagName === "TEXTAREA")) return;
      if (e.key.length === 1) {
        bufRef.current = (bufRef.current + e.key.toLowerCase()).slice(-6);
        if (bufRef.current === "refine" && phaseRef.current === "done") {
          bufRef.current = "";
          refine();
        }
      }
    };
    window.addEventListener("keydown", onKey);
    return () => window.removeEventListener("keydown", onKey);
  }, [start, stop, reset, refine, busy]);

  // reset on app change
  useEffect(() => {
    run.current++;
    textRef.current = "";
    setText("");
    phaseRef.current = "idle";
    setPhase("idle");
  }, [app]);

  // push to parent
  useEffect(() => {
    onDemo({ active: busy, text, progress: 12 + text.length / 12 });
  }, [busy, text, onDemo]);

  // tilt on scroll
  const stageRef = useRef<HTMLDivElement>(null);
  const { scrollYProgress } = useScroll({ target: stageRef, offset: ["start end", "center center"] });
  const rotX = useTransform(scrollYProgress, [0, 1], [14, 0]);
  const scl = useTransform(scrollYProgress, [0, 1], [0.92, 1]);

  const headerLabel =
    phase === "refined"
      ? "Session refined"
      : phase === "deleting" || phase === "retyping"
      ? "Refining your session…"
      : phase === "idle"
      ? "Your workspace. Supercharged."
      : "Streaming to your workspace";

  const speakLabel =
    phase === "listening" || phase === "typing"
      ? "Listening. Click to stop"
      : phase === "deleting"
      ? "Deleting session…"
      : phase === "retyping"
      ? "Typing the rewrite…"
      : phase === "idle"
      ? "Press to speak"
      : "Try it again";

  const showCaret = busy;
  const title = app === "vscode" ? "workspace / utils.ts" : app === "slack" ? "Acme · #engineering" : "Personal / Product ideas";

  return (
    <section id="simulator" className="relative overflow-hidden bg-paper px-6 py-32 text-ink md:px-16 md:py-44">
      <div className="pointer-events-none absolute -right-40 top-20 h-[600px] w-[600px] rounded-full bg-[radial-gradient(circle,rgba(76,141,255,0.2),transparent_65%)]" />
      <div className="relative mx-auto max-w-6xl">
        <Reveal>
          <ChapterMark num="III" title="Your turn" tone="light" />
        </Reveal>
        <Reveal delay={0.05} className="mt-8">
          <Eyebrow tone="light">TRY IT HERE</Eyebrow>
        </Reveal>
        <h2 className="font-display mt-5 text-[clamp(2.6rem,7vw,6rem)] leading-[0.98]">
          <RiseText text="Less typing." />
          <br />
          <RiseText text="More momentum." className="italic text-clay-deep" delay={0.2} />
        </h2>
        <Reveal delay={0.2}>
          <p className="mt-6 max-w-xl text-lg text-mute-dark">Dictate it raw, then say refine and watch the session rewrite itself.</p>
        </Reveal>

        <div ref={stageRef} className="mt-16 grid gap-6 lg:grid-cols-[0.8fr_1.2fr]" style={{ perspective: 1600 }}>
          {/* controls */}
          <Reveal>
            <div className="h-full rounded-[28px] border border-black/10 bg-cream/70 p-5 sm:p-7 shadow-[0_30px_80px_-40px_rgba(0,0,0,0.35)] backdrop-blur">
              <div className="flex items-center gap-2 font-mono text-[10.5px] tracking-[0.25em] text-mute-dark">
                <span className="h-2 w-2 rounded-full bg-sage" style={{ animation: "pulse-dot 1.6s infinite" }} />
                INTERACTIVE PLAYGROUND
              </div>
              <h3 className="font-display mt-4 text-4xl leading-tight">Think it. Say it. Watch it happen.</h3>
              <p className="mt-3 text-[15px] text-mute-dark">
                Your voice, right where your cursor is. Dictate it messy — then say 'refine'.
              </p>

              <div className="mt-8">
                <div className="mb-3 font-mono text-[10.5px] tracking-[0.2em] text-mute-dark">01 CHOOSE YOUR WORKSPACE</div>
                <div className="relative flex rounded-full border border-black/10 bg-black/[0.04] p-1">
                  {APPS.map((a) => (
                    <button
                      key={a.key}
                      onClick={() => setApp(a.key)}
                      className={cn("relative z-10 flex-1 rounded-full py-2 text-[13px] font-medium transition-colors", app === a.key ? "text-cream" : "text-mute-dark hover:text-ink")}
                    >
                      {app === a.key && (
                        <motion.span layoutId="simTab" className="absolute inset-0 -z-10 rounded-full bg-ink" transition={{ type: "spring", stiffness: 380, damping: 32 }} />
                      )}
                      {a.label}
                    </button>
                  ))}
                </div>
              </div>

              <div className="mt-6">
                <div className="mb-3 font-mono text-[10.5px] tracking-[0.2em] text-mute-dark">02 MAKE IT YOURS</div>
                <button
                  onClick={() => setAuto((a) => !a)}
                  className="flex w-full items-center justify-between rounded-2xl border border-black/10 bg-white/50 px-4 py-3 text-left text-[14px]"
                  role="switch"
                  aria-checked={auto}
                >
                  <span>{auto ? "Auto-refine & polish" : "Raw transcription"}</span>
                  <span className={cn("relative h-6 w-11 rounded-full transition-colors", auto ? "bg-clay" : "bg-black/20")}>
                    <span className={cn("absolute top-0.5 h-5 w-5 rounded-full bg-white shadow transition-all", auto ? "left-[22px]" : "left-0.5")} />
                  </span>
                </button>
              </div>

              <button
                onClick={() => (busy ? stop() : start())}
                className="group mt-7 flex w-full items-center justify-between rounded-2xl bg-ink px-5 py-4 text-cream shadow-xl transition-transform hover:-translate-y-0.5"
              >
                <span className="flex items-center gap-3 text-[14.5px] sm:text-[15px] font-medium">
                  {busy ? <Square size={16} className="text-clay" /> : <Mic size={17} className="text-clay" />}
                  {speakLabel}
                </span>
                {busy ? <VoiceBars count={10} height={20} /> : (
                  <span className="hidden sm:flex items-center gap-1">
                    <KeyCap>Ctrl</KeyCap>
                    <KeyCap>Space</KeyCap>
                  </span>
                )}
              </button>

              {phase === "done" && !auto && (
                <motion.button
                  initial={{ opacity: 0, y: 12 }}
                  animate={{ opacity: 1, y: 0 }}
                  onClick={refine}
                  className="mt-3 flex w-full items-center justify-between rounded-2xl border border-clay bg-clay/10 px-4 py-3 sm:px-5 sm:py-4 text-clay-deep transition hover:bg-clay/20"
                >
                  <span className="flex items-center gap-2.5 sm:gap-3 text-[13.5px] sm:text-[15px] font-medium">
                    <Sparkles size={17} /> Say 'refine' — watch it rewrite
                  </span>
                  <KeyCap tone="light" className="hidden sm:inline-flex">refine</KeyCap>
                </motion.button>
              )}

              <div className="mt-5 min-h-[44px] text-[13px] text-mute-dark">
                {phase === "refined" ? (
                  <motion.div initial={{ opacity: 0 }} animate={{ opacity: 1 }}>
                    <div className="flex items-start gap-2 text-ink">
                      <Check size={16} className="mt-0.5 shrink-0 text-sage" /> Refined in place — deleted and retyped, just like the native app.
                    </div>
                    <div className="mt-1.5 pl-6 text-mute-dark">Triggers: refine · polish · elaborate (+ expand alias).</div>
                  </motion.div>
                ) : (
                  "Simulated dictation + refine. Your mic stays off."
                )}
              </div>
            </div>
          </Reveal>

          {/* preview */}
          <motion.div style={{ rotateX: rotX, scale: scl, transformOrigin: "50% 100%" }}>
            <div className="overflow-hidden rounded-[28px] border border-black/20 bg-ink shadow-[0_60px_120px_-40px_rgba(0,0,0,0.6)]">
              <div className="flex items-center justify-between border-b border-white/[0.07] px-5 py-3.5">
                <div className="flex items-center gap-3 text-[12.5px] text-cream">
                  <span
                    className={cn("h-2 w-2 rounded-full", busy ? "bg-clay" : phase === "refined" ? "bg-sage" : "bg-mute/60")}
                    style={busy ? { animation: "pulse-dot 1.2s infinite" } : undefined}
                  />
                  {headerLabel}
                </div>
                <button onClick={reset} className="flex items-center gap-1.5 rounded-full border border-white/10 px-3 py-1 text-[11px] text-mute transition hover:border-clay/50 hover:text-cream">
                  <RotateCcw size={11} /> Reset
                </button>
              </div>
              <div className="border-b border-white/[0.07] bg-ink-2 px-5 py-2 font-mono text-[10.5px] tracking-wider text-mute">{title}</div>
              {app === "vscode" && <VSCodeWindow text={text} showCaret={showCaret} />}
              {app === "slack" && <SlackWindow text={text} showCaret={showCaret} />}
              {app === "notion" && <NotionWindow text={text} showCaret={showCaret} />}
              <div className="flex items-center justify-between border-t border-white/[0.07] bg-ink-2 px-5 py-2.5 font-mono text-[10.5px] text-mute">
                <span>{busy ? "Receiving voice input" : "Ready for your voice"}</span>
                <span>{app === "vscode" ? "TypeScript  UTF-8" : app === "slack" ? "All changes saved" : "Notion"}</span>
              </div>
              <div className="flex flex-wrap items-center gap-x-6 gap-y-2 border-t border-white/[0.07] px-5 py-3 text-[12px] text-mute">
                <span className="flex items-center gap-1.5"><Zap size={13} className="text-clay" /><Ticker value={busy || phase === "done" || phase === "refined" ? 142 : 180} />ms latency</span>
                <span className="flex items-center gap-1.5"><Mic size={13} className="text-clay" />16kHz live audio</span>
                <span className="flex items-center gap-1.5"><ShieldCheck size={13} className="text-clay" />DPAPI encrypted</span>
              </div>
            </div>
            <p className="mt-4 text-center text-xs text-mute-dark">Illustrative performance · Native app uses the AI Engine</p>
          </motion.div>
        </div>
      </div>
    </section>
  );
}
