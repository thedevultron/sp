import { useEffect, useRef, useState } from 'react';

/** WebGPU fullscreen cinematic shader — violet nebula + light beams + grain.
/// Falls back to 2D canvas nebula when WebGPU is unavailable. */
export default function WebGPUHero({ scrollRef }: { scrollRef: React.RefObject<number> }) {
  const canvasRef = useRef<HTMLCanvasElement | null>(null);
  const mouse = useRef({ x: 0.5, y: 0.35 });
  const [fallback, setFallback] = useState(false);

  useEffect(() => {
    const onMove = (e: MouseEvent) => {
      mouse.current.x = e.clientX / window.innerWidth;
      mouse.current.y = e.clientY / window.innerHeight;
    };
    window.addEventListener('mousemove', onMove, { passive: true });
    return () => window.removeEventListener('mousemove', onMove);
  }, []);

  useEffect(() => {
    let raf = 0;
    let dead = false;
    const canvas = canvasRef.current;
    if (!canvas) return;

    const startFallback2D = () => {
      setFallback(true);
      const ctx = canvas.getContext('2d');
      if (!ctx) return;
      const draw = (t: number) => {
        if (dead) return;
        const w = (canvas.width = canvas.clientWidth * Math.min(2, window.devicePixelRatio || 1));
        const h = (canvas.height = canvas.clientHeight * Math.min(2, window.devicePixelRatio || 1));
        const time = t * 0.001;
        const scroll = scrollRef.current ?? 0;
        const g = ctx.createRadialGradient(
          w * (0.5 + (mouse.current.x - 0.5) * 0.12), h * 0.34, 0,
          w * 0.5, h * 0.4, Math.max(w, h) * 0.75
        );
        g.addColorStop(0, '#241b5e');
        g.addColorStop(0.4, '#120f30');
        g.addColorStop(1, '#05060f');
        ctx.fillStyle = g;
        ctx.fillRect(0, 0, w, h);
        // beams
        ctx.globalAlpha = 0.5 - scroll * 0.3;
        for (let i = 0; i < 3; i++) {
          const y = h * (0.55 + i * 0.09) + Math.sin(time * 0.6 + i * 2) * 10;
          const bg = ctx.createLinearGradient(0, y, w, y);
          bg.addColorStop(0, 'rgba(182,217,252,0)');
          bg.addColorStop(0.5, `rgba(150,170,255,${0.10 - i * 0.025})`);
          bg.addColorStop(1, 'rgba(182,217,252,0)');
          ctx.fillStyle = bg;
          ctx.fillRect(0, y, w, 2);
        }
        ctx.globalAlpha = 1;
        raf = requestAnimationFrame(draw);
      };
      raf = requestAnimationFrame(draw);
    };

    const startWebGPU = async () => {
      try {
        const nav = navigator as Navigator & { gpu?: GPU };
        if (!nav.gpu) throw new Error('no webgpu');
        const adapter = await nav.gpu.requestAdapter({ powerPreference: 'high-performance' });
        if (!adapter) throw new Error('no adapter');
        const device = await adapter.requestDevice();
        const context = canvas.getContext('webgpu') as GPUCanvasContext | null;
        if (!context) throw new Error('no ctx');
        const format = nav.gpu.getPreferredCanvasFormat();
        context.configure({ device, format, alphaMode: 'opaque' });

        const shader = /* wgsl */ `
          struct U { time: f32, mx: f32, my: f32, scroll: f32, aspect: f32 };
          @group(0) @binding(0) var<uniform> u: U;
          struct VS { @builtin(position) pos: vec4f };
          @vertex fn vs(@builtin(vertex_index) i: u32) -> VS {
            var p = array<vec2f, 3>(vec2f(-1.,-1.), vec2f(3.,-1.), vec2f(-1.,3.));
            var o: VS; o.pos = vec4f(p[i], 0., 1.); return o;
          }
          fn hash(p: vec2f) -> f32 { return fract(sin(dot(p, vec2f(127.1, 311.7))) * 43758.5453); }
          fn noise(p: vec2f) -> f32 {
            let i = floor(p); let f = fract(p); let k = f*f*(3.-2.*f);
            return mix(mix(hash(i), hash(i+vec2f(1,0)), k.x), mix(hash(i+vec2f(0,1)), hash(i+vec2f(1,1)), k.x), k.y);
          }
          @fragment fn fs(v: VS) -> @location(0) vec4f {
            let uv = v.pos.xy / vec2f(1280.0, 720.0);
            var p = vec2f(v.pos.x / 720.0 * u.aspect, v.pos.y / 720.0);
            let m = vec2f(u.mx - 0.5, (1.0 - u.my) - 0.5);
            let t = u.time * 0.12;
            // nebula layers
            var n = noise(p * 1.6 + vec2f(t, -t * 0.6));
            n += 0.5 * noise(p * 3.4 - vec2f(t * 0.7, t * 0.4));
            n /= 1.5;
            var col = vec3f(0.019, 0.023, 0.058); // #05060f
            let violet = vec3f(0.32, 0.19, 0.85);
            let ice = vec3f(0.55, 0.75, 0.98);
            let d = length(p - vec2f(0.0 + m.x * 0.35, 0.25 + m.y * 0.25));
            let glow = exp(-d * d * 2.4) * (0.55 + n * 0.8);
            col += violet * glow * 0.85;
            col += ice * exp(-d * d * 7.0) * 0.22;
            // horizon beams
            let beam = exp(-pow((uv.y - 0.66 - 0.02 * sin(uv.x * 9.0 + u.time * 0.5)) * 40.0, 2.0));
            col += vec3f(0.35, 0.45, 0.8) * beam * 0.10;
            let beam2 = exp(-pow((uv.y - 0.74) * 55.0, 2.0));
            col += vec3f(0.4, 0.5, 0.9) * beam2 * 0.06;
            // drifting stars / dust
            let sp = fract(p * vec2f(60.0, 90.0) + vec2f(t * 2.0, 0.0));
            let star = step(0.985, hash(floor(p * vec2f(60.0, 90.0)))) * smoothstep(0.4, 0.0, length(sp - 0.5));
            col += vec3f(0.7, 0.8, 1.0) * star * 0.5 * (1.0 - u.scroll);
            // vignette + scroll dim
            col *= 1.0 - u.scroll * 0.55;
            let vig = smoothstep(1.5, 0.35, length(p - vec2f(0.0, 0.1)));
            col *= mix(0.55, 1.0, vig);
            // grain
            col += (hash(v.pos.xy + fract(u.time) * 100.0) - 0.5) * 0.035;
            return vec4f(col, 1.0);
          }
        `;
        const mod = device.createShaderModule({ code: shader });
        const pipeline = device.createRenderPipeline({
          layout: 'auto',
          vertex: { module: mod, entryPoint: 'vs' },
          fragment: { module: mod, entryPoint: 'fs', targets: [{ format }] },
          primitive: { topology: 'triangle-list' },
        });
        const buf = device.createBuffer({ size: 20, usage: GPUBufferUsage.UNIFORM | GPUBufferUsage.COPY_DST });
        const bind = device.createBindGroup({ layout: pipeline.getBindGroupLayout(0), entries: [{ binding: 0, resource: { buffer: buf } }] });
        const start = performance.now();
        const frame = () => {
          if (dead) return;
          const w = Math.floor(canvas.clientWidth * Math.min(2, window.devicePixelRatio || 1));
          const h = Math.floor(canvas.clientHeight * Math.min(2, window.devicePixelRatio || 1));
          if (canvas.width !== w || canvas.height !== h) { canvas.width = w; canvas.height = h; }
          const data = new Float32Array([
            (performance.now() - start) / 1000,
            mouse.current.x, mouse.current.y,
            Math.min(1, Math.max(0, scrollRef.current ?? 0)),
            canvas.width / Math.max(1, canvas.height),
          ]);
          device.queue.writeBuffer(buf, 0, data);
          const enc = device.createCommandEncoder();
          const pass = enc.beginRenderPass({
            colorAttachments: [{ view: context.getCurrentTexture().createView(), loadOp: 'clear', storeOp: 'store', clearValue: { r: 0.02, g: 0.023, b: 0.06, a: 1 } }],
          });
          pass.setPipeline(pipeline);
          pass.setBindGroup(0, bind);
          pass.draw(3);
          pass.end();
          device.queue.submit([enc.finish()]);
          raf = requestAnimationFrame(frame);
        };
        raf = requestAnimationFrame(frame);
      } catch {
        startFallback2D();
      }
    };

    const reduced = window.matchMedia('(prefers-reduced-motion: reduce)').matches;
    if (reduced) { startFallback2D(); }
    else { void startWebGPU(); }
    return () => { dead = true; cancelAnimationFrame(raf); };
  }, [scrollRef]);

  return (
    <canvas
      ref={canvasRef}
      aria-hidden="true"
      style={{ position: 'absolute', inset: 0, width: '100%', height: '100%', display: 'block' }}
    />
  );
}

export function VoiceBars({ count = 36, playing = true }: { count?: number; playing?: boolean }) {
  const ref = useRef<HTMLDivElement | null>(null);
  useEffect(() => {
    if (!playing) return;
    let raf = 0;
    const els = ref.current?.children;
    if (!els) return;
    const t0 = performance.now();
    const tick = (t: number) => {
      const time = (t - t0) / 1000;
      for (let i = 0; i < els.length; i++) {
        const el = els[i] as HTMLElement;
        const v = 6 + Math.abs(Math.sin(time * 2.2 + i * 0.55)) * 26 + Math.sin(time * 5 + i) * 3;
        el.style.height = `${v.toFixed(1)}px`;
        el.style.opacity = `${(0.35 + (v / 34) * 0.65).toFixed(2)}`;
      }
      raf = requestAnimationFrame(tick);
    };
    raf = requestAnimationFrame(tick);
    return () => cancelAnimationFrame(raf);
  }, [playing, count]);
  return (
    <div ref={ref} style={{ display: 'flex', alignItems: 'center', gap: 5, height: 36 }} aria-hidden="true">
      {Array.from({ length: count }).map((_, i) => (
        <span key={i} className="vbar" style={{ height: 8 }} />
      ))}
    </div>
  );
}
