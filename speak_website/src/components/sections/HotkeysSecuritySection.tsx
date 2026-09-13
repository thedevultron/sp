import { useEffect, useState } from "react";
import { Cpu, Lock, ServerOff } from "lucide-react";
import { GlassCard } from "../ui/GlassCard";
import { KeyCap } from "../ui/KeyCap";
import { Reveal } from "../ui/Reveal";
import { ScrollFloat } from "../cinematic/TextMotion";
import FoldText from "../FoldText";
import type { HotkeyDef } from "../../types";

const HOTKEYS: HotkeyDef[] = [
  {
    keys: [
      { label: "Ctrl", match: "Control" },
      { label: "Space", match: "Space" },
    ],
    label: "Global Dictation Toggle",
    description: "You summon the capsule over any window. Focus stays put.",
  },
  {
    keys: [
      { label: "Win", match: "Meta" },
      { label: "Shift", match: "Shift" },
    ],
    label: "Screen Companion",
    description: "You stream viewport plus voice for live visual review.",
  },
  {
    keys: [
      { label: "Ctrl", match: "Control" },
      { label: "Win", match: "Meta" },
    ],
    label: "Purge Session",
    description: "You wipe context and start fresh in one move.",
  },
  {
    keys: [{ label: "Esc", match: "Escape" }],
    label: "Clear and Tray",
    description: "You erase ink and send SPEAK to the tray.",
  },
];

const PILLARS = [
  {
    icon: Lock,
    stat: "DPAPI · AES-256",
    title: "Windows Credential Manager",
    copy: "You paste keys once. Windows DPAPI seals them. No plaintext. No disk leak.",
  },
  {
    icon: ServerOff,
    stat: "0 log lines",
    title: "Zero Intermediate Servers",
    copy: "You stream direct to Gemini over WebSockets. No proxy. No tracker. No middleman.",
  },
  {
    icon: Cpu,
    stat: "<0.1% CPU idle",
    title: "Silent Footprint",
    copy: "SPEAK idles under 0.1% CPU in the tray. You call it. It answers.",
  },
];

export function HotkeysSecuritySection() {
  const [pressed, setPressed] = useState<Set<string>>(new Set());

  useEffect(() => {
    const down = (e: KeyboardEvent) => {
      const key = e.code === "Space" ? "Space" : e.key === "Escape" ? "Escape" : e.key;
      setPressed((s) => new Set(s).add(key));
    };
    const up = (e: KeyboardEvent) => {
      const key = e.code === "Space" ? "Space" : e.key === "Escape" ? "Escape" : e.key;
      setPressed((s) => {
        const n = new Set(s);
        n.delete(key);
        return n;
      });
    };
    const blur = () => setPressed(new Set());
    window.addEventListener("keydown", down);
    window.addEventListener("keyup", up);
    window.addEventListener("blur", blur);
    return () => {
      window.removeEventListener("keydown", down);
      window.removeEventListener("keyup", up);
      window.removeEventListener("blur", blur);
    };
  }, []);

  return (
    <section id="security" className="relative py-24 sm:py-32">
      <div className="mx-auto max-w-[1200px] px-6">
        <ScrollFloat>
          <Reveal>
            <p className="text-center font-mono text-[11px] uppercase tracking-[0.22em] text-fog/60">
              03 — Keys and trust
            </p>
          </Reveal>
          <h2 className="mx-auto mt-5 max-w-[20ch] text-center font-display text-4xl font-medium tracking-tight sm:text-5xl">
            <FoldText
              text="You hold the keys. Nothing leaves the machine."
              splitBy="word"
              hinge="top"
              trigger="scroll"
              duration={0.6}
              stagger={0.03}
              ease="power3.out"
              fontSize="1em"
              fontWeight={500}
              color="#d1e4fa"
              style={{ lineHeight: "1.14", letterSpacing: "-0.01em" }}
            />
          </h2>
        </ScrollFloat>

        <div className="mt-16 grid gap-5 lg:grid-cols-[1.06fr_0.94fr]">
          {/* Tactile hotkey matrix */}
          <Reveal delay={0.1}>
            <GlassCard className="h-full p-7 sm:p-8">
              <div className="flex items-center justify-between">
                <span className="font-mono text-[11px] uppercase tracking-[0.18em] text-fog">Hotkey matrix</span>
                <span className="font-mono text-[10px] uppercase tracking-[0.14em] text-fog/60">4 bindings</span>
              </div>

              <div className="mt-4 divide-y divide-edge">
                {HOTKEYS.map((h) => (
                  <div key={h.label} className="flex items-center justify-between gap-6 py-5">
                    <div className="flex shrink-0 items-center gap-1.5">
                      {h.keys.map((k, i) => (
                        <span key={k.label} className="flex items-center gap-1.5">
                          {i > 0 && <span className="font-mono text-[11px] text-fog/60">+</span>}
                          <KeyCap active={pressed.has(k.match)}>{k.label}</KeyCap>
                        </span>
                      ))}
                    </div>
                    <div className="min-w-0 text-right">
                      <p className="truncate text-[14px] font-medium text-frost">{h.label}</p>
                      <p className="mt-0.5 text-[12.5px] leading-snug text-fog">{h.description}</p>
                    </div>
                  </div>
                ))}
              </div>

              <p className="mt-5 rounded-lg border border-edge bg-white/[0.02] px-4 py-2.5 text-center font-mono text-[10.5px] tracking-wide text-fog/80">
                Press keys now. The matrix lights up with you
              </p>
            </GlassCard>
          </Reveal>

          {/* Security pillars */}
          <div className="flex flex-col">
            {PILLARS.map((p, i) => {
              const Icon = p.icon;
              return (
                <Reveal key={p.title} delay={0.12 + i * 0.1} className={i > 0 ? "border-t border-edge" : ""}>
                  <div className="group flex gap-5 py-7 first:pt-0">
                    <div className="grid h-11 w-11 shrink-0 place-items-center rounded-full border border-edge bg-white/[0.04] shadow-[inset_0_1px_0_rgba(255,255,255,0.12)] transition-all duration-500 group-hover:border-[rgba(182,217,252,0.4)] group-hover:shadow-[0_0_24px_rgba(182,217,252,0.14)]">
                      <Icon size={18} strokeWidth={1.5} className="text-frost" />
                    </div>
                    <div className="min-w-0">
                      <div className="flex flex-wrap items-center gap-3">
                        <span className="font-mono text-[11px] tabular-nums text-fog/50">0{i + 1}</span>
                        <h3 className="font-display text-lg font-medium text-frost">{p.title}</h3>
                        <span className="rounded-full border border-edge bg-white/[0.03] px-2.5 py-0.5 font-mono text-[9.5px] uppercase tracking-[0.12em] text-blueprint">
                          {p.stat}
                        </span>
                      </div>
                      <p className="mt-2.5 text-[14px] leading-relaxed text-fog">{p.copy}</p>
                    </div>
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
