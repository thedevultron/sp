import { useEffect, useState } from 'react';
import { ArrowUpRight } from 'lucide-react';
import { APP_NAME, SITE_VERSION } from '../../site';

export default function TopNav({ onTour, touring }: { onTour: () => void; touring: boolean }) {
  const [scrolled, setScrolled] = useState(false);
  useEffect(() => {
    const f = () => setScrolled(window.scrollY > 30);
    f();
    window.addEventListener('scroll', f, { passive: true });
    return () => window.removeEventListener('scroll', f);
  }, []);
  const go = (e: React.MouseEvent, id: string) => {
    e.preventDefault();
    document.getElementById(id)?.scrollIntoView({ behavior: 'smooth' });
  };
  return (
    <header className={`site-header${scrolled ? ' is-scrolled' : ''}`}>
      <div className="nav-inner">
        <a href="#overview" onClick={(e) => go(e, 'overview')} style={{ display: 'flex', alignItems: 'center', gap: 10, textDecoration: 'none', color: 'inherit' }}>
          <svg width="26" height="26" viewBox="0 0 32 32"><rect width="32" height="32" rx="8" fill="#0d1120" stroke="rgba(182,217,252,.2)" /><g fill="#b6d9fc"><rect x="7" y="12" width="2.6" height="8" rx="1.3" /><rect x="11.2" y="8" width="2.6" height="16" rx="1.3" /><rect x="15.4" y="11" width="2.6" height="10" rx="1.3" /><rect x="19.6" y="7" width="2.6" height="18" rx="1.3" /><rect x="23.8" y="13" width="2.6" height="6" rx="1.3" /></g></svg>
          <span className="font-display" style={{ fontWeight: 700, letterSpacing: '-0.02em' }}>{APP_NAME}</span>
          <span className="font-mono2" style={{ fontSize: 10, border: '1px solid rgba(182,217,252,.25)', borderRadius: 999, padding: '2px 8px', color: '#b6d9fc' }}>{SITE_VERSION}</span>
        </a>
        <nav className="nav-links" style={{ display: 'flex', gap: 26, fontSize: 13.5, color: '#aab3cc' }}>
          {[['How it works', 'how-it-works'], ['Features', 'features'], ['Why', 'why'], ['Privacy', 'privacy']].map(([l, id]) => (
            <a key={id} href={`#${id}`} onClick={(e) => go(e, id)} style={{ color: 'inherit', textDecoration: 'none' }}>{l}</a>
          ))}
        </nav>
        <div style={{ display: 'flex', alignItems: 'center', gap: 10 }}>
          <span className="font-mono2" style={{ fontSize: 11, color: '#8b93b0', display: 'flex', alignItems: 'center', gap: 7 }}>
            <span style={{ width: 7, height: 7, borderRadius: '50%', background: '#3ddc84', boxShadow: '0 0 12px #3ddc84' }} />Free. Forever.
          </span>
          <button onClick={onTour} className="btn-ghost" style={{ padding: '10px 18px', fontSize: 13 }}>
            {touring ? 'Stop tour' : 'Cinematic tour'}
          </button>
          <a href="#finale" onClick={(e) => go(e, 'finale')} className="btn-primary" style={{ padding: '10px 18px', fontSize: 13 }}>
            Get {APP_NAME}<ArrowUpRight size={14} />
          </a>
        </div>
      </div>
    </header>
  );
}
