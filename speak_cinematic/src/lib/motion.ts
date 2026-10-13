import { useEffect, useRef } from 'react';
import { gsap } from 'gsap';
import { ScrollTrigger } from 'gsap/ScrollTrigger';

gsap.registerPlugin(ScrollTrigger);

export function useCinematicScroll(enabled: boolean, heroScroll: React.RefObject<number>) {
  useEffect(() => {
    if (!enabled) return;
    const ctx = gsap.context(() => {
      // hero camera push
      gsap.to('.hero-copy', {
        y: -90, opacity: 0, scale: 0.97, ease: 'none',
        scrollTrigger: { trigger: '.hero', start: 'top top', end: 'bottom 35%', scrub: 0.7 },
      });
      gsap.to('.hero-capsule', {
        y: -140, scale: 0.94, rotateX: 6, ease: 'none',
        scrollTrigger: { trigger: '.hero', start: 'top top', end: 'bottom top', scrub: 0.9 },
      });
      const st = ScrollTrigger.create({
        trigger: document.body, start: 'top top', end: 'max', scrub: 0.6,
        onUpdate: (self) => { if (heroScroll.current !== undefined) heroScroll.current = self.progress; },
      });
      // chapters drift in
      gsap.utils.toArray<HTMLElement>('.chapter').forEach((sec) => {
        gsap.fromTo(sec, { y: 60 }, {
          y: 0, ease: 'none',
          scrollTrigger: { trigger: sec, start: 'top bottom', end: 'top 30%', scrub: 0.8 },
        });
        const head = sec.querySelector('.chapter-head');
        if (head) {
          gsap.fromTo(head, { y: 50, opacity: 0.2 }, {
            y: 0, opacity: 1, ease: 'none',
            scrollTrigger: { trigger: sec, start: 'top 85%', end: 'top 35%', scrub: 0.7 },
          });
        }
      });
      // mask reveals
      gsap.utils.toArray<HTMLElement>('.mask-line > span').forEach((el) => {
        gsap.fromTo(el, { yPercent: 110 }, {
          yPercent: 0, duration: 1.1, ease: 'expo.out',
          scrollTrigger: { trigger: el, start: 'top 88%', once: true },
        });
      });
      // cards cascade
      gsap.utils.toArray<HTMLElement>('.rise').forEach((el, i) => {
        gsap.fromTo(el, { y: 44, opacity: 0 }, {
          y: 0, opacity: 1, duration: 0.9, ease: 'expo.out', delay: (i % 3) * 0.08,
          scrollTrigger: { trigger: el, start: 'top 90%', once: true },
        });
      });
      // finale breathes open
      gsap.fromTo('.finale-card', { y: 60, scale: 0.97 }, {
        y: 0, scale: 1, ease: 'none',
        scrollTrigger: { trigger: '.finale', start: 'top bottom', end: 'top 25%', scrub: 0.8 },
      });
      return () => { st.kill(); };
    });
    const t = window.setTimeout(() => ScrollTrigger.refresh(), 200);
    return () => { window.clearTimeout(t); ctx.revert(); };
  }, [enabled, heroScroll]);
}

export function useSpotlight() {
  const ref = useRef<HTMLDivElement | null>(null);
  useEffect(() => {
    const root = ref.current;
    if (!root) return;
    const move = (e: MouseEvent) => {
      const cards = (e.target as HTMLElement).closest?.('.feature-card') as HTMLElement | null;
      root.querySelectorAll('.feature-card').forEach((c) => {
        const card = c as HTMLElement;
        const spot = card.querySelector('.spotlight') as HTMLElement | null;
        if (!spot) return;
        if (card === cards) {
          const r = card.getBoundingClientRect();
          spot.style.left = `${e.clientX - r.left}px`;
          spot.style.top = `${e.clientY - r.top}px`;
        }
      });
    };
    window.addEventListener('mousemove', move, { passive: true });
    return () => window.removeEventListener('mousemove', move);
  }, []);
  return ref;
}
