import CountUp from "../CountUp";

/** Proof metric: real React Bits CountUp + suffix. Fires once in view. */
export function ProofMetric({
  to,
  suffix = "",
  className = "",
}: {
  to: number;
  suffix?: string;
  className?: string;
}) {
  return (
    <span className={`tabular-nums ${className}`}>
      <CountUp to={to} duration={1.6} />
      {suffix}
    </span>
  );
}
