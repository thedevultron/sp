import React, { useEffect, useRef, useState } from 'react';
import {
  createFullscreenScene,
  cssSize,
  getWebGPUDevice,
  hexToRgb,
  type FullscreenScene,
} from './gpu/webgpu';

interface GrainientProps {
  timeSpeed?: number;
  colorBalance?: number;
  warpStrength?: number;
  warpFrequency?: number;
  warpSpeed?: number;
  warpAmplitude?: number;
  blendAngle?: number;
  blendSoftness?: number;
  rotationAmount?: number;
  noiseScale?: number;
  grainAmount?: number;
  grainScale?: number;
  grainAnimated?: boolean;
  contrast?: number;
  gamma?: number;
  saturation?: number;
  centerX?: number;
  centerY?: number;
  zoom?: number;
  color1?: string;
  color2?: string;
  color3?: string;
  lightMode?: boolean;
  className?: string;
}

/* Uniform words: [iRes.xy, iTime, timeSpeed, balance, warpStr, warpFreq,
   warpSpeed, warpAmp, blendAngle, blendSoft, rotAmt, noiseScale, grainAmt,
   grainScale, grainAnim, contrast, gamma, sat, zoom, lightMode, pad,
   center.xy, c1.rgb, pad, c2.rgb, pad, c3.rgb, pad] = 36 */
const FRAG_WGSL = /* wgsl */ `
struct U {
  iResolution: vec2f,
  iTime: f32, uTimeSpeed: f32, uColorBalance: f32, uWarpStrength: f32,
  uWarpFrequency: f32, uWarpSpeed: f32, uWarpAmplitude: f32, uBlendAngle: f32,
  uBlendSoftness: f32, uRotationAmount: f32, uNoiseScale: f32, uGrainAmount: f32,
  uGrainScale: f32, uGrainAnimated: f32, uContrast: f32, uGamma: f32,
  uSaturation: f32, uZoom: f32, uLightMode: f32, _pad0: f32,
  uCenterOffset: vec2f,
  uColor1: vec3f, _pad1: f32,
  uColor2: vec3f, _pad2: f32,
  uColor3: vec3f, _pad3: f32,
};
@group(0) @binding(0) var<uniform> u: U;

// Order-agnostic smoothstep: identical to the classic formula on every
// backend, including the reversed-edge blends this artwork relies on.
fn sstep(e0: f32, e1: f32, x: f32) -> f32 {
  let t = clamp((x - e0) / (e1 - e0), 0.0, 1.0);
  return t * t * (3.0 - 2.0 * t);
}

fn rot(a: f32) -> mat2x2f {
  let s = sin(a); let c = cos(a);
  return mat2x2f(c, -s, s, c);
}

fn hash(p: vec2f) -> vec2f {
  var q = vec2f(dot(p, vec2f(2127.1, 81.17)), dot(p, vec2f(1269.5, 283.37)));
  return fract(sin(q) * 43758.5453);
}

fn vnoise(p: vec2f) -> f32 {
  let i = floor(p); let f = fract(p);
  let w = f * f * (3.0 - 2.0 * f);
  let n = mix(
    mix(dot(-1.0 + 2.0 * hash(i + vec2f(0.0, 0.0)), f - vec2f(0.0, 0.0)),
        dot(-1.0 + 2.0 * hash(i + vec2f(1.0, 0.0)), f - vec2f(1.0, 0.0)), w.x),
    mix(dot(-1.0 + 2.0 * hash(i + vec2f(0.0, 1.0)), f - vec2f(0.0, 1.0)),
        dot(-1.0 + 2.0 * hash(i + vec2f(1.0, 1.0)), f - vec2f(1.0, 1.0)), w.x), w.y);
  return 0.5 + 0.5 * n;
}

@fragment fn fs(@builtin(position) pos: vec4f) -> @location(0) vec4f {
  let C = vec2f(pos.x, u.iResolution.y - pos.y);
  let t = u.iTime * u.uTimeSpeed;
  let uv = C / u.iResolution;
  let ratio = u.iResolution.x / u.iResolution.y;
  var tuv = uv - vec2f(0.5) + u.uCenterOffset;
  tuv /= max(u.uZoom, 0.001);

  let degree = vnoise(vec2f(t * 0.1, tuv.x * tuv.y) * u.uNoiseScale);
  tuv.y *= 1.0 / ratio;
  tuv *= rot((degree - 0.5) * u.uRotationAmount * 3.14159265 / 180.0 + 3.14159265);
  tuv.y *= ratio;

  let frequency = u.uWarpFrequency;
  let ws = max(u.uWarpStrength, 0.001);
  let amplitude = u.uWarpAmplitude / ws;
  let warpTime = t * u.uWarpSpeed;
  tuv.x += sin(tuv.y * frequency + warpTime) / amplitude;
  tuv.y += sin(tuv.x * (frequency * 1.5) + warpTime) / (amplitude * 0.5);

  let b = u.uColorBalance;
  let s = max(u.uBlendSoftness, 0.0);
  let blendRot = rot(u.uBlendAngle * 3.14159265 / 180.0);
  let blendX = (tuv * blendRot).x;
  let edge0 = -0.3 - b - s;
  let edge1 = 0.2 - b + s;
  let v0 = 0.5 - b + s;
  let v1 = -0.3 - b - s;
  let layer1 = mix(u.uColor3, u.uColor2, sstep(edge0, edge1, blendX));
  let layer2 = mix(u.uColor2, u.uColor1, sstep(edge0, edge1, blendX));
  var col = mix(layer1, layer2, sstep(v0, v1, tuv.y));

  var grainUv = uv * max(u.uGrainScale, 0.001);
  if (u.uGrainAnimated > 0.5) { grainUv += vec2f(u.iTime * 0.05); }
  let grain = fract(sin(dot(grainUv, vec2f(12.9898, 78.233))) * 43758.5453);
  col += (grain - 0.5) * u.uGrainAmount;

  col = (col - vec3f(0.5)) * u.uContrast + vec3f(0.5);
  let luma = dot(col, vec3f(0.2126, 0.7152, 0.0722));
  col = mix(vec3f(luma), col, u.uSaturation);
  col = pow(max(col, vec3f(0.0)), vec3f(1.0 / max(u.uGamma, 0.001)));
  col = clamp(col, vec3f(0.0), vec3f(1.0));
  if (u.uLightMode > 0.5) {
    let energy = max(max(col.r, col.g), col.b);
    let hue = col / max(energy, 0.001);
    let chroma = length(col - vec3f(dot(col, vec3f(0.333333))));
    let coverage = clamp(0.12 + chroma * 1.15 + energy * 0.18, 0.0, 0.88);
    col = mix(vec3f(1.0), clamp(hue * 0.58 + col * 0.18, vec3f(0.0), vec3f(1.0)), coverage);
  }

  return vec4f(col, 1.0);
}
`;

type Ctx = { scene: FullscreenScene; canvas: HTMLCanvasElement };
const ctxMap = new WeakMap<HTMLDivElement, Ctx>();

type GrainProps = {
  timeSpeed: number; colorBalance: number; warpStrength: number; warpFrequency: number;
  warpSpeed: number; warpAmplitude: number; blendAngle: number; blendSoftness: number;
  rotationAmount: number; noiseScale: number; grainAmount: number; grainScale: number;
  grainAnimated: boolean; contrast: number; gamma: number; saturation: number;
  centerX: number; centerY: number; zoom: number;
  color1: string; color2: string; color3: string; lightMode: boolean;
};

function applyGrainProps(v: Float32Array, p: GrainProps) {
  v[3] = p.timeSpeed;
  v[4] = p.colorBalance;
  v[5] = p.warpStrength;
  v[6] = p.warpFrequency;
  v[7] = p.warpSpeed;
  v[8] = p.warpAmplitude;
  v[9] = p.blendAngle;
  v[10] = p.blendSoftness;
  v[11] = p.rotationAmount;
  v[12] = p.noiseScale;
  v[13] = p.grainAmount;
  v[14] = p.grainScale;
  v[15] = p.grainAnimated ? 1.0 : 0.0;
  v[16] = p.contrast;
  v[17] = p.gamma;
  v[18] = p.saturation;
  v[19] = p.zoom;
  v[20] = p.lightMode ? 1.0 : 0.0;
  v[22] = p.centerX;
  v[23] = p.centerY;
  const c1 = hexToRgb(p.color1);
  const c2 = hexToRgb(p.color2);
  const c3 = hexToRgb(p.color3);
  v[24] = c1[0]; v[25] = c1[1]; v[26] = c1[2];
  v[28] = c2[0]; v[29] = c2[1]; v[30] = c2[2];
  v[32] = c3[0]; v[33] = c3[1]; v[34] = c3[2];
}

const Grainient: React.FC<GrainientProps> = ({
  timeSpeed = 0.25,
  colorBalance = 0.0,
  warpStrength = 1.0,
  warpFrequency = 5.0,
  warpSpeed = 2.0,
  warpAmplitude = 50.0,
  blendAngle = 0.0,
  blendSoftness = 0.05,
  rotationAmount = 500.0,
  noiseScale = 2.0,
  grainAmount = 0.1,
  grainScale = 2.0,
  grainAnimated = false,
  contrast = 1.5,
  gamma = 1.0,
  saturation = 1.0,
  centerX = 0.0,
  centerY = 0.0,
  zoom = 0.9,
  color1 = '#FF9FFC',
  color2 = '#5227FF',
  color3 = '#B497CF',
  lightMode = false,
  className = ''
}) => {
  const containerRef = useRef<HTMLDivElement | null>(null);
  const [unsupported, setUnsupported] = useState(false);
  const propsRef = useRef<GrainProps>({
    timeSpeed, colorBalance, warpStrength, warpFrequency, warpSpeed, warpAmplitude,
    blendAngle, blendSoftness, rotationAmount, noiseScale, grainAmount, grainScale,
    grainAnimated, contrast, gamma, saturation, centerX, centerY, zoom,
    color1, color2, color3, lightMode,
  });
  propsRef.current = {
    timeSpeed, colorBalance, warpStrength, warpFrequency, warpSpeed, warpAmplitude,
    blendAngle, blendSoftness, rotationAmount, noiseScale, grainAmount, grainScale,
    grainAnimated, contrast, gamma, saturation, centerX, centerY, zoom,
    color1, color2, color3, lightMode,
  };

  // Effect 1: build WebGPU scene once, pause when offscreen / tab hidden
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

    const setSize = () => {
      if (!scene) return;
      const { w, h } = cssSize(container);
      scene.setSize(w * dpr, h * dpr);
      scene.uniforms[0] = Math.max(1, Math.floor(w * dpr));
      scene.uniforms[1] = Math.max(1, Math.floor(h * dpr));
    };

    const loop = (t: number) => {
      if (!scene) return;
      scene.uniforms[2] = (t - t0) * 0.001;
      scene.writeUniforms();
      scene.frame({ r: 0, g: 0, b: 0, a: 1 });
      raf = requestAnimationFrame(loop);
    };

    const tryStart = () => {
      if (isVisible && isPageVisible && raf === 0 && scene) raf = requestAnimationFrame(loop);
    };
    const tryStop = () => {
      if (raf !== 0) { cancelAnimationFrame(raf); raf = 0; }
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
        const next = await createFullscreenScene(device, canvas, FRAG_WGSL, 36, 'opaque');
        if (!next) {
          setUnsupported(true);
          return;
        }
        scene = next;
        ctxMap.set(container, { scene, canvas });
        applyGrainProps(scene.uniforms, propsRef.current);
        setSize();
        scene.writeUniforms();
        scene.frame({ r: 0, g: 0, b: 0, a: 1 });

        ro = new ResizeObserver(setSize);
        ro.observe(container);
        io = new IntersectionObserver(
          ([entry]) => { isVisible = entry.isIntersecting; if (isVisible) tryStart(); else tryStop(); },
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
      ctxMap.delete(container);
      scene?.destroy();
      try { if (canvas && canvas.parentNode === container) container.removeChild(canvas); } catch { /* ignore */ }
    };
  }, []); // scene created once

  // Effect 2: sync props to uniforms — zero GPU cost, no teardown
  useEffect(() => {
    const container = containerRef.current;
    if (!container) return;
    const ctx = ctxMap.get(container);
    if (!ctx) return;
    applyGrainProps(ctx.scene.uniforms, propsRef.current);
  }, [
    timeSpeed, colorBalance, warpStrength, warpFrequency, warpSpeed,
    warpAmplitude, blendAngle, blendSoftness, rotationAmount, noiseScale,
    grainAmount, grainScale, grainAnimated, contrast, gamma, saturation,
    centerX, centerY, zoom, color1, color2, color3, lightMode
  ]);

  return (
    <div ref={containerRef} className={`relative h-full w-full overflow-hidden ${className}`.trim()}>
      {unsupported && <div className="grain-fallback" aria-hidden="true" />}
    </div>
  );
};

export default Grainient;
