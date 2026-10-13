import { useRef, type ReactNode, type ButtonHTMLAttributes } from 'react';
import { motion, useReducedMotion } from 'motion/react';
import { Download } from 'lucide-react';

export function EyebrowLabel({ children }: { children: ReactNode }) { return <div className="eyebrow"><span />{children}<span /></div>; }
export function KeyCap({ children }: { children: ReactNode }) { return <kbd>{children}</kbd>; }
export function WaveLogo({ small = false }: { small?: boolean }) {
  // Minimal Linear mark: 5 blue bars.
  return <span className={`wave-logo ${small ? 'small' : ''}`} aria-hidden="true">{[10, 18, 26, 16, 10].map((h, i) => <i key={i} style={{ height: h }} />)}</span>;
}
export function VoidVioletButton({ children, ...props }: ButtonHTMLAttributes<HTMLButtonElement>) {
  return <button {...props} className={`button primary ${props.className || ''}`}><Download size={15} />{children}</button>;
}
export function GhostPillButton({ children, ...props }: ButtonHTMLAttributes<HTMLButtonElement>) {
  return <button {...props} className={`button ghost ${props.className || ''}`}>{children}</button>;
}
export function Reveal({ children, className = '', delay = 0 }: { children: ReactNode; className?: string; delay?: number }) {
  const reduced = useReducedMotion();
  if (reduced) return <div className={className}>{children}</div>;
  // Cinematic settle: rise + de-blur on one expo-out ease. Transform/opacity/filter only.
  return (
    <motion.div
      className={`cine-blur ${className}`}
      initial={{ opacity: 0, y: 28, filter: 'blur(8px)' }}
      whileInView={{ opacity: 1, y: 0, filter: 'blur(0px)' }}
      viewport={{ once: true, margin: '-64px' }}
      transition={{ duration: 0.9, delay, ease: [0.22, 1, 0.36, 1] }}
    >
      {children}
    </motion.div>
  );
}
export function GlassCard({ children, className = '', interactive = true }: { children: ReactNode; className?: string; interactive?: boolean }) {
  const ref = useRef<HTMLDivElement>(null);
  const reduced = useReducedMotion();
  if (!interactive) return <div ref={ref} className={`glass-card ${className}`}>{children}</div>;
  // Linear: no tilt theatrics. Keep a whisper of pointer light, nothing more.
  return (
    <div
      ref={ref}
      className={`glass-card ${className}`}
      onPointerMove={e => {
        if (!ref.current || reduced) return;
        const r = ref.current.getBoundingClientRect();
        ref.current.style.setProperty('--mouse-x', `${e.clientX - r.left}px`);
        ref.current.style.setProperty('--mouse-y', `${e.clientY - r.top}px`);
      }}
    >
      {children}
    </div>
  );
}
