import {
  motion,
  useScroll,
  useTransform,
  type MotionValue,
} from "framer-motion";
import { useRef, type ReactNode } from "react";
import { ArrowUpRight, Download } from "lucide-react";
import { cn } from "../utils/cn";

export function WaveLogo({ size = 28, className }: { size?: number; className?: string }) {
  const bars = [
    { x: 4, h: 8 },
    { x: 9, h: 16 },
    { x: 14, h: 22 },
    { x: 19, h: 14 },
    { x: 24, h: 6 },
  ];
  return (
    <svg width={size} height={size} viewBox="0 0 32 32" className={className} aria-hidden>
      {bars.map((b) => (
        <rect key={b.x} x={b.x} y={16 - b.h / 2} width="3" height={b.h} rx="1.5" fill="#4c8dff" />
      ))}
    </svg>
  );
}

export function KeyCap({
  children,
  tone = "dark",
  className,
}: {
  children: ReactNode;
  tone?: "dark" | "light";
  className?: string;
}) {
  return (
    <kbd
      className={cn(
        "inline-flex min-w-[1.6rem] items-center justify-center rounded-md border px-1.5 py-0.5 font-mono text-[11px] leading-none shadow-[0_1px_0_rgba(0,0,0,0.35)]",
        tone === "dark"
          ? "border-white/15 bg-white/[0.06] text-cream"
          : "border-black/15 bg-white/60 text-ink",
        className
      )}
    >
      {children}
    </kbd>
  );
}

export function Eyebrow({
  children,
  tone = "dark",
  className,
}: {
  children: ReactNode;
  tone?: "dark" | "light";
  className?: string;
}) {
  return (
    <div
      className={cn(
        "flex items-center gap-3 font-mono text-[11px] uppercase tracking-[0.22em]",
        tone === "dark" ? "text-clay" : "text-clay-deep",
        className
      )}
    >
      <span className="h-px w-8 bg-current opacity-70" />
      {children}
    </div>
  );
}

export function PrimaryButton({
  children,
  onClick,
  href,
  download,
  className,
  icon = true,
  target,
}: {
  children: ReactNode;
  onClick?: () => void;
  href?: string;
  download?: boolean;
  className?: string;
  icon?: boolean;
  target?: string;
}) {
  const cls = cn(
    "group relative inline-flex items-center gap-3 overflow-hidden rounded-full bg-clay px-6 py-3.5 text-[15px] font-medium text-ink shadow-[0_10px_40px_-10px_rgba(76,141,255,0.7)] transition-transform duration-300 hover:-translate-y-0.5 active:translate-y-0",
    className
  );
  const inner = (
    <>
      <span className="absolute inset-0 -translate-x-full bg-gradient-to-r from-transparent via-white/40 to-transparent transition-transform duration-700 group-hover:translate-x-full" />
      {icon && <Download size={17} className="relative" />}
      <span className="relative flex items-center gap-3">{children}</span>
    </>
  );
  if (href)
    return (
      <a href={href} className={cls} download={download} target={target} rel={target ? "noreferrer" : undefined}>
        {inner}
      </a>
    );
  return (
    <button onClick={onClick} className={cls}>
      {inner}
    </button>
  );
}

export function GhostButton({
  children,
  onClick,
  href,
  arrow = true,
  tone = "dark",
  className,
  target,
  download,
}: {
  children: ReactNode;
  onClick?: () => void;
  href?: string;
  arrow?: boolean;
  tone?: "dark" | "light";
  className?: string;
  target?: string;
  download?: boolean;
}) {
  const cls = cn(
    "group inline-flex items-center gap-2 rounded-full border px-5 py-3 text-[14px] font-medium transition-all duration-300",
    tone === "dark"
      ? "border-white/15 text-cream hover:border-clay/60 hover:bg-white/[0.04]"
      : "border-black/15 text-ink hover:border-clay-deep hover:bg-black/[0.03]",
    className
  );
  const inner = (
    <>
      {children}
      {arrow && (
        <ArrowUpRight
          size={16}
          className="transition-transform duration-300 group-hover:-translate-y-0.5 group-hover:translate-x-0.5"
        />
      )}
    </>
  );
  if (href)
    return (
      <a href={href} className={cls} target={target} download={download} rel={target ? "noreferrer" : undefined}>
        {inner}
      </a>
    );
  return (
    <button onClick={onClick} className={cls}>
      {inner}
    </button>
  );
}

/** Rise + deblur reveal on enter */
export function Reveal({
  children,
  delay = 0,
  className,
  y = 36,
}: {
  children: ReactNode;
  delay?: number;
  className?: string;
  y?: number;
}) {
  return (
    <motion.div
      className={className}
      initial={{ opacity: 0, y, filter: "blur(10px)" }}
      whileInView={{ opacity: 1, y: 0, filter: "blur(0px)" }}
      viewport={{ once: true, margin: "-10% 0px -10% 0px" }}
      transition={{ duration: 1, delay, ease: [0.16, 1, 0.3, 1] }}
    >
      {children}
    </motion.div>
  );
}

/** Heading that reveals line-by-line (words rising out of a mask) */
export function RiseText({
  text,
  className,
  delay = 0,
}: {
  text: string;
  className?: string;
  delay?: number;
}) {
  const words = text.split(" ");
  return (
    <span className={className} role="text" aria-label={text}>
      {words.map((w, i) => (
        <span key={i} className="inline-block overflow-hidden pb-[0.12em] align-bottom" aria-hidden>
          <motion.span
            className="inline-block"
            initial={{ y: "110%", rotate: 4 }}
            whileInView={{ y: "0%", rotate: 0 }}
            viewport={{ once: true, margin: "-10%" }}
            transition={{ duration: 1.1, delay: delay + i * 0.07, ease: [0.16, 1, 0.3, 1] }}
          >
            {w}
            {i < words.length - 1 ? "\u00A0" : ""}
          </motion.span>
        </span>
      ))}
    </span>
  );
}

function Word({
  children,
  progress,
  range,
  className,
}: {
  children: string;
  progress: MotionValue<number>;
  range: [number, number];
  className?: string;
}) {
  const opacity = useTransform(progress, range, [0.14, 1]);
  const y = useTransform(progress, range, [6, 0]);
  return (
    <motion.span style={{ opacity, y }} className={cn("inline-block", className)}>
      {children}
    </motion.span>
  );
}

/** Words light up as you scroll through the block */
export function ScrollWords({
  text,
  className,
  highlights = [],
  progress,
  start = 0,
  end = 1,
}: {
  text: string;
  className?: string;
  highlights?: string[];
  progress: MotionValue<number>;
  start?: number;
  end?: number;
}) {
  const words = text.split(" ");
  return (
    <p className={className}>
      {words.map((w, i) => {
        const a = start + (i / words.length) * (end - start);
        const b = a + (end - start) / words.length * 3;
        const clean = w.replace(/[.,]/g, "").toLowerCase();
        const hi = highlights.includes(clean);
        return (
          <span key={i}>
            <Word progress={progress} range={[a, Math.min(b, end)]} className={hi ? "text-ember italic" : ""}>
              {w}
            </Word>{" "}
          </span>
        );
      })}
    </p>
  );
}

export function useSectionProgress(offset: any = ["start start", "end end"]) {
  const ref = useRef<HTMLDivElement>(null);
  const { scrollYProgress } = useScroll({ target: ref, offset });
  return { ref, progress: scrollYProgress };
}

export function VoiceBars({
  count = 24,
  className,
  height = 40,
  color = "#4c8dff",
  active = true,
}: {
  count?: number;
  className?: string;
  height?: number;
  color?: string;
  active?: boolean;
}) {
  return (
    <div className={cn("flex items-center gap-[3px]", className)} style={{ height }}>
      {Array.from({ length: count }).map((_, i) => {
        const base = 0.35 + 0.65 * Math.abs(Math.sin(i * 0.9));
        return (
          <span
            key={i}
            className="w-[3px] origin-center rounded-full"
            style={{
              height: `${base * 100}%`,
              background: color,
              opacity: active ? 0.4 + base * 0.6 : 0.3,
              animation: active ? `bar ${0.7 + (i % 5) * 0.18}s ease-in-out ${i * 0.05}s infinite` : "none",
              transform: active ? undefined : "scaleY(0.3)",
            }}
          />
        );
      })}
    </div>
  );
}

export function SectionShell({
  id,
  tone = "dark",
  children,
  className,
}: {
  id?: string;
  tone?: "dark" | "light" | "ember";
  children: ReactNode;
  className?: string;
}) {
  return (
    <section
      id={id}
      className={cn(
        "relative",
        tone === "dark" && "bg-ink text-cream",
        tone === "light" && "bg-paper text-ink",
        tone === "ember" && "bg-ink-2 text-cream",
        className
      )}
    >
      {children}
    </section>
  );
}

export function ChapterMark({
  num,
  title,
  tone = "dark",
}: {
  num: string;
  title: string;
  tone?: "dark" | "light";
}) {
  return (
    <div
      className={cn(
        "flex items-center gap-4 font-mono text-[11px] uppercase tracking-[0.25em]",
        tone === "dark" ? "text-mute" : "text-mute-dark"
      )}
    >
      <span className="font-display text-3xl italic normal-case tracking-normal text-clay">{num}</span>
      <span>{title}</span>
    </div>
  );
}
