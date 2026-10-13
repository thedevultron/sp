import { useEffect, useRef, useState, type CSSProperties } from 'react';
import {
  FULLSCREEN_TRIANGLE_WGSL,
  createShaderModuleChecked,
  cssSize,
  getWebGPUDevice,
  hexToRgb,
} from './gpu/webgpu';

const MAX_STRANDS = 12;
const MAX_COLORS = 8;

/* Uniform words: [time, pad, res.xy, colors[8].rgb(+pad each),
   colorCount, strandCount, speed, amp, waviness, thick, glow, taper,
   spread, hueShift, intensity, opacity, scale, sat] (64 words, 256 B) */
const STRANDS_FRAG_WGSL = /* wgsl */ `
struct U {
  uTime: f32, _p0: f32, uResolution: vec2f,
  uColors: array<vec3f, 8>,
  uColorCount: f32, uStrandCount: f32, uSpeed: f32, uAmplitude: f32,
  uWaviness: f32, uThickness: f32, uGlow: f32, uTaper: f32,
  uSpread: f32, uHueShift: f32, uIntensity: f32, uOpacity: f32,
  uScale: f32, uSaturation: f32, _p1: vec2f,
};
@group(0) @binding(0) var<uniform> u: U;

const PI: f32 = 3.14159265;

fn spectrum(t: f32) -> vec3f {
  return 0.5 + 0.5 * cos(2.0 * PI * (t + vec3f(0.00, 0.33, 0.67)));
}

fn samplePalette(t: f32) -> vec3f {
  let tt = fract(t);
  let n = max(u.uColorCount, 1.0);
  let scaled = tt * n;
  var idx = u32(scaled);
  let blend = fract(scaled);
  var nextIdx = idx + 1u;
  if (f32(nextIdx) >= n) { nextIdx = 0u; }
  if (idx >= 8u) { idx = 7u; }
  if (nextIdx >= 8u) { nextIdx = 0u; }
  return mix(u.uColors[idx], u.uColors[nextIdx], blend);
}

fn strandColor(t: f32) -> vec3f {
  if (u.uColorCount > 0.5) { return samplePalette(t); }
  return spectrum(t);
}

@fragment fn fs(@builtin(position) pos: vec4f) -> @location(0) vec4f {
  let frag = vec2f(pos.x, u.uResolution.y - pos.y);
  var uv = (frag - 0.5 * u.uResolution) / u.uResolution.y;
  uv /= max(u.uScale, 0.0001);

  let e = 0.06 + u.uIntensity * 0.94;
  let env = pow(max(cos(uv.x * PI * 1.3), 0.0), u.uTaper);

  var col = vec3f(0.0);
  let strands = i32(u.uStrandCount + 0.5);

  for (var i = 0; i < 12; i++) {
    if (i >= strands) { break; }

    let fi = f32(i);
    let ph = fi * 1.7 * u.uSpread;
    let freq = (2.0 + fi * 0.35) * u.uWaviness;
    let spd = 1.4 + fi * 1.2;

    let tt = u.uTime * u.uSpeed;
    let w = sin(uv.x * freq + tt * spd + ph) * 0.60
          + sin(uv.x * freq * 1.1 - tt * spd * 0.7 + ph * 1.7) * 0.40;

    let amp = (0.1 + 0.02 * e) * env * u.uAmplitude;
    let y = w * amp;

    let d = abs(uv.y - y);
    let thick = (0.001 + 0.05 * e) * (0.35 + env) * u.uThickness;
    var g = thick / (d + thick * 0.45);
    g = g * g;

    let h = fi / f32(max(strands, 1)) + uv.x * 0.30 + u.uTime * 0.04 + u.uHueShift;
    col += strandColor(h) * g * env;
  }

  col *= 0.45 + 0.7 * e;
  col = 1.0 - exp(-col * u.uGlow);

  let gray = dot(col, vec3f(0.2126, 0.7152, 0.0722));
  col = max(mix(vec3f(gray), col, u.uSaturation), vec3f(0.0));

  let lum = max(max(col.r, col.g), col.b);
  let alpha = clamp(lum, 0.0, 1.0) * u.uOpacity;

  return vec4f(col * u.uOpacity, alpha);
}
`;

/* Glass uniforms: [res.xy, radius, refraction, dispersion] (8 words, 32 B) */
const GLASS_FRAG_WGSL = /* wgsl */ `
struct G {
  uResolution: vec2f,
  uRadius: f32, uRefraction: f32, uDispersion: f32, _p: vec2f,
};
@group(0) @binding(0) var scene_: texture_2d<f32>;
@group(0) @binding(1) var samp: sampler;
@group(0) @binding(2) var<uniform> u: G;

// Order-agnostic smoothstep (the lens rim relies on reversed edges).
fn sstep(e0: f32, e1: f32, x: f32) -> f32 {
  let t = clamp((x - e0) / (e1 - e0), 0.0, 1.0);
  return t * t * (3.0 - 2.0 * t);
}

fn toUv(p: vec2f) -> vec2f {
  return p * (u.uResolution.y / u.uResolution) + vec2f(0.5);
}

@fragment fn fs(@builtin(position) pos: vec4f) -> @location(0) vec4f {
  let frag = vec2f(pos.x, u.uResolution.y - pos.y);
  let p = (frag - 0.5 * u.uResolution) / u.uResolution.y;
  let d = length(p);
  let r = u.uRadius;

  let edge = (abs(dpdx(d)) + abs(dpdy(d))) * 1.5;
  let mask = 1.0 - sstep(r - edge, r + edge, d);
  if (mask <= 0.0) {
    return vec4f(0.0);
  }

  // sphere height: 0 at the rim, 1 at the center
  let z = sqrt(max(r * r - d * d, 0.0)) / r;
  let nd = d / r; // 0 at the center, 1 at the rim

  // refraction is confined to a narrow band near the rim
  let dir = select(vec2f(0.0), p / d, d > 0.0);
  let lens = sstep(0.85, 1.0, nd) * pow(nd, 6.0);
  let offset = -dir * lens * u.uRefraction * 0.15;
  let disp = -dir * lens * u.uDispersion * 0.012;

  var light: vec3f;
  // textureSampleLevel: sampling must not rely on implicit derivatives
  // because this fragment runs after a non-uniform branch on @builtin(position).
  light.r = textureSampleLevel(scene_, samp, toUv(p + offset - disp), 0.0).r;
  light.g = textureSampleLevel(scene_, samp, toUv(p + offset), 0.0).g;
  light.b = textureSampleLevel(scene_, samp, toUv(p + offset + disp), 0.0).b;

  // neutral fresnel rim (no color tint so the glass stays clear)
  let fres = pow(1.0 - z, 3.0);
  let rim = vec3f(1.0) * fres * 0.18;

  // specular highlight from the upper-left
  let lightDir = normalize(vec2f(-0.55, 0.6));
  var spec = pow(max(dot(p / max(r, 1e-4), lightDir), 0.0), 6.0);
  spec *= sstep(r, r * 0.55, d);

  let emissive = light + rim + vec3f(spec) * 0.4;
  let emissiveA = clamp(max(max(emissive.r, emissive.g), emissive.b), 0.0, 1.0);

  // almost clear glass body: only a faint neutral darkening near the rim
  let bodyA = 0.05 + fres * 0.05;

  // composite emissive light over the clear body (premultiplied)
  var outA = emissiveA + bodyA * (1.0 - emissiveA);
  var outRGB = emissive;

  outRGB *= mask;
  outA *= mask;

  return vec4f(outRGB, outA);
}
`;

export interface StrandsProps {
  colors?: string[];
  count?: number;
  speed?: number;
  amplitude?: number;
  waviness?: number;
  thickness?: number;
  glow?: number;
  taper?: number;
  spread?: number;
  hueShift?: number;
  intensity?: number;
  saturation?: number;
  opacity?: number;
  scale?: number;
  glass?: boolean;
  refraction?: number;
  dispersion?: number;
  glassSize?: number;
  className?: string;
  style?: CSSProperties;
}

type StrandSettings = Required<Omit<StrandsProps, 'className' | 'style'>>;

const buildPalette = (colors: string[]): Array<[number, number, number]> => {
  const filled = colors && colors.length ? colors : ['#ffffff'];
  const padded: Array<[number, number, number]> = [];
  for (let i = 0; i < MAX_COLORS; i++) {
    padded.push(hexToRgb(filled[i] ?? filled[filled.length - 1]));
  }
  return padded;
};

function writeStrandUniforms(v: Float32Array, p: StrandSettings) {
  const palette = buildPalette(p.colors);
  for (let i = 0; i < MAX_COLORS; i++) {
    v[4 + i * 4] = palette[i][0];
    v[4 + i * 4 + 1] = palette[i][1];
    v[4 + i * 4 + 2] = palette[i][2];
  }
  v[36] = Math.min(p.colors.length, MAX_COLORS);
  v[37] = Math.min(Math.max(Math.round(p.count), 1), MAX_STRANDS);
  v[38] = p.speed;
  v[39] = p.amplitude;
  v[40] = p.waviness;
  v[41] = p.thickness;
  v[42] = p.glow;
  v[43] = p.taper;
  v[44] = p.spread;
  v[45] = p.hueShift;
  v[46] = p.intensity;
  v[47] = p.opacity;
  v[48] = p.scale;
  v[49] = p.saturation;
}

export default function Strands({
  colors = ['#FF4242', '#7C3AED', '#06B6D4', '#EAB308'],
  count = 3,
  speed = 0.5,
  amplitude = 1,
  waviness = 1,
  thickness = 0.7,
  glow = 2.6,
  taper = 3,
  spread = 1,
  hueShift = 0,
  intensity = 0.6,
  saturation = 1.5,
  opacity = 1,
  scale = 1.5,
  glass = false,
  refraction = 1,
  dispersion = 1,
  glassSize = 1,
  className = '',
  style
}: StrandsProps) {
  const propsRef = useRef<StrandSettings>({
    colors, count, speed, amplitude, waviness, thickness, glow, taper, spread,
    hueShift, intensity, saturation, opacity, scale, glass, refraction, dispersion, glassSize
  });
  propsRef.current = {
    colors, count, speed, amplitude, waviness, thickness, glow, taper, spread,
    hueShift, intensity, saturation, opacity, scale, glass, refraction, dispersion, glassSize
  };

  const ctnDom = useRef<HTMLDivElement>(null);
  const [unsupported, setUnsupported] = useState(false);

  useEffect(() => {
    const ctn = ctnDom.current;
    if (!ctn) return;
    let cancelled = false;
    let raf = 0;
    let ro: ResizeObserver | null = null;
    let io: IntersectionObserver | null = null;
    let isVisible = true;
    let isPageVisible = !document.hidden;
    const dpr = Math.min(window.devicePixelRatio || 1, 2);

    let device: GPUDevice | null = null;
    let canvas: HTMLCanvasElement | null = null;
    let context: GPUCanvasContext | null = null;
    let format: GPUTextureFormat = 'bgra8unorm';
    let strandPipeline: GPURenderPipeline | null = null;
    let strandUniforms: Float32Array | null = null;
    let strandUniformBuffer: GPUBuffer | null = null;
    let strandBindGroup: GPUBindGroup | null = null;
    let glassPipeline: GPURenderPipeline | null = null;
    let glassUniforms: Float32Array | null = null;
    let glassUniformBuffer: GPUBuffer | null = null;
    let glassBindGroup: GPUBindGroup | null = null;
    let sceneTexture: GPUTexture | null = null;
    let sceneView: GPUTextureView | null = null;
    let texW = 0;
    let texH = 0;

    const ensureSceneTexture = (w: number, h: number) => {
      if (!device) return;
      if (sceneTexture && texW === w && texH === h) return;
      sceneTexture?.destroy();
      sceneTexture = device.createTexture({
        size: { width: w, height: h },
        format: 'rgba16float',
        usage: GPUTextureUsage.RENDER_ATTACHMENT | GPUTextureUsage.TEXTURE_BINDING,
      });
      sceneView = sceneTexture.createView();
      texW = w;
      texH = h;
      if (glassPipeline && device) {
        glassBindGroup = device.createBindGroup({
          layout: glassPipeline.getBindGroupLayout(0),
          entries: [
            { binding: 0, resource: sceneView },
            { binding: 1, resource: device.createSampler({ magFilter: 'linear', minFilter: 'linear' }) },
            { binding: 2, resource: { buffer: glassUniformBuffer as GPUBuffer } },
          ],
        });
      }
    };

    const resize = () => {
      if (!device || !canvas || !context || !strandUniforms || !glassUniforms) return;
      const { w, h } = cssSize(ctn);
      const pw = Math.max(1, Math.floor(w * dpr));
      const ph = Math.max(1, Math.floor(h * dpr));
      canvas.width = pw;
      canvas.height = ph;
      context.configure({ device, format, alphaMode: 'premultiplied' });
      strandUniforms[2] = pw;
      strandUniforms[3] = ph;
      glassUniforms[0] = pw;
      glassUniforms[1] = ph;
      ensureSceneTexture(pw, ph);
    };

    const renderFrame = (t: number) => {
      if (!device || !context || !strandPipeline || !strandBindGroup || !strandUniforms || !strandUniformBuffer) return;
      const p = propsRef.current;
      strandUniforms[0] = t * 0.001;
      writeStrandUniforms(strandUniforms, p);
      device.queue.writeBuffer(strandUniformBuffer, 0, strandUniforms.buffer, strandUniforms.byteOffset, strandUniforms.byteLength);

      const encoder = device.createCommandEncoder();
      if (p.glass && glassPipeline && glassBindGroup && glassUniformBuffer && glassUniforms && sceneView) {
        const pass = encoder.beginRenderPass({
          colorAttachments: [{ view: sceneView, clearValue: { r: 0, g: 0, b: 0, a: 0 }, loadOp: 'clear', storeOp: 'store' }],
        });
        pass.setPipeline(strandPipeline);
        pass.setBindGroup(0, strandBindGroup);
        pass.draw(3);
        pass.end();

        glassUniforms[2] = 0.46 * p.glassSize;
        glassUniforms[3] = p.refraction;
        glassUniforms[4] = p.dispersion;
        device.queue.writeBuffer(glassUniformBuffer, 0, glassUniforms.buffer, glassUniforms.byteOffset, glassUniforms.byteLength);
        const view = context.getCurrentTexture().createView();
        const gpass = encoder.beginRenderPass({
          colorAttachments: [{ view, clearValue: { r: 0, g: 0, b: 0, a: 0 }, loadOp: 'clear', storeOp: 'store' }],
        });
        gpass.setPipeline(glassPipeline);
        gpass.setBindGroup(0, glassBindGroup);
        gpass.draw(3);
        gpass.end();
      } else {
        const view = context.getCurrentTexture().createView();
        const pass = encoder.beginRenderPass({
          colorAttachments: [{ view, clearValue: { r: 0, g: 0, b: 0, a: 0 }, loadOp: 'clear', storeOp: 'store' }],
        });
        pass.setPipeline(strandPipeline);
        pass.setBindGroup(0, strandBindGroup);
        pass.draw(3);
        pass.end();
      }
      device.queue.submit([encoder.finish()]);
    };

    const update = (t: number) => {
      raf = requestAnimationFrame(update);
      renderFrame(t);
    };
    const tryStart = () => {
      if (isVisible && isPageVisible && raf === 0 && device) raf = requestAnimationFrame(update);
    };
    const tryStop = () => {
      if (raf !== 0) { cancelAnimationFrame(raf); raf = 0; }
    };
    const onVisibility = () => {
      isPageVisible = !document.hidden;
      if (isPageVisible) tryStart();
      else tryStop();
    };

    getWebGPUDevice().then(async (dev) => {
      if (cancelled) return;
      if (!dev) {
        setUnsupported(true);
        return;
      }
      // GPU lost mid-session: stop the loop and drop to static artwork.
      dev.lost.then(() => {
        if (cancelled) return;
        tryStop();
        setUnsupported(true);
      });
      try {
        device = dev;
        canvas = document.createElement('canvas');
        canvas.style.width = '100%';
        canvas.style.height = '100%';
        canvas.style.display = 'block';
        canvas.style.backgroundColor = 'transparent';
        ctn.appendChild(canvas);
        const ctx = canvas.getContext('webgpu');
        if (!ctx) {
          setUnsupported(true);
          return;
        }
        context = ctx;
        format = navigator.gpu.getPreferredCanvasFormat();

        const vsModule = await createShaderModuleChecked(device, FULLSCREEN_TRIANGLE_WGSL);
        const strandModule = await createShaderModuleChecked(device, STRANDS_FRAG_WGSL);
        const glassModule = await createShaderModuleChecked(device, GLASS_FRAG_WGSL);
        if (!vsModule || !strandModule || !glassModule) {
          setUnsupported(true);
          return;
        }
        strandPipeline = device.createRenderPipeline({
          layout: 'auto',
          vertex: { module: vsModule, entryPoint: 'vs' },
          fragment: { module: strandModule, entryPoint: 'fs', targets: [{ format }] },
          primitive: { topology: 'triangle-list' },
        });
        strandUniforms = new Float32Array(64);
        strandUniformBuffer = device.createBuffer({ size: 256, usage: GPUBufferUsage.UNIFORM | GPUBufferUsage.COPY_DST });
        strandBindGroup = device.createBindGroup({
          layout: strandPipeline.getBindGroupLayout(0),
          entries: [{ binding: 0, resource: { buffer: strandUniformBuffer } }],
        });

        glassPipeline = device.createRenderPipeline({
          layout: 'auto',
          vertex: { module: vsModule, entryPoint: 'vs' },
          fragment: { module: glassModule, entryPoint: 'fs', targets: [{ format }] },
          primitive: { topology: 'triangle-list' },
        });
        glassUniforms = new Float32Array(8);
        glassUniformBuffer = device.createBuffer({ size: 32, usage: GPUBufferUsage.UNIFORM | GPUBufferUsage.COPY_DST });

        resize();
        writeStrandUniforms(strandUniforms, propsRef.current);
        device.queue.writeBuffer(strandUniformBuffer, 0, strandUniforms.buffer, strandUniforms.byteOffset, strandUniforms.byteLength);
        renderFrame(performance.now());

        ro = new ResizeObserver(resize);
        ro.observe(ctn);
        window.addEventListener('resize', resize);
        io = new IntersectionObserver(
          ([entry]) => { isVisible = entry.isIntersecting; if (isVisible) tryStart(); else tryStop(); },
          { threshold: 0 }
        );
        io.observe(ctn);
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
      window.removeEventListener('resize', resize);
      document.removeEventListener('visibilitychange', onVisibility);
      sceneTexture?.destroy();
      strandUniformBuffer?.destroy();
      glassUniformBuffer?.destroy();
      if (canvas && canvas.parentNode === ctn) ctn.removeChild(canvas);
    };
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  return (
    <div ref={ctnDom} className={`relative w-full h-full bg-transparent ${className}`} style={style}>
      {unsupported && <div className="strands-fallback" aria-hidden="true" />}
    </div>
  );
}
