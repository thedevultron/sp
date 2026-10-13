/// <reference types="@webgpu/types" />

/**
 * Shared WebGPU bootstrap for fullscreen-shader visuals.
 * One cached device for every canvas; callers own their pipelines,
 * uniform buffers, loops, and fallbacks.
 */

let devicePromise: Promise<GPUDevice | null> | null = null;

export function isWebGPUSupported(): boolean {
  try {
    return typeof navigator !== 'undefined' && 'gpu' in navigator && !!(navigator as Navigator & { gpu?: unknown }).gpu;
  } catch {
    return false;
  }
}

export function getWebGPUDevice(): Promise<GPUDevice | null> {
  if (!devicePromise) {
    const attempt = (async (): Promise<GPUDevice | null> => {
      try {
        if (!isWebGPUSupported()) return null;
        // powerPreference is ignored on some Windows drivers and logs a
        // console warning; request without it.
        const adapter = await navigator.gpu.requestAdapter();
        if (!adapter) return null;
        const device = await adapter.requestDevice();
        device.lost.then(() => {
          devicePromise = null;
        });
        return device;
      } catch {
        return null;
      }
    })();
    // Never leave visuals hanging on a stalled driver prompt: fall back fast.
    const timeout = new Promise<null>((resolve) => window.setTimeout(() => resolve(null), 3000));
    devicePromise = Promise.race([attempt, timeout]).then((device) => {
      if (!device) devicePromise = null;
      return device;
    });
  }
  return devicePromise;
}

export function hexToRgb(hex: string): [number, number, number] {
  const result = /^#?([a-f\d]{2})([a-f\d]{2})([a-f\d]{2})$/i.exec(hex);
  if (!result) return [1, 1, 1];
  return [parseInt(result[1], 16) / 255, parseInt(result[2], 16) / 255, parseInt(result[3], 16) / 255];
}

export const FULLSCREEN_TRIANGLE_WGSL = /* wgsl */ `
@vertex fn vs(@builtin(vertex_index) i: u32) -> @builtin(position) vec4f {
  var p = array<vec2f, 3>(vec2f(-1.0, -1.0), vec2f(3.0, -1.0), vec2f(-1.0, 3.0));
  return vec4f(p[i], 0.0, 1.0);
}
`;

export interface FullscreenScene {
  device: GPUDevice;
  context: GPUCanvasContext;
  format: GPUTextureFormat;
  pipeline: GPURenderPipeline;
  uniformBuffer: GPUBuffer;
  uniforms: Float32Array;
  setSize: (pixelWidth: number, pixelHeight: number) => void;
  writeUniforms: () => void;
  frame: (clear: GPUColor) => void;
  destroy: () => void;
}

/**
 * Create a shader module and reject it when compilation reports errors, so
 * one bad WGSL string can never poison the device with repeated validation
 * failures (and console spam). Returns null on any error.
 */
export async function createShaderModuleChecked(
  device: GPUDevice,
  code: string
): Promise<GPUShaderModule | null> {
  let module: GPUShaderModule;
  try {
    module = device.createShaderModule({ code });
  } catch {
    return null;
  }
  try {
    const info = await module.getCompilationInfo();
    if (info.messages.some((m) => m.type === 'error')) return null;
  } catch {
    return null;
  }
  return module;
}

/**
 * Build a fullscreen-triangle pipeline with a single uniform buffer
 * (group 0, binding 0, fragment-visible). `uniformWords` is the
 * Float32Array length backing the buffer. Async: shader compilation is
 * validated before the pipeline is created, so a bad shader returns null
 * and callers fall back to static artwork.
 */
export async function createFullscreenScene(
  device: GPUDevice,
  canvas: HTMLCanvasElement,
  fragmentWGSL: string,
  uniformWords: number,
  alphaMode: GPUCanvasAlphaMode = 'premultiplied'
): Promise<FullscreenScene | null> {
  const context = canvas.getContext('webgpu');
  if (!context) return null;
  const format = navigator.gpu.getPreferredCanvasFormat();

  const vsModule = await createShaderModuleChecked(device, FULLSCREEN_TRIANGLE_WGSL);
  const fsModule = await createShaderModuleChecked(device, fragmentWGSL);
  if (!vsModule || !fsModule) return null;

  let pipeline: GPURenderPipeline;
  try {
    pipeline = device.createRenderPipeline({
      layout: 'auto',
      vertex: { module: vsModule, entryPoint: 'vs' },
      fragment: { module: fsModule, entryPoint: 'fs', targets: [{ format }] },
      primitive: { topology: 'triangle-list' },
    });
  } catch {
    return null;
  }

  const paddedBytes = Math.ceil((uniformWords * 4) / 16) * 16;
  const uniformBuffer = device.createBuffer({ size: paddedBytes, usage: GPUBufferUsage.UNIFORM | GPUBufferUsage.COPY_DST });
  const bindGroup = device.createBindGroup({
    layout: pipeline.getBindGroupLayout(0),
    entries: [{ binding: 0, resource: { buffer: uniformBuffer } }],
  });
  const uniforms = new Float32Array(uniformWords);

  let configuredW = 0;
  let configuredH = 0;

  return {
    device,
    context,
    format,
    pipeline,
    uniformBuffer,
    uniforms,
    setSize(pixelWidth: number, pixelHeight: number) {
      const w = Math.max(1, Math.floor(pixelWidth));
      const h = Math.max(1, Math.floor(pixelHeight));
      if (canvas.width !== w) canvas.width = w;
      if (canvas.height !== h) canvas.height = h;
      if (configuredW !== w || configuredH !== h) {
        configuredW = w;
        configuredH = h;
        context.configure({ device, format, alphaMode });
      }
    },
    writeUniforms() {
      device.queue.writeBuffer(uniformBuffer, 0, uniforms.buffer, uniforms.byteOffset, uniforms.byteLength);
    },
    frame(clear: GPUColor) {
      const encoder = device.createCommandEncoder();
      const view = context.getCurrentTexture().createView();
      const pass = encoder.beginRenderPass({
        colorAttachments: [{ view, clearValue: clear, loadOp: 'clear', storeOp: 'store' }],
      });
      pass.setPipeline(pipeline);
      pass.setBindGroup(0, bindGroup);
      pass.draw(3);
      pass.end();
      device.queue.submit([encoder.finish()]);
    },
    destroy() {
      uniformBuffer.destroy();
    },
  };
}

/** CSS pixel size of an element, floored, minimum 1px. */
export function cssSize(el: HTMLElement): { w: number; h: number } {
  const rect = el.getBoundingClientRect();
  return { w: Math.max(1, Math.floor(rect.width)), h: Math.max(1, Math.floor(rect.height)) };
}
