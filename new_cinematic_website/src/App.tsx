import { useCallback, useEffect, useRef, useState } from "react";
import { AnimatePresence, motion, useScroll, useSpring } from "framer-motion";
import Lenis from "lenis";
import { ArrowUpRight, Menu, X } from "lucide-react";
import { Loader } from "./components/Loader";
import { Hero } from "./components/Hero";
import { About, Manifesto } from "./components/Story";
import { Pipeline } from "./components/Pipeline";
import { Simulator } from "./components/Simulator";
import { Features } from "./components/Features";
import { Refine } from "./components/Refine";
import { Privacy } from "./components/Privacy";
import { DownloadFooter, Showcase } from "./components/Closing";
import { Docs } from "./components/Docs";
import { ProductModal } from "./components/Modals";
import { ChatDock } from "./components/ChatDock";
import { WaveLogo } from "./components/ui";
import { GITHUB_REPO_URL, type DemoState, type ModalKind } from "./site";
import { registerLenis, scrollToId, scrollToTop } from "./lib/scroll";
import { cn } from "./utils/cn";

const NAV_LINKS = [
  { label: "Overview", href: "#overview" },
  { label: "How it works", href: "#how-it-works" },
  { label: "Features", href: "#features" },
  { label: "Privacy", href: "#privacy" },
  { label: "Docs", href: "#/docs" },
];

const CHAPTERS = [
  { id: "overview", label: "Prologue" },
  { id: "manifesto", label: "I · The weight of typing" },
  { id: "how-it-works", label: "II · The shortcut" },
  { id: "simulator", label: "III · Your turn" },
  { id: "features", label: "IV · The toolkit" },
  { id: "refine", label: "V · The rewrite" },
  { id: "privacy", label: "VI · The vault" },
  { id: "showcase", label: "VII · Epilogue" },
];

type Page = "home" | "docs";

function parseHash(): { page: Page; id: string } {
  const p = window.location.pathname.toLowerCase();
  const h = window.location.hash;
  if (p === "/docs" || p.startsWith("/docs/") || h.startsWith("#/docs")) {
    const id = h.includes("#") ? h.split("#").pop() || "" : "";
    return { page: "docs", id };
  }
  return { page: "home", id: h.replace("#", "") };
}

export default function App() {
  const [loaded, setLoaded] = useState(false);
  const [page, setPage] = useState<Page>(() => parseHash().page);
  const [modal, setModal] = useState<ModalKind>(null);
  const [chat, setChat] = useState(false);
  const [menu, setMenu] = useState(false);
  const [scrolled, setScrolled] = useState(false);
  const [apiKey, setApiKey] = useState("");
  const [demo, setDemo] = useState<DemoState>({ active: false, text: "", progress: 12 });
  const [chapter, setChapter] = useState("overview");
  const pageRef = useRef<Page>(page);

  const { scrollYProgress } = useScroll();
  const progressX = useSpring(scrollYProgress, { stiffness: 120, damping: 30, restDelta: 0.001 });

  // smooth scroll
  useEffect(() => {
    if (window.matchMedia("(prefers-reduced-motion: reduce)").matches) return;
    const lenis = new Lenis({ duration: 1.15, smoothWheel: true });
    registerLenis(lenis);
    let raf = 0;
    const loop = (t: number) => {
      lenis.raf(t);
      raf = requestAnimationFrame(loop);
    };
    raf = requestAnimationFrame(loop);
    return () => {
      cancelAnimationFrame(raf);
      lenis.destroy();
      registerLenis(null);
    };
  }, []);

  // lock scroll during loader
  useEffect(() => {
    document.body.style.overflow = loaded ? "" : "hidden";
  }, [loaded]);

  // routing
  const route = useCallback((initial = false) => {
    const { page: next, id } = parseHash();
    const changed = next !== pageRef.current;
    pageRef.current = next;
    setPage(next);
    setMenu(false);
    const go = () => {
      if (id && document.getElementById(id)) scrollToId(id, changed || initial);
      else if (!initial) scrollToTop(changed);
    };
    if (changed || initial) setTimeout(go, initial ? 700 : 120);
    else go();
  }, []);

  useEffect(() => {
    const onClick = (e: MouseEvent) => {
      const a = (e.target as Element).closest?.("a");
      if (!a || a.hasAttribute("download")) return;
      const href = a.getAttribute("href");
      if (!href || !href.startsWith("#")) return;
      e.preventDefault();
      if (window.location.hash !== href) history.pushState(null, "", href);
      route();
    };
    const onPop = () => route();
    document.addEventListener("click", onClick);
    window.addEventListener("popstate", onPop);
    window.addEventListener("hashchange", onPop);
    if (window.location.hash) route(true);
    return () => {
      document.removeEventListener("click", onClick);
      window.removeEventListener("popstate", onPop);
      window.removeEventListener("hashchange", onPop);
    };
  }, [route]);

  // nav bg + chapter tracking
  useEffect(() => {
    const onScroll = () => setScrolled(window.scrollY > 40);
    onScroll();
    window.addEventListener("scroll", onScroll, { passive: true });
    return () => window.removeEventListener("scroll", onScroll);
  }, []);

  useEffect(() => {
    if (page !== "home") return;
    const obs = new IntersectionObserver(
      (entries) => entries.forEach((e) => e.isIntersecting && setChapter(e.target.id)),
      { rootMargin: "-45% 0px -50% 0px" }
    );
    const t = setTimeout(() => {
      CHAPTERS.forEach((c) => {
        const el = document.getElementById(c.id);
        if (el) obs.observe(el);
      });
    }, 100);
    return () => {
      clearTimeout(t);
      obs.disconnect();
    };
  }, [page]);

  const openModal = useCallback((m: ModalKind) => setModal(m), []);
  const closeModal = useCallback(() => setModal(null), []);
  const closeChat = useCallback(() => setChat(false), []);

  return (
    <div className="min-h-screen bg-ink font-sans text-cream">
      <AnimatePresence>{!loaded && <Loader onDone={() => setLoaded(true)} />}</AnimatePresence>

      <motion.div style={{ scaleX: progressX }} className="fixed left-0 right-0 top-0 z-[70] h-[2px] origin-left bg-gradient-to-r from-clay to-amber" />

      {/* NAV */}
      <motion.header
        initial={{ y: -80, opacity: 0 }}
        animate={loaded ? { y: 0, opacity: 1 } : {}}
        transition={{ duration: 1, delay: 0.3, ease: [0.16, 1, 0.3, 1] }}
        className={cn(
          "fixed inset-x-0 top-0 z-[60] transition-all duration-500",
          scrolled ? "border-b border-white/[0.07] bg-ink/75 backdrop-blur-xl" : "border-b border-transparent"
        )}
      >
        <div className="mx-auto flex h-[68px] max-w-7xl items-center justify-between gap-4 px-5 md:px-10">
          <a href="#overview" className="flex items-center gap-2.5" onClick={() => setMenu(false)}>
            <WaveLogo size={28} />
            <span className="font-display text-[1.6rem] leading-none text-cream">Voxula</span>
          </a>
          <nav className="hidden items-center gap-1 lg:flex">
            {NAV_LINKS.map((l) => (
              <a key={l.label} href={l.href} className="rounded-full px-3.5 py-2 text-[13.5px] text-mute transition hover:bg-white/[0.06] hover:text-cream">
                {l.label}
              </a>
            ))}
            <a href={GITHUB_REPO_URL} target="_blank" rel="noreferrer" className="flex items-center gap-1 rounded-full px-3.5 py-2 text-[13.5px] text-mute transition hover:bg-white/[0.06] hover:text-cream">
              GitHub <ArrowUpRight size={13} />
            </a>
          </nav>
          <div className="flex items-center gap-3">
            <span className="hidden items-center gap-2 rounded-full border border-white/10 px-3 py-1.5 text-[12px] text-mute xl:flex">
              <span className="h-1.5 w-1.5 rounded-full bg-sage" style={{ animation: "pulse-dot 1.6s infinite" }} />
              Free. Forever.
            </span>
            <button
              onClick={() => openModal("download")}
              className="flex items-center gap-1.5 rounded-full bg-cream px-4 py-2 text-[13.5px] font-medium text-ink transition hover:bg-clay"
            >
              <span className="hidden sm:inline">Get Voxula AI</span>
              <span className="sm:hidden">Get</span>
              <ArrowUpRight size={14} />
            </button>
            <button onClick={() => setMenu((m) => !m)} aria-label="Menu" className="rounded-full border border-white/10 p-2 text-cream lg:hidden">
              {menu ? <X size={18} /> : <Menu size={18} />}
            </button>
          </div>
        </div>
        <AnimatePresence>
          {menu && (
            <motion.div
              initial={{ height: 0, opacity: 0 }}
              animate={{ height: "auto", opacity: 1 }}
              exit={{ height: 0, opacity: 0 }}
              className="overflow-hidden border-t border-white/[0.07] bg-ink/95 backdrop-blur-xl lg:hidden"
            >
              <div className="flex flex-col px-6 py-4">
                {[...NAV_LINKS].map((l) => (
                  <a key={l.label} href={l.href} onClick={() => setMenu(false)} className="font-display border-b border-white/[0.06] py-4 text-3xl text-cream">
                    {l.label}
                  </a>
                ))}
                <a href={GITHUB_REPO_URL} target="_blank" rel="noreferrer" onClick={() => setMenu(false)} className="font-display flex items-center gap-2 py-4 text-3xl text-cream">
                  GitHub <ArrowUpRight size={22} className="text-clay" />
                </a>
              </div>
            </motion.div>
          )}
        </AnimatePresence>
      </motion.header>

      {/* chapter indicator */}
      {page === "home" && loaded && (
        <div className="pointer-events-none fixed right-5 top-1/2 z-40 hidden -translate-y-1/2 flex-col items-end gap-3 xl:flex">
          {CHAPTERS.map((c) => {
            const on = chapter === c.id;
            return (
              <a key={c.id} href={`#${c.id}`} className="pointer-events-auto group flex items-center gap-3">
                <span className={cn("font-mono text-[10px] tracking-wider transition-all duration-300", on ? "translate-x-0 text-cream opacity-100" : "translate-x-2 text-mute opacity-0 group-hover:translate-x-0 group-hover:opacity-100")}>
                  {c.label}
                </span>
                <span className={cn("block rounded-full transition-all duration-500", on ? "h-6 w-[3px] bg-clay" : "h-1.5 w-1.5 bg-white/25 group-hover:bg-clay/70")} />
              </a>
            );
          })}
        </div>
      )}

      <AnimatePresence mode="wait">
        <motion.main
          key={page}
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          exit={{ opacity: 0 }}
          transition={{ duration: 0.4, ease: [0.16, 1, 0.3, 1] }}
        >
          {page === "home" ? (
            <>
              <Hero ready={loaded} demo={demo} openModal={openModal} />
              <div id="manifesto">
                <Manifesto />
              </div>
              <About />
              <Pipeline />
              <Simulator onDemo={setDemo} />
              <Features />
              <Refine />
              <Privacy />
              <Showcase openModal={openModal} />
              <DownloadFooter openModal={openModal} openChat={() => setChat(true)} />
            </>
          ) : (
            <>
              <Docs openModal={openModal} />
              <DownloadFooter openModal={openModal} openChat={() => setChat(true)} />
            </>
          )}
        </motion.main>
      </AnimatePresence>

      <ProductModal kind={modal} onClose={closeModal} keyValue={apiKey} setKeyValue={setApiKey} />
      <ChatDock open={chat} onClose={closeChat} />
    </div>
  );
}
