import { motion, useReducedMotion } from 'motion/react';

// Deterministic staggered-char entrance (no scroll measuring, no font
// measuring): each glyph animates on its own as it scrolls into view,
// exactly once. Motion clears transforms at rest, so gradient-clipped
// text stays pixel-perfect.
export default function CharStagger({ text, className = '', charClassName = '', delay = 0, step = 0.035, duration = 0.8 }: {
  text: string; className?: string; charClassName?: string; delay?: number; step?: number; duration?: number;
}) {
  const chars = Array.from(text);
  const reduce = useReducedMotion();
  if (reduce) {
    return (
      <span className={className} style={{ whiteSpace: 'pre-wrap' }}>
        <span className="sr-only">{text}</span>
        {chars.map((c, i) => (
          <span key={i} aria-hidden="true" className={charClassName}>
            {c}
          </span>
        ))}
      </span>
    );
  }
  return (
    <span className={className}>
      <span className="sr-only">{text}</span>
      {chars.map((c, i) => (
        <motion.span
          key={i}
          aria-hidden="true"
          className={charClassName}
          initial={{ opacity: 0, y: 48 }}
          whileInView={{ opacity: 1, y: 0 }}
          viewport={{ once: true, margin: '-80px' }}
          transition={{ duration, delay: delay + i * step, ease: [0.22, 1, 0.36, 1] }}
        >
          {c === ' ' ? ' ' : c}
        </motion.span>
      ))}
    </span>
  );
}
