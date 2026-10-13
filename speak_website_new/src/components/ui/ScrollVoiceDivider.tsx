import { motion, useReducedMotion } from 'motion/react';
import VoiceLines from './VoiceLines';

/**
 * ScrollVoiceDivider — a cinematic breath between sections.
 * Hairline rules draw outward while the speaking lines keep a quiet
 * pulse. The whole strip drifts + settles as it enters.
 */
export default function ScrollVoiceDivider({ caption = 'LIVE · IN FLOW' }: { caption?: string }) {
  const reduced = useReducedMotion();
  return (
    <motion.div
      className="voice-divider"
      aria-hidden="true"
      initial={reduced ? { opacity: 0 } : { opacity: 0, y: 24 }}
      whileInView={reduced ? { opacity: 1 } : { opacity: 1, y: 0 }}
      viewport={{ once: true, margin: '-80px' }}
      transition={{ duration: 0.9, ease: [0.22, 1, 0.36, 1] }}
    >
      <motion.span
        className="voice-divider-rule"
        initial={reduced ? {} : { scaleX: 0 }}
        whileInView={reduced ? {} : { scaleX: 1 }}
        viewport={{ once: true, margin: '-80px' }}
        transition={{ duration: 1.2, ease: [0.22, 1, 0.36, 1] }}
      />
      <span className="voice-divider-core">
        <VoiceLines bars={22} height={30} label="Voice activity" />
        <em>{caption}</em>
      </span>
      <motion.span
        className="voice-divider-rule"
        initial={reduced ? {} : { scaleX: 0 }}
        whileInView={reduced ? {} : { scaleX: 1 }}
        viewport={{ once: true, margin: '-80px' }}
        transition={{ duration: 1.2, ease: [0.22, 1, 0.36, 1] }}
      />
    </motion.div>
  );
}
