import type { ReactNode } from 'react';
import { motion, useReducedMotion } from 'motion/react';

/**
 * SectionTransition — Linear film-cut.
 * A 1px graphite hairline draws across, then content settles with
 * rise + de-blur on a shared expo-out ease. No glow, no violet.
 */
export default function SectionTransition({
  children,
  beam = false,
}: {
  children: ReactNode;
  beam?: boolean;
}) {
  const reduced = useReducedMotion();
  return (
    <div className="section-handoff">
      {beam && !reduced && (
        <motion.span
          className="handoff-beam"
          aria-hidden="true"
          initial={{ scaleX: 0, opacity: 0 }}
          whileInView={{ scaleX: 1, opacity: 0.6 }}
          viewport={{ once: true, margin: '-72px' }}
          transition={{ duration: 1.2, ease: [0.22, 1, 0.36, 1] }}
        />
      )}
      {beam && reduced && <span className="handoff-beam is-static" aria-hidden="true" />}
      <motion.div
        className="handoff-body"
        initial={reduced ? { opacity: 0 } : { opacity: 0, y: 32, filter: 'blur(8px)' }}
        whileInView={reduced ? { opacity: 1 } : { opacity: 1, y: 0, filter: 'blur(0px)' }}
        viewport={{ once: true, margin: '-48px' }}
        transition={{ duration: reduced ? 0.3 : 0.9, ease: [0.22, 1, 0.36, 1] }}
      >
        {children}
      </motion.div>
    </div>
  );
}
