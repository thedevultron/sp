import { useEffect, useState } from "react";
import { Download } from "lucide-react";
import { cn } from "../../utils/cn";
import { VoidVioletButton } from "./VoidVioletButton";
import { INSTALLER_FILE, INSTALLER_URL, INSTALLER_VERSION } from "../../lib/download";

interface TopNavProps {
  onNavigate: (id: string) => void;
}

const LINKS = [
  { id: "simulator", label: "Simulator" },
  { id: "pillars", label: "Architecture" },
  { id: "security", label: "Security" },
];

export function TopNav({ onNavigate }: TopNavProps) {
  const [scrolled, setScrolled] = useState(false);

  useEffect(() => {
    let raf = 0;
    const onScroll = () => {
      if (raf) return;
      raf = requestAnimationFrame(() => {
        raf = 0;
        setScrolled(window.scrollY > 28);
      });
    };
    onScroll();
    window.addEventListener("scroll", onScroll, { passive: true });
    return () => {
      window.removeEventListener("scroll", onScroll);
      cancelAnimationFrame(raf);
    };
  }, []);

  return (
    <header className="fixed inset-x-0 top-0 z-50 px-3 sm:px-6">
      <div
        className={cn(
          "mx-auto mt-4 flex max-w-[920px] items-center justify-between gap-4 rounded-full border py-2 pl-4 pr-2 transition-all duration-500",
          scrolled
            ? "border-edge bg-[rgba(5,6,15,0.85)] shadow-[var(--shadow-widget)] backdrop-blur-xl"
            : "border-transparent bg-transparent"
        )}
      >
        <button
          type="button"
          onClick={() => onNavigate("top")}
          className="group flex items-center gap-2.5"
          aria-label="SPEAK — back to top"
        >
          <svg viewBox="0 0 24 24" className="h-[22px] w-[22px] transition-transform duration-300 group-hover:scale-110" aria-hidden="true">
            <rect x="1" y="1" width="22" height="22" rx="7" fill="rgba(186,214,247,0.06)" stroke="rgba(186,215,247,0.22)" strokeWidth="1" />
            <rect x="5.5" y="10" width="2" height="4" rx="1" fill="#b6d9fc" />
            <rect x="9.25" y="7" width="2" height="10" rx="1" fill="#663af3" />
            <rect x="13" y="9" width="2" height="6" rx="1" fill="#b6d9fc" />
            <rect x="16.75" y="11" width="2" height="3" rx="1" fill="#b6d9fc" opacity="0.7" />
          </svg>
          <span className="font-display text-[15px] font-semibold tracking-[0.24em] text-frost">SPEAK</span>
          <span className="rounded-[6px] border border-edge px-1.5 py-0.5 font-mono text-[9.5px] uppercase tracking-[0.1em] text-blueprint">
            v{INSTALLER_VERSION}
          </span>
        </button>

        <nav className="hidden items-center gap-1 md:flex" aria-label="Primary">
          {LINKS.map((l) => (
            <button
              key={l.id}
              type="button"
              onClick={() => onNavigate(l.id)}
              className="rounded-full px-3.5 py-1.5 text-[13px] font-medium text-fog transition-colors duration-200 hover:bg-white/[0.04] hover:text-frost"
            >
              {l.label}
            </button>
          ))}
        </nav>

        <VoidVioletButton size="md" href={INSTALLER_URL} download={INSTALLER_FILE} icon={<Download size={15} strokeWidth={2} />}>
          <span className="hidden sm:inline">Download</span>
          <span className="sm:hidden">Get</span>
        </VoidVioletButton>
      </div>
    </header>
  );
}
