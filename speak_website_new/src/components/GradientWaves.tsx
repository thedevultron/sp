import React, { useEffect, useRef, useState } from 'react';
import {
  createFullscreenScene,
  cssSize,
  getWebGPUDevice,
  hexToRgb,
  type FullscreenScene,
} from './gpu/webgpu';

export type GradientWavesDetail = 'low' | 'medium' | 'high';

export interface GradientWavesProps {
  horizonColor?: string;
  waveColor?: string;
  crestColor?: string;
  speed?: number;
  amplitude?: number;
  waveScale?: number;
  waveRatio?: number;
  swell?: number;
  turbulence?: number;
  tilt?: number;
  zoom?: number;
  height?: number;
  fogDepth?: number;
  detail?: GradientWavesDetail;
  brightness?: number;
  opacity?: number;
  mouseInteraction?: boolean;
  parallaxStrength?: number;
  grain?: boolean;
  grainIntensity?: number;
  className?: string;
}

const detailToSteps = (detail: GradientWavesDetail): number => {
  if (detail === 'low') return 40.0;
  if (detail === 'high') return 110.0;
  return 70.0;
};

/* Uniform words: [iRes.xy, iTime, speed, amp, scale, ratio, swell, turb, tilt,
   zoom, height, fog, steps, bright, opacity, grain, grainI, mouse.xy, parallax,
   mouseOn, pad, pad, horizon.rgb, pad, wave.rgb, pad, crest.rgb, pad] = 36 */
const FRAG_WGSL = /* wgsl */ `
struct U {
  iResolution: vec2f,
  iTime: f32, uSpeed: f32, uAmplitude: f32, uWaveScale: f32,
  uWaveRatio: f32, uSwell: f32, uTurbulence: f32, uTilt: f32, uZoom: f32,
  uHeight: f32, uFogDepth: f32, uSteps: f32, uBrightness: f32, uOpacity: f32,
  uGrain: f32, uGrainIntensity: f32, uMouse: vec2f, uParallax: f32, uEnableMouse: f32,
  _pad0: vec2f,
  uHorizonColor: vec3f, _pad1: f32,
  uWaveColor: vec3f, _pad2: f32,
  uCrestColor: vec3f, _pad3: f32,
};
@group(0) @binding(0) var<uniform> u: U;

const MAX_DIST: f32 = 20000.0;

fn hash21(p: vec2f) -> f32 {
  var p3 = fract(vec3f(p.xyx) * 0.1031);
  p3 += dot(p3, p3.yzx + vec3f(33.33));
  return fract((p3.x + p3.y) * p3.z);
}

fn plasma(r: vec3f, freq: vec2f, tc: vec4f) -> f32 {
  var mx = r.x + tc.x;
  mx += u.uSwell * sin((r.y + mx) / 20.0 + tc.y);
  var my = r.y - tc.z;
  my += u.uTurbulence * cos(r.x / 23.0 + tc.w);
  return r.z - (sin(mx * freq.x) * u.uAmplitude + sin(my * freq.y) * u.uAmplitude + u.uHeight);
}

fn raymarch(pos: vec3f, dir: vec3f, freq: vec2f, tc: vec4f) -> f32 {
  var dist = 0.0;
  for (var i = 0; i < 128; i++) {
    if (f32(i) >= u.uSteps) { break; }
    let dscene = plasma(pos + dist * dir, freq, tc);
    if (abs(dscene) < 0.1) { break; }
    dist += 0.9 * dscene;
    if (!(abs(dist) < MAX_DIST)) { return MAX_DIST; }
  }
  return dist;
}

@fragment fn fs(@builtin(position) pos: vec4f) -> @location(0) vec4f {
  let frag = vec2f(pos.x, u.iResolution.y - pos.y);
  let T = u.iTime * u.uSpeed;
  let freq = vec2f(u.uWaveScale / 7.0, (u.uWaveScale * u.uWaveRatio) / 3.0);
  let tc = vec4f(T / 0.130, T / 0.810, T / 0.200, T / 0.710);
  var c: f32; var s: f32;
  let vfov = (3.14159 / 2.3) / max(u.uZoom, 0.05);
  let cam = vec3f(0.0, 0.0, 30.0);
  var uv = (frag / u.iResolution) - vec2f(0.5);
  uv.x *= u.iResolution.x / u.iResolution.y;
  uv.y *= -1.0;

  var dir = vec3f(0.0, 0.0, -1.0);
  let ulen = length(uv);
  let xrot = vfov * ulen;
  c = cos(xrot); s = sin(xrot);
  dir = mat3x3f(1.0, 0.0, 0.0, 0.0, c, -s, 0.0, s, c) * dir;
  let nuv = select(vec2f(1.0, 0.0), uv / ulen, ulen > 1e-5);
  c = nuv.x; s = nuv.y;
  dir = mat3x3f(c, -s, 0.0, s, c, 0.0, 0.0, 0.0, 1.0) * dir;
  c = cos(u.uTilt); s = sin(u.uTilt);
  dir = mat3x3f(c, 0.0, s, 0.0, 1.0, 0.0, -s, 0.0, c) * dir;

  if (u.uEnableMouse > 0.5) {
    let yaw = (u.uMouse.x - 0.5) * u.uParallax * 0.4;
    let pitch = (u.uMouse.y - 0.5) * u.uParallax * 0.4;
    c = cos(yaw); s = sin(yaw);
    dir = mat3x3f(c, 0.0, s, 0.0, 1.0, 0.0, -s, 0.0, c) * dir;
    c = cos(pitch); s = sin(pitch);
    dir = mat3x3f(1.0, 0.0, 0.0, 0.0, c, -s, 0.0, s, c) * dir;
  }

  let dist = raymarch(cam, dir, freq, tc);
  let p = cam + dist * dir;

  let t = clamp(u.uFogDepth / max(dist, 0.001), 0.0, 1.0);
  let body = mix(u.uWaveColor, u.uCrestColor, clamp(p.z * 0.08 + 0.5, 0.0, 1.0));
  var col = mix(u.uHorizonColor, body, t);
  col *= u.uBrightness;
  col = clamp(col, vec3f(0.0), vec3f(1.0));

  var alpha = clamp(t, 0.0, 1.0) * u.uOpacity;
  if (u.uGrain > 0.5) {
    let cyc = u.iTime - floor(u.iTime / 64.0) * 64.0;
    let g = hash21(frag + cyc * 11.0);
    alpha += (g - 0.5) * u.uGrainIntensity;
  }
  alpha = clamp(alpha, 0.0, 1.0);
  return vec4f(col * alpha, alpha);
}
`;

type Ctx = { scene: FullscreenScene; canvas: HTMLCanvasElement };
const ctxMap = new WeakMap<HTMLDivElement, Ctx>();

type WaveProps = {
  horizonColor: string; waveColor: string; crestColor: string; speed: number;
  amplitude: number; waveScale: number; waveRatio: number; swell: number;
  turbulence: number; tilt: number; zoom: number; height: number; fogDepth: number;
  detail: GradientWavesDetail; brightness: number; opacity: number;
  mouseInteraction: boolean; parallaxStrength: number; grain: boolean; grainIntensity: number;
};

function applyWaveProps(v: Float32Array, p: WaveProps) {
  v[3] = p.speed;
  v[4] = p.amplitude;
  v[5] = p.waveScale;
  v[6] = p.waveRatio;
  v[7] = p.swell;
  v[8] = p.turbulence;
  v[9] = p.tilt;
  v[10] = p.zoom;
  v[11] = p.height;
  v[12] = p.fogDepth;
  v[13] = detailToSteps(p.detail);
  v[14] = p.brightness;
  v[15] = p.opacity;
  v[16] = p.grain ? 1.0 : 0.0;
  v[17] = p.grainIntensity;
  v[20] = p.parallaxStrength;
  v[21] = p.mouseInteraction ? 1.0 : 0.0;
  const h = hexToRgb(p.horizonColor);
  const w = hexToRgb(p.waveColor);
  const cr = hexToRgb(p.crestColor);
  v[24] = h[0]; v[25] = h[1]; v[26] = h[2];
  v[28] = w[0]; v[29] = w[1]; v[30] = w[2];
  v[32] = cr[0]; v[33] = cr[1]; v[34] = cr[2];
}

const GradientWaves: React.FC<GradientWavesProps> = ({
  horizonColor = '#5227FF',
  waveColor = '#FF9FFC',
  crestColor = '#FFFFFF',
  speed = 0.4,
  amplitude = 2.5,
  waveScale = 0.6,
  waveRatio = 0.9,
  swell = 35,
  turbulence = 20,
  tilt = 1.11,
  zoom = 1.0,
  height = 5.5,
  fogDepth = 15,
  detail = 'medium',
  brightness = 1.0,
  opacity = 1.0,
  mouseInteraction = true,
  parallaxStrength = 0.5,
  grain = true,
  grainIntensity = 0.05,
  className = ''
}) => {
  const containerRef = useRef<HTMLDivElement | null>(null);
  const enableMouseRef = useRef<boolean>(mouseInteraction);
  const [unsupported, setUnsupported] = useState(false);
  const propsRef = useRef<WaveProps>({
    horizonColor, waveColor, crestColor, speed, amplitude, waveScale, waveRatio,
    swell, turbulence, tilt, zoom, height, fogDepth, detail, brightness, opacity,
    mouseInteraction, parallaxStrength, grain, grainIntensity,
  });
  propsRef.current = {
    horizonColor, waveColor, crestColor, speed, amplitude, waveScale, waveRatio,
    swell, turbulence, tilt, zoom, height, fogDepth, detail, brightness, opacity,
    mouseInteraction, parallaxStrength, grain, grainIntensity,
  };

  useEffect(() => {
    const container = containerRef.current;
    if (!container) return;
    let cancelled = false;
    let scene: FullscreenScene | null = null;
    let canvas: HTMLCanvasElement | null = null;
    let raf = 0;
    let ro: ResizeObserver | null = null;
    let io: IntersectionObserver | null = null;
    let isVisible = true;
    let isPageVisible = !document.hidden;
    const t0 = performance.now();
    const dpr = Math.min(window.devicePixelRatio || 1, 2);
    const currentMouse: [number, number] = [0.5, 0.5];
    const targetMouse: [number, number] = [0.5, 0.5];

    const setSize = () => {
      if (!scene || !container) return;
      const { w, h } = cssSize(container);
      scene.setSize(w * dpr, h * dpr);
      scene.uniforms[0] = Math.max(1, Math.floor(w * dpr));
      scene.uniforms[1] = Math.max(1, Math.floor(h * dpr));
    };

    const loop = (t: number) => {
      if (!scene) return;
      scene.uniforms[2] = (t - t0) * 0.001;
      const tx = enableMouseRef.current ? targetMouse[0] : 0.5;
      const ty = enableMouseRef.current ? targetMouse[1] : 0.5;
      currentMouse[0] += 0.05 * (tx - currentMouse[0]);
      currentMouse[1] += 0.05 * (ty - currentMouse[1]);
      scene.uniforms[18] = currentMouse[0];
      scene.uniforms[19] = currentMouse[1];
      scene.writeUniforms();
      scene.frame({ r: 0, g: 0, b: 0, a: 0 });
      raf = requestAnimationFrame(loop);
    };

    const tryStart = () => {
      if (isVisible && isPageVisible && raf === 0 && scene) raf = requestAnimationFrame(loop);
    };
    const tryStop = () => {
      if (raf !== 0) {
        cancelAnimationFrame(raf);
        raf = 0;
      }
    };

    const onPointerMove = (e: PointerEvent) => {
      if (!canvas) return;
      const rect = canvas.getBoundingClientRect();
      targetMouse[0] = (e.clientX - rect.left) / rect.width;
      targetMouse[1] = 1.0 - (e.clientY - rect.top) / rect.height;
    };
    const onPointerLeave = () => {
      targetMouse[0] = 0.5;
      targetMouse[1] = 0.5;
    };
    const onVisibility = () => {
      isPageVisible = !document.hidden;
      if (isPageVisible) tryStart();
      else tryStop();
    };

    getWebGPUDevice().then(async (device) => {
      if (cancelled) return;
      if (!device) {
        setUnsupported(true);
        return;
      }
      // GPU lost mid-session: stop the loop and drop to static artwork.
      device.lost.then(() => {
        if (cancelled) return;
        tryStop();
        setUnsupported(true);
      });
      try {
        canvas = document.createElement('canvas');
        canvas.style.width = '100%';
        canvas.style.height = '100%';
        canvas.style.display = 'block';
        container.appendChild(canvas);
        const next = await createFullscreenScene(device, canvas, FRAG_WGSL, 36, 'premultiplied');
        if (!next) {
          setUnsupported(true);
          return;
        }
        scene = next;
        ctxMap.set(container, { scene, canvas });
        enableMouseRef.current = propsRef.current.mouseInteraction;
        applyWaveProps(scene.uniforms, propsRef.current);
        setSize();
        scene.writeUniforms();
        scene.frame({ r: 0, g: 0, b: 0, a: 0 });

        ro = new ResizeObserver(setSize);
        ro.observe(container);
        canvas.addEventListener('pointermove', onPointerMove);
        canvas.addEventListener('pointerleave', onPointerLeave);
        io = new IntersectionObserver(
          ([entry]) => {
            isVisible = entry.isIntersecting;
            if (isVisible) tryStart();
            else tryStop();
          },
          { threshold: 0 }
        );
        io.observe(container);
        document.addEventListener('visibilitychange', onVisibility);
        tryStart();
      } catch {
        setUnsupported(true);
      }
    });

    return () => {
      cancelled = true;
      tryStop();
      ro?.disconnect();
      io?.disconnect();
      document.removeEventListener('visibilitychange', onVisibility);
      if (canvas) {
        canvas.removeEventListener('pointermove', onPointerMove);
        canvas.removeEventListener('pointerleave', onPointerLeave);
      }
      ctxMap.delete(container);
      scene?.destroy();
      try {
        if (canvas && canvas.parentNode === container) container.removeChild(canvas);
      } catch {
        /* ignore */
      }
    };
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  useEffect(() => {
    const container = containerRef.current;
    if (!container) return;
    const ctx = ctxMap.get(container);
    if (!ctx) return;
    enableMouseRef.current = mouseInteraction;
    applyWaveProps(ctx.scene.uniforms, propsRef.current);
  }, [
    horizonColor, waveColor, crestColor, speed, amplitude, waveScale, waveRatio,
    swell, turbulence, tilt, zoom, height, fogDepth, detail, brightness, opacity,
    grain, grainIntensity, mouseInteraction, parallaxStrength
  ]);

  return (
    <div ref={containerRef} className={`relative h-full w-full overflow-hidden ${className}`.trim()}>
      {unsupported && <div className="gradient-fallback" aria-hidden="true" />}
    </div>
  );
};

export default GradientWaves;
