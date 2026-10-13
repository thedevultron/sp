import { Mic } from 'lucide-react';
import { CardShell } from './CardShell';
import { PILLARS } from './pillars';

const WAVE = [10, 18, 30, 44, 34, 22, 40, 26, 34, 20, 30, 16, 26, 14, 24, 12, 22, 12, 20, 11, 18, 10, 16, 10, 14, 9, 12];

export default function VoiceDictationCard() {
  const p = PILLARS[0];
  return (
    <CardShell
      icon={<Mic size={18} />}
      tag={p.tag}
      title={p.title}
      text={p.text}
      foot={p.foot}
      visual={
        <div className="vox-static-wave">
          <span className="vox-mic-ring">
            <Mic size={15} />
          </span>
          <div className="vox-bars">
            {WAVE.map((h, i) => (
              <i key={i} style={{ height: `${h}px` }} />
            ))}
          </div>
        </div>
      }
    />
  );
}
