import { useCallback, useEffect, useRef, useState } from 'react';
import Lenis from 'lenis';
import { gsap } from 'gsap';
import { ScrollTrigger } from 'gsap/ScrollTrigger';
import { AnimatePresence, motion, useReducedMotion } from 'motion/react';
import { ArrowUpRight, Menu, X } from 'lucide-react';
import { WaveLogo } from './components/ui/Primitives';
import CinematicLoader from './components/ui/CinematicLoader';
import ProductModal from './components/ui/ProductModal';
import DocsPage from './components/docs/DocsPage';
import { AboutSection, HeroSection, PipelineSection, SimulatorSection, BentoPillarsSection, HotkeysSecuritySection, ExpandShowcaseSection, DownloadFooterSection } from './components/sections/ProductSections';
import { DOCS_HASH, SITE_VERSION, GITHUB_REPO_URL } from './site';
import SectionTransition from './components/SectionTransition';
import ChatDock from './components/chat/ChatDock';
import './styles/authkit-tokens.css';
import './styles/globals.css';

gsap.registerPlugin(ScrollTrigger);

type ModalType = 'settings' | 'guide' | 'download' | 'support' | null;
type Page = 'home' | 'docs';

function getPage(): Page {
  return typeof window !== 'undefined' && window.location.hash.startsWith('#/docs') ? 'docs' : 'home';
}

const EASE = [0.22, 1, 0.36, 1] as const;

export default function App() {
  const [modal, setModal] = useState<ModalType>(null);
  const [menu, setMenu] = useState(false);
  const [chatOpen, setChatOpen] = useState(false);
  const [activeSection, setActiveSection] = useState('overview');
  const [scrolled, setScrolled] = useState(false);
  const [demo, setDemo] = useState({ active: false, text: '', progress: 12 });
  const [page, setPage] = useState<Page>(() => getPage());
  const [loading, setLoading] = useState(true);
  const lenisRef = useRef<Lenis | null>(null);
  const progressRef = useRef<HTMLDivElement | null>(null);
  const reduced = useReducedMotion();
  const closeModal = useCallback(() => setModal(null), []);
  const updateDemo = useCallback((s: typeof demo) => setDemo(s), []);
  const finishLoading = useCallback(() => setLoading(false), []);

  const scrollToSection = useCallback((hash: string) => {
    const el = document.querySelector(hash);
    if (!el) return;
    if (lenisRef.current && !reduced) {
      lenisRef.current.scrollTo(el as HTMLElement, { offset: -92, duration: 1.4 });
    } else {
      (el as HTMLElement).scrollIntoView({ behavior: reduced ? 'auto' : 'smooth' });
    }
  }, [reduced]);

  useEffect(() => {
    const onScroll = () => {
      setScrolled(window.scrollY > 40);
      // Blue scroll progress — the one functional accent.
      const max = document.documentElement.scrollHeight - window.innerHeight;
      const p = max > 0 ? Math.min(1, Math.max(0, window.scrollY / max)) : 0;
      if (progressRef.current) progressRef.current.style.transform = `scaleX(${p})`;
    };
    onScroll();
    window.addEventListener('scroll', onScroll, { passive: true });
    if (reduced) {
      setLoading(false);
      return () => window.removeEventListener('scroll', onScroll);
    }
    const lenis = new Lenis({ duration: 1.15, smoothWheel: true });
    lenisRef.current = lenis;
    lenis.on('scroll', ScrollTrigger.update);
    const tick = (time: number) => lenis.raf(time * 1000);
    gsap.ticker.add(tick);
    gsap.ticker.lagSmoothing(0);
    return () => { window.removeEventListener('scroll', onScroll); gsap.ticker.remove(tick); lenis.destroy(); lenisRef.current = null; };
  }, [reduced]);

  // Freeze scroll behind the mic-check loader.
  useEffect(() => {
    if (loading) lenisRef.current?.stop();
    else lenisRef.current?.start();
  }, [loading]);

  // Cinematic scroll choreography — one owner per property, scrub for
  // atmosphere, once for entrances. Transform + opacity + filter only.
  useEffect(() => {
    if (reduced || page !== 'home' || loading) return;
    const ctx = gsap.context(() => {
      // Act I — hero copy drifts + fades; the capsule is never blurred.
      gsap.to('.hero-copy', {
        y: -48, opacity: 0,
        ease: 'none',
        scrollTrigger: { trigger: '.hero', start: 'top top', end: 'bottom 30%', scrub: 0.6 },
      });
      gsap.to('.hero-product-cine', {
        y: -120, scale: 0.96, ease: 'none',
        scrollTrigger: { trigger: '.hero', start: 'top top', end: 'bottom top', scrub: 0.8 },
      });
      gsap.to('.scroll-cue', {
        opacity: 0, y: -16, ease: 'none',
        scrollTrigger: { trigger: '.hero', start: 'top top', end: '30% top', scrub: 0.5 },
      });
      // Act II — each section's headline settles with a slow drift.
      gsap.utils.toArray<HTMLElement>('.section').forEach((sec) => {
        gsap.fromTo(sec, { y: 28 }, {
          y: 0, ease: 'none',
          scrollTrigger: { trigger: sec, start: 'top bottom', end: 'top 35%', scrub: 0.7 },
        });
      });
      // Act III — cards cascade once, staggered on a shared clock.
      gsap.utils.toArray<HTMLElement>('.vox-bento-cell').forEach((el, i) => {
        gsap.fromTo(el, { y: 36, opacity: 0 }, {
          y: 0, opacity: 1, duration: 0.9, ease: 'expo.out', delay: (i % 3) * 0.06,
          scrollTrigger: { trigger: el, start: 'top 88%', once: true },
        });
      });
      gsap.utils.toArray<HTMLElement>('.pipeline-step, .hotkey-row, .guide-steps > div').forEach((el, i) => {
        gsap.fromTo(el, { y: 28, opacity: 0 }, {
          y: 0, opacity: 1, duration: 0.8, ease: 'expo.out', delay: (i % 3) * 0.07,
          scrollTrigger: { trigger: el, start: 'top 90%', once: true },
        });
      });
      // Finale — the closing CTA breathes open as you arrive.
      gsap.fromTo('.expand-cta', { scale: 0.96, opacity: 0.6 }, {
        scale: 1, opacity: 1, ease: 'none',
        scrollTrigger: { trigger: '.expand-section', start: 'top bottom', end: 'center center', scrub: 0.7 },
      });
      gsap.fromTo('.download-card', { y: 40, scale: 0.98 }, {
        y: 0, scale: 1, ease: 'none',
        scrollTrigger: { trigger: '.download-section', start: 'top bottom', end: 'top 30%', scrub: 0.7 },
      });
    });
    const t = window.setTimeout(() => ScrollTrigger.refresh(), 160);
    return () => { window.clearTimeout(t); ctx.revert(); };
  }, [page, reduced, loading]);

  useEffect(() => {
    if (modal || chatOpen) lenisRef.current?.stop();
    else if (!loading) lenisRef.current?.start();
  }, [modal, chatOpen, loading]);

  useEffect(() => {
    ScrollTrigger.refresh();
    if (lenisRef.current && !reduced) lenisRef.current.scrollTo(0, { immediate: true });
    else window.scrollTo({ top: 0, behavior: 'auto' });
  }, [page, reduced]);

  useEffect(() => {
    const onHash = () => {
      const next = getPage();
      setPage(next);
      setMenu(false);
      const hash = window.location.hash;
      const anchor = next === 'docs' && hash.includes('#docs-') ? hash.slice(hash.lastIndexOf('#') + 1) : null;
      window.setTimeout(() => {
        if (anchor) {
          const el = document.getElementById(anchor);
          if (!el) return;
          if (lenisRef.current && !reduced) lenisRef.current.scrollTo(el as HTMLElement, { offset: -92, duration: 1.2 });
          else el.scrollIntoView({ behavior: reduced ? 'auto' : 'smooth' });
        }
        else if (next === 'docs') window.scrollTo({ top: 0 });
      }, 60);
    };
    window.addEventListener('hashchange', onHash);
    return () => window.removeEventListener('hashchange', onHash);
  }, [reduced]);

  useEffect(() => {
    if (page !== 'home') return;
    const observer = new IntersectionObserver(entries => { entries.forEach(e => { if (e.isIntersecting) setActiveSection(e.target.id); }); }, { rootMargin: '-10% 0px -65% 0px' });
    document.querySelectorAll('section[id]').forEach(s => observer.observe(s));
    return () => observer.disconnect();
  }, [page]);

  const goSection = useCallback((e: React.MouseEvent, href: string) => {
    e.preventDefault();
    setMenu(false);
    if (page !== 'home') {
      window.location.hash = href;
      window.setTimeout(() => scrollToSection(href), 140);
      return;
    }
    try { window.history.replaceState(null, '', href); } catch { /* noop */ }
    scrollToSection(href);
  }, [page, scrollToSection]);

  const links = [['Overview', '#overview', 'overview'], ['How it works', '#how-it-works', 'how-it-works'], ['Features', '#features', 'features'], ['Privacy', '#privacy', 'privacy'], ['Docs', DOCS_HASH, 'docs']];
  return (
    <>
      <AnimatePresence>{loading && !reduced && <CinematicLoader key="loader" onDone={finishLoading} />}</AnimatePresence>
      <div className="scroll-progress" aria-hidden="true"><i ref={progressRef} /></div>
      <header className={scrolled ? 'site-header is-scrolled' : 'site-header'}>
        <div className="nav-inner">
          <a href="#overview" className="brand" onClick={(e) => goSection(e, '#overview')}><WaveLogo small /><span>Voxula AI</span><span className="nav-version">{SITE_VERSION}</span></a>
          <nav className={menu ? 'main-nav open' : 'main-nav'} aria-label="Main navigation">
            {links.map(([label, href, id]) => {
              const active = id === 'docs' ? page === 'docs' : page === 'home' && activeSection === id;
              return (
                <a
                  key={id}
                  href={href}
                  className={active ? 'active' : ''}
                  aria-current={active ? 'page' : undefined}
                  onClick={(e) => { if (id === 'docs') { setMenu(false); return; } goSection(e, href); }}
                >
                  {active && (reduced
                    ? <span className="nav-pill" aria-hidden="true" />
                    : <motion.span layoutId="nav-pill" className="nav-pill" transition={{ type: 'spring', stiffness: 420, damping: 36 }} aria-hidden="true" />
                  )}
                  <span className="nav-label">{label}</span>
                </a>
              );
            })}
            <a
              href={GITHUB_REPO_URL}
              target="_blank"
              rel="noreferrer"
              className="nav-github-navlink"
              onClick={() => setMenu(false)}
            >
              <span className="nav-label" style={{ display: 'inline-flex', alignItems: 'center', gap: '4px' }}>
                GitHub <ArrowUpRight size={11} />
              </span>
            </a>
          </nav>
          <div className="nav-actions">
            <span className="free-status"><span className="status-dot" />Free. Forever.</span>
            <a
              href={GITHUB_REPO_URL}
              target="_blank"
              rel="noreferrer"
              className="nav-github-link"
              aria-label="GitHub Repository"
              title={`GitHub: ${GITHUB_REPO_URL.replace('https://github.com/', '')}`}
            >
              <svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><path d="M15 22v-4a4.8 4.8 0 0 0-1-3.5c3 0 6-2 6-5.5.08-1.25-.27-2.48-1-3.5.28-1.15.28-2.35 0-3.5 0 0-1 0-3 1.5-2.64-.5-5.36-.5-8 0C6 2 5 2 5 2c-.3 1.15-.3 2.35 0 3.5A5.403 5.403 0 0 0 4 9c0 3.5 3 5.5 6 5.5-.39.49-.68 1.05-.85 1.65-.17.6-.22 1.23-.15 1.85v4" /><path d="M9 18c-4.51 2-5-2-7-2" /></svg>
              <span>GitHub</span>
            </a>
            <button className="nav-download" onClick={() => setModal('download')}><span className="nav-download-full">Get Voxula AI</span><span className="nav-download-short">Get</span><ArrowUpRight size={14} /></button>
            <button className={`menu-toggle${menu ? ' is-open' : ''}`} aria-label={menu ? 'Close menu' : 'Open menu'} aria-expanded={menu} onClick={() => setMenu(!menu)}>{menu ? <X size={21} /> : <Menu size={21} />}</button>
          </div>
        </div>
      </header>
      <main>
        <AnimatePresence mode="wait">
          <motion.div
            key={page}
            initial={reduced ? { opacity: 0 } : { opacity: 0, y: 16, filter: 'blur(6px)' }}
            animate={reduced ? { opacity: 1 } : { opacity: 1, y: 0, filter: 'blur(0px)' }}
            exit={reduced ? { opacity: 0 } : { opacity: 0, y: -12, filter: 'blur(6px)' }}
            transition={{ duration: reduced ? 0.18 : 0.38, ease: [...EASE] }}
          >
            {page === 'docs' ? (
              <><DocsPage onDownload={() => setModal('download')} /><div className="page-content"><SectionTransition><DownloadFooterSection onModal={setModal} onChat={() => setChatOpen(true)} /></SectionTransition></div></>
            ) : (
              <>
                <SectionTransition beam={false}><HeroSection demo={demo} onModal={setModal} /></SectionTransition>
                <div className="page-content">
                  <SectionTransition><PipelineSection /></SectionTransition>
                  <SectionTransition><SimulatorSection onUpdate={updateDemo} /></SectionTransition>
                  <SectionTransition><BentoPillarsSection /></SectionTransition>
                  <SectionTransition><AboutSection /></SectionTransition>
                  <SectionTransition><HotkeysSecuritySection /></SectionTransition>
                  <SectionTransition><ExpandShowcaseSection onModal={setModal} /></SectionTransition>
                  <SectionTransition><DownloadFooterSection onModal={setModal} onChat={() => setChatOpen(true)} /></SectionTransition>
                </div>
              </>
            )}
          </motion.div>
        </AnimatePresence>
      </main>
      <ProductModal type={modal} onClose={closeModal} />
      {chatOpen && <ChatDock onClose={() => setChatOpen(false)} />}
    </>
  );
}
