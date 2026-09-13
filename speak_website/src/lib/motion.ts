import { gsap } from "gsap";
import { ScrollTrigger } from "gsap/ScrollTrigger";

let registered = false;

export function ensureScrollPlugins() {
  if (!registered) {
    gsap.registerPlugin(ScrollTrigger);
    registered = true;
  }
  return { gsap, ScrollTrigger };
}

export const MOTION_TOKENS = {
  enterEase: "power4.out",
  entryEase: [0.22, 1, 0.36, 1] as const,
  textDuration: 0.95,
  cardDuration: 1.0,
  wordStagger: 0.05,
  cardStagger: 0.08,
  revealY: 36,
  blurFrom: "blur(8px)",
  blurTo: "blur(0px)",
} as const;

export function isMotionSafe(): boolean {
  if (typeof window === "undefined") return false;
  const reduce = window.matchMedia("(prefers-reduced-motion: reduce)").matches;
  const coarse = window.matchMedia("(pointer: coarse)").matches;
  const narrow = window.innerWidth < 768;
  return !reduce && !coarse && !narrow;
}

export function isWebGPUSupported(): boolean {
  return typeof navigator !== "undefined" && "gpu" in navigator;
}

export async function tryInitWebGPU(): Promise<unknown> {
  try {
    if (!isWebGPUSupported()) return null;
    // eslint-disable-next-line @typescript-eslint/no-explicit-any
    const gpu = (navigator as any).gpu;
    const adapter = await gpu.requestAdapter({ powerPreference: "high-performance" });
    return adapter ?? null;
  } catch {
    return null;
  }
}

export function refreshScrollTriggers(delay = 120) {
  ensureScrollPlugins();
  window.setTimeout(() => ScrollTrigger.refresh(), delay);
  window.addEventListener("load", () => ScrollTrigger.refresh(), { once: true });
}
