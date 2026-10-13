import { useEffect, useState } from 'react';
import { Settings, BookOpen, X, ChevronDown, Monitor, Mic, ArrowUpRight } from 'lucide-react';
import { AnimatePresence, motion } from 'motion/react';
import { GhostPillButton } from '../ui/Primitives';

export function WaveformDots({ active = false }: { active?: boolean }) { return <span role="img" className={`waveform-dots ${active ? 'active' : ''}`} aria-label={active ? 'Listening' : 'Microphone ready'}>{[0,1,2,3,4].map(i => <i key={i} style={{ animationDelay: `${i * .13}s` }} />)}</span>; }
export function SmartTokenBar({ progress = 12 }: { progress?: number }) { return <div className="token-track" tabIndex={0} aria-label={`Context usage ${Math.round(progress)} percent`}><span style={{ width: `${progress}%`, background: progress > 90 ? '#ef4444' : progress > 75 ? '#f59e0b' : '#22c55e' }} /><div className="token-tooltip">Tokens: {Math.round(progress * 1280).toLocaleString()} / 128,000 · 180ms</div></div>; }
export default function SpeakCapsuleWidget({ active = false, text = '', progress = 12, onSettings, onGuide }: { active?: boolean; text?: string; progress?: number; onSettings: () => void; onGuide: () => void }) {
  const [open, setOpen] = useState(false);
  const [hidden, setHidden] = useState(false);
  const [vision, setVision] = useState(false);
  useEffect(() => {
    const onEscape = (event: KeyboardEvent) => { if(event.key === 'Escape') { setVision(false); setOpen(false); } };
    window.addEventListener('keydown', onEscape);
    return () => window.removeEventListener('keydown', onEscape);
  }, []);
  if(hidden) return <div className="capsule-restore"><GhostPillButton onClick={() => setHidden(false)}><Mic size={15}/>Show Voxula AI capsule<ArrowUpRight size={14}/></GhostPillButton></div>;
  return <motion.div className={`speak-capsule ${vision ? 'vision-on' : ''}`} initial={{ opacity: 0, y: 30 }} animate={{ opacity: 1, y: 0 }} transition={{ type: 'spring', stiffness: 65, damping: 19, delay: .3 }}>
    <div className="capsule-top"><div className="capsule-status"><span className={`status-dot ${active ? 'listening' : ''}`}/><strong>VOXULA</strong><span className="ready-badge">{active ? 'Live' : 'Ready'}</span></div><WaveformDots active={active}/><div className="capsule-actions"><button aria-label="Settings" onClick={onSettings}><Settings size={13}/><span>Settings</span></button><button aria-label="Guide" onClick={onGuide}><BookOpen size={13}/><span>Guide</span></button><button className="hide-action" aria-label="Hide capsule" onClick={() => setHidden(true)}><X size={13}/><span>Hide</span></button></div></div>
    <SmartTokenBar progress={progress}/>
    <div className="capsule-bottom"><button className="transcript-toggle" aria-expanded={open} onClick={() => setOpen(!open)}><ChevronDown size={13} style={{ transform: open ? 'rotate(180deg)' : '' }}/>Transcript<span className="tiny-dot"/></button><span className="capsule-hint">{vision ? 'Screen vision enabled · demo' : 'Your next thought, one shortcut away.'}</span><button className={`monitor-toggle ${vision ? 'selected' : ''}`} aria-label="Toggle screen vision demo" aria-pressed={vision} onClick={() => setVision(!vision)}><Monitor size={15}/></button></div>
    <AnimatePresence>{open && <motion.div className="transcript-drawer" initial={{ height: 0, opacity: 0 }} animate={{ height: 'auto', opacity: 1 }} exit={{ height: 0, opacity: 0 }}><div><span className="mono">LIVE TRANSCRIPT</span><p>{text || 'Press Ctrl + Space in the simulator below. Your words will appear here, in real time.'}{active && <span className="typing-cursor"/>}</p></div></motion.div>}</AnimatePresence>
    {vision && <div className="vision-corners" aria-hidden="true"><i/><i/><i/><i/></div>}
  </motion.div>;
}
