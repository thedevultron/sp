import { SlidersHorizontal, Sparkles } from 'lucide-react';
import { CardShell } from './CardShell';
import { PILLARS } from './pillars';

export default function CustomActionsCard() {
  const p = PILLARS[4];
  return (
    <CardShell
      icon={<SlidersHorizontal size={18} />}
      tag={p.tag}
      title={p.title}
      text={p.text}
      foot={p.foot}
      visual={
        <div className="vox-static-actions">
          <span>
            <Sparkles size={11} />
            summarize
          </span>
          <span className="vox-action-dim">elaborate</span>
          <span className="vox-action-dim">polish</span>
        </div>
      }
    />
  );
}
