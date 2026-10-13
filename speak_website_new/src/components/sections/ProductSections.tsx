import { ArrowUpRight, AudioLines, Check, KeyRound, Keyboard, Layers, LockKeyhole, Monitor, ShieldCheck, Smartphone, Wallet, Cpu, Combine } from 'lucide-react';
import { motion, useReducedMotion } from 'motion/react';
import { EyebrowLabel, GlassCard, GhostPillButton, KeyCap, Reveal, VoidVioletButton, WaveLogo } from '../ui/Primitives';
import SpeakCapsuleWidget from '../widget/SpeakCapsuleWidget';
import BlurText from '../BlurText';
import CharStagger from '../ui/CharStagger';
import BentoGrid from '../bento/BentoGrid';
import LiveTypingPlayground from '../simulator/LiveTypingPlayground';
import { DOCS_HASH, SITE_VERSION, GITHUB_REPO_URL, GITHUB_INSTALLER_DOWNLOAD_URL } from '../../site';

type DemoState = { active: boolean; text: string; progress: number };
type ModalType = 'settings' | 'guide' | 'download' | 'support' | null;

export function HeroSection({ demo, onModal }: { demo: DemoState; onModal: (type: ModalType) => void }) {
  const reduced = useReducedMotion();
  return (
    <section className="hero" id="overview">
      <div className="hero-content">
        <div className="hero-copy">
        <Reveal>
          <EyebrowLabel>VOXULA AI <span className="version-tag">{SITE_VERSION.toUpperCase()}</span></EyebrowLabel>
        </Reveal>
        <Reveal delay={0.08}>
          <h1>
            <CharStagger text="Your Voice." className="hero-split" charClassName="hero-char" delay={0.05} step={0.03} />
            <br /> <CharStagger text="Everywhere." className="hero-split" charClassName="hero-char" delay={0.28} step={0.03} />
          </h1>
        </Reveal>
        <Reveal delay={0.16}>
          <p className="hero-description">
            Press <span className="inline-hotkey">Ctrl + Space</span> to type into any app. Sub-second, private, free.
          </p>
        </Reveal>
        <Reveal className="hero-ctas" delay={0.22}>
          <VoidVioletButton onClick={() => onModal('download')}>Download for Windows <span className="button-divider" /><span className="free-label">It’s free</span></VoidVioletButton>
          <GhostPillButton onClick={() => document.getElementById('simulator')?.scrollIntoView({ behavior: reduced ? 'auto' : 'smooth' })}>Launch web simulator<ArrowUpRight size={15} /></GhostPillButton>
        </Reveal>
        <Reveal delay={0.26}>
          <div className="hero-meta"><span><Monitor size={12} />Native Windows 11</span><i /><span>Free tier included</span><i /><span>Bring your own key</span></div>
        </Reveal>
        </div>
        <div className="hero-product">
          <motion.div
            className="hero-product-cine"
            initial={reduced ? { opacity: 0 } : { opacity: 0, y: 48, scale: 0.97, filter: 'blur(10px)' }}
            whileInView={reduced ? { opacity: 1 } : { opacity: 1, y: 0, scale: 1, filter: 'blur(0px)' }}
            viewport={{ once: true, margin: '-80px' }}
            transition={{ duration: 1.1, delay: 0.3, ease: [0.22, 1, 0.36, 1] }}
          >
            <div className="product-caption"><span className="caption-line" />VOXULA CAPSULE — LIVE<span className="caption-line" /></div>
            <SpeakCapsuleWidget {...demo} onSettings={() => onModal('settings')} onGuide={() => onModal('guide')} />
            <div className="capsule-under">
              <span><LockKeyhole size={11} />Private by design</span>
              <span className="product-shortcut"><KeyCap>ctrl</KeyCap><span>+</span><KeyCap>space</KeyCap><span>and you’re in flow.</span></span>
              <span>Sub-second latency</span>
            </div>
          </motion.div>
        </div>
        <Reveal className="compatibility" delay={0.1}>
          <span className="compatibility-label">WORKS WHERE YOU WORK</span>
          <div className="marquee-band">
            <div className="app-brands" style={{ padding: '20px 0' }}>
              <span>VS Code</span><span>Slack</span><span>Notion</span><span>Word</span><span>Any app</span>
            </div>
          </div>
        </Reveal>
        {!reduced && (
          <div className="scroll-cue" aria-hidden="true"><em>SCROLL</em><span className="scroll-cue-line"><i /></span></div>
        )}
      </div>
    </section>
  );
}

export function PipelineSection() {
  const steps = [
    { icon: KeyRound, title: 'Bring a key. We’ll find it.', text: 'Auto-detects GEMINI_API_KEY or your saved vault key, with a free-tier fallback. Keys stay on your device.', detail: '01 / CONNECT' },
    { icon: Keyboard, title: 'One shortcut. Any app.', text: 'Press Ctrl + Space. Voxula appears over your active window with a live transcript — without stealing focus.', detail: '02 / SUMMON' },
    { icon: AudioLines, title: 'Speak at the speed of thought.', text: 'Words stream to your cursor sub-second. Say “refine” and the session rewrites itself in place.', detail: '03 / FLOW' },
  ];
  return (
    <section className="section pipeline-section" id="how-it-works">
      <Reveal><EyebrowLabel>HOW IT WORKS</EyebrowLabel><BlurText as="h2" text="Instant execution. Zero friction." animateBy="words" delay={90} stepDuration={0.35} className="h2-look" /><p className="section-intro">From a thought to the page, in less than a second.</p></Reveal>
      <div className="pipeline-grid">{steps.map((s, i) => <Reveal key={s.title} delay={i * 0.08} className="pipeline-step"><div className="step-icon"><s.icon size={20} /><span>{i + 1}</span></div><span className="step-detail">{s.detail}</span><h3>{s.title}</h3><p>{s.text}</p></Reveal>)}</div>
    </section>
  );
}

export function SimulatorSection({ onUpdate }: { onUpdate: (s: DemoState) => void }) {
  return (
    <section className="section simulator-section" id="simulator">
      <Reveal>
        <div className="section-heading-row">
          <div><div className="left-eyebrow"><span />TRY IT HERE</div><BlurText text="Less typing. More momentum." animateBy="words" delay={90} stepDuration={0.35} className="h2-look left-look" /></div>
          <p>Dictate it raw, then say refine and watch the session rewrite itself.</p>
        </div>
      </Reveal>
      <Reveal><LiveTypingPlayground onUpdate={onUpdate} /></Reveal>
    </section>
  );
}

export function BentoPillarsSection() {
  return (
    <section className="section bento-section" id="features">
      <Reveal><EyebrowLabel>FEATURES</EyebrowLabel><BlurText as="h2" text="Quietly powerful." animateBy="words" delay={90} stepDuration={0.35} className="h2-look" /><p className="section-intro">Six capabilities. One shortcut. Say <strong>refine</strong>, <strong>polish</strong>, or <strong>elaborate</strong> — the session rewrites itself. Full guide in <a href={DOCS_HASH} style={{ textDecoration: 'underline' }}>Docs</a>.</p></Reveal>
      <BentoGrid />
    </section>
  );
}

// Removed per brief — the mid-page ray wash. Kept as null so old imports don't break.
export function MidRaysDivider() {
  return null;
}

export function ExpandShowcaseSection({ onModal }: { onModal: (m: ModalType) => void }) {
  const reduced = useReducedMotion();
  return (
    <section className="section expand-section" id="showcase">
      <Reveal>
        <motion.div
          className="expand-cta"
          initial={reduced ? { opacity: 0 } : { opacity: 0, y: 32, scale: 0.98 }}
          whileInView={reduced ? { opacity: 1 } : { opacity: 1, y: 0, scale: 1 }}
          viewport={{ once: true, margin: '-80px' }}
          transition={{ duration: 0.9, ease: [0.22, 1, 0.36, 1] }}
        >
          <span className="mini-eyebrow">VOXULA AI IN ACTION</span>
          <h3>Say it. Consider it done.</h3>
          <p>Dictate raw. Say refine. Ship polished.</p>
          <button className="button primary" onClick={() => onModal('download')}>Get Voxula AI<ArrowUpRight size={15} /></button>
        </motion.div>
      </Reveal>
    </section>
  );
}

export function AboutSection() {
  return (
    <section className="section about-section" id="about">
      <Reveal><EyebrowLabel>WHY VOXULA EXISTS</EyebrowLabel><BlurText as="h2" text="Built because the alternatives cost too much." animateBy="words" delay={90} stepDuration={0.35} className="h2-look" /><p className="section-intro">Subscription voice tools or CPU-hungry local models. Voxula is neither — one free, featherweight Windows app.</p></Reveal>
      <Reveal>
        <GlassCard className="docs-card" interactive={false}>
          <p>Great voice tools either charge monthly or hog the CPU running local models. Voxula AI is an always-on voice copilot <strong>and</strong> sub-second dictation in one tray app that idles quietly until you call it. Bring a free key. That is the whole business model.</p>
          <div className="guide-steps">
            <div><span><Wallet size={16} /></span><section><h3>No subscriptions.</h3><p>Voice should not cost monthly. Free tier included.</p></section></div>
            <div><span><Cpu size={16} /></span><section><h3>Sips CPU.</h3><p>No heavy local models. Cloud transcription, tray-idle footprint.</p></section></div>
            <div><span><Combine size={16} /></span><section><h3>Copilot plus dictation.</h3><p>A screen-seeing assistant and instant typer in one flow.</p></section></div>
          </div>
        </GlassCard>
      </Reveal>
    </section>
  );
}

export function HotkeysSecuritySection() {
  const shortcuts = [
    { keys: ['Ctrl', 'Space'], name: 'Global dictation', sub: 'Your voice, typed wherever your cursor is.' },
    { keys: ['Win', 'Shift'], name: 'Screen companion', sub: 'Voice + live screen, together.' },
    { keys: ['Ctrl', 'Win'], name: 'Fresh start', sub: 'Purge transcript and token counter.' },
    { keys: ['Esc'], name: 'Back to focus', sub: 'Clear the canvas and dismiss to tray.' },
  ];
  return (
    <section className="section security-section" id="privacy">
      <Reveal><EyebrowLabel>PRIVACY</EyebrowLabel><BlurText as="h2" text="Your words are yours." animateBy="words" delay={90} stepDuration={0.35} className="h2-look" /><p className="section-intro">Local DPAPI encryption. Zero telemetry. No compromises.</p></Reveal>
      <Reveal>
        <div className="security-layout">
          <div className="privacy-visual">
            <div className="lock-disc"><LockKeyhole size={28} /></div>
            <span className="encrypted-label"><ShieldCheck size={12} />ON-DEVICE ENCRYPTION</span>
            <span className="privacy-caption">Never our data.<br />Always your voice.</span>
          </div>
          <div className="hotkey-list">
            <div className="hotkey-label"><Keyboard size={14} />BUILT INTO MUSCLE MEMORY</div>
            {shortcuts.map(s => <div className="hotkey-row" key={s.name}><div><strong>{s.name}</strong><p>{s.sub}</p></div><div className="key-group">{s.keys.map((k, i) => <span key={k}>{i > 0 && <em style={{ color: '#62666d', margin: '0 4px' }}>+</em>}<KeyCap>{k}</KeyCap></span>)}</div></div>)}
          </div>
        </div>
      </Reveal>
      <div className="security-pillars">
        {[
          { icon: LockKeyhole, title: 'Your keys. Under lock.', text: 'Windows Credential Manager encrypts API keys locally with DPAPI.' },
          { icon: ShieldCheck, title: 'Direct line. No middleman.', text: 'Encrypted connection straight to the voice service. No tracking.' },
          { icon: Layers, title: 'Almost invisible.', text: 'Idles quietly in your tray until inspiration strikes.' },
        ].map((p, i) => <Reveal delay={i * 0.08} key={p.title}><p.icon size={18} /><h3>{p.title}</h3><p>{p.text}</p></Reveal>)}
      </div>
      <Reveal><p className="section-intro" style={{ marginTop: 24 }}>Voice refine triggers: <strong>refine</strong> · <strong>polish</strong> · <strong>elaborate</strong> (plus <strong>expand</strong> alias and up to 3 custom actions in Settings → Refine).</p></Reveal>
    </section>
  );
}

export function DownloadFooterSection({ onModal, onChat }: { onModal: (m: ModalType) => void; onChat?: () => void }) {
  return (
    <>
      <section className="section download-section" id="download">
        <Reveal>
          <GlassCard className="download-card" interactive={false}>
            <div className="download-logo"><WaveLogo /></div>
            <EyebrowLabel>100% FREE. ENTIRELY YOURS.</EyebrowLabel>
            <h2 style={{ marginTop: 16 }}>Find your voice. Get into flow.</h2>
            <p>Less between you and your next great idea.<br />New to Voxula AI? Read the <a href={DOCS_HASH} style={{ textDecoration: 'underline' }}>Docs</a> first.</p>
            <div style={{ marginTop: 22 }}><VoidVioletButton onClick={() => onModal('download')}>Download Voxula AI for Windows<ArrowUpRight size={15} /></VoidVioletButton></div>
            {onChat && <div className="download-ask"><button type="button" className="ask-link" onClick={onChat}>Questions? <span>Ask about Voxula</span></button></div>}
            <div className="download-specs">{SITE_VERSION} <i /> Native x64 <i /> Windows 10 / 11 <i /> Free forever</div>
            <div className="download-checks"><span><Check size={12} />Free key supported</span><span><Check size={12} />No subscription required</span><span><Check size={12} />Unsigned build — if Windows warns, click More info then Run anyway</span></div>
          </GlassCard>
        </Reveal>
        <Reveal>
          <div className="mobile-strip"><span className="mobile-icon"><Smartphone size={20} /></span><div><h3>Your flow doesn’t stop at your desk.</h3><p>Take voice notes on the move with the mobile companion.</p></div><button onClick={() => onModal('guide')}>Explore the companion<ArrowUpRight size={15} /></button></div>
        </Reveal>
      </section>
      <footer>
        <div className="footer-main"><a className="brand" href="#overview"><WaveLogo small />Voxula AI<span className="footer-by">by Amir Bagawan</span></a><div className="footer-links"><a href={DOCS_HASH}>Documentation</a><a href={GITHUB_REPO_URL} target="_blank" rel="noreferrer">GitHub<ArrowUpRight size={12} /></a><a href={GITHUB_INSTALLER_DOWNLOAD_URL} download>Installer (.exe)<ArrowUpRight size={12} /></a><a href="#privacy">Keyboard reference</a><button onClick={() => onModal('support')}>Support<ArrowUpRight size={12} /></button></div></div>
        <div className="footer-bottom"><span>© 2026 Amir Bagawan. Built for speed, privacy, and flow.</span><span className="footer-system"><span className="status-dot" />All systems in flow</span></div>
        <div className="system-requirements">DirectX 11+ · Windows 10 Build 19041+ or Windows 11 · 64-bit</div>
      </footer>
    </>
  );
}
