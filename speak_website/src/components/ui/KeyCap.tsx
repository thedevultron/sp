import type { ReactNode } from "react";
import { cn } from "../../utils/cn";

interface KeyCapProps {
  children: ReactNode;
  active?: boolean;
  className?: string;
}

/** Tactile <kbd> keycap with inset top highlight and depressed state. */
export function KeyCap({ children, active = false, className }: KeyCapProps) {
  return (
    <kbd className={cn("keycap", active && "keycap-active", className)}>
      {children}
    </kbd>
  );
}
