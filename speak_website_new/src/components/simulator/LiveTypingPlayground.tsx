import { useCallback, useEffect, useRef, useState } from 'react';
import { ArrowUpRight, Check, Code2, FileText, Hash, Mic, RotateCcw, ShieldCheck, Sparkles, Square, Terminal, Zap } from 'lucide-react';
import { GlassCard, KeyCap } from '../ui/Primitives';
import TickerNumber from '../ui/TickerNumber';
import { WaveformDots } from '../widget/SpeakCapsuleWidget';

type Target = 'VS Code' | 'Slack' | 'Notion';
const scripts: Record<Target, { raw: string; polish: string }> = {
 'VS Code': { raw: '// get the users that are active and sort by name\nconst activeUsers = users\n  .filter(user => user.isActive)\n  .sort((a, b) => a.name.localeCompare(b.name));', polish: '// Return active users, alphabetically by name.\nconst getActiveUsers = (users: User[]): User[] => {\n  return users\n    .filter(({ isActive }) => isActive)\n    .sort((a, b) => a.name.localeCompare(b.name));\n};' },
 'Slack': { raw: 'hey team so the voice integration is ready and um latency is looking really good. can someone take a look at the pull request before we ship tomorrow?', polish: 'Hey team — the voice integration is ready for review.\n\nLatency is consistently under 200ms, and all tests are passing. Please review the pull request before tomorrow’s release.\n\nThanks for helping us ship something great.' },
 'Notion': { raw: 'okay so the idea is to make a voice first workflow and not have to switch apps. we need global shortcuts, live transcription and maybe screen sharing too.', polish: '# A voice-first workflow\n\nBuild a companion that turns thoughts into action, without switching apps.\n\n## Core priorities\n• System-wide keyboard shortcuts\n• Real-time, low-latency transcription\n• Multimodal screen understanding\n\nLess friction. More flow.' }
};
export function AppMockupWindow({ target, text, active }: { target: Target; text: string; active: boolean }) {
 return <div className={`app-window target-${target.replace(' ', '').toLowerCase()}`}><div className="app-titlebar"><div className="window-dots"><i/><i/><i/></div><span>{target === 'VS Code' ? 'workspace / utils.ts' : target === 'Slack' ? 'Acme · #engineering' : 'Personal / Product ideas'}</span><span className="preview-label">LIVE PREVIEW</span></div><div className="app-main"><div className="app-rail">{target === 'VS Code' ? <><FileText/><Code2/><Hash/><Terminal/></> : target === 'Slack' ? <><Hash/><Hash/><Hash/></> : <><FileText/><FileText/></>}</div><div className="editor-area"><div className="editor-tab">{target === 'VS Code' ? <><span className="ts-icon">TS</span>utils.ts<XSmall/></> : target === 'Slack' ? <><Hash size={14}/>engineering</> : <><FileText size={14}/>Product ideas</>}</div>{target === 'VS Code' ? <div className="code-area"><div className="line-numbers">{Array.from({length: 11}, (_, i) => <span key={i}>{i+1}</span>)}</div><pre>{text || '// Your next great idea starts with your voice.\n\n'}<span className={`typing-cursor ${active ? 'is-active' : ''}`}/></pre></div> : <div className="document-area">{target === 'Slack' && <div className="message-author"><div className="avatar">AB</div><strong>Amir</strong><span>Just now</span></div>}<pre>{text || (target === 'Slack' ? 'Your team is one thought away.\nSpeak to start your message…' : '# Your next big idea\n\nSpeak to bring it to life…')}<span className="typing-cursor"/></pre></div>}</div></div><div className="editor-status"><span><Check size={11}/>{active ? 'Receiving voice input' : 'Ready for your voice'}</span><span>{target === 'VS Code' ? 'TypeScript     UTF-8' : 'All changes saved'}<span className="status-dot"/></span></div></div>;
}
function XSmall() { return <span className="tab-x">×</span>; }
export default function LiveTypingPlayground({ onUpdate }: { onUpdate: (s: { active: boolean; text: string; progress: number }) => void }) {
 const [target, setTarget] = useState<Target>('VS Code');
 const [polish, setPolish] = useState(false);
 const [text, setText] = useState('');
 const [active, setActive] = useState(false);
 const [done, setDone] = useState(false);
 const [refined, setRefined] = useState(false);
 const [refineStage, setRefineStage] = useState<null | 'deleting' | 'typing'>(null);
 const timer = useRef<ReturnType<typeof setInterval> | null>(null);
 const refineReady = useRef(false);
 const stop = useCallback(() => { if(timer.current) clearInterval(timer.current); timer.current = null; setActive(false); setRefineStage(null); }, []);
 const reset = useCallback(() => { stop(); setText(''); setDone(false); setRefined(false); }, [stop]);
 const run = useCallback(() => {
  if(active || refineStage) { stop(); return; }
  setText(''); setDone(false); setRefined(false); setActive(true);
  const content = scripts[target][polish ? 'polish' : 'raw']; let index = 0;
  timer.current = setInterval(() => { index += 2; setText(content.slice(0, index)); if(index >= content.length) { stop(); setDone(true); } }, 22);
 }, [active, refineStage, target, polish, stop]);
 // Say "refine" → delete-and-replace, like the native app (measured
 // Backspaces, then the rewrite typed in place — no clipboard, no Ctrl+A).
 const refine = useCallback(() => {
  if(!refineReady.current || active || refineStage) return;
  setRefineStage('deleting');
  const from = scripts[target].raw; const to = scripts[target].polish;
  setText(from);
  let remaining = from.length;
  timer.current = setInterval(() => {
   remaining -= 7;
   if(remaining <= 0) {
    if(timer.current) clearInterval(timer.current);
    setText(''); setRefineStage('typing');
    let index = 0;
    timer.current = setInterval(() => {
     index += 3; setText(to.slice(0, index));
     if(index >= to.length) { stop(); setDone(true); setRefined(true); }
    }, 16);
    return;
   }
   setText(from.slice(0, remaining));
  }, 14);
 }, [active, refineStage, target, stop]);
 const canRefine = done && !polish && !refined && !active && !refineStage && text.length > 0;
 useEffect(() => { refineReady.current = canRefine; }, [canRefine]);
 useEffect(() => { const listener = (e: KeyboardEvent) => { if(e.ctrlKey && e.code === 'Space') { e.preventDefault(); if(document.querySelector('[role="dialog"]')) return; document.getElementById('simulator')?.scrollIntoView({ behavior: 'smooth', block: 'center' }); run(); } if(e.key === 'Escape') stop(); if(e.ctrlKey && e.metaKey) { e.preventDefault(); reset(); } }; window.addEventListener('keydown', listener); return () => window.removeEventListener('keydown', listener); }, [run, stop, reset]);
 // Type the word "refine" anywhere and the session rewrites itself.
 useEffect(() => {
  let buffer = '';
  const listener = (e: KeyboardEvent) => {
   if(e.ctrlKey || e.metaKey || e.altKey) return;
   if(e.key.length !== 1) return;
   if((e.target as HTMLElement)?.tagName === 'INPUT') return;
   buffer = (buffer + e.key.toLowerCase()).slice(-6);
   if(buffer === 'refine') { buffer = ''; refine(); }
  };
  window.addEventListener('keydown', listener);
  return () => window.removeEventListener('keydown', listener);
 }, [refine]);
 useEffect(() => { onUpdate({ active: active || refineStage !== null, text, progress: 12 + text.length / 12 }); }, [active, refineStage, text, onUpdate]);
 useEffect(() => () => { if(timer.current) clearInterval(timer.current); }, []);
 const changeTarget = (t: Target) => { stop(); setTarget(t); setText(''); setDone(false); setRefined(false); };
 const busy = active || refineStage !== null;
 return <GlassCard className="playground"><div className="playground-controls"><div className="live-demo-label"><span className="status-dot"/>INTERACTIVE PLAYGROUND</div><h3>Think it. Say it.<br/>Watch it happen.</h3><p>Your voice, right where your cursor is.<br/>Dictate it messy — then say “refine”.</p><label className="control-label">01 <span>CHOOSE YOUR WORKSPACE</span></label><div className="app-tabs" role="tablist" aria-label="Target application">{(['VS Code', 'Slack', 'Notion'] as Target[]).map(t => <button role="tab" aria-selected={target === t} key={t} onClick={() => changeTarget(t)} className={target === t ? 'selected' : ''}>{t === 'VS Code' ? <Code2 size={14}/> : t === 'Slack' ? <Hash size={14}/> : <FileText size={14}/>}{t}</button>)}</div><label className="control-label">02 <span>MAKE IT YOURS</span></label><button className="polish-control" role="switch" aria-checked={polish} onClick={() => { if(!busy) { setPolish(!polish); setDone(false); setRefined(false); setText(''); } }} disabled={busy}><span><Zap size={14}/>{polish ? 'Auto-refine & polish' : 'Raw transcription'}</span><span className={`toggle ${polish ? 'on' : ''}`}><i/></span></button><button className={`speak-button ${busy ? 'speaking' : ''}`} onClick={run}>{busy ? <Square size={15}/> : <Mic size={16}/>}<span>{refineStage === 'deleting' ? 'Deleting session…' : refineStage === 'typing' ? 'Typing the rewrite…' : active ? 'Listening. Click to stop' : done ? 'Try it again' : 'Press to speak'}</span>{busy ? <WaveformDots active/> : <span className="button-keys"><KeyCap>Ctrl</KeyCap><KeyCap>Space</KeyCap></span>}</button>{canRefine && <button className="speak-button" onClick={refine} aria-label="Say refine to rewrite the session"><Sparkles size={16}/><span>Say “refine” — watch it rewrite</span><span className="button-keys"><KeyCap>refine</KeyCap></span></button>}{refined && <span className="demo-disclaimer"><Check size={10}/> Refined in place — deleted and retyped, just like the native app.</span>}<span className="demo-disclaimer">{refined ? 'Triggers: refine · polish · elaborate (+ expand alias).' : 'Simulated dictation + refine. Your mic stays off.'}</span></div><div className="playground-preview"><div className="preview-top"><span><span className="status-dot"/>{refineStage ? 'Refining your session…' : active ? 'Streaming to your workspace' : refined ? 'Session refined' : 'Your workspace. Supercharged.'}</span><button aria-label="Reset simulator" onClick={() => { reset(); }}><RotateCcw size={14}/></button></div><AppMockupWindow target={target} text={text} active={busy}/><div className="telemetry"><span><Zap size={12}/><b><TickerNumber to={busy || done ? 142 : 180}/><small>ms</small></b> latency</span><span><Mic size={12}/><b>16<small>kHz</small></b> live audio</span><span><ShieldCheck size={12}/>DPAPI encrypted</span></div><div className="simulation-note">Illustrative performance · Native app uses the AI Engine <ArrowUpRight size={11}/></div></div></GlassCard>;
}
