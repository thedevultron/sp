import { Sparkles } from 'lucide-react';
import { CardShell } from './CardShell';
import { PILLARS } from './pillars';

export default function RefineCard() {
  const p = PILLARS[5];
  return (
    <CardShell
      icon={<Sparkles size={18} />}
      tag={p.tag}
      title={p.title}
      text={p.text}
      foot={p.foot}
      visual={
        <div className="vox-static-refine">
          <span className="vox-refine-before">um, so here’s what I’m thinking...</span>
          <div className="vox-refine-after">
            <Sparkles size={13} />
            <span>A clear idea. Beautifully expressed.</span>
          </div>
        </div>
      }
    />
  );
}
