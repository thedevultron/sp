import { Gauge } from 'lucide-react';
import { CardShell } from './CardShell';
import { PILLARS } from './pillars';

const SEGMENTS = 28;
const FILLED = 8;

export default function ContextCard() {
  const p = PILLARS[3];
  return (
    <CardShell
      icon={<Gauge size={18} />}
      tag={p.tag}
      title={p.title}
      text={p.text}
      foot={p.foot}
      visual={
        <div className="vox-static-meter">
          <div className="vox-meter-row">
            <span>Session context</span>
            <span>
              18,420 <em>/ 128k</em>
            </span>
          </div>
          <div className="vox-meter-segs">
            {Array.from({ length: SEGMENTS }, (_, i) => (
              <i key={i} className={i < FILLED ? 'filled' : ''} />
            ))}
          </div>
          <span className="vox-meter-ok">
            <span className="status-dot" />
            Plenty of room to think
          </span>
        </div>
      }
    />
  );
}
