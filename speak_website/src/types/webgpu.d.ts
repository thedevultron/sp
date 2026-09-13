/* Minimal ambient WebGPU types (project TS DOM lib predates WebGPU). */
export {};

declare global {
  type GPUTextureFormat = string;
  type GPUPowerPreference = "low-power" | "high-performance";

  interface GPU {
    requestAdapter(options?: { powerPreference?: GPUPowerPreference }): Promise<GPUAdapter | null>;
    getPreferredCanvasFormat(): GPUTextureFormat;
  }

  interface GPUAdapter {
    requestDevice(descriptor?: unknown): Promise<GPUDevice>;
  }

  interface GPUBuffer {
    destroy?(): void;
  }

  interface GPUShaderModule {
    [key: string]: unknown;
  }

  interface GPURenderPipeline {
    getBindGroupLayout(index: number): GPUBindGroupLayout;
  }

  interface GPUBindGroupLayout {
    [key: string]: unknown;
  }

  interface GPUBindGroup {
    [key: string]: unknown;
  }

  interface GPUCommandEncoder {
    beginRenderPass(descriptor: unknown): GPURenderPassEncoder;
    finish(): unknown;
  }

  interface GPURenderPassEncoder {
    setPipeline(pipeline: GPURenderPipeline): void;
    setBindGroup(index: number, bindGroup: GPUBindGroup): void;
    draw(vertexCount: number): void;
    end(): void;
  }

  interface GPUQueue {
    writeBuffer(buffer: GPUBuffer, bufferOffset: number, data: Float32Array): void;
    submit(commandBuffers: unknown[]): void;
  }

  interface GPUDevice {
    queue: GPUQueue;
    createBuffer(descriptor: { size: number; usage: number }): GPUBuffer;
    createShaderModule(descriptor: { code: string }): GPUShaderModule;
    createRenderPipeline(descriptor: unknown): GPURenderPipeline;
    createBindGroup(descriptor: { layout: GPUBindGroupLayout; entries: Array<{ binding: number; resource: { buffer: GPUBuffer } }> }): GPUBindGroup;
    createCommandEncoder(): GPUCommandEncoder;
    destroy(): void;
  }

  interface GPUCanvasContext {
    configure(options: { device: GPUDevice; format: GPUTextureFormat; alphaMode?: string }): void;
    unconfigure(): void;
    getCurrentTexture(): { createView(): unknown };
  }

  // eslint-disable-next-line @typescript-eslint/no-unused-vars
  interface Navigator {
    gpu?: GPU;
  }

  const GPUBufferUsage: {
    UNIFORM: number;
    COPY_DST: number;
  };
}
