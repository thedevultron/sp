import { useCallback, useEffect, useRef, useState } from "react";
import Lenis from "lenis";
import { gsap } from "gsap";
import { ScrollTrigger } from "gsap/ScrollTrigger";
import { motion, useMotionValue, useReducedMotion, useSpring } from "framer-motion";
import { TopNav } from "./components/ui/TopNav";
import { HeroSection } from "./components/sections/HeroSection";
import { PipelineSection } from "./components/sections/PipelineSection";
import { SimulatorSection } from "./components/sections/SimulatorSection";
import { BentoPillarsSection } from "./components/sections/BentoPillarsSection";
import { HotkeysSecuritySection } from "./components/sections/HotkeysSecuritySection";
import { DownloadFooterSection } from "./components/sections/DownloadFooterSection";
import { Preloader } from "./components/cinematic/Preloader";
import ClickSpark from "./components/ClickSpark";
import { ensureScrollPlugins, refreshScrollTriggers } from "./lib/motion";
import { getQualityTier, qualityFlags } from "./lib/perf";

gsap.registerPlugin(ScrollTrigger);

export default function App() {
  const reduce = useReducedMotion();
  const lenisRef = useRef<Lenis | null>(null);
  const [ready, setReady] = useState(false);
  const [tier] = useState(() => getQualityTier());
  const flags = qualityFlags(tier);

  /* Quality gate on <html> for CSS fallbacks. */
  useEffect(() => {
    document.documentElement.classList.toggle("quality-low", tier === "low");
    document.documentElement.classList.toggle("quality-medium", tier === "medium");
    document.documentElement.classList.toggle("quality-high", tier === "high");
  }, [tier]);

  /* Lenis bound into GSAP ticker. Tuned lerp + bypass on low/reduced/coarse/narrow. */
  useEffect(() => {
    ensureScrollPlugins();
    const reduceMotion = window.matchMedia("(prefers-reduced-motion: reduce)").matches;
    const coarse = window.matchMedia("(pointer: coarse)").matches;
    const narrow = window.innerWidth < 768;
    if (reduceMotion || coarse || narrow || tier === "low") return;

    const lenis = new Lenis({ lerp: 0.1, smoothWheel: true, wheelMultiplier: 1 });
    lenisRef.current = lenis;
    lenis.on("scroll", ScrollTrigger.update);
    const tick = (time: number) => lenis.raf(time * 1000);
    gsap.ticker.add(tick);
    gsap.ticker.lagSmoothing(0);

    return () => {
      gsap.ticker.remove(tick);
      lenis.destroy();
      lenisRef.current = null;
    };
  }, [tier]);

  /* Scroll-depth drives beam via transform/opacity only (compositor, no repaint). */
  useEffect(() => {
    let raf = 0;
    const st = ScrollTrigger.create({
      trigger: document.body,
      start: "top top",
      end: "bottom bottom",
      scrub: 0.8,
      onUpdate: (self) => {
        cancelAnimationFrame(raf);
        raf = requestAnimationFrame(() => {
          const p = self.progress;
          document.documentElement.style.setProperty("--beam-shift", `${(p * 220).toFixed(1)}px`);
          document.documentElement.style.setProperty("--beam-opacity", (1 - p * 0.35).toFixed(3));
          document.documentElement.style.setProperty("--scroll-progress", p.toFixed(4));
        });
      },
    });
    refreshScrollTriggers();
    return () => {
      cancelAnimationFrame(raf);
      st.kill();
    };
  }, []);

  const navigate = useCallback(
    (id: string) => {
      const el = document.getElementById(id);
      if (!el) return;
      if (lenisRef.current) {
        lenisRef.current.scrollTo(el, { offset: id === "top" ? 0 : -24, duration: 1.35 });
      } else {
        el.scrollIntoView({ behavior: reduce ? "auto" : "smooth", block: "start" });
      }
    },
    [reduce]
  );

  const sparkWrap = flags.sparks && !reduce;

  const chrome = (
    <>
      <AmbientCanvas noise={flags.noise} />
      {flags.cursorGlow && <CursorGlow />}
      <TopNav onNavigate={navigate} />
      <main className="relative z-10">
        <HeroSection onNavigate={navigate} />
        <div className="section-divider" aria-hidden="true" />
        <PipelineSection />
        <SimulatorSection />
        <BentoPillarsSection />
        <HotkeysSecuritySection />
        <div className="section-divider" aria-hidden="true" />
        <DownloadFooterSection onNavigate={navigate} />
      </main>
    </>
  );

  return (
    <div className="relative min-h-screen overflow-x-clip bg-midnight font-body text-frost">
      {!ready && <Preloader onDone={() => setReady(true)} />}
      {sparkWrap ? (
        <ClickSpark
          sparkColor="#d8ecf8"
          sparkSize={9}
          sparkRadius={22}
          sparkCount={8}
          duration={520}
          easing="ease-out"
          extraScale={1.15}
        >
          {chrome}
        </ClickSpark>
      ) : (
        chrome
      )}
    </div>
  );
}

/* ── Ambient layers: blueprint grid, conic halo, scroll beam, noise ── */

function AmbientCanvas({ noise }: { noise: boolean }) {
  return (
    <>
      <div className="blueprint-grid" aria-hidden="true" />
      <div className="conic-halo" aria-hidden="true" />
      <div className="scroll-beam" aria-hidden="true" />
      {noise && <div className="noise-layer" aria-hidden="true" />}
    </>
  );
}

/* ── Lagging moon-mist glow — high-tier desktops only ── */

function CursorGlow() {
  const reduce = useReducedMotion();
  const [enabled, setEnabled] = useState(false);
  const left = useMotionValue(-800);
  const top = useMotionValue(-800);
  const sLeft = useSpring(left, { stiffness: 55, damping: 20, mass: 0.55 });
  const sTop = useSpring(top, { stiffness: 55, damping: 20, mass: 0.55 });

  useEffect(() => {
    setEnabled(
      !reduce &&
        window.matchMedia("(pointer: fine)").matches &&
        window.innerWidth >= 1280 &&
        getQualityTier() === "high"
    );
  }, [reduce]);

  useEffect(() => {
    if (!enabled) return;
    let raf = 0;
    let x = -800;
    let y = -800;
    const move = (e: MouseEvent) => {
      x = e.clientX;
      y = e.clientY;
      if (!raf) {
        raf = requestAnimationFrame(() => {
          raf = 0;
          left.set(x);
          top.set(y);
        });
      }
    };
    window.addEventListener("mousemove", move, { passive: true });
    return () => {
      window.removeEventListener("mousemove", move);
      cancelAnimationFrame(raf);
    };
  }, [enabled, left, top]);

  if (!enabled) return null;

  return (
    <motion.div
      aria-hidden="true"
      className="pointer-events-none fixed z-[1] -ml-[280px] -mt-[280px] h-[560px] w-[560px] rounded-full"
      style={{
        left: sLeft,
        top: sTop,
        background:
          "radial-gradient(circle, rgba(216,236,248,0.06) 0%, rgba(186,215,247,0.022) 42%, transparent 68%)",
      }}
    />
  );
}
