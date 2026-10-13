import { Monitor, Radio } from 'lucide-react';
import { CardShell } from './CardShell';
import { PILLARS } from './pillars';

export default function VisionCompanionCard() {
  const p = PILLARS[1];
  return (
    <CardShell
      icon={<Monitor size={18} />}
      tag={p.tag}
      title={p.title}
      text={p.text}
      foot={p.foot}
      visual={
        <div className="vox-static-screen">
          <div className="vox-screen">
            <div className="vox-screen-dots">
              <i />
              <i />
              <i />
            </div>
            <span />
            <span />
            <span />
            <div className="vox-screen-focus">
              <span>AI VISION</span>
            </div>
          </div>
          <div className="vox-live-chip">
            <Radio size={11} />
            Live
          </div>
        </div>
      }
    />
  );
}
