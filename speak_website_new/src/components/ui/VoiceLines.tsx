import { useReducedMotion } from 'motion/react';

type VoiceLinesProps = {
  bars?: number;
  className?: string;
  /** bar color — defaults to the blue accent */
  color?: string;
  height?: number;
  label?: string;
};

/**
 * VoiceLines — the cinematic "speaking lines" motif.
 * A row of vertical bars animating like live speech. Transform-only,
 * paused under reduced motion. Used in the loader, dividers and scroll cues.
 */
export default function VoiceLines({ bars = 28, className = '', color, height = 44, label }: VoiceLinesProps) {
  const reduced = useReducedMotion();
  const list = Array.from({ length: bars }, (_, i) => i);
  return (
    <span
      className={`voice-lines${reduced ? ' is-static' : ''} ${className}`}
      role="img"
      aria-label={label ?? 'Speaking waveform'}
      style={{ height, ['--voice-color' as string]: color ?? 'var(--color-acid-lime)' }}
    >
      {list.map((i) => (
        <i key={i} style={{ animationDelay: `${(i % 14) * 0.09}s`, animationDuration: `${0.9 + ((i * 37) % 50) / 100}s` }} />
      ))}
    </span>
  );
}
