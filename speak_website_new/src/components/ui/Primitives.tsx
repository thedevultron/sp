import { useRef, type ReactNode, type ButtonHTMLAttributes } from 'react';
import { motion, useReducedMotion } from 'framer-motion';
import { Download } from 'lucide-react';

export function EyebrowLabel({ children }: { children: ReactNode }) { return <div className="eyebrow"><span />{children}<span /></div>; }
export function KeyCap({ children }: { children: ReactNode }) { return <kbd>{children}</kbd>; }
export function WaveLogo({ small = false }: { small?: boolean }) { return <span className={`wave-logo ${small ? 'small' : ''}`} aria-hidden="true">{[12, 23, 32, 21, 12].map((h, i) => <i key={i} style={{ height: h }} />)}</span>; }
export function VoidVioletButton({ children, ...props }: ButtonHTMLAttributes<HTMLButtonElement>) { return <button {...props} className={`button primary ${props.className || ''}`}><Download size={16} />{children}</button>; }
export function GhostPillButton({ children, ...props }: ButtonHTMLAttributes<HTMLButtonElement>) { return <button {...props} className={`button ghost ${props.className || ''}`}>{children}</button>; }
export function Reveal({ children, className = '', delay = 0 }: { children: ReactNode; className?: string; delay?: number }) { const reduced = useReducedMotion(); return <motion.div className={className} initial={{ opacity: 0, y: reduced ? 0 : 24 }} whileInView={{ opacity: 1, y: 0 }} viewport={{ once: true, margin: '-40px' }} transition={{ duration: .7, delay, ease: [.22, 1, .36, 1] }}>{children}</motion.div>; }
export function GlassCard({ children, className = '' }: { children: ReactNode; className?: string }) {
  const ref = useRef<HTMLDivElement>(null);
  const reduced = useReducedMotion();
  return <div ref={ref} className={`glass-card ${className}`} onPointerMove={e => { if (!ref.current || reduced) return; const r = ref.current.getBoundingClientRect(); ref.current.style.setProperty('--mouse-x', `${e.clientX-r.left}px`); ref.current.style.setProperty('--mouse-y', `${e.clientY-r.top}px`); ref.current.style.transform = `perspective(1200px) rotateX(${-(e.clientY-r.top-r.height/2)/160}deg) rotateY(${(e.clientX-r.left-r.width/2)/160}deg)`; }} onPointerLeave={() => { if(ref.current) ref.current.style.transform = ''; }}>{children}</div>;
}
