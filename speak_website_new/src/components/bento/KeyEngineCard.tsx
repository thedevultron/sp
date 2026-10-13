import { Check, KeyRound } from 'lucide-react';
import { CardShell } from './CardShell';
import { PILLARS } from './pillars';

export default function KeyEngineCard() {
  const p = PILLARS[2];
  return (
    <CardShell
      icon={<KeyRound size={18} />}
      tag={p.tag}
      title={p.title}
      text={p.text}
      foot={p.foot}
      visual={
        <div className="vox-static-keys">
          <span>
            <KeyRound size={13} />
            Primary key<i className="status-dot" />
          </span>
          <span className="vox-key-dim">
            <KeyRound size={13} />
            Backup key
            <Check size={11} />
          </span>
        </div>
      }
    />
  );
}
