import { useEffect, useRef, useState } from "react";
import { getQualityTier } from "../../lib/perf";
import { cn } from "../../utils/cn";

interface WebGPURaysProps {
  className?: string;
  /** Hex ray tint, e.g. #b6d9fc */
  color?: string;
  /** Drift speed multiplier */
  speed?: number;
  /** Overall beam strength */
  intensity?: number;
  opacity?: number;
}

const WGSL = /* wgsl */ `
struct U {
  u0: vec4f, // time, aspect, intensity, speed
  u1: vec4f, // tint A rgb + pad
  u2: vec4f, // tint B rgb + pad
  u3: vec4f, // res xy + pad pad
};
@group(0) @binding(0) var<uniform> u: U;

struct VSOut { @builtin(position) pos: vec4f; };

@vertex fn vs(@builtin(vertex_index) i: u32) -> VSOut {
  var p = array<vec2f, 3>(vec2f(-1.0, -1.0), vec2f(3.0, -1.0), vec2f(-1.0, 3.0));
  var o: VSOut;
  o.pos = vec4f(p[i], 0.0, 1.0);
  return o;
}

@fragment fn fs(@builtin(position) frag: vec4f) -> @location(0) vec4f {
  let res = u.u3.xy;
  let uv = frag.xy / res;
  // Fan origin above top-center; aspect-corrected so beams stay radial.
  let p = vec2f((uv.x - 0.5) * u.u0.y, uv.y + 0.18);
  let r = length(p);
  let ang = atan2(p.y, p.x);
  let t = u.u0.x * u.u0.w;
  let wob = sin(ang * 3.0 - t * 0.5) * 0.6;
  var beams = 0.5 + 0.5 * sin(ang * 7.0 + t + wob);
  beams = beams * beams * beams;
  let axial = exp(-r * 2.4);
  let vfade = exp(-max(uv.y - 0.05, 0.0) * 2.0);
  let glow = exp(-r * 5.0) * 0.6;
  let m = clamp((beams * axial + glow) * vfade * u.u0.z, 0.0, 1.0);
  let col = mix(u.u2.rgb, u.u1.rgb, beams) * m;
  return vec4f(col, m);
}
`;

function hexToRgb(hex: string): [number, number, number] {
  const m = /^#?([a-f\d]{2})([a-f\d]{2})([a-f\d]{2})$/i.exec(hex.trim());
  if (!m) return [0.71, 0.85, 0.99];
  return [parseInt(m[1], 16) / 255, parseInt(m[2], 16) / 255, parseInt(m[3], 16) / 255];
}

/** Ultra-lean WebGPU light rays. Low-power adapter, quarter-res, 30fps, pauses offscreen. */
export default function WebGPURays({
  className,
  color = "#b6d9fc",
  speed = 0.55,
  intensity = 0.9,
  opacity = 0.85,
}: WebGPURaysProps) {
  const wrapRef = useRef<HTMLDivElement>(null);
  const canvasRef = useRef<HTMLCanvasElement>(null);
  const [failed, setFailed] = useState(false);
  const params = useRef({ color, speed, intensity });
  params.current = { color, speed, intensity };

  useEffect(() => {
    const wrap = wrapRef.current;
    const canvas = canvasRef.current;
    if (!wrap || !canvas) return;

    // Cheap exits first — no GPU touched on weak setups (vercel: async-cheap-condition-before-await).
    if (window.matchMedia("(prefers-reduced-motion: reduce)").matches) {
      setFailed(true);
      return;
    }
    if (getQualityTier() === "low") {
      setFailed(true);
      return;
    }
    const nav = navigator as Navigator & { gpu?: GPU };
    if (!nav.gpu) {
      setFailed(true);
      return;
    }

    let device: GPUDevice | null = null;
    let context: GPUCanvasContext | null = null;
    let raf = 0;
    let running = false;
    let last = 0;
    let startT = performance.now();
    let uniform: GPUBuffer | null = null;
    let pipeline: GPURenderPipeline | null = null;
    let bindGroup: GPUBindGroup | null = null;
    let disposed = false;
    const RENDER_SCALE = 0.25;
    const FRAME_BUDGET = 1000 / 30;

    const data = new Float32Array(16);
    const tintA = hexToRgb(params.current.color);
    const tintB: [number, number, number] = [0.4, 0.23, 0.95]; // void violet depth

    const resize = () => {
      if (!wrap || !canvas || !device || !context) return;
      const w = Math.max(2, Math.floor(wrap.clientWidth * RENDER_SCALE));
      const h = Math.max(2, Math.floor(wrap.clientHeight * RENDER_SCALE));
      if (canvas.width !== w || canvas.height !== h) {
        canvas.width = w;
        canvas.height = h;
      }
    };

    const frame = (now: number) => {
      if (!running || disposed) return;
      if (document.hidden) {
        raf = requestAnimationFrame(frame);
        return;
      }
      if (now - last < FRAME_BUDGET) {
        raf = requestAnimationFrame(frame);
        return;
      }
      last = now;
      if (device && context && uniform && pipeline && bindGroup) {
        const w = canvas.width || 2;
        const h = canvas.height || 2;
        data[0] = (now - startT) / 1000;
        data[1] = w / h;
        data[2] = params.current.intensity;
        data[3] = params.current.speed;
        data[4] = tintA[0];
        data[5] = tintA[1];
        data[6] = tintA[2];
        data[7] = 0;
        data[8] = tintB[0];
        data[9] = tintB[1];
        data[10] = tintB[2];
        data[11] = 0;
        data[12] = w;
        data[13] = h;
        data[14] = 0;
        data[15] = 0;
        device.queue.writeBuffer(uniform, 0, data);
        const enc = device.createCommandEncoder();
        const pass = enc.beginRenderPass({
          colorAttachments: [
            {
              view: context.getCurrentTexture().createView(),
              loadOp: "clear",
              clearValue: { r: 0, g: 0, b: 0, a: 0 },
              storeOp: "store",
            },
          ],
        });
        pass.setPipeline(pipeline);
        pass.setBindGroup(0, bindGroup);
        pass.draw(3);
        pass.end();
        device.queue.submit([enc.finish()]);
      }
      raf = requestAnimationFrame(frame);
    };

    const start = () => {
      if (running || disposed) return;
      running = true;
      last = 0;
      raf = requestAnimationFrame(frame);
    };
    const stop = () => {
      running = false;
      if (raf) cancelAnimationFrame(raf);
      raf = 0;
    };

    let io: IntersectionObserver | null = null;
    let ro: ResizeObserver | null = null;
    const onVis = () => {
      if (document.hidden) return;
      const r = wrap.getBoundingClientRect();
      if (r.bottom > 0 && r.top < window.innerHeight) start();
    };

    (async () => {
      try {
        // Low-power = integrated GPU on dual-GPU machines: minimal watts for this shader.
        // Fall back to the default adapter so WebGPU still engages where low-power is unavailable.
        const adapter =
          (await nav.gpu!.requestAdapter({ powerPreference: "low-power" })) ??
          (await nav.gpu!.requestAdapter());
        if (!adapter || disposed) {
          setFailed(true);
          return;
        }
        device = await adapter.requestDevice();
        if (disposed) {
          device.destroy();
          return;
        }
        context = canvas.getContext("webgpu") as unknown as GPUCanvasContext | null;
        if (!context) {
          setFailed(true);
          return;
        }
        const format = nav.gpu!.getPreferredCanvasFormat();
        context.configure({ device, format, alphaMode: "premultiplied" });
        uniform = device.createBuffer({ size: 64, usage: GPUBufferUsage.UNIFORM | GPUBufferUsage.COPY_DST });
        const module = device.createShaderModule({ code: WGSL });
        pipeline = device.createRenderPipeline({
          layout: "auto",
          vertex: { module, entryPoint: "vs" },
          fragment: { module, entryPoint: "fs", targets: [{ format, blend: { color: { srcFactor: "one", dstFactor: "one-minus-src-alpha" }, alpha: { srcFactor: "one", dstFactor: "one-minus-src-alpha" } } }] },
          primitive: { topology: "triangle-list" },
        });
        bindGroup = device.createBindGroup({
          layout: pipeline.getBindGroupLayout(0),
          entries: [{ binding: 0, resource: { buffer: uniform } }],
        });
        resize();
        ro = new ResizeObserver(resize);
        ro.observe(wrap);
        io = new IntersectionObserver(([e]) => (e.isIntersecting ? start() : stop()), {
          threshold: 0,
          rootMargin: "200px",
        });
        io.observe(wrap);
        document.addEventListener("visibilitychange", onVis);
        onVis();
      } catch {
        setFailed(true);
      }
    })();

    return () => {
      disposed = true;
      stop();
      io?.disconnect();
      ro?.disconnect();
      document.removeEventListener("visibilitychange", onVis);
      try {
        device?.destroy();
      } catch {
        /* noop */
      }
    };
  }, []);

  if (failed) return <div className="adaptive-rays-fallback" aria-hidden="true" />;

  return (
    <div ref={wrapRef} className={cn("absolute inset-0 overflow-hidden", className)} aria-hidden="true" style={{ opacity }}>
      <canvas ref={canvasRef} className="block h-full w-full" />
    </div>
  );
}
