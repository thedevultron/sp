import { useEffect, useRef, useState } from "react";

export type QualityTier = "high" | "medium" | "low";

let cached: QualityTier | null = null;

export function getQualityTier(): QualityTier {
  if (cached) return cached;
  if (typeof window === "undefined") return "high";
  try {
    const reduce = window.matchMedia("(prefers-reduced-motion: reduce)").matches;
    const coarse = window.matchMedia("(pointer: coarse)").matches;
    const narrow = window.innerWidth < 768;
    if (reduce) {
      cached = "low";
      return cached;
    }
    // eslint-disable-next-line @typescript-eslint/no-explicit-any
    const nav = navigator as any;
    const mem = typeof nav?.deviceMemory === "number" ? nav.deviceMemory : 8;
    const cores = typeof nav?.hardwareConcurrency === "number" ? nav.hardwareConcurrency : 8;
    const dpr = Math.min(window.devicePixelRatio || 1, 3);

    if (coarse || narrow) {
      cached = mem <= 4 || cores <= 4 ? "low" : "medium";
      return cached;
    }
    if (mem <= 4 || cores <= 4 || dpr >= 2.5) {
      cached = "medium";
      return cached;
    }
    cached = "high";
    return cached;
  } catch {
    cached = "medium";
    return cached;
  }
}

export function qualityFlags(tier: QualityTier) {
  return {
    rays: tier !== "low",
    raysFollowMouse: tier === "high",
    tilt: tier === "high",
    spotlight: tier !== "low",
    cursorGlow: tier === "high",
    noise: tier === "high",
    sparks: tier !== "low",
    magnet: tier !== "low",
    marqueeVelocity: tier !== "low",
    dprCap: tier === "high" ? 1.5 : tier === "medium" ? 1.25 : 1,
  } as const;
}

export function useQualityTier(): QualityTier {
  const [tier, setTier] = useState<QualityTier>(() => getQualityTier());
  useEffect(() => {
    const onResize = () => {
      cached = null;
      setTier(getQualityTier());
    };
    window.addEventListener("resize", onResize);
    return () => window.removeEventListener("resize", onResize);
  }, []);
  return tier;
}

/** Pause expensive work when tab hidden or section offscreen. */
export function useInViewport<T extends HTMLElement>(threshold = 0.05) {
  const [inView, setInView] = useState(true);
  const innerRef = useRef<T | null>(null);
  const setRef = (el: T | null) => {
    innerRef.current = el;
  };
  useEffect(() => {
    const el = innerRef.current;
    if (!el || typeof IntersectionObserver === "undefined") return;
    const io = new IntersectionObserver(
      ([entry]) => {
        if (document.hidden) {
          setInView(false);
          return;
        }
        setInView(entry.isIntersecting);
      },
      { threshold }
    );
    io.observe(el);
    const onVis = () => {
      if (document.hidden) setInView(false);
      else if (innerRef.current) {
        const r = innerRef.current.getBoundingClientRect();
        setInView(r.bottom > 0 && r.top < window.innerHeight);
      }
    };
    document.addEventListener("visibilitychange", onVis);
    return () => {
      io.disconnect();
      document.removeEventListener("visibilitychange", onVis);
    };
  }, [threshold]);
  return { ref: setRef, inView };
}

export function isFinePointer(): boolean {
  if (typeof window === "undefined") return false;
  return window.matchMedia("(pointer: fine)").matches && window.innerWidth >= 1024;
}
