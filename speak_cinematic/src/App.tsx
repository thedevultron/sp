import { useCallback, useEffect, useRef, useState } from 'react';
import Lenis from 'lenis';
import { gsap } from 'gsap';
import { ScrollTrigger } from 'gsap/ScrollTrigger';
import { AnimatePresence, useReducedMotion } from 'motion/react';
import TopNav from './components/ui/TopNav';
import Preloader from './components/cinematic/Preloader';
import TourOverlay from './components/cinematic/TourOverlay';
import HeroSection from './components/sections/HeroSection';
import PipelineSection from './components/sections/PipelineSection';
import FeaturesSection from './components/sections/FeaturesSection';
import WhySection from './components/sections/WhySection';
import PrivacySection from './components/sections/PrivacySection';
import FinaleSection from './components/sections/FinaleSection';
import { useCinematicScroll, useSpotlight } from './lib/motion';
import { CHAPTERS } from './site';
import './styles/globals.css';

gsap.registerPlugin(ScrollTrigger);

export default function App() {
  const [loading, setLoading] = useState(true);
  const [touring, setTouring] = useState(false);
  const [chapter, setChapter] = useState(0);
  const lenisRef = useRef<Lenis | null>(null);
  const heroScroll = useRef(0);
  const progressRef = useRef<HTMLDivElement | null>(null);
  const tourTimer = useRef<number | null>(null);
  const reduced = useReducedMotion();
  const spotRef = useSpotlight();
  const ready = !loading;

  useCinematicScroll(ready && !reduced, heroScroll);

  // Lenis smooth scroll
  useEffect(() => {
    if (reduced) { setLoading(false); return; }
    const lenis = new Lenis({ duration: 1.2, smoothWheel: true });
    lenisRef.current = lenis;
    lenis.on('scroll', ScrollTrigger.update);
    const tick = (t: number) => lenis.raf(t * 1000);
    gsap.ticker.add(tick);
    gsap.ticker.lagSmoothing(0);
    return () => { gsap.ticker.remove(tick); lenis.destroy(); lenisRef.current = null; };
  }, [reduced]);

  // scroll progress + freeze behind loader
  useEffect(() => {
    const onScroll = () => {
      const max = document.documentElement.scrollHeight - window.innerHeight;
      const p = max > 0 ? window.scrollY / max : 0;
      if (progressRef.current) progressRef.current.style.transform = `scaleX(${p})`;
    };
    window.addEventListener('scroll', onScroll, { passive: true });
    return () => window.removeEventListener('scroll', onScroll);
  }, []);

  useEffect(() => {
    if (loading) lenisRef.current?.stop();
    else lenisRef.current?.start();
  }, [loading]);

  useEffect(() => {
    document.body.classList.toggle('touring', touring);
  }, [touring]);

  // magnetic buttons
  useEffect(() => {
    if (reduced || !ready) return;
    const els = Array.from(document.querySelectorAll('.magnetic')) as HTMLElement[];
    const clean: (() => void)[] = [];
    els.forEach((el) => {
      const move = (e: MouseEvent) => {
        const r = el.getBoundingClientRect();
        const x = e.clientX - (r.left + r.width / 2);
        const y = e.clientY - (r.top + r.height / 2);
        el.style.transform = `translate(${x * 0.12}px, ${y * 0.18}px)`;
      };
      const leave = () => { el.style.transform = ''; };
      el.addEventListener('mousemove', move);
      el.addEventListener('mouseleave', leave);
      clean.push(() => { el.removeEventListener('mousemove', move); el.removeEventListener('mouseleave', leave); });
    });
    return () => clean.forEach((f) => f());
  }, [ready, reduced]);

  const stopTour = useCallback(() => {
    setTouring(false);
    if (tourTimer.current) window.clearTimeout(tourTimer.current);
    lenisRef.current?.start();
  }, []);

  const jumpTo = useCallback((i: number) => {
    const id = CHAPTERS[i].id;
    setChapter(i);
    const el = document.getElementById(id);
    if (!el) return;
    if (lenisRef.current) lenisRef.current.scrollTo(el as HTMLElement, { offset: -70, duration: 2.2 });
    else el.scrollIntoView({ behavior: 'smooth' });
  }, []);

  const startTour = useCallback(() => {
    if (touring) { stopTour(); return; }
    setTouring(true);
    setChapter(0);
    lenisRef.current?.stop();
    let i = 0;
    const step = () => {
      const id = CHAPTERS[i].id;
      setChapter(i);
      document.getElementById(id)?.scrollIntoView({ behavior: 'smooth' });
      i += 1;
      if (i >= CHAPTERS.length) {
        tourTimer.current = window.setTimeout(() => stopTour(), 5200);
      } else {
        tourTimer.current = window.setTimeout(step, 4200);
      }
    };
    window.setTimeout(step, 400);
  }, [touring, stopTour]);

  // any manual scroll/wheel stops tour
  useEffect(() => {
    if (!touring) return;
    const stop = () => stopTour();
    window.addEventListener('wheel', stop, { passive: true });
    window.addEventListener('touchmove', stop, { passive: true });
    return () => { window.removeEventListener('wheel', stop); window.removeEventListener('touchmove', stop); };
  }, [touring, stopTour]);

  return (
    <div ref={spotRef as React.RefObject<HTMLDivElement>} style={{ position: 'relative', minHeight: '100vh', background: '#05060f', color: '#eef4ff', overflowX: 'clip' }}>
      <AnimatePresence>{loading && !reduced && <Preloader key="loader" onDone={() => setLoading(false)} />}</AnimatePresence>
      <div className="scroll-progress" aria-hidden="true"><i ref={progressRef} /></div>
      <div className="letterbox-top" /><div className="letterbox-bottom" />
      <div className="blueprint-grid" aria-hidden="true" />
      <div className="vignette" aria-hidden="true" />
      <div className="noise-layer" aria-hidden="true" />
      <TopNav onTour={startTour} touring={touring} />
      <main style={{ position: 'relative', zIndex: 1 }}>
        <HeroSection heroScroll={heroScroll} onTour={startTour} />
        <div style={{ height: 1, background: 'linear-gradient(90deg,transparent,rgba(182,217,252,.18),transparent)' }} />
        <PipelineSection />
        <FeaturesSection />
        <WhySection />
        <PrivacySection />
        <FinaleSection />
      </main>
      {touring && <TourOverlay index={chapter} onStop={stopTour} onJump={jumpTo} />}
    </div>
  );
}
