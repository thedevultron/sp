import { motion, useReducedMotion } from "framer-motion";
import { KeyRound, Keyboard, Zap } from "lucide-react";
import { Reveal } from "../ui/Reveal";
import { ScrollFloat } from "../cinematic/TextMotion";
import FoldText from "../FoldText";

const STEPS = [
  {
    icon: KeyRound,
    title: "You paste a key",
    copy: "SPEAK reads your GEMINI_API_KEY from the local vault. You add a second key. SPEAK swaps on rate limit with zero pause.",
  },
  {
    icon: Keyboard,
    title: "You hold Ctrl+Space",
    copy: "The capsule opens over the active window. Focus stays where you left it. You release to commit.",
  },
  {
    icon: Zap,
    title: "You speak at pace",
    copy: "Audio streams through Gemini Live. Text lands at the caret in 142 ms median. You keep typing nothing.",
  },
];

export function PipelineSection() {
  const reduce = useReducedMotion();

  return (
    <section id="pipeline" className="relative py-24 sm:py-32">
      <div className="mx-auto max-w-[1200px] px-6">
        <ScrollFloat>
          <Reveal>
            <p className="text-center font-mono text-[11px] uppercase tracking-[0.22em] text-fog/60">
              01 — Pipeline
            </p>
          </Reveal>
          <h2 className="mx-auto mt-5 max-w-[16ch] text-center font-display text-4xl font-medium tracking-tight sm:text-5xl">
            <FoldText
              text="You press. SPEAK delivers."
              splitBy="word"
              hinge="top"
              trigger="scroll"
              duration={0.6}
              stagger={0.035}
              ease="power3.out"
              fontSize="1em"
              fontWeight={500}
              color="#d1e4fa"
              style={{ lineHeight: "1.14", letterSpacing: "-0.01em" }}
            />
          </h2>
          <Reveal delay={0.14}>
            <p className="mx-auto mt-5 max-w-[52ch] text-center text-[15px] leading-relaxed text-fog">
              Three moves take you from install to dictation. No setup wizard. No context switch.
            </p>
          </Reveal>
        </ScrollFloat>

        <div className="relative mt-16">
          {/* Connecting hairline */}
          <div aria-hidden="true" className="absolute left-[18%] right-[18%] top-8 hidden md:block">
            <motion.div
              className="h-px w-full origin-left bg-gradient-to-r from-transparent via-[rgba(186,215,247,0.3)] to-transparent"
              initial={reduce ? { opacity: 0 } : { scaleX: 0, opacity: 0 }}
              whileInView={reduce ? { opacity: 1 } : { scaleX: 1, opacity: 1 }}
              viewport={{ once: true, margin: "-80px" }}
              transition={{ duration: 1.2, delay: 0.3, ease: [0.22, 1, 0.36, 1] }}
            />
          </div>

          <div className="grid gap-14 md:grid-cols-3 md:gap-10">
            {STEPS.map((step, i) => {
              const Icon = step.icon;
              return (
                <Reveal key={step.title} delay={0.15 + i * 0.14} className="relative">
                  <div className="flex flex-col items-center text-center">
                    <div className="relative z-10 grid h-16 w-16 place-items-center rounded-full border border-edge bg-[rgba(186,214,247,0.06)] shadow-[inset_0_1px_0_rgba(255,255,255,0.12),0_12px_28px_rgba(0,0,0,0.5)] transition-all duration-500 hover:border-[rgba(182,217,252,0.45)] hover:shadow-[inset_0_1px_0_rgba(255,255,255,0.12),0_0_32px_rgba(182,217,252,0.16)]">
                      <Icon size={22} strokeWidth={1.5} className="text-frost" />
                    </div>
                    <span className="mt-6 font-mono text-[11px] uppercase tracking-[0.2em] text-blueprint">
                      Step 0{i + 1}
                    </span>
                    <h3 className="mt-2.5 font-display text-xl font-medium text-frost">{step.title}</h3>
                    <p className="mt-3 max-w-[36ch] text-[14px] leading-relaxed text-fog">{step.copy}</p>
                  </div>
                </Reveal>
              );
            })}
          </div>
        </div>
      </div>
    </section>
  );
}
