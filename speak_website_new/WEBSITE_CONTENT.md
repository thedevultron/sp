# Voxula AI Website — Complete Content & Data Export
Source folder: `speak_website_new`
Generated for rebuilding a new website. All copy, structure, links, docs, and product data extracted from source files.

---

## 1. Brand & Global Config (`src/site.ts`)

- **APP_NAME:** Voxula AI
- **APP_SHORT:** VOXULA
- **SITE_VERSION:** v2.1
- **Tagline / H1:** "Your Voice. Everywhere."
- **Hero sub:** "Press Ctrl + Space to type into any app. Sub-second, private, free."
- **Author:** Amir Bagawan
- **Copyright:** © 2026 Amir Bagawan. Built for speed, privacy, and flow.
- **Meta title:** Voxula AI — Your Voice. Everywhere.
- **Meta description:** Voxula AI — Your Voice. Everywhere. A native Windows AI voice dictation and multimodal companion, powered by Gemini Live. Explore the interactive demo.
- **Theme color:** #08090a
- **Favicon:** inline SVG wave bars (blue #4c8dff on dark)
- **Fonts:** Inter (300-590) + JetBrains Mono 400 via Google Fonts
- **Analytics:** Google tag G-R01FSKETV4

### Installer / Release wiring (single source of truth)
- **INSTALLER_FILE:** `SPEAK_Setup_v2.1.exe`
- **INSTALLER_SIZE:** `64.3 MB`
- **INSTALLER_PATH:** `downloads/SPEAK_Setup_v2.1.exe` (relative URL, works on any static host)
- **INSTALLER_FALLBACK_FILE:** `SPEAK_Setup_v2.0.exe`
- **GITHUB_REPO_URL:** https://github.com/codedebuggalt/voxula_ai_installer
- **GITHUB_INSTALLER_DOWNLOAD_URL:** https://github.com/codedebuggalt/voxula_ai_installer/raw/main/SPEAK_Setup_v2.1.exe
- **GEMINI_KEY_URL:** https://aistudio.google.com/apikey
- **DOCS_HASH:** `#/docs`
- **Hosting:** Firebase Hosting (`firebase.json`), project `voxula-ai`, public `dist`, SPA rewrites `** -> /index.html`
- **Security headers:** X-Content-Type-Options nosniff, X-Frame-Options DENY, Referrer-Policy strict-origin-when-cross-origin, Permissions-Policy microphone=(), camera=(), geolocation=()
- **Downloads header:** Content-Disposition attachment for `/downloads/**`
- **robots.txt:** Allow /, Sitemap https://voxula.ai/sitemap.xml
- **public/downloads/README.txt:** Real ~100MB exe NOT committed to git. Place built installer at `downloads/SPEAK_Setup_v2.1.exe` before build, or `scripts/copy-installer.mjs` auto-copies from `../../speak_app/installer/SPEAK_Setup_v2.1.exe`. Download modal falls back to quick-start guide if missing.

### Positioning statements (reuse verbatim)
- "Your Voice. Everywhere. A native Windows AI voice dictation and multimodal companion, powered by the AI Engine. Free forever — bring your own API key."
- "Great voice tools either charge monthly or hog the CPU running local models. Voxula AI is an always-on voice copilot and sub-second dictation in one tray app that idles quietly until you call it. Bring a free key. That is the whole business model."
- "Built because the alternatives cost too much."
- "Voice should not cost monthly. Free tier included."
- "No subscriptions. Sips CPU. Copilot plus dictation."
- Nav badge: "Free. Forever."
- Footer status: "All systems in flow"

---

## 2. Site Structure / Navigation (`src/App.tsx`)

**Pages (hash routing):**
- `home` = `#overview` (default)
- `docs` = `#/docs` + anchor `#docs-*`

**Nav links:**
1. Overview → #overview
2. How it works → #how-it-works
3. Features → #features
4. Privacy → #privacy
5. Docs → #/docs
6. GitHub (external, ArrowUpRight icon) → GITHUB_REPO_URL

**Nav actions:**
- Status pill: green dot + "Free. Forever."
- GitHub button (icon + "GitHub")
- CTA button: "Get Voxula AI" / mobile "Get" + ArrowUpRight → opens Download modal
- Mobile hamburger Menu/X

**Home page section order:**
1. Hero (`#overview`)
2. Pipeline / How it works (`#how-it-works`)
3. Simulator / Try it here (`#simulator`)
4. Bento Pillars / Features (`#features`)
5. About (`#about`)
6. Hotkeys + Security (`#privacy`)
7. Expand Showcase (`#showcase`)
8. Download + Footer (`#download` + footer)
9. ChatDock (modal, opened from download section "Ask about Voxula")
10. ProductModal (settings/guide/download/support)

**Docs page:** sidebar (10 sections) + main + DownloadFooterSection at bottom.

---

## 3. Hero Section (`ProductSections.tsx` HeroSection)

- **Eyebrow:** VOXULA AI + version tag `V2.1`
- **H1:** "Your Voice." (line 1) "Everywhere." (line 2) — staggered char animation
- **Description:** Press `Ctrl + Space` to type into any app. Sub-second, private, free.
- **CTA primary (violet):** "Download for Windows" + divider + "It's free" → Download modal
- **CTA secondary (ghost pill):** "Launch web simulator" + ArrowUpRight → scroll to #simulator
- **Meta row:** [Monitor icon] Native Windows 11 · Free tier included · Bring your own key
- **Product visual:** caption "VOXULA CAPSULE — LIVE" with lines, SpeakCapsuleWidget (mirrors simulator demo state), under-row: [Lock] Private by design · `ctrl` + `space` and you're in flow · Sub-second latency
- **Compatibility strip:** label "WORKS WHERE YOU WORK", marquee: VS Code, Slack, Notion, Word, Any app
- **Scroll cue:** SCROLL + line (desktop only)

---

## 4. How It Works / Pipeline (`#how-it-works`)

- **Eyebrow:** HOW IT WORKS
- **H2:** "Instant execution. Zero friction."
- **Intro:** "From a thought to the page, in less than a second."

**3 steps:**
1. **01 / CONNECT — "Bring a key. We'll find it."**
   Auto-detects GEMINI_API_KEY or your saved vault key, with a free-tier fallback. Keys stay on your device.
2. **02 / SUMMON — "One shortcut. Any app."**
   Press Ctrl + Space. Voxula appears over your active window with a live transcript — without stealing focus.
3. **03 / FLOW — "Speak at the speed of thought."**
   Words stream to your cursor sub-second. Say "refine" and the session rewrites itself in place.

---

## 5. Simulator / Interactive Playground (`#simulator`)

- **Eyebrow:** TRY IT HERE
- **H2:** "Less typing. More momentum."
- **Intro:** "Dictate it raw, then say refine and watch the session rewrite itself."
- **Label:** INTERACTIVE PLAYGROUND (green dot)
- **H3:** "Think it. Say it. Watch it happen."
- **Sub:** "Your voice, right where your cursor is. Dictate it messy — then say 'refine'."
- **Controls:**
  - 01 CHOOSE YOUR WORKSPACE: tabs VS Code / Slack / Notion
  - 02 MAKE IT YOURS: toggle switch "Raw transcription" ↔ "Auto-refine & polish"
  - Speak button: Mic icon + "Press to speak" + keys Ctrl Space. While busy: Square icon + "Listening. Click to stop" / "Deleting session…" / "Typing the rewrite…" + waveform. After done: "Try it again"
  - Refine button (appears after dictation done, raw mode): Sparkles + "Say 'refine' — watch it rewrite" + key `refine`
  - After refined: check "Refined in place — deleted and retyped, just like the native app." + "Triggers: refine · polish · elaborate (+ expand alias)."
  - Disclaimer default: "Simulated dictation + refine. Your mic stays off."
- **Keyboard:** Ctrl+Space starts demo (scrolls to simulator), Esc stops, Ctrl+Win resets, typing word "refine" triggers rewrite
- **Preview header:** status dot + "Your workspace. Supercharged." / "Streaming to your workspace" / "Refining your session…" / "Session refined" + Reset button
- **Mock app windows:**
  - VS Code: title "workspace / utils.ts", tab TS utils.ts, rail FileText/Code2/Hash/Terminal, code area with line numbers 1-11, footer "Receiving voice input / Ready for your voice" + "TypeScript UTF-8"
  - Slack: title "Acme · #engineering", tab #engineering, author AB Amir Just now, footer "All changes saved"
  - Notion: title "Personal / Product ideas", tab Product ideas
  - Placeholder when empty: code "// Your next great idea starts with your voice." / Slack "Your team is one thought away. Speak to start your message…" / Notion "# Your next big idea Speak to bring it to life…"
- **Telemetry row:** Zap [Ticker]ms latency (142 busy/done, 180 idle) · Mic 16kHz live audio · ShieldCheck DPAPI encrypted
- **Note:** "Illustrative performance · Native app uses the AI Engine"
- **Behavior:** types raw at 2 chars/22ms, refine deletes at 7 chars/14ms then retypes polish at 3 chars/16ms. LiveTypingPlayground drives hero capsule via onUpdate {active, text, progress: 12 + text.length/12}

### Simulator scripts (exact copy for rebuild)

**VS Code raw:**
```
// get the users that are active and sort by name
const activeUsers = users
  .filter(user => user.isActive)
  .sort((a, b) => a.name.localeCompare(b.name));
```
**VS Code polish:**
```
// Return active users, alphabetically by name.
const getActiveUsers = (users: User[]): User[] => {
  return users
    .filter(({ isActive }) => isActive)
    .sort((a, b) => a.name.localeCompare(b.name));
};
```
**Slack raw:**
```
hey team so the voice integration is ready and um latency is looking really good. can someone take a look at the pull request before we ship tomorrow?
```
**Slack polish:**
```
Hey team — the voice integration is ready for review.

Latency is consistently under 200ms, and all tests are passing. Please review the pull request before tomorrow's release.

Thanks for helping us ship something great.
```
**Notion raw:**
```
okay so the idea is to make a voice first workflow and not have to switch apps. we need global shortcuts, live transcription and maybe screen sharing too.
```
**Notion polish:**
```
# A voice-first workflow

Build a companion that turns thoughts into action, without switching apps.

## Core priorities
• System-wide keyboard shortcuts
• Real-time, low-latency transcription
• Multimodal screen understanding

Less friction. More flow.
```

---

## 6. Features / Bento Grid (`#features`)

- **Eyebrow:** FEATURES
- **H2:** "Quietly powerful."
- **Intro:** "Six capabilities. One shortcut. Say refine, polish, or elaborate — the session rewrites itself. Full guide in Docs."

**6 pillars (`pillars.ts` — keep order):**

1. **voice — INSTANT DICTATION — "Your voice. Direct to cursor."**
   Live dictation streamed at 16 kHz and typed at your cursor — any app, sub-second, multilingual auto-detect.
   Foot: `Ctrl + Space` · span 4 · visual: mic ring + static wave bars [10,18,30,44,34,22,40,26,34,20,30,16,26,14,24,12,22,12,20,11,18,10,16,10,14,9,12]

2. **vision — MULTIMODAL COMPANION — "An AI that sees — and acts."**
   A voice companion on the AI Engine: optional ~1 fps screen share plus voice desktop control — "click Send", "scroll down" — narrated step by step.
   Foot: `Win + Shift` · span 2 · visual: mock browser window + "AI VISION" focus + Live chip

3. **keys — MULTI-KEY ENGINE — "Stay in flow. Never in a queue."**
   Primary + backup keys in Windows Credential Manager. On rate limits or drops, Voxula AI rotates keys and reconnects.
   Foot: `Always connected` · span 2 · visual: Primary key (green dot) + Backup key (check)

4. **context — SMART CONTEXT — "Full context. Full control."**
   Live token bar: green 0–60%, orange 61–85%, red 86–100%. Hover for exact tokens and session time. Purge anytime.
   Foot: `Ctrl + Win` · span 4 · visual: "Session context 18,420 /128k" + 28 segments (8 filled) + green dot "Plenty of room to think"

5. **custom — CUSTOM ACTIONS — "Teach it your own words."**
   Up to 3 custom refine actions with your own trigger words — say "summarize" and the whole session obeys. Craft them in Settings → Refine.
   Foot: `Settings → Refine` · span 3 · visual: chips `summarize` + dim `elaborate` `polish`

6. **refine — REFINE & POLISH — "Say “refine” — it refines."**
   Say refine, polish, or elaborate and the whole session is deleted and retyped, cleaner. Self-correction aware, plus 3 custom actions.
   Foot: `Say “refine”` · span 3 · visual: before "um, so here's what I'm thinking..." → after Sparkles "A clear idea. Beautifully expressed."

---

## 7. About Section (`#about`)

- **Eyebrow:** WHY VOXULA EXISTS
- **H2:** "Built because the alternatives cost too much."
- **Intro:** "Subscription voice tools or CPU-hungry local models. Voxula is neither — one free, featherweight Windows app."
- **Card body:** "Great voice tools either charge monthly or hog the CPU running local models. Voxula AI is an always-on voice copilot and sub-second dictation in one tray app that idles quietly until you call it. Bring a free key. That is the whole business model."
- **3 points:**
  - Wallet icon — "No subscriptions." / "Voice should not cost monthly. Free tier included."
  - Cpu icon — "Sips CPU." / "No heavy local models. Cloud transcription, tray-idle footprint."
  - Combine icon — "Copilot plus dictation." / "A screen-seeing assistant and instant typer in one flow."

---

## 8. Privacy / Hotkeys / Security (`#privacy`)

- **Eyebrow:** PRIVACY
- **H2:** "Your words are yours."
- **Intro:** "Local DPAPI encryption. Zero telemetry. No compromises."
- **Left visual:** lock disc (LockKeyhole 28), badge ShieldCheck "ON-DEVICE ENCRYPTION", caption "Never our data. Always your voice."
- **Right list label:** Keyboard icon "BUILT INTO MUSCLE MEMORY"
- **4 shortcuts:**
  - Ctrl + Space — Global dictation — "Your voice, typed wherever your cursor is."
  - Win + Shift — Screen companion — "Voice + live screen, together."
  - Ctrl + Win — Fresh start — "Purge transcript and token counter."
  - Esc — Back to focus — "Clear the canvas and dismiss to tray."
- **3 pillars:**
  - LockKeyhole — "Your keys. Under lock." / "Windows Credential Manager encrypts API keys locally with DPAPI."
  - ShieldCheck — "Direct line. No middleman." / "Encrypted connection straight to the voice service. No tracking."
  - Layers — "Almost invisible." / "Idles quietly in your tray until inspiration strikes."
- **Footer note:** "Voice refine triggers: refine · polish · elaborate (plus expand alias and up to 3 custom actions in Settings → Refine)."

---

## 9. Showcase CTA (`#showcase`)

- **Mini eyebrow:** VOXULA AI IN ACTION
- **H3:** "Say it. Consider it done."
- **P:** "Dictate raw. Say refine. Ship polished."
- **Button:** "Get Voxula AI" + ArrowUpRight → Download modal

---

## 10. Download + Footer (`#download`)

**Download card:**
- Logo WaveLogo
- Eyebrow: "100% FREE. ENTIRELY YOURS."
- H2: "Find your voice. Get into flow."
- P: "Less between you and your next great idea. New to Voxula AI? Read the Docs first." (Docs link underlined)
- Button: "Download Voxula AI for Windows" + ArrowUpRight → Download modal
- Ask link (if chat enabled): "Questions? Ask about Voxula" → opens ChatDock
- Specs: `v2.1 · Native x64 · Windows 10 / 11 · Free forever`
- Checks: Check "Free key supported" · Check "No subscription required" · Check "Unsigned build — if Windows warns, click More info then Run anyway"

**Mobile strip:**
- Smartphone icon
- H3: "Your flow doesn't stop at your desk."
- P: "Take voice notes on the move with the mobile companion."
- Button: "Explore the companion" + ArrowUpRight → Guide modal

**Footer:**
- Brand: WaveLogo small + "Voxula AI" + "by Amir Bagawan" → #overview
- Links: Documentation (#/docs) · GitHub + ArrowUpRight (external) · Installer (.exe) + ArrowUpRight (direct download) · Keyboard reference (#privacy) · Support button (Support modal)
- Bottom: "© 2026 Amir Bagawan. Built for speed, privacy, and flow." + green dot "All systems in flow"
- System requirements line: "DirectX 11+ · Windows 10 Build 19041+ or Windows 11 · 64-bit"

---

## 11. Capsule Widget (`SpeakCapsuleWidget.tsx`)

Floating demo capsule used in hero:
- Top row: status dot (green, pulsing when active) + "VOXULA" + badge "Live"/"Ready" · WaveformDots (5 dots) · actions Settings / Guide / Hide
- Token bar: SmartTokenBar, width = progress%, color green default, orange >75, red >90. Tooltip "Tokens: {progress*1280} / 128,000 · 180ms"
- Bottom: Transcript toggle (chevron) + hint "Your next thought, one shortcut away." / vision mode "Screen vision enabled · demo" + Monitor toggle
- Transcript drawer (expandable): mono "LIVE TRANSCRIPT" + text or "Press Ctrl + Space in the simulator below. Your words will appear here, in real time." + cursor when active
- Vision mode: corner brackets overlay
- Hidden state: GhostPillButton Mic "Show Voxula AI capsule" + ArrowUpRight
- Esc closes vision/drawer

---

## 12. Docs Page (`#/docs`, `DocsPage.tsx`)

- **Hero eyebrow:** DOCS · VOXULA AI V2.1
- **H2 (scroll reveal):** "How to use Voxula AI."
- **Intro:** "Setup, dictation, companion, refine, context, canvas, settings, security — everything the app does, on one page."
- **Info box:** BookOpen "New here? Start with the installer, then the 3-step flow. Install → add an API key → focus any app and press Ctrl + Space. The simulator on the home page mirrors this flow, including refine."
- **Sidebar:** kicker "Installation guide", version "v2.1 · 10 sections", numbered nav 01-10, CTA "Get the installer" (Download icon)

### 01 GET STARTED (`#docs-start`) — "Install and connect."
1. Install Voxula AI for Windows. Run the installer `SPEAK_Setup_v2.1.exe` (64.3 MB, Windows 10 Build 19041+ or Windows 11, 64-bit, DirectX 11+). Hosted on GitHub (voxula_ai_installer). No admin rights needed. Optional desktop/startup shortcuts, uninstaller included. Direct download .exe link.
2. Bring an API key. Voxula AI auto-detects GEMINI_API_KEY, or open Settings → Setup to paste a primary + backup key. Keys live in Windows Credential Manager, never in plain files. Get a free key link.
3. Focus any app and speak. Put your cursor in Notepad, Word, VS Code, Slack, Discord, or a browser field. Press Ctrl+Space and talk — words type at your cursor, sub-second.
Buttons: Get the installer (primary) + GitHub Repo (ghost).

### 02 DICTATION (`#docs-dictation`) — "Live voice dictation." Hotkey Ctrl+Space toggle on/off.
- Streams mic audio (16 kHz mono) to live transcription.
- Types directly at the cursor in whatever app is focused — multilingual auto-detect, sub-second.
- Capsule shows live status, sound-wave visualizer (mic vs. voice), interim preview, and token bar.
- Press Ctrl+Space again to stop. Capsule hides to the tray.

### 03 COMPANION (`#docs-companion`) — "Multimodal live companion." Hotkey Win+Shift voice + optional screen share.
- Real-time voice conversation (replies play through speakers; capsule shows Speaking… / Listening… / Working…).
- Optional live screen sharing (~1 fps JPEG) so assistant sees desktop. Toggle anytime via capsule monitor button or Settings → Live Screen — mid-session, audio keeps running.
- Voice desktop control: powered by AI Engine — tell it "click Send", "scroll down", "press Ctrl+S". It acts on what it sees, one step at a time, narrating as it goes. Say stop to halt instantly.
- Screen-off mode = voice-only companion.
- Info box: Monitor icon "Screen frames stream only while a session is active, and only to Google's AI service."

### 04 REFINE (`#docs-refine`) — "Say “refine” — it refines." Triggers refine · polish · elaborate (+ expand alias). Or capsule buttons / tray → Refine.
- Rewrites everything typed this session (since purge or dictation start).
- Delete-and-replace: original removed with measured Backspaces and rewrite typed in place — no clipboard, no Ctrl+A, no Enter presses.
- Self-correction aware: "could you set meeting at 9pm actually 5pm" → "Could we schedule the meeting for 5:00 PM?" (obsolete info dropped, times normalized).
- If Voxula AI has focus, refine asks you to click your document first, then say the word again — history kept so retry works.
- Table: refine = Clean rewrite (grammar, clarity, structure) · polish = Tighten tone (emails, messages, notes) · elaborate = Expand idea (detail, examples, formatting)
- Tip: dictate messy in home simulator, hit Say "refine" and watch delete+retype.
- Custom refine actions (up to 3): Settings → Refine tab: edit Refine/Polish/Elaborate prompts + triggers, or add own (e.g. name Summarize, trigger summarize, custom prompt). Appear immediately in capsule, tray Refine menu, voice triggers after Save. Trigger words: a–z 0–9 -, 2–24 chars, must be unique.

### 05 CONTEXT (`#docs-context`) — "Token bar and purge."
- 3px bar under capsule: green 0–60%, orange 61–85%, red 86–100%.
- Hover reveals exact token counts, session time, remaining buffer.
- Ctrl+Win instantly stops session, clears transcript + typed history + token counter, hard-resets connection.

### 06 CANVAS & TRAY (`#docs-canvas`) — "Draw, then dismiss."
- Screen canvas: fullscreen transparent ink layer — B / 1–3 color keys, right-click clears, Esc exits. Mark screen while talking to companion.
- System tray: show/hide capsule, Dictation, Companion, Purge, Refine submenu, Guide, Settings, Exit — with notifications for save/refine/speaker/screen events.
- Capsule hidden? By design (hotkey-only): press Ctrl+Space or tray → Show capsule.

### 07 SETTINGS (`#docs-settings`) — "Four tabs, full control."
- S Setup: Primary + backup API keys (masked), Test button, free-tier status.
- G Guide: Shortcut reference, always one click away.
- P Preferences: Microphone select/refresh, custom vocabulary + signature mark, system prompt, creativity slider, live-screen toggle + frame detail, agent reasoning depth (Low/Medium/High), Windows startup.
- R Refine: Prompts, trigger words, up to 3 custom actions.

### 08 AI ENGINE (`#docs-models`) — "What runs where."
Table:
| Use | Engine |
| Dictation | AI Engine (speech-to-text) |
| Companion (live audio + screen + PC control) | AI Engine with automatic fallback |
| Refine (one-shot edit) | AI Engine with automatic fallback |
Note: Stored configs with retired IDs self-repair on load. On connection failure client rotates keys and retries — after 3 failures in 30s stops loudly instead of hot-looping.

### 09 SECURITY & PRIVACY (`#docs-security`) — "Your words are yours."
- Keys live in Windows Credential Manager (target SPEAK_AI_App), never in plain files. UI masks them; logs mask them.
- Free-tier fallback key ships obfuscated, used only when vault empty — your keys always win.
- Config writes atomic to %APPDATA%\SPEAK_AI\config.json, ACL-restricted to your user; all values sanitized on load.
- Typing uses SendInput unicode (multilingual-safe). Clipboard never used for injection; no Enter synthesized. Single-instance lock, debounced hotkeys, bounded queues.
- Mic + screen stream only during active session, only to Google's AI service. Transcript history resets every launch (no restore). No analytics, no accounts.

### 10 TROUBLESHOOTING (`#docs-troubleshooting`) — "Back to flow, fast."
- Companion shows "Model unavailable, trying next…" then "Live connect failed" → Keys invalid/quota or network. Settings → Setup → Test key; add backup key.
- "Speaker error / reply dropped", no voice → Output device busy/missing. Check speaker, restart companion.
- "Mic silent / Mic Error" → Wrong input device. Preferences → Microphone → Refresh.
- Refine says "Click your document, then <word>" → Capsule had focus. Click target app, say trigger again (hands-free works best).
- Capsule hidden → By design (hotkey-only). Ctrl+Space, or tray → Show capsule.
- Live connect keeps failing → Bad stored engine IDs self-repair on load; otherwise check keys/network.
- Info box: ShieldCheck "This site is a preview: the simulator uses sample text and never touches your mic, screen, or keys."

---

## 13. Modals (`ProductModal.tsx`)

All modals: backdrop click/Esc closes, focus trap, body scroll lock. Header logo WaveLogo small + eyebrow VOXULA AI / {PREFERENCES | YOUR NEXT CHAPTER | HERE TO HELP | FIELD GUIDE} + H2.

### Settings modal — eyebrow PREFERENCES, H2 "Make yourself at home."
P: "Explore native app preferences. This preview never sends your key to a server."
Form: label KeyRound "API key" + "SESSION ONLY", input password/text "Paste your API key", show/hide Eye, error "Please enter an API key of at least 20 characters.", link "Get a free API key", info box ShieldCheck "The native app stores keys in Windows Credential Manager with DPAPI encryption. This browser preview keeps the key in memory only and does not connect to any AI service.", submit "Save preview preference" → Check "Saved for this preview session", "Remove saved key" link.

### Guide modal — eyebrow FIELD GUIDE, H2 "A little guidance. Zero friction."
Tabs: Get started / Shortcuts / Refine
- Get started: 01 Bring your own API key (Create key in Google AI Studio. Native app auto-detects GEMINI_API_KEY or saved vault key.) · 02 Make any app your workspace (cursor in VS Code, Slack, Notion, Word, or other text field.) · 03 Press Ctrl+Space. Speak freely. (Toggle dictation, or try sample-text simulator. No mic permission needed for demo.) + link "Open the full Docs — setup, refine, security"
- Shortcuts: Ctrl+Space Toggle global dictation · Win+Shift Multimodal screen companion (toggle vision mid-session) · Ctrl+Win Purge session and flush memory · Esc Clear canvas and dismiss. Note: Browser preview supports Ctrl+Space and Esc. System shortcuts live in native app. Voice triggers (refine·polish·elaborate) in Refine tab.
- Refine: Sparkles "Say “refine” — it refines." (Say refine/polish/elaborate or tap capsule buttons. Whole session deleted and retyped, cleaner — no clipboard, no Ctrl+A.) · 02 Try it in simulator (Dictate messy with Raw on, press Say "refine" — or type word refine — watch delete-and-replace.) + link "Refine + custom actions, explained in Docs"

### Download modal — eyebrow YOUR NEXT CHAPTER, H2 "Meet Voxula AI v2.1."
Lede: "A native Windows companion, built for speed, privacy, and your next great idea."
Release card: Monitor icon, "Voxula AI for Windows v2.1", "Native x64 · Windows 10 / 11 · Free forever", size 64.3 MB
Info box: Download icon "SPEAK_Setup_v2.1.exe (64.3 MB) Official setup wizard hosted on GitHub. 64-bit · No admin rights required · Uninstaller included."
Actions: DownloadButton "Download Windows Installer (v2.1)" (href GITHUB_INSTALLER…, download attr, star-beam + click sparks) → thank-you card · Ghost "View GitHub Repository (Source & Release)" · Ghost "Save the quick-start guide" (BookOpen → Check "Quick-start guide downloaded") · Ghost "Try the web simulator" (scrolls to #simulator)
Thank-you card: Check circle, "Thank you.", "Your download has started. Run the installer, grab a free API key, and press Ctrl+Space in any app.", VoiceLines 24 bars, steps 1 Run setup wizard 2 Paste free API key 3 Speak anywhere
Footnote: Lock "No account. No subscription. Your key, your control."

### Support modal — eyebrow HERE TO HELP, H2 "Let's keep you in flow."
P: "Start with a few quick checks to get back to your workflow."
FAQ:
- Dictation isn't appearing → cursor in editable field, mic permissions, API key active.
- API key reached limit → Add backup key in settings. Failover rotates. Google quotas apply.
- How does refine work? → Say refine/polish/elaborate (or capsule/tray). Deleted with Backspaces, retyped cleanly. If Voxula had focus, click document first, say again.
- Does this website record my microphone? → No. Simulator streams pre-written sample text locally. No mic/screen/account access.
Info box: Mail "Most answers live in Docs, including full troubleshooting table. For release-specific help, use support info bundled with native app."

### Quick-start guide file text (downloadable `Voxula-AI-2.1-Quick-Start.txt`):
```
Voxula AI v2.1 — Quick Start (Amir Bagawan, 2026)

SYSTEM REQUIREMENTS
Windows 10 Build 19041+ or Windows 11, 64-bit, DirectX 11+.

INSTALL
1. Run the installer SPEAK_Setup_v2.1.exe (Setup wizard, no admin needed).
   Direct Download: https://github.com/codedebuggalt/voxula_ai_installer/raw/main/SPEAK_Setup_v2.1.exe
   GitHub: https://github.com/codedebuggalt/voxula_ai_installer
2. Launch Voxula AI from the tray icon.

SETUP
1. Get a free API key at https://aistudio.google.com/apikey
2. Settings → Setup: paste primary + optional backup key (Credential Manager, masked). Or set GEMINI_API_KEY env — auto-detected.
3. Settings → Preferences: pick microphone, vocabulary, creativity. Settings → Refine: custom actions.

USE
- Ctrl+Space: Live Voice Dictation. Focus any app, speak, words type at cursor.
- Win+Shift: Multimodal Live Companion (voice + optional ~1 fps screen share, toggle mid-session).
- Voice desktop control: tell it "click Send", "scroll down", "press Ctrl+S" — acts on what it sees, narrating each step. Say "stop" to halt.
- Say "refine", "polish", or "elaborate" (or capsule/tray buttons): rewrites whole session in place.
- Ctrl+Win: Purge session. Esc: clear canvas, dismiss.
- Token bar: green 0–60%, orange 61–85%, red 86–100%. Hover for exact counts.

FULL GUIDE: open Docs on website (#/docs).
Web simulator uses sample text — no mic, screen, or key access.
```

---

## 14. Chat Assistant ("Ask Voxula", `ChatDock.tsx` + `useChat.ts` + `docsEngine.ts` + `api/chat.ts`)

- Entry: "Questions? Ask about Voxula" link in download card → centered card → first keystroke animates to docked window right side. Esc closes.
- Header: MessageCircle icon, "Ask Voxula", sub "Answers from the Docs", X close
- Greeting: "Hi — ask me anything about Voxula. Short answers, straight from the Docs."
- Suggestions: "How do I install it?" / "What does refine do?" / "Is my voice private?"
- Input: "Ask about Voxula…" max 2000 chars, send ArrowUp button
- Typing indicator: 3 dots. Error box + "Try again" retry.
- Backend: POST /api/chat (server proxy, GEMINI_API_KEY server-only, rate limit 20 req/10min per IP, 8-msg history, 2000-char cap, 512 output tokens, model chain with runtime validation, RAG over corpus.json top-3 chunks 1800-char budget). Falls back to client-side docsEngine if /api fails (static hosting).
- Client canned answers (reuse for new site chatbot):
  - install/download/setup → 4-step install (download exe 64.3MB from GitHub/download button, run wizard no admin, bring free Google AI Studio key or GEMINI_API_KEY, cursor + Ctrl+Space)
  - refine/polish/elaborate → hands-free rewriter, Backspaces delete + retype at cursor, custom prompts in Settings→Refine
  - private/privacy/security/key → Credential Manager DPAPI, streams only during sessions to Google, zero telemetry/no proxy/no analytics
  - companion/screen/vision/see → Win+Shift, AI Engine, speaks via speakers, optional ~1fps desktop, toggle mid-session
  - click/control/agent/operate/desktop → "click Send", "scroll down", "type hello…", "press Ctrl+S", step-by-step narrated, reasoning Low/Med/High in Preferences→Agent Reasoning, governor 25-step/no loops, stop halts
  - model → AI Engine with auto fallback, reasoning depth in Preferences, table in Docs→AI Engine
  - shortcut/hotkey → Ctrl+Space dictation, Win+Shift companion, Ctrl+Win purge, Esc dismiss, Say refine rewrite
  - free/cost/price/subscription → 100% free no subs, bring free Google key, fallback key included
  - github/source/code/repo → codedebuggalt/voxula_ai_installer, inspect or download SPEAK_Setup_v2.1.exe
  - fallback → ranked keyword retrieval over docs chunks, else "couldn't find… check Docs (#/docs) or GitHub"
- Rules: short plain 2-3 sentences, no hype/emoji, never name model versions/providers (say "AI Engine"), never reveal chain/keys, only answer from context, point to Docs if unsure, no Mac/Linux/mobile download (only mobile companion mention).

---

## 15. llms.txt (SEO / AI index, `public/llms.txt`)

Title Voxula AI, tagline + 10 Docs links (Installation, Dictation 16kHz, Companion screen share, Refine triggers, Token bar Ctrl+Win, Canvas+tray, Settings 4 tabs, AI Engine fallback, Security Credential Manager/no telemetry, Troubleshooting) + Download Installer link + GitHub Repository link. All absolute https://voxula.ai/#/docs#… URLs.

---

## 16. Visual / UX notes for rebuild

- Dark theme "frosted glass cathedral at midnight": near-black #05060f / #08090a canvas, frost-glass cards, hairline borders, single Void Violet #663af3 CTA, pill buttons, blueprint grid + spotlight in Settings.
- Accent blue #4c8dff (logo bars, scroll progress bar top). VoiceLines color var --color-acid-lime default, blue elsewhere.
- Motion: Lenis smooth scroll 1.15s, GSAP ScrollTrigger — hero copy drifts/fades, product y-120 scale .96 scrub, sections y28→0 scrub, bento/pipeline cascade once expo.out, expand CTA scale .96→1 scrub, download card y40 scrub. Page transition blur+y. Reveal rise+deblur. CharStagger hero. Ticker numbers. Reduced-motion fallbacks throughout.
- Loader: CinematicLoader midnight booth — WaveLogo + VOXULA AI + 36 voice bars + hairline progress + MIC CHECK 000% (~1.7s, mic-check stutter first third), exits rise+blur. Skipped if reduced motion.
- Bento: custom varied grid spans 4/2/2/4/3/3, GlowCard border-glow (blue 76,141,255 radius 260) + grid bridge glow radius 380px spilling across gaps.
- Buttons: VoidVioletButton (primary w/ Download icon), GhostPillButton, DownloadButton star-beam orbit + click sparks (10 sparks, 650ms), KeyCap kbd chips.
- SectionTransition: 1px graphite hairline + rise+blur.
- Voice divider motif: hairline rules + 22 voice bars + caption LIVE·IN FLOW.
- Components available: BlurText, CharStagger, ScrollReveal, ScrollExpand, MaskedHeading (gradient SVG data URIs MASKED_GRADIENT_SRC purple/blue, SCROLL_FRAME_SRC), TextLoop (SVG path wave/circle/infinity/arch/line), GradientWaves, Grainient, Strands, StrokeText, TickerNumber, VoiceLines, WaveformDots, TokenBar.

---

## 17. All links & anchors checklist

- #overview, #how-it-works, #simulator, #features, #about, #privacy, #showcase, #download
- #/docs, #/docs#docs-start, #docs-dictation, #docs-companion, #docs-refine, #docs-context, #docs-canvas, #docs-settings, #docs-models, #docs-security, #docs-troubleshooting, #docs-top
- https://github.com/codedebuggalt/voxula_ai_installer
- https://github.com/codedebuggalt/voxula_ai_installer/raw/main/SPEAK_Setup_v2.1.exe
- https://aistudio.google.com/apikey
- https://voxula.ai/sitemap.xml, https://voxula.ai/#/docs#… (10x)
- Google Fonts Inter + JetBrains Mono, gtag G-R01FSKETV4

---

## 18. Rebuild prompt (paste into new-site builder)

> Build a dark cinematic marketing + docs site for "Voxula AI — Your Voice. Everywhere." v2.1 by Amir Bagawan. Free Windows (10 Build 19041+/11, x64, DirectX11+, 64.3MB SPEAK_Setup_v2.1.exe via https://github.com/codedebuggalt/voxula_ai_installer) voice dictation + multimodal companion. Home sections in order: Hero (H1 Your Voice/Everywhere, Ctrl+Space sub, Download for Windows / Launch simulator CTAs, capsule preview, works-in VS Code/Slack/Notion/Word/Any app), How it works (3 steps Connect/Summon/Flow), Interactive simulator (VS Code/Slack/Notion tabs with exact raw→polish scripts above + refine delete-and-retype demo), Features (6 cards with exact titles/text/foot above), About (no-subscriptions/sips-CPU/copilot+dictation), Privacy+shortcuts (Ctrl+Space dictation, Win+Shift companion, Ctrl+Win purge, Esc dismiss; DPAPI/no telemetry), Showcase CTA (Say it. Consider it done.), Download card (100% FREE ENTIRELY YOURS, specs, unsigned-build note, Ask-about-Voxula chat) + mobile companion strip + footer (Documentation/GitHub/Installer/Keyboard/Support, © 2026, DirectX line). Docs page with all 10 sections verbatim from §12. Modals: Settings (API key preview), Guide (3 tabs), Download (release card + thank-you steps), Support (4 FAQs). Chatbot with canned answers from §14. Keep all hotkeys, filenames, sizes, URLs exact.
