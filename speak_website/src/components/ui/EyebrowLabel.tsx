import type { ReactNode } from "react";
import { cn } from "../../utils/cn";

interface EyebrowLabelProps {
  children: ReactNode;
  align?: "left" | "center";
  className?: string;
}

/** dotDigital-style all-caps mono label flanked by fading hairline rules. */
export function EyebrowLabel({ children, align = "center", className }: EyebrowLabelProps) {
  return (
    <div
      className={cn(
        "flex items-center gap-5",
        align === "center" ? "justify-center" : "justify-start",
        className
      )}
    >
      <span
        aria-hidden="true"
        className={cn(
          "h-px w-full max-w-[150px] flex-1 bg-gradient-to-r from-transparent to-[rgba(186,215,247,0.3)]",
          align === "left" && "hidden"
        )}
      />
      <span className="whitespace-nowrap font-mono text-[15px] font-normal uppercase leading-none tracking-[0.1em] text-mist">
        <span className="text-fog/60">[</span> {children} <span className="text-fog/60">]</span>
      </span>
      <span
        aria-hidden="true"
        className="h-px w-full max-w-[150px] flex-1 bg-gradient-to-l from-transparent to-[rgba(186,215,247,0.3)]"
      />
    </div>
  );
}
