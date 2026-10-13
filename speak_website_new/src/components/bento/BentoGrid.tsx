import { useRef } from 'react';
import { motion, useReducedMotion } from 'motion/react';
import GlowCard from './GlowCard';
import VoiceDictationCard from './VoiceDictationCard';
import VisionCompanionCard from './VisionCompanionCard';
import KeyEngineCard from './KeyEngineCard';
import ContextCard from './ContextCard';
import CustomActionsCard from './CustomActionsCard';
import RefineCard from './RefineCard';
import { PILLARS } from './pillars';

const CARDS = [VoiceDictationCard, VisionCompanionCard, KeyEngineCard, ContextCard, CustomActionsCard, RefineCard];

/** Pointer reach (px) for the cross-card bridge glow written to each cell. */
const BRIDGE_RADIUS = 380;

/**
 * Custom varied bento grid. One animation only: ReactBits border-glow (GlowCard),
 * plus a grid-level proximity tracker — hover one card and the violet light
 * spills over the gaps onto its neighbors' borders. Card bodies stay static.
 */
export default function BentoGrid() {
  const reduced = useReducedMotion();
  const cellRefs = useRef<Array<HTMLDivElement | null>>([]);
  const rafRef = useRef(0);
  const pointer = useRef({ x: -9999, y: -9999 });

  const applyProximity = () => {
    rafRef.current = 0;
    for (const el of cellRefs.current) {
      if (!el) continue;
      const r = el.getBoundingClientRect();
      const cx = Math.max(r.left, Math.min(pointer.current.x, r.right));
      const cy = Math.max(r.top, Math.min(pointer.current.y, r.bottom));
      const dist = Math.hypot(pointer.current.x - cx, pointer.current.y - cy);
      const p = Math.max(0, 1 - dist / BRIDGE_RADIUS);
      el.style.setProperty('--grid-glow', p.toFixed(3));
      el.style.setProperty('--bridge-x', `${(((pointer.current.x - r.left) / r.width) * 100).toFixed(2)}%`);
      el.style.setProperty('--bridge-y', `${(((pointer.current.y - r.top) / r.height) * 100).toFixed(2)}%`);
    }
  };

  const clearProximity = () => {
    for (const el of cellRefs.current) {
      if (!el) continue;
      el.style.setProperty('--grid-glow', '0');
    }
  };

  return (
    <div
      className="vox-bento-grid"
      onPointerMove={(e) => {
        if (reduced) return;
        pointer.current = { x: e.clientX, y: e.clientY };
        if (!rafRef.current) rafRef.current = requestAnimationFrame(applyProximity);
      }}
      onPointerLeave={() => {
        pointer.current = { x: -9999, y: -9999 };
        if (rafRef.current) cancelAnimationFrame(rafRef.current);
        rafRef.current = 0;
        clearProximity();
      }}
    >
      {CARDS.map((Card, i) => (
        <motion.div
          key={PILLARS[i].key}
          ref={(el) => { cellRefs.current[i] = el; }}
          className={`vox-bento-cell ${PILLARS[i].span}`}
          initial={{ opacity: 0, y: reduced ? 0 : 26 }}
          whileInView={{ opacity: 1, y: 0 }}
          viewport={{ once: true, margin: '-60px' }}
          transition={{ duration: 0.7, delay: reduced ? 0 : (i % 3) * 0.09, ease: [0.22, 1, 0.36, 1] }}
        >
          <GlowCard className="vox-bento-glow">
            <Card />
          </GlowCard>
        </motion.div>
      ))}
    </div>
  );
}
