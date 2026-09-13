import { useEffect, useRef, useState } from "react";
import WebGPURays from "./WebGPURays";
import { getQualityTier, qualityFlags } from "../../lib/perf";
import { cn } from "../../utils/cn";

interface AdaptiveRaysProps {
  className?: string;
  raysColor?: string;
  raysSpeed?: number;
  /** Strength of the beam. Maps to the WebGPU intensity uniform. */
  intensity?: number;
  opacity?: number;
  /** Set false to force the zero-GPU CSS fallback (keeps total GPU contexts at one). */
  webgpu?: boolean;
}

/**
 * WebGPU light rays on capable machines, static CSS glow fallback otherwise.
 * Hero owns the single GPU context; secondary placements use pure CSS.
 * Pauses rendering offscreen + on hidden tabs to keep GPUs cool.
 */
export function AdaptiveRays({
  className,
  raysColor = "#b6d9fc",
  raysSpeed = 0.55,
  intensity = 0.9,
  opacity = 0.85,
  webgpu = true,
}: AdaptiveRaysProps) {
  const wrapRef = useRef<HTMLDivElement>(null);
  const [visible, setVisible] = useState(true);
  const [tier] = useState(() => getQualityTier());
  const flags = qualityFlags(tier);

  useEffect(() => {
    const el = wrapRef.current;
    if (!el || typeof IntersectionObserver === "undefined") return;
    const io = new IntersectionObserver(([e]) => setVisible(e.isIntersecting), {
      threshold: 0,
      rootMargin: "240px",
    });
    io.observe(el);
    const onVis = () => setVisible(!document.hidden);
    document.addEventListener("visibilitychange", onVis);
    return () => {
      io.disconnect();
      document.removeEventListener("visibilitychange", onVis);
    };
  }, []);

  const showGPU = webgpu && flags.rays && visible;

  return (
    <div
      ref={wrapRef}
      className={cn("adaptive-rays", className)}
      aria-hidden="true"
      style={{ opacity }}
    >
      {showGPU ? (
        <WebGPURays color={raysColor} speed={raysSpeed} intensity={intensity} opacity={1} />
      ) : (
        <div className="adaptive-rays-fallback" />
      )}
    </div>
  );
}
