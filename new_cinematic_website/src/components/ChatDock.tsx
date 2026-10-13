import { useEffect, useRef, useState } from "react";
import { AnimatePresence, motion } from "framer-motion";
import { ArrowUp, MessageCircle, RotateCcw, X } from "lucide-react";
import { answerLocal } from "../lib/docsEngine";
import { cn } from "../utils/cn";

interface Msg {
  role: "user" | "assistant";
  text: string;
}

const SUGGESTIONS = ["How do I install it?", "What does refine do?", "Is my voice private?"];

export function ChatDock({ open, onClose }: { open: boolean; onClose: () => void }) {
  const [docked, setDocked] = useState(false);
  const [input, setInput] = useState("");
  const [msgs, setMsgs] = useState<Msg[]>([]);
  const [typing, setTyping] = useState(false);
  const [lastQ, setLastQ] = useState("");
  const endRef = useRef<HTMLDivElement>(null);
  const inputRef = useRef<HTMLInputElement>(null);

  useEffect(() => {
    if (open) {
      setDocked(false);
      setTimeout(() => inputRef.current?.focus(), 200);
      const onKey = (e: KeyboardEvent) => e.key === "Escape" && onClose();
      window.addEventListener("keydown", onKey);
      return () => window.removeEventListener("keydown", onKey);
    }
  }, [open, onClose]);

  useEffect(() => {
    endRef.current?.scrollIntoView({ behavior: "smooth", block: "end" });
  }, [msgs, typing]);

  const ask = (q: string) => {
    const text = q.trim().slice(0, 2000);
    if (!text || typing) return;
    setDocked(true);
    setLastQ(text);
    setMsgs((m) => [...m, { role: "user", text }]);
    setInput("");
    setTyping(true);
    setTimeout(() => {
      setMsgs((m) => [...m, { role: "assistant", text: answerLocal(text) }]);
      setTyping(false);
    }, 700 + Math.random() * 500);
  };

  return (
    <AnimatePresence>
      {open && (
        <motion.div
          key="chat"
          className={cn("fixed inset-0 z-[80]", docked ? "pointer-events-none" : "flex items-center justify-center p-4")}
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          exit={{ opacity: 0 }}
        >
          {!docked && <div className="absolute inset-0 bg-black/60 backdrop-blur-md" onClick={onClose} />}
          <motion.div
            layout
            transition={{ type: "spring", stiffness: 190, damping: 26 }}
            data-lenis-prevent
            className={cn(
              "pointer-events-auto flex flex-col overflow-hidden border border-white/10 bg-panel shadow-[0_50px_140px_-30px_rgba(0,0,0,1)]",
              docked
                ? "absolute bottom-4 right-4 top-auto h-[min(620px,calc(100vh-2rem))] w-[calc(100vw-2rem)] rounded-[28px] sm:w-[400px]"
                : "relative h-[min(560px,90vh)] w-full max-w-[520px] rounded-[32px]"
            )}
          >
            <div className="flex items-center justify-between border-b border-white/[0.07] px-5 py-4">
              <div className="flex items-center gap-3">
                <span className="flex h-9 w-9 items-center justify-center rounded-full bg-clay/15 text-clay">
                  <MessageCircle size={17} />
                </span>
                <div>
                  <div className="text-[15px] text-cream">Ask Voxula</div>
                  <div className="text-[12px] text-mute">Answers from the Docs</div>
                </div>
              </div>
              <button onClick={onClose} aria-label="Close chat" className="rounded-full p-2 text-mute transition hover:bg-white/10 hover:text-cream">
                <X size={16} />
              </button>
            </div>

            <div className="flex-1 space-y-4 overflow-y-auto px-5 py-5">
              <div className="max-w-[85%] rounded-2xl rounded-tl-md bg-white/[0.05] px-4 py-3 text-[14px] leading-relaxed text-cream/90">
                Hi — ask me anything about Voxula. Short answers, straight from the Docs.
              </div>
              {msgs.length === 0 && (
                <div className="flex flex-wrap gap-2 pt-1">
                  {SUGGESTIONS.map((s) => (
                    <button key={s} onClick={() => ask(s)} className="rounded-full border border-white/10 px-3.5 py-2 text-[13px] text-mute transition hover:border-clay/60 hover:text-cream">
                      {s}
                    </button>
                  ))}
                </div>
              )}
              {msgs.map((m, i) => (
                <motion.div
                  key={i}
                  initial={{ opacity: 0, y: 10 }}
                  animate={{ opacity: 1, y: 0 }}
                  className={cn(
                    "max-w-[85%] rounded-2xl px-4 py-3 text-[14px] leading-relaxed",
                    m.role === "user" ? "ml-auto rounded-tr-md bg-clay text-ink" : "rounded-tl-md bg-white/[0.05] text-cream/90"
                  )}
                >
                  {m.text}
                </motion.div>
              ))}
              {typing && (
                <div className="flex w-fit gap-1.5 rounded-2xl rounded-tl-md bg-white/[0.05] px-4 py-3.5">
                  {[0, 1, 2].map((i) => (
                    <span key={i} className="h-1.5 w-1.5 rounded-full bg-mute" style={{ animation: `bar 0.9s ease-in-out ${i * 0.15}s infinite` }} />
                  ))}
                </div>
              )}
              {!typing && msgs.length > 0 && (
                <button onClick={() => lastQ && ask(lastQ)} className="flex items-center gap-1.5 text-[12px] text-mute transition hover:text-clay">
                  <RotateCcw size={12} /> Try again
                </button>
              )}
              <div ref={endRef} />
            </div>

            <form
              onSubmit={(e) => {
                e.preventDefault();
                ask(input);
              }}
              className="border-t border-white/[0.07] p-4"
            >
              <div className="flex items-center gap-2 rounded-full border border-white/10 bg-ink px-4 py-1.5 focus-within:border-clay/60">
                <input
                  ref={inputRef}
                  value={input}
                  maxLength={2000}
                  onChange={(e) => {
                    setInput(e.target.value);
                    if (!docked && e.target.value) setDocked(true);
                  }}
                  placeholder="Ask about Voxula…"
                  className="flex-1 bg-transparent py-2 text-[14px] text-cream outline-none placeholder:text-mute/60"
                />
                <button type="submit" aria-label="Send" disabled={!input.trim() || typing} className="flex h-8 w-8 items-center justify-center rounded-full bg-clay text-ink transition disabled:opacity-30">
                  <ArrowUp size={16} />
                </button>
              </div>
            </form>
          </motion.div>
        </motion.div>
      )}
    </AnimatePresence>
  );
}
