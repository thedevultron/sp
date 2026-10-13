import type { ReactNode } from 'react';
import { ArrowUpRight } from 'lucide-react';

export function CardShell({
  icon,
  tag,
  title,
  text,
  foot,
  visual,
}: {
  icon: ReactNode;
  tag: string;
  title: string;
  text: string;
  foot: string;
  visual: ReactNode;
}) {
  return (
    <article className="vox-card">
      <div className="vox-card-top">
        <span className="vox-card-icon">{icon}</span>
        <span className="vox-card-tag">{tag}</span>
        <ArrowUpRight size={14} className="vox-card-arrow" aria-hidden="true" />
      </div>
      <div className="vox-card-visual" aria-hidden="true">
        {visual}
      </div>
      <h3>{title}</h3>
      <p>{text}</p>
      <div className="vox-card-foot">
        <span>{foot}</span>
        <span className="vox-card-plus">+</span>
      </div>
    </article>
  );
}
