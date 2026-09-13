import type { ReactNode } from "react";
import { cn } from "../../utils/cn";

interface VoidVioletButtonProps {
  children: ReactNode;
  icon?: ReactNode;
  onClick?: () => void;
  href?: string;
  /** Passed to the anchor as the download filename. Forces a file download. */
  download?: string | boolean;
  size?: "md" | "lg";
  className?: string;
  disabled?: boolean;
}

/** The singular chromatic action — solid Void Violet pill. */
export function VoidVioletButton({
  children,
  icon,
  onClick,
  href,
  download,
  size = "md",
  className,
  disabled,
}: VoidVioletButtonProps) {
  const cls = cn(
    "group/vbtn btn-shine relative inline-flex items-center justify-center gap-2.5 overflow-hidden rounded-full",
    "bg-violet font-body font-medium text-white",
    "shadow-[0_8px_28px_rgba(102,58,243,0.35),inset_0_1px_0_rgba(255,255,255,0.28)]",
    "transition-all duration-300 ease-out",
    !disabled &&
      "hover:bg-violet-bright hover:shadow-[0_0_0_1px_rgba(122,82,255,0.55),0_14px_44px_rgba(102,58,243,0.5)] active:scale-[0.97]",
    disabled && "cursor-wait",
    size === "lg" ? "px-8 py-3.5 text-[15px]" : "px-6 py-2.5 text-sm",
    className
  );

  const inner = (
    <>
      {/* top sheen */}
      <span
        aria-hidden="true"
        className="pointer-events-none absolute inset-x-4 top-0 h-px bg-gradient-to-r from-transparent via-white/50 to-transparent"
      />
      {icon && <span className="shrink-0 transition-transform duration-300 group-hover/vbtn:scale-110">{icon}</span>}
      <span className="whitespace-nowrap">{children}</span>
    </>
  );

  if (href) {
    return (
      <a href={href} onClick={onClick} download={download ?? (href.endsWith(".exe") ? true : undefined)} className={cls}>
        {inner}
      </a>
    );
  }
  return (
    <button type="button" onClick={onClick} disabled={disabled} className={cls}>
      {inner}
    </button>
  );
}
