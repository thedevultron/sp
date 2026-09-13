import { AnimatePresence, motion } from "framer-motion";
import { cn } from "../../utils/cn";

interface TranscriptDrawerProps {
  open: boolean;
  text: string;
  streaming: boolean;
}

/** Frosted-glass slide-down drawer carrying the live transcript. */
export function TranscriptDrawer({ open, text, streaming }: TranscriptDrawerProps) {
  return (
    <AnimatePresence initial={false}>
      {open && (
        <motion.div
          key="transcript-drawer"
          initial={{ height: 0, opacity: 0 }}
          animate={{ height: "auto", opacity: 1 }}
          exit={{ height: 0, opacity: 0 }}
          transition={{ duration: 0.45, ease: [0.22, 1, 0.36, 1] }}
          className="overflow-hidden"
        >
          <div className="mt-3.5 rounded-xl border border-edge bg-[rgba(186,214,247,0.03)] p-4 shadow-[inset_0_1px_0_rgba(255,255,255,0.06)]">
            <div className="mb-2 flex items-center gap-2">
              <span
                className={cn(
                  "h-1.5 w-1.5 rounded-full",
                  streaming ? "anim-ping-soft bg-token-green" : "bg-fog/50"
                )}
              />
              <span className="font-mono text-[10px] uppercase tracking-[0.16em] text-fog">
                {streaming ? "Live transcript" : "Transcript · idle"}
              </span>
            </div>
            <p className="min-h-[3.4em] font-body text-[13px] leading-relaxed text-mist">
              {text.length > 0 ? text : <span className="text-fog/60">Waiting for speech. Press Ctrl+Space.</span>}
              {streaming && <span className="type-caret" />}
            </p>
          </div>
        </motion.div>
      )}
    </AnimatePresence>
  );
}
