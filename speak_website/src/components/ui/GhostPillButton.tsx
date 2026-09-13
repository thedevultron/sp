import type { ReactNode } from "react";
import { cn } from "../../utils/cn";

interface GhostPillButtonProps {
  children: ReactNode;
  icon?: ReactNode;
  onClick?: () => void;
  className?: string;
}

/** Translucent frosted pill with inset hairline edge. */
export function GhostPillButton({ children, icon, onClick, className }: GhostPillButtonProps) {
  return (
    <button
      type="button"
      onClick={onClick}
      className={cn(
        "group/gbtn btn-shine inline-flex items-center justify-center gap-2.5 rounded-full px-6 py-3",
        "border border-edge bg-[rgba(186,214,247,0.06)] text-[14px] font-medium text-frost",
        "shadow-[inset_0_1px_0_rgba(255,255,255,0.1)]",
        "transition-all duration-300 ease-out",
        "hover:border-[rgba(186,215,247,0.28)] hover:bg-[rgba(186,214,247,0.11)] hover:text-white active:scale-[0.97]",
        className
      )}
    >
      {icon && <span className="shrink-0 text-mist transition-colors duration-300 group-hover/gbtn:text-blueprint">{icon}</span>}
      <span className="whitespace-nowrap">{children}</span>
    </button>
  );
}
