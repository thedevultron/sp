# SPEAK — Complete Feature Documentation

**SPEAK** is a Windows desktop application (Python / PySide6) that provides real-time voice dictation and a multimodal AI companion powered by the Google Gemini Live API. Speak into any app and the transcription is typed directly at your cursor; open the companion for a live, bidirectional voice conversation with optional screen sharing.

- **App name:** SPEAK
- **Version:** 2.1.0
- **Author / Publisher:** Amir Bagawan
- **Platform:** Windows 10/11 (macOS/Linux support is partial in `permission_manager`)
- **Entry point:** `main.py`
- **Source root:** `src/`

---

## Table of Contents

1. [Core Features](#1-core-features)
   - [Live Voice Dictation](#11-live-voice-dictation-ctrl--space)
   - [Multimodal Live Companion](#12-multimodal-live-companion-win--shift)
   - [Refine / Polish / Elaborate](#13-refine--polish--elaborate-voice-or-buttons)
   - [Custom Refine Actions](#14-custom-refine-actions)
   - [Live Screen Sharing](#15-live-screen-sharing)
   - [Screen Drawing Canvas](#16-screen-drawing-canvas-overlay)
   - [Multi-Session Engine](#17-multi-session-engine-ctrl--tab)
   - [Purge & Hard Reset](#18-purge--hard-reset-ctrl--win)
   - [Token / Context Usage Bar](#19-token--context-usage-bar)
   - [Persistent Memory](#110-persistent-memory-save_memory--forget_memory)
2. [Global Hotkeys](#2-global-hotkeys)
3. [User Interface](#3-user-interface)
   - [Floating Capsule](#31-floating-capsule-hud)
   - [Settings Window](#32-settings-window)
   - [System Tray](#33-system-tray)
   - [Onboarding Wizard](#34-onboarding-wizard)
   - [Icons & Window Effects](#35-icons--window-effects)
4. [Architecture & Modules](#4-architecture--modules)
5. [AI Models & Failover](#5-ai-models--failover)
6. [Configuration Reference](#6-configuration-reference)
7. [Security & Privacy](#7-security--privacy)
8. [Text Injection Engine](#8-text-injection-engine)
9. [Dependencies](#9-dependencies)
10. [Build, Install & Distribution](#10-build-install--distribution)
11. [Troubleshooting](#11-troubleshooting)

---

## 1. Core Features

### 1.1 Live Voice Dictation (Ctrl + Space)

Real-time speech-to-text that types into **any application** at the cursor position.

- **Audio capture:** 16 kHz mono microphone stream (`sounddevice`, 512-sample chunks) with automatic fallback to the default device if the configured device fails.
- **Transcription:** speech-to-text engine using a strict STT-only config — text responses + `input_audio_transcription` only (no tools/thinking/system prompt, which the transcribe server rejects).
- **Live preview:** Interim transcripts are shown in the capsule as you speak (`interim_updated` signal), before the finalized text is typed.
- **Multilingual:** automatic language detection by the model; SMART transcription mode (locked).
- **Auto-reconnect:** preview speech sessions cap at ~10 min. When the server closes cleanly (`go_away`), SPEAK automatically reconnects with the same key/config after 1 s — no user action needed.
- **Refine trigger detection:** spoken trigger words (e.g. saying "refine") are detected in both final and interim text mid-dictation.
- **Focus safety:** text is only typed when a non-SPEAK window is focused; typed content is measured per-session for exact delete-and-replace.

### 1.2 Multimodal Live Companion (Ctrl + /)

A bidirectional voice conversation.

- **Bidirectional audio:** mic uplink + 24 kHz speaker playback of the voice (voice `"Aoede"`).
- **Engine chain:** AI Engine with automatic fallback (deep-reasoning primary, fast backup, then legacy fallbacks), tried in order until one connects.
- **Reasoning depth:** thinking `LOW / MEDIUM / HIGH` (default `MEDIUM`, Settings > Preferences > Agent Reasoning). Transcription stays `SMART`-locked.
- **Live screen sharing:** optionally streams the screen to the model as motion-burst JPEG frames (~1 fps still, bursts on change up to the configured rate, default 3, max 15) — see [Live Screen Sharing](#15-live-screen-sharing).
- **Tool use:** type + send, desktop control, plus memory — all async (`NON_BLOCKING`):
  - **`typeTextAtCursor`** (content + verification flags + tone): drafts and types structured text into the focused field.
    - **Auto-Send (default, full authority):** text is typed and Enter is pressed automatically.
    - **Verification Active (opt-in):** text is typed but NOT submitted — you press Enter.
    - Model-supplied verification flags win; Settings defaults fill the gaps.
    - **Tone adaptation:** `concise` collapses whitespace; `formal/friendly/casual` ensure terminal punctuation.
  - **Desktop control (`pc_*`):** the agent operates the PC by voice — `pc_click`, `pc_double_click`, `pc_right_click`, `pc_move`, `pc_drag`, `pc_scroll`, `pc_type`, `pc_key`, `pc_hotkey`, `pc_wait`. Coordinates are 0–999 on the visible screen frame, scaled to the active monitor. One action per turn, narrated, grounded in the latest frame.
  - **`save_memory`** / **`forget_memory`**: durable user facts, capped small (see Memory below).
  - Guards: Unicode injection (no clipboard), focus checks, status confirmation + tool response on every call.
  - **PC safety governor:** desktop UI actions only (no shell); 25-step budget per session; identical-repeat refusal (no loops); every action audit-logged; stop-word / Esc halts instantly.
- **Echo/duplicate guard:** SHA1 digests of recently played audio chunks (10 s window, max 32 entries) prevent the same audio from playing twice when the server surfaces it both top-level and per-part.
- **Interruption handling:** barge-in flushes queued reply audio and clears the digest cache so an old turn never overlaps the new one.
- **System instruction:** customizable in Settings; SPEAK always appends a verbal-confirmation + cursor-tone suffix (never replaces user text).

### 1.3 Refine / Polish / Elaborate (voice or buttons)

Rewrite the dictation session text with one word or button press.

- **Actions:**
  - **Refine** — fixes a raw speech transcript: resolves self-corrections ("9pm actually 5pm" → keep 5pm only), removes filler ("um", "uh", "like"), fixes grammar/punctuation, normalizes times ("500pm" → "5:00 PM").
  - **Polish** — copyedit to publication-ready quality (word choice, rhythm, clarity).
  - **Elaborate** — expands the text with helpful detail, examples, and structure while staying faithful to final intent. (Legacy voice alias: **"expand"**.)
- **Two ways to trigger:** say the trigger word during dictation, or click the button in the capsule / tray Refine submenu.
- **Precise delete-and-replace:** the exact typed session text is deleted via measured Backspaces and replaced with the refined result. **No clipboard clobbering, no Ctrl+A, never presses Enter.**
- **Parallel fast path:** the refine call and the backspace deletion run concurrently (`asyncio.gather`) for speed.
- **Restore-on-failure:** if the engine fails after deletion, the original text is retyped (when focus is safe); if focus moved mid-refine, restore is skipped and the user is told the original is still in the capsule.
- **Engine:** automatic with built-in fallback chain; the API call runs off the event loop in an executor.
- **Output sanitization:** strips code fences, leading labels ("Refined text:"), balanced quotes; collapses excess newlines; caps at 4,000 chars.
- **Custom vocabulary:** custom words and the signature "Mark" are appended to refine prompts and the live system instruction.

### 1.4 Custom Refine Actions

Up to **3 user-defined rewrite actions** configured in Settings → Refine:

- Each has: name (max 24 chars), a unique voice trigger (2–24 chars, `a-z 0-9 -` only), and a prompt (max 2,000 chars).
- Appears everywhere after Save: capsule buttons, tray Refine submenu, and voice triggering.
- Trigger conflicts with built-ins are rejected at save time; everything is sanitized (charset + length caps) on load.

### 1.5 Live Screen Sharing

Companion mode can see your screen.

- **Capture:** `mss` grab of the monitor under the cursor (active screen, primary fallback) → PIL downscale (min 640×360, capped to 1280 px width) → JPEG (quality 72; MEDIUM detail ≈ 560 tokens/frame, HIGH ≈ 1120). Steady send: 1 fps heartbeat when still, at most 1 frame per 0.5 s on change (server-friendly — flooding got throttled into blindness). The loop never quits on errors: backoff retries while the session lives, restartable mid-session. Stale permission gates re-check (throttled) instead of blanking forever. First live frame confirms `Companion Live + Screen — agent can see`; every 20th frame logs effective fps + bytes as flow proof.
- **Detail setting:** **Preferences → Live Screen → Frame detail** — MEDIUM (default, balanced) or HIGH (max clarity, ~2x context burn).
- **Toggle anywhere:** capsule monitor button, Settings checkbox, or config — all kept in sync bidirectionally (no feedback loops). Takes effect live mid-session (new send loop spawned without touching audio).
- **Performance:** capture and JPEG encoding run in an executor so the event loop never blocks (50–400 ms/frame on 4K).
- **Resilience:** ≥10 consecutive blank frames warn (but voice continues); ≥20 send failures give up on video while keeping the voice session alive. A screen crash can never kill the audio session (supervised separately).
- **Token accounting:** each frame costs an estimated +560 tokens (MEDIUM) or +1120 (HIGH); exact totals sync from API usage metadata.

### 1.6 Screen Drawing Canvas (overlay)

Full-screen transparent annotation layer for marking up the desktop during a session.

- Spans the entire virtual desktop (multi-monitor aware).
- **Draw:** left-drag freehand strokes.
- **Colors:** `1`/`B` = Blueprint Blue (default), `2` = Ember Glow, `3` = Frost Glow.
- **Clear:** right-click clears all strokes; `Ctrl+C` clears without hiding.
- **Exit:** `Esc` clears and hides the overlay.
- Dimmed background tint + top hint banner while active.

### 1.7 Multi-Session Engine (Ctrl + Tab)

Hot-swappable live sessions with FIFO eviction.

- **Ctrl+Tab:** spawns a new session record, stops the current live audio/screen, and starts a fresh live companion immediately. Also available as a window-level shortcut fallback and a button on the Sessions page.
- **Session records** hold lightweight metadata only (the live handles stay in `GeminiLiveManager`): session id, mode (`dictation`/`companion`/`none`), model, created/last-active timestamps, transcript chars/words, status (`active`/`stored`/`evicted`).
- **FIFO eviction:** when the stored count exceeds the max (default 5, configurable 1–20), the oldest-created non-active session is evicted first — the active session is never evicted.
- **Live stats:** each session's transcript chars/words update live; the Sessions page auto-refreshes via the `sessions_changed` signal.
- **Count indicator** is live from launch (first session is seeded at startup).

### 1.8 Purge & Hard Reset (Ctrl + Win)

One-keystroke total reset:

- Stops the current session (mic, playback, screen).
- Clears the transcript buffer, injection history, and token counter.
- Hard-resets the live connection.

### 1.9 Token / Context Usage Bar

- 3 px progress bar under the capsule pill row.
- **Semantic colors:** green ≤60%, orange ≤85%, red >85% of the 128,000-token context window.
- **Hover tooltip:** exact counts (`Context  12,345 / 128,000  (9.6%)`), session elapsed time, and "Reset Ctrl+Win" hint.
- Audio chunks estimated at `len/320` tokens; companion sessions sync exact totals from the API's `usage_metadata`.

### 1.10 Persistent Memory (`save_memory` / `forget_memory`)

The companion remembers small facts about you across sessions without eating the context window.

- **Store:** `%APPDATA%\SPEAK_AI\user_memory.json` — atomic writes, sanitized (control chars stripped, whitespace collapsed).
- **Caps (token-cheap):** max 30 facts, 140 chars each, 1500 chars total (~350 tokens); prompt block capped at ~1200 chars. Dedupes exact repeats.
- **Agent tools:** `save_memory(fact)` ("remember my deploy key is…", keep under 20 words) and `forget_memory(query)` (fact id or keyword substring).
- **Auto-load:** every companion connect prepends `User memory (persisted across sessions…)` bullet list to the system instruction.
- **Purge (`Ctrl+Win`) clears transcript + tokens only — memory survives until `forget_memory` or manual file delete.**

---

## 2. Global Hotkeys

System-wide (work in any app), implemented with a `pynput` keyboard listener (daemon thread, keys are **not** suppressed).

| Combo | Action | Guards |
|---|---|---|
| **Ctrl + Space** | Show capsule + start/toggle dictation | Highest priority; Space discarded after fire |
| **Ctrl + /** | Show capsule + start/toggle companion | Replaces Win+Shift (avoids Snip clash); `/`/`?`/OEM VKs all map to slash |
| **Ctrl + Win** | Purge & hard reset (transcript + tokens, not memory) | Fires on the chord; Win is sticky-safe |
| **Ctrl + Tab** | New live session (spawn + switch) | Only when Space is not also pressed; window-level `QShortcut` fallback when the global hook is suppressed by focus |
| **Esc** | Stop live session only (app keeps running in tray) | Ignored when idle; never suppresses Esc in other apps |

Details:

- **Debounce:** 600 ms per action — holding keys or key-repeat can't double-fire.
- **Key normalization:** both Windows keys (VK 91/92) map to `WIN`; ctrl/cmd variants normalized.
- **Misfire protection:** combo exclusivity (e.g. Ctrl+/ suppressed while Space/Tab is held).
- Thread-safe signal emission; listener failures never crash the thread.

---

## 3. User Interface

The app follows an "Authkit frosted-glass / midnight" design system: midnight surfaces (`#0B1023`/`#05060F`), frost text (`#D1E4FA`), and **Void Violet (`#663AF3`)** as the only chromatic CTA color — everything else stays monochrome. Lucide-style stroke icons only, no emoji.

### 3.1 Floating Capsule (HUD)

An always-on-top, frameless, translucent, **draggable** capsule centered above the taskbar.

- **Hidden on startup** — appears only on hotkey, tray toggle, or notification click. Correctly positioned on multi-monitor / high-DPI setups and never extends under the taskbar (live geometry re-clamping via `sig_geometry_changed`).
- **Custom title bar (30 px):** status dot + "SPEAK · Ctrl+Space to dictate" + close-only chrome button. Open-hand drag via event filter (buttons never start a drag).
- **Pill row:** elided status label (full text in tooltip) → animated 5-bar **wave visualizer** (mic = frost grey gradient, Gemini = ice-blue gradient; idle "breathing" sine drift; 16 ms eased animation) → hint word (Listening / Working / Error / Refining / Ready, color-coded) → **Settings**, **Guide**, **Hide** buttons.
- **Mini capsule:** titlebar `−` (or double-click) minimizes to a ~330×52 icon-only pill — 7-bar live wave in the middle (extends up/down while you speak, stills when silent; click it to expand), then Transcript / Screen / Settings / Expand / Hide icon buttons, no text, tooltips on hover. Transcript-button expands and opens the sheet; screen toggle stays synced with full mode.
- **Token bar** under the pill row (see above).
- **Inline controls:** Transcript panel toggle (chevron), checkable **screen-share toggle** (monitor/eye-off icon), inline interim transcript label.
- **Expandable transcript sheet:** live word count, **Copy** button (turns "Copied" ✓ for 1.3 s), **Clear** button, read-only transcript (placeholder: "Transcription appears here. Say refine, polish or elaborate."), and a REFINE row of up to 6 action buttons (Refine [violet], Polish, Elaborate + custom actions) with the active voice triggers listed as a hint.
- **Close semantics:** titlebar ✕ and Hide both stop the session and hide to tray (app keeps running).
- **Resize:** size grip + manual bottom-right resize zone (height capped at 620 px); custom painted glass plate with halo shadow, frost highlight, and hairline border; Windows 11 rounded corners applied on show.

### 3.2 Settings Window

The app's main window — opens **maximized with native OS chrome** (native drag + Aero Snap preserved deliberately). Esc hides to tray. Collapsible sidebar (208 px → 58 px icons-only) with six pages:

| Page | Contents |
|---|---|
| **Setup** (API keys) | Primary key (password field + Show + Test), backup keys list (**masked previews only** — `AIzaSy…last4 (N chars)`) with auto-switch on quota, embedded free-tier badge when active, Enter-to-add, duplicate detection. |
| **Guide** (Shortcuts) | Shortcut rows (Ctrl+Space / Ctrl+/ / Ctrl+Win / voice refine), tray tip, capsule behavior card (close-only chrome, status dot colors, refine semantics). |
| **Preferences** | Microphone device picker + Refresh, custom words + signature Mark, system prompt, creativity slider (0.00–2.00, default 0.30), "Share live screen in companion" checkbox (motion bursts), "Launch on Windows startup" checkbox, **Message Verification** radio (Verification Active vs Auto-Send), read-only **Live Configuration Locks** badges (Transcription SMART, Thinking HIGH, live tools). |
| **Refine** | Per-action prompts + voice triggers for Refine/Polish/Elaborate, up to 3 custom actions (enable checkbox, name, unique trigger, prompt), Reset-to-defaults button. |
| **Sessions** | Multi-Session Engine controls: Max Stored Sessions slider + spinbox (1–20, default 5), live active/stored counts, stored-session list (`● active` / `○ stored` with mode, status, words, created time), New Session (Ctrl+Tab) button. |
| **Help** | Feature directory (Screen Share, Live Transcription, Smart Insertion), shortcut cheat-sheet table, troubleshooting Q&A (cursor typing, permission banner, mic, Live connect failures). |

Additional UI features:

- **Permission banner:** amber inline diagnostic (shown when screen capture is pending/denied) with a violet **Grant Permission** button (triggers the native OS dialog + capture retry) and a **Later** dismiss.
- **Model bar:** live badges for the dictation and companion models plus the locked "Thinking HIGH · Transcription SMART" badge.
- **API status badge** in the header (green/orange/red/muted), updated by key tests and permission events.
- **Save & Launch** validates keys and custom triggers (warns via message box, offers free-tier save anyway), sanitizes all values, persists, refreshes refine UI in capsule + tray, and notifies readiness (capsule stays hidden until hotkey).
- Painted midnight backdrop with radial spotlight + blueprint grid; all pages in smooth-scroll areas.

### 3.3 System Tray

Minimal dark tray (`QSystemTrayIcon`) — the app lives here when windows are closed.

- **Menu items (in order):** Show/Hide capsule · Dictation (Ctrl+Space) · Companion (Ctrl+/) · Purge (Ctrl+Win) · **Refine submenu** (built-ins + enabled custom actions, max 6) · Guide · Settings · Exit (salmon).
- **Activation:** single click, double click, or clicking any notification toggles the capsule.
- **Notifications:** balloon notifications (default 2,800 ms) for readiness, save, refine completion ("replaced — N words in target app"), permission events, errors, and new sessions.
- Tooltip: `SPEAK · Ctrl+Space to dictate`.

### 3.4 Onboarding Wizard

First-run "Welcome to SPEAK" modal (two steps, 520×400):

1. **API key page** — password input (pre-filled from vault) with a **Test** button that pings Gemini and shows Validated (green) or the error (ember).
2. **Guide page** — the three essential shortcuts + tray tip. **Finish** marks `first_run_completed` and closes.

### 3.5 Icons & Window Effects

- **`icons.py`:** dependency-free Lucide icon provider — ~40 inline SVG paths rendered via `QSvgRenderer` (24×24, stroke 1.85, round caps, Moon Mist `#C7D3EA` default, tintable per call, `info` fallback).
- **`window_effects.py`:** Windows 11 DWM helpers via ctypes — rounded corners (`DWMWCP_ROUND`), 1 px border-artifact removal (`DWMWA_BORDER_COLOR` = COLOR_NONE), DWM shadow (`DwmExtendFrameIntoClientArea`), and optional **Mica** backdrop. All are safe no-ops on unsupported systems.
- **App icon:** auto-generated minimal icon (blue waveform bars on rounded black base) if missing — used for window, tray, and installer.

---

## 4. Architecture & Modules

```
main.py                       App lifecycle, single-instance guard, wiring, capsule positioning
└── src/
    ├── config.py             ConfigManager ("config_vault") — settings, API-key vault, sanitization
    ├── _embedded_key.py      Obfuscated embedded fallback API key (free tier)
    ├── hotkeys.py            GlobalHotkeyListener — system-wide hotkeys (pynput)
    ├── audio_engine.py       AudioEngine — mic capture, RMS visualizer feed, playback pipeline
    ├── gemini_client.py      GeminiLiveManager — Live modes, refine, failover, tool use, tokens
    ├── injection_service.py  InjectionService — precise cursor typing + delete-and-replace
    ├── screen_engine.py      ScreenEngine — permission-gated screen capture → JPEG frames
    ├── permission_manager.py ScreenPermissionManager + MicPermissionManager — OS permission handshakes + diagnostics
    ├── session_manager.py    SessionManager — multi-session metadata + FIFO eviction
    ├── transcript_buffer.py  TranscriptBuffer — transcript history, interim preview, autosave
    ├── tray.py               SpeakSystemTray — tray menu, notifications, signals
    └── ui/
        ├── floating_capsule.py  Capsule HUD (wave visualizer, token bar, transcript sheet)
        ├── settings_dialog.py   Main settings window (6 pages, permission banner, model bar)
        ├── onboarding_wizard.py First-run wizard (API key + guide)
        ├── screen_canvas.py     Full-screen annotation overlay
        ├── icons.py             Lucide icon renderer
        └── window_effects.py    Windows 11 DWM effects
```

**Data flow:**

```
Hotkeys / Tray / Capsule buttons
        ↓
GeminiLiveManager (modes, refine, failover, tool use)
        ↓                                  ↓
AudioEngine (mic + playback)        ScreenEngine (frames → Live)
        ↓
TranscriptBuffer (history)  +  InjectionService (typing at cursor)
        ↓
Qt signals → Capsule UI / Tray notifications / Settings UI
```

**Key engineering patterns:**

- **qasync** integrates the asyncio event loop with Qt — async pipelines drive all Live communication; blocking work (API calls, screen capture, typing) runs in executors/threads so the UI never freezes.
- **Defensive imports:** every external dependency (`mss`, `pyautogui`, `pynput`, `ctypes`, `win32`, Quartz, `google-genai`) is imported with capability flags and fallback chains.
- **Signal-driven sync:** capsule ↔ settings ↔ engine state (screen share, sessions, refine actions) is kept consistent with `blockSignals` guards against feedback loops.
- **No silent failures:** errors surface as statuses, banners, or tray notifications; every async flow is cancellation-safe (refine flag can never wedge).

---

## 5. AI Engine & Failover

| Purpose | Engine |
|---|---|
| Dictation (speech-to-text) | AI Engine (auto-reconnect on clean close) |
| Companion (live voice) | AI Engine with automatic fallback chain |
| Refine (text) | AI Engine with automatic fallback chain |

- **Retired-ID auto-repair:** known-bad engine IDs stored in old configs are silently upgraded. User-custom values are never wiped.
- **Key rotation:** on engine failure after all fallbacks are tried, SPEAK rotates to the next API key (primary → env → backups → embedded) and restarts the mode.
- **Failover storm guard:** ≥3 failovers within 30 s stop loudly with guidance instead of hot-looping; a successful connect resets the counter.
- **Dictation 400 special case:** a config rejection stops with an "upgrade the SDK (google-genai ≥ 2.22)" hint rather than rotating keys pointlessly.
- **Reasoning depth:** thinking `LOW / MEDIUM / HIGH` (default `MEDIUM`, Settings-selectable). Transcription mode **SMART** is enforced on every connect and cannot be downgraded by a hand-edited config file.
- **Error classification:** exceptions are bucketed into quota/rate-limit, model-not-found, bad-request, auth, server-unavailable, connect-error — with actionable messages that never contain key text.

---

## 6. Configuration Reference

Stored at `%APPDATA%\SPEAK_AI\config.json` (atomic writes, user-only ACL). API keys are stored separately in **Windows Credential Manager** (keyring service `SPEAK_AI_App`).

| Key | Default | Purpose |
|---|---|---|
| `dictation_model` | `gemini-3.5-transcribe-live` | STT model |
| `companion_model` | `gemini-3.8-live-extended-thinking` | Live companion model (primary) |
| `companion_backup_model` | `gemini-3.8-live` | First fallback |
| `refine_model` / `refine_fallback_model` | `gemini-3.5-flash-lite` / `gemini-3.1-flash-lite` | Refine chain |
| `temperature` / `top_p` | 0.2 / 0.95 | Sampling (temperature slider 0–2, cooler default curbs hallucinations) |
| `thinking_budget` | 0 | Legacy (2.5-era); 3.x uses thinking levels instead |
| `live_thinking_level` | `MEDIUM` | Agent reasoning depth: `LOW` / `MEDIUM` / `HIGH` (Settings > Agent Reasoning) |
| `verification_mode` | `auto_send` | `auto_send` (type + Enter, full authority) or `verification_active` (type + wait for Enter) |
| `max_stored_sessions` | 5 | Multi-session FIFO limit (1–20) |
| `system_instruction` | SPEAK persona | Custom companion instruction |
| `windows_startup` | false | Launch on Windows startup (Startup-folder .bat) |
| `first_run_completed` | false | Onboarding wizard gate |
| `audio_device_index` | null | Microphone selection |
| `screen_fps` | 3.0 | Live vision max burst rate (clamped 0.2–15; static screens heartbeat at ~1 fps regardless) |
| `pen_color` / `pen_width` | `#0A84FF` / 3 | Drawing canvas defaults |
| `auto_refine_replace` | true | Refine replaces session text |
| `transcript_autosave` | false | Persist transcript history between actions (history starts fresh each launch) |
| `custom_words` | [] | Vocabulary hints (max 80) |
| `custom_mark` | "" | Signature appended to prompts (max 120) |
| `enable_screen_share` | true | Companion screen sharing on by default |
| `screen_detail` | `MEDIUM` | Frame detail: `MEDIUM` (~560 tok/frame) or `HIGH` (~1120 tok/frame) |
| `refine_prompts` / `refine_triggers` | {} / defaults | Settings-editable prompts and voice triggers |
| `custom_actions` | [] | Up to 3 custom refine actions |
| `live_thinking_level` / `live_transcription_mode` | MEDIUM / SMART | Thinking is Settings-selectable; transcription is **locked** |

**API key resolution order:** primary vault key → `GEMINI_API_KEY` env → backup keys (up to 20) → embedded fallback key (only if user has none). Keys are validated for length (20–256) and `AIza` prefix warnings; rotation happens on failover.

---

## 7. Security & Privacy

### API keys

- Stored in **Windows Credential Manager** via `keyring` — never in the config file.
- **Masked everywhere:** UI shows `AIzaSy…last4 (N chars)`; logs use `abc123***wxyz` or `embedded(hidden)`; error messages redact the key prefix.
- **Embedded fallback key** (`src/_embedded_key.py`): obfuscated as 3 base64 fragments of an XOR-ed value keyed by app identity — a binary strings-dump won't reveal it; used only for the free tier when the user has no keys; never logged or displayed.
- Backup keys sanitized: deduped, length-checked, capped at 20.

### Config integrity

- Atomic writes (`.tmp` → replace) with fallback direct write.
- ACL restricted to the current user (`icacls /inheritance:r /grant:r`) with `CREATE_NO_WINDOW` (no terminal flash).
- **All stored values sanitized on load:** clamps (sessions 1–20, fps 0.2–15, temp 0–2), charset regex cleaning, length caps (prompts 2,000, words 80×40, triggers 2–24, memory facts 30×140 chars / 1500 total), control-char stripping (prompt-injection hygiene), uniqueness enforcement. Transcription mode (SMART) can never be downgraded; thinking depth is validated to LOW/MEDIUM/HIGH.

### Text injection safety

- **Never presses Enter** from the injection service (reserved for the caller's auto-submit).
- **Never uses the clipboard** and never sends Ctrl+A — user content outside the measured session can't be destroyed.
- **Foreground verification:** before every injection and every 200 presses during long backspace floods, SPEAK verifies it is not deleting into its own window; on focus-skip it does nothing (history kept for a correct retry).
- 4,000-char caps on typed history and deletes; chunked Win32 `SendInput` arrays (120 presses per chunk with pauses); honest return counts.

### Runtime safety

- **Single-instance guard:** `QLockFile` prevents double instances (double hotkeys / double mic).
- Bounded queues everywhere (mic 200, playback 256 chunks; chunk size capped at 4 s of audio) with drop-oldest policies — no memory blowups, event loop never blocked.
- Watchdogs: double-fire guards, failover storm guard, mic-dead detection, blank-frame streak warnings.
- Watchdog timers and playback run on dedicated threads; `stream.write` never runs on the asyncio loop.

### Privacy

- Microphone and screen streams are only captured during active sessions and sent only to Google's Gemini API.
- Transcript history starts **fresh every launch** (previous sessions are deliberately not restored); autosave is optional and off by default.
- No analytics, no accounts, no network calls other than Gemini.

---

## 8. Text Injection Engine

`InjectionService` types dictation/refined text into the foreground app with exact per-session accounting:

- **Typing backends:** Win32 `SendInput` with `KEYEVENTF_UNICODE` per-character pairs (arbitrary Unicode, no clipboard) → pyautogui fallback. Short text (<180 chars) prefers ctypes SendInput; longer text prefers pyautogui `write`.
- **Deletion backends:** pynput BackSpace floods (abort mid-flood if focus moves) → SendInput VK_BACK chunks → pyautogui.
- **Session accounting:** every typed segment is measured; `precise_replace` deletes exactly the measured count (falling back to the transcript snapshot length when no history exists), then types the refined text and resets history so the *next* refine deletes exactly the refined content.
- **Focus restore:** remembers the last non-SPEAK target window and can restore focus before deleting.
- **Async API:** `precise_replace_async` runs the blocking replace on an executor thread.

---

## 9. Dependencies

| Package | Version | Purpose |
|---|---|---|
| PySide6 | 6.8.2 | Qt 6 GUI (widgets, tray, signals) |
| qasync | 0.27.1 | asyncio ↔ Qt event-loop integration |
| google-genai | ≥2.19.0, <3.0.0 | Gemini Live SDK (SMART transcription needs ≥2.19) |
| pynput | 1.8.1 | Global keyboard listener (hotkeys) |
| sounddevice | 0.5.2 | Mic capture + audio playback |
| numpy | 2.1.3 | Audio sample processing |
| mss | 10.1.0 | Fast screen capture |
| pillow | 11.1.0 | JPEG frame encoding |
| pywin32 | 310 | Win32 APIs (SendInput, DWM, ACLs) |
| keyring | 25.6.0 | Windows Credential Manager key storage |
| pyautogui | 0.9.54 | Legacy input automation fallback |
| pyinstaller | 6.12.0 | Build tool (not a runtime dep) |

---

## 10. Build, Install & Distribution

- **Build EXE:** `python build.py` → PyInstaller `--onefile --windowed` → `dist\SPEAK.exe` (~90–130 MB) with assets bundled, embedded key hidden-imported, `google.genai` collected, version stamped, plus SHA256 and signing note.
- **Installer:** Inno Setup 6 (`installer.iss`) → `installer\SPEAK_Setup_v2.1.exe`. One-click, `PrivilegesRequired=lowest` (no admin needed), LZMA2/ultra64 compression, optional desktop icon and startup tasks (unchecked by default), uninstaller included, publisher "Amir Bagawan".
- **Running from source:** create a venv, `pip install -r requirements.txt`, run `python main.py` (uses `pythonw.exe` via the startup .bat when registered).
- **First run:** onboarding wizard → API key (or free tier with the embedded key) → guide.

See `HOW_TO_INSTALL.md` for the step-by-step installer guide.

---

## 11. Troubleshooting

| Symptom | Cause | Fix |
|---|---|---|
| Cursor not typing | SPEAK window focused, verification waiting for Enter, or focus moved during injection | Click into the target app first; press Enter if Verification Active; retry |
| Amber permission banner | OS blocked/denied screen capture | Click **Grant Permission** (opens native settings), approve, then grant again |
| Mic silent | Wrong device selected | Settings → Preferences → Refresh device list |
| "Model unavailable, trying next…" | Live model down/unreachable | Automatic model + key failover; add a backup key; check model IDs |
| Refine focus warning | You switched windows mid-refine | Original text is kept in the capsule; re-run refine with the target app focused |
| Capsule hidden | By design on startup | Press Ctrl+Space or click the tray icon |
| Persistent connect failure | 3 failovers in 30 s (storm guard) | Stop loudly — verify API keys and companion model IDs |
| Dictation stops after ~10 min | Preview STT session cap | Automatic reconnect (same key/config) — no action needed |
| Quota errors (429) | Key rate limits | Add backup keys (auto-switch) or rely on embedded-key rotation |
