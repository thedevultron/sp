import { useEffect, useState } from 'react';
import { ArrowUpRight, BookOpen, Download, KeyRound, Keyboard, LockKeyhole, Monitor, ShieldCheck } from 'lucide-react';
import { EyebrowLabel, GlassCard, KeyCap, Reveal } from '../ui/Primitives';
import ScrollReveal from '../ScrollReveal';
import { GEMINI_KEY_URL, INSTALLER_FILE, INSTALLER_SIZE, SITE_VERSION, GITHUB_REPO_URL, GITHUB_INSTALLER_DOWNLOAD_URL } from '../../site';

const toc = [
  ['Get started', 'docs-start'],
  ['Dictation', 'docs-dictation'],
  ['Companion', 'docs-companion'],
  ['Refine', 'docs-refine'],
  ['Context & purge', 'docs-context'],
  ['Canvas & tray', 'docs-canvas'],
  ['Settings', 'docs-settings'],
  ['Models', 'docs-models'],
  ['Security & privacy', 'docs-security'],
  ['Troubleshooting', 'docs-troubleshooting'],
] as const;

export default function DocsPage({ onDownload }: { onDownload: () => void }) {
  const [active, setActive] = useState<string>('docs-start');

  useEffect(() => {
    const sections = toc
      .map(([, id]) => document.getElementById(id))
      .filter((el): el is HTMLElement => el !== null);
    if (!sections.length) return;
    const observer = new IntersectionObserver(
      (entries) => {
        entries.forEach((entry) => {
          if (entry.isIntersecting) setActive(entry.target.id);
        });
      },
      { rootMargin: '-12% 0px -70% 0px' }
    );
    sections.forEach((s) => observer.observe(s));
    return () => observer.disconnect();
  }, []);

  return (
    <div className="page-content docs-page docs-layout">
      <aside className="docs-sidebar" aria-label="Docs index">
        <div className="docs-side-inner">
          <p className="docs-side-kicker">Installation guide</p>
          <p className="docs-side-version">{SITE_VERSION} · 10 sections</p>
          <nav className="docs-side-nav" aria-label="Docs sections">
            {toc.map(([label, id], i) => (
              <a
                key={id}
                href={`#/docs#${id}`}
                className={active === id ? 'active' : ''}
                aria-current={active === id ? 'true' : undefined}
              >
                <span className="docs-side-num">{String(i + 1).padStart(2, '0')}</span>
                <span>{label}</span>
              </a>
            ))}
          </nav>
          <button className="button primary docs-side-cta" onClick={onDownload}>
            <Download size={15} />Get the installer
          </button>
        </div>
      </aside>

      <div className="docs-main">
      <section className="section docs-hero" id="docs-top">
        <Reveal>
          <EyebrowLabel>DOCS · VOXULA AI {SITE_VERSION.toUpperCase()}</EyebrowLabel>
          <ScrollReveal containerClassName="docs-sr" textClassName="docs-sr-text">How to use Voxula AI.</ScrollReveal>
          <p className="section-intro" style={{ textAlign: 'left', marginLeft: 0 }}>
            Setup, dictation, companion, refine, context, canvas, settings, security — everything the app does, on one page.
          </p>
        </Reveal>
        <Reveal delay={0.12}>
          <div className="info-box">
            <BookOpen size={18} />
            <p><strong>New here? Start with the installer, then the 3-step flow.</strong><br />Install → add an API key → focus any app and press Ctrl + Space. The simulator on the home page mirrors this flow, including refine.</p>
          </div>
        </Reveal>
      </section>

      <section className="section docs-section" id="docs-start">
        <Reveal>
          <div className="left-eyebrow"><span />01 · GET STARTED</div>
          <ScrollReveal containerClassName="docs-sr" textClassName="docs-sr-text">Install and connect.</ScrollReveal>
        </Reveal>
        <Reveal>
          <GlassCard className="docs-card">
            <div className="guide-steps">
              <div><span>01</span><section><h3>Install Voxula AI for Windows.</h3><p>Run the <strong>installer {INSTALLER_FILE}</strong> ({INSTALLER_SIZE}, Windows 10 Build 19041+ or Windows 11, 64-bit, DirectX 11+). Hosted on <a className="text-link" href={GITHUB_REPO_URL} target="_blank" rel="noreferrer">GitHub (voxula_ai_installer)<ArrowUpRight size={12} /></a>. No admin rights needed. Optional desktop / startup shortcuts, uninstaller included. <a className="text-link" href={GITHUB_INSTALLER_DOWNLOAD_URL} download={INSTALLER_FILE}>Direct download .exe<ArrowUpRight size={12} /></a></p></section></div>
              <div><span>02</span><section><h3>Bring an API key.</h3><p>Voxula AI auto-detects <strong>GEMINI_API_KEY</strong>, or open Settings → Setup to paste a primary + backup key. Keys live in Windows Credential Manager, never in plain files. <a className="text-link" href={GEMINI_KEY_URL} target="_blank" rel="noreferrer">Get a free key<ArrowUpRight size={12} /></a></p></section></div>
              <div><span>03</span><section><h3>Focus any app and speak.</h3><p>Put your cursor in Notepad, Word, VS Code, Slack, Discord, or a browser field. Press <KeyCap>Ctrl + Space</KeyCap> and talk — words type at your cursor, sub-second.</p></section></div>
            </div>
            <div style={{ display: 'flex', gap: '12px', flexWrap: 'wrap', marginTop: '20px' }}>
              <button className="button primary" onClick={onDownload}><Download size={16} />Get the installer</button>
              <a className="button ghost" href={GITHUB_REPO_URL} target="_blank" rel="noreferrer"><ArrowUpRight size={15} />GitHub Repo</a>
            </div>
          </GlassCard>
        </Reveal>
      </section>

      <section className="section docs-section" id="docs-dictation">
        <Reveal>
          <div className="left-eyebrow"><span />02 · DICTATION</div>
          <ScrollReveal containerClassName="docs-sr" textClassName="docs-sr-text">Live voice dictation.</ScrollReveal>
          <p className="section-intro" style={{ textAlign: 'left', marginLeft: 0 }}>Hotkey: <KeyCap>Ctrl + Space</KeyCap> — toggle on / off.</p>
        </Reveal>
        <Reveal>
          <GlassCard className="docs-card">
            <ul className="docs-list">
              <li>Streams mic audio (16 kHz mono) to live transcription.</li>
              <li>Types <strong>directly at the cursor</strong> in whatever app is focused — multilingual auto-detect, sub-second.</li>
              <li>Capsule shows live status, sound-wave visualizer (mic vs. voice), interim preview, and token bar.</li>
              <li>Press <KeyCap>Ctrl + Space</KeyCap> again to stop. Capsule hides to the tray.</li>
            </ul>
          </GlassCard>
        </Reveal>
      </section>

      <section className="section docs-section" id="docs-companion">
        <Reveal>
          <div className="left-eyebrow"><span />03 · COMPANION</div>
          <ScrollReveal containerClassName="docs-sr" textClassName="docs-sr-text">Multimodal live companion.</ScrollReveal>
          <p className="section-intro" style={{ textAlign: 'left', marginLeft: 0 }}>Hotkey: <KeyCap>Win + Shift</KeyCap> — voice + optional screen share.</p>
        </Reveal>
        <Reveal>
          <GlassCard className="docs-card">
            <ul className="docs-list">
              <li>Real-time voice conversation (replies play through your speakers; capsule shows <strong>Speaking… / Listening… / Working…</strong>).</li>
              <li>Optional <strong>live screen sharing</strong> (~1 fps JPEG) so the assistant sees your desktop. Toggle anytime via the capsule monitor button or Settings → Live Screen — mid-session, audio keeps running.</li>
              <li><strong>Voice desktop control:</strong> powered by the AI Engine — tell it <strong>“click Send”</strong>, <strong>“scroll down”</strong>, <strong>“press Ctrl+S”</strong>. It acts on what it sees, one step at a time, narrating as it goes. Say <strong>stop</strong> to halt instantly.</li>
              <li>Screen-off mode = voice-only companion.</li>
            </ul>
            <div className="info-box"><Monitor size={18} /><p>Screen frames stream <strong>only</strong> while a session is active, and only to Google's AI service.</p></div>
          </GlassCard>
        </Reveal>
      </section>

      <section className="section docs-section" id="docs-refine">
        <Reveal>
          <div className="left-eyebrow"><span />04 · REFINE</div>
          <ScrollReveal containerClassName="docs-sr" textClassName="docs-sr-text">Say “refine” — it refines.</ScrollReveal>
          <p className="section-intro" style={{ textAlign: 'left', marginLeft: 0 }}>Voice triggers: <strong>refine</strong> · <strong>polish</strong> · <strong>elaborate</strong> (plus <strong>expand</strong> alias). Or tap capsule buttons / tray → Refine.</p>
        </Reveal>
        <Reveal>
          <GlassCard className="docs-card">
            <ul className="docs-list">
              <li>Rewrites <strong>everything typed this session</strong> (since purge or dictation start).</li>
              <li>Delete-and-replace: the original is removed with measured Backspaces and the rewrite is typed in place — <strong>no clipboard, no Ctrl+A, no Enter presses</strong>.</li>
              <li>Self-correction aware: <em>“could you set meeting at 9pm actually 5pm”</em> → <em>“Could we schedule the meeting for 5:00 PM?”</em> (obsolete info dropped, times normalized).</li>
              <li>If Voxula AI has focus, refine asks you to <strong>click your document first</strong>, then say the word again — history is kept so retry works.</li>
            </ul>
            <div className="modal-shortcuts">
              {[['refine', 'Clean rewrite — grammar, clarity, structure'], ['polish', 'Tighten tone — emails, messages, notes'], ['elaborate', 'Expand the idea — detail, examples, formatting']].map(([k, v]) => (
                <div key={k}><KeyCap>{k}</KeyCap><span>{v}</span></div>
              ))}
              <p>Try it below-style: dictate something messy in the home-page simulator, then hit <strong>Say “refine”</strong> and watch it delete and retype the clean version.</p>
            </div>
          </GlassCard>
        </Reveal>
        <Reveal>
          <GlassCard className="docs-card">
            <h3>Custom refine actions (up to 3).</h3>
            <p>Settings → <strong>Refine tab</strong>: edit the Refine / Polish / Elaborate prompts and their trigger words, or add your own (e.g. name <strong>Summarize</strong>, trigger <strong>summarize</strong>, custom prompt). They appear immediately in the capsule, tray Refine menu, and voice triggers after Save. Trigger words: <strong>a–z 0–9 -</strong>, 2–24 chars, must be unique.</p>
          </GlassCard>
        </Reveal>
      </section>

      <section className="section docs-section" id="docs-context">
        <Reveal>
          <div className="left-eyebrow"><span />05 · CONTEXT</div>
          <ScrollReveal containerClassName="docs-sr" textClassName="docs-sr-text">Token bar and purge.</ScrollReveal>
        </Reveal>
        <Reveal>
          <GlassCard className="docs-card">
            <ul className="docs-list">
              <li>3 px bar under the capsule: <strong>green 0–60%</strong>, <strong>orange 61–85%</strong>, <strong>red 86–100%</strong>.</li>
              <li>Hover reveals exact token counts, session time, and remaining buffer.</li>
              <li><KeyCap>Ctrl + Win</KeyCap> instantly stops the session, clears transcript + typed history + token counter, and hard-resets the connection.</li>
            </ul>
          </GlassCard>
        </Reveal>
      </section>

      <section className="section docs-section" id="docs-canvas">
        <Reveal>
          <div className="left-eyebrow"><span />06 · CANVAS & TRAY</div>
          <ScrollReveal containerClassName="docs-sr" textClassName="docs-sr-text">Draw, then dismiss.</ScrollReveal>
        </Reveal>
        <Reveal>
          <GlassCard className="docs-card">
            <ul className="docs-list">
              <li><strong>Screen canvas:</strong> fullscreen transparent ink layer — <KeyCap>B</KeyCap> / <KeyCap>1–3</KeyCap> color keys, right-click clears, <KeyCap>Esc</KeyCap> exits. Mark the screen while talking to the companion.</li>
              <li><strong>System tray:</strong> show/hide capsule, Dictation, Companion, Purge, Refine submenu, Guide, Settings, Exit — with notifications for save / refine / speaker / screen events.</li>
              <li><strong>Capsule hidden?</strong> By design (hotkey-only): press <KeyCap>Ctrl + Space</KeyCap> or tray → Show capsule.</li>
            </ul>
          </GlassCard>
        </Reveal>
      </section>

      <section className="section docs-section" id="docs-settings">
        <Reveal>
          <div className="left-eyebrow"><span />07 · SETTINGS</div>
          <ScrollReveal containerClassName="docs-sr" textClassName="docs-sr-text">Four tabs, full control.</ScrollReveal>
        </Reveal>
        <Reveal>
          <GlassCard className="docs-card">
            <div className="guide-steps">
              <div><span>S</span><section><h3>Setup.</h3><p>Primary + backup API keys (masked), Test button, free-tier status.</p></section></div>
              <div><span>G</span><section><h3>Guide.</h3><p>Shortcut reference, always one click away.</p></section></div>
              <div><span>P</span><section><h3>Preferences.</h3><p>Microphone select / refresh, custom vocabulary + signature mark, system prompt, creativity slider, live-screen toggle + frame detail, agent reasoning depth (Low / Medium / High), Windows startup.</p></section></div>
              <div><span>R</span><section><h3>Refine.</h3><p>Prompts, trigger words, and up to 3 custom actions.</p></section></div>
            </div>
          </GlassCard>
        </Reveal>
      </section>

      <section className="section docs-section" id="docs-models">
        <Reveal>
          <div className="left-eyebrow"><span />08 · AI ENGINE</div>
          <ScrollReveal containerClassName="docs-sr" textClassName="docs-sr-text">What runs where.</ScrollReveal>
        </Reveal>
        <Reveal>
          <GlassCard className="docs-card">
            <div className="docs-table-wrap">
              <table className="docs-table">
                <thead><tr><th>Use</th><th>Engine</th></tr></thead>
                <tbody>
                  <tr><td>Dictation</td><td>AI Engine (speech-to-text)</td></tr>
                  <tr><td>Companion (live audio + screen + PC control)</td><td>AI Engine with automatic fallback</td></tr>
                  <tr><td>Refine (one-shot edit)</td><td>AI Engine with automatic fallback</td></tr>
                </tbody>
              </table>
            </div>
            <p>Stored configs with retired IDs self-repair on load. On connection failure the client rotates keys and retries — after 3 failures in 30 s it stops loudly instead of hot-looping.</p>
          </GlassCard>
        </Reveal>
      </section>

      <section className="section docs-section" id="docs-security">
        <Reveal>
          <div className="left-eyebrow"><span />09 · SECURITY & PRIVACY</div>
          <ScrollReveal containerClassName="docs-sr" textClassName="docs-sr-text">Your words are yours.</ScrollReveal>
        </Reveal>
        <Reveal>
          <GlassCard className="docs-card">
            <ul className="docs-list">
              <li><KeyRound size={13} /> Keys live in <strong>Windows Credential Manager</strong> (target <code>SPEAK_AI_App</code>), never in plain files. UI masks them; logs mask them.</li>
              <li><ShieldCheck size={13} /> Free-tier fallback key ships obfuscated and is used only when your vault is empty — your keys always win.</li>
              <li><LockKeyhole size={13} /> Config writes are atomic to <code>%APPDATA%\SPEAK_AI\config.json</code>, ACL-restricted to your user; all values sanitized on load.</li>
              <li><Keyboard size={13} /> Typing uses <code>SendInput</code> unicode (multilingual-safe). Clipboard never used for injection; no Enter synthesized. Single-instance lock, debounced hotkeys, bounded queues.</li>
              <li>Mic + screen stream <strong>only</strong> during an active session, only to Google's AI service. Transcript history resets every launch (no restore). No analytics, no accounts.</li>
            </ul>
          </GlassCard>
        </Reveal>
      </section>

      <section className="section docs-section" id="docs-troubleshooting">
        <Reveal>
          <div className="left-eyebrow"><span />10 · TROUBLESHOOTING</div>
          <ScrollReveal containerClassName="docs-sr" textClassName="docs-sr-text">Back to flow, fast.</ScrollReveal>
        </Reveal>
        <Reveal>
          <GlassCard className="docs-card">
            <div className="support-faq" style={{ marginTop: 0 }}>
              {[
                ['Companion shows “Model unavailable, trying next…” then “Live connect failed”', 'Keys invalid / quota, or network. Settings → Setup → Test key; add a backup key.'],
                ['“Speaker error / reply dropped”, no voice', 'Output device busy or missing. Check speaker, restart companion.'],
                ['“Mic silent / Mic Error”', 'Wrong input device. Preferences → Microphone → Refresh.'],
                ['Refine says “Click your document, then <word>”', 'Capsule had focus. Click the target app, say the trigger again (hands-free works best).'],
                ['Capsule hidden', 'By design (hotkey-only). Ctrl+Space, or tray → Show capsule.'],
                ['Live connect keeps failing', 'Bad stored engine IDs self-repair on load; otherwise check keys / network.'],
              ].map(([q, a]) => <details key={q}><summary>{q}</summary><p>{a}</p></details>)}
            </div>
            <div className="info-box"><ShieldCheck size={18} /><p>This site is a preview: the simulator uses sample text and never touches your mic, screen, or keys.</p></div>
          </GlassCard>
        </Reveal>
      </section>
      </div>
    </div>
  );
}
