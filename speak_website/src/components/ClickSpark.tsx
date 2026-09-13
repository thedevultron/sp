import React, { useRef, useEffect, useCallback } from 'react';

interface ClickSparkProps {
  sparkColor?: string;
  sparkSize?: number;
  sparkRadius?: number;
  sparkCount?: number;
  duration?: number;
  easing?: 'linear' | 'ease-in' | 'ease-out' | 'ease-in-out';
  extraScale?: number;
  children?: React.ReactNode;
}

interface Spark {
  x: number;
  y: number;
  angle: number;
  startTime: number;
}

const ClickSpark: React.FC<ClickSparkProps> = ({
  sparkColor = '#fff',
  sparkSize = 10,
  sparkRadius = 15,
  sparkCount = 8,
  duration = 400,
  easing = 'ease-out',
  extraScale = 1.0,
  children
}) => {
  const canvasRef = useRef<HTMLCanvasElement>(null);
  const sparksRef = useRef<Spark[]>([]);
  const rafRef = useRef(0);
  const opts = useRef({ sparkColor, sparkSize, sparkRadius, sparkCount, duration, easing, extraScale });
  opts.current = { sparkColor, sparkSize, sparkRadius, sparkCount, duration, easing, extraScale };

  /* Viewport-sized canvas at DPR 1 — a fullscreen spark layer costs ~4x less than DPR 2. */
  useEffect(() => {
    const canvas = canvasRef.current;
    if (!canvas) return;
    let t: ReturnType<typeof setTimeout>;
    const resize = () => {
      const w = Math.floor(window.innerWidth);
      const h = Math.floor(window.innerHeight);
      if (canvas.width !== w || canvas.height !== h) {
        canvas.width = w;
        canvas.height = h;
      }
    };
    const debounced = () => {
      clearTimeout(t);
      t = setTimeout(resize, 120);
    };
    resize();
    window.addEventListener('resize', debounced);
    return () => {
      window.removeEventListener('resize', debounced);
      clearTimeout(t);
      if (rafRef.current) cancelAnimationFrame(rafRef.current);
      rafRef.current = 0;
    };
  }, []);

  const easeFunc = useCallback((t: number) => {
    switch (opts.current.easing) {
      case 'linear':
        return t;
      case 'ease-in':
        return t * t;
      case 'ease-in-out':
        return t < 0.5 ? 2 * t * t : -1 + (4 - 2 * t) * t;
      default:
        return t * (2 - t);
    }
  }, []);

  /* Event-driven loop: runs only while sparks are alive, idles at zero cost otherwise. */
  const draw = useCallback(
    (timestamp: number) => {
      const canvas = canvasRef.current;
      const ctx = canvas?.getContext('2d');
      if (!canvas || !ctx) {
        rafRef.current = 0;
        return;
      }
      const o = opts.current;
      ctx.clearRect(0, 0, canvas.width, canvas.height);

      sparksRef.current = sparksRef.current.filter((spark: Spark) => {
        const elapsed = timestamp - spark.startTime;
        if (elapsed >= o.duration) return false;
        const eased = easeFunc(elapsed / o.duration);
        const distance = eased * o.sparkRadius * o.extraScale;
        const lineLength = o.sparkSize * (1 - eased);
        const x1 = spark.x + distance * Math.cos(spark.angle);
        const y1 = spark.y + distance * Math.sin(spark.angle);
        const x2 = spark.x + (distance + lineLength) * Math.cos(spark.angle);
        const y2 = spark.y + (distance + lineLength) * Math.sin(spark.angle);
        ctx.strokeStyle = o.sparkColor;
        ctx.lineWidth = 2;
        ctx.beginPath();
        ctx.moveTo(x1, y1);
        ctx.lineTo(x2, y2);
        ctx.stroke();
        return true;
      });

      if (sparksRef.current.length > 0) {
        rafRef.current = requestAnimationFrame(draw);
      } else {
        rafRef.current = 0;
        ctx.clearRect(0, 0, canvas.width, canvas.height);
      }
    },
    [easeFunc]
  );

  const kick = useCallback(() => {
    if (!rafRef.current) rafRef.current = requestAnimationFrame(draw);
  }, [draw]);

  const handleClick = (e: React.MouseEvent<HTMLDivElement>): void => {
    const now = performance.now();
    const n = opts.current.sparkCount;
    for (let i = 0; i < n; i++) {
      sparksRef.current.push({ x: e.clientX, y: e.clientY, angle: (2 * Math.PI * i) / n, startTime: now });
    }
    kick();
  };

  return (
    <div className="relative w-full h-full" onClick={handleClick}>
      <canvas ref={canvasRef} className="pointer-events-none fixed inset-0 z-[60]" />
      {children}
    </div>
  );
};

export default ClickSpark;
