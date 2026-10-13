# SPEAK — Usage Docs

> Voice dictation + live AI companion for Windows 10/11. Speak into any app; the companion can see your screen, press keys, click, type, and remember you.
> Version 2.1.0 · By Amir Bagawan · `DOCS.md` (user guide) — dev details live in `FEATURES.md`.

---

## Contents

1. [Install & first run](#1-install--first-run)
2. [Hotkeys cheat sheet](#2-hotkeys-cheat-sheet)
3. [Dictation — speak to type](#3-dictation--speak-to-type)
4. [Companion — live voice + screen](#4-companion--live-voice--screen)
5. [Letting the agent control your screen](#5-letting-the-agent-control-your-screen)
6. [Refine / Polish / Elaborate](#6-refine--polish--elaborate)
7. [Memory — what SPEAK remembers](#7-memory--what-speak-remembers)
8. [Floating capsule (full + mini)](#8-floating-capsule-full--mini)
9. [System tray](#9-system-tray)
10. [Settings guide](#10-settings-guide)
11. [Multi-session + purge](#11-multi-session--purge)
 12. [AI Engine, tokens & limits](#12-ai-engine-tokens--limits)
13. [Privacy & safety](#13-privacy--safety)
14. [Troubleshooting](#14-troubleshooting)

---

## 1. Install & first run

1. Install with `installer\SPEAK_Setup_v2.1.exe` (no admin needed) and launch SPEAK.
 2. Settings opens fullscreen. Optional: paste an API key (`AIzaSy…` from [Google AI Studio](https://aistudio.google.com/app/apikey)) into **Setup → Primary API key**, click **Test**, then **Save & Launch**.
   - No key? The built-in free tier works immediately.

   - Add **backup keys** to survive quota errors — SPEAK auto-switches.
3. Pick your microphone in **Preferences** if the default is wrong (use **Refresh** after plugging hardware).
4. The capsule stays hidden until you press a hotkey — SPEAK lives in the system tray near the clock.

> Startup launch is opt-in only (**Preferences → Launch on Windows startup**).

---

## 2. Hotkeys cheat sheet

All hotkeys are global (work in any app). Keys are never swallowed — other apps keep their behavior.

| Press | What happens |
|---|---|
| **Ctrl + Space** | Dictation on/off. Types what you say at the cursor. Press again to stop. |
| **Ctrl + /** | Companion on/off. Live voice + screen. Press again to stop. The `/` key is the slash key (US/UK `?` and OEM variants also work). |
| **Esc** | Stop whatever is live (dictation or companion). The app keeps running in the tray. Ignored when idle. |
| **Ctrl + Win** | Purge: stop session, clear transcript + typed history + token counter, hard-reset the connection. Memory is kept. |
| **Ctrl + Tab** | New live session: spawn + switch immediately (old session stored, FIFO eviction applies). |

Tip: if a chord misfires, release all keys and press it cleanly once — every action is debounced (600 ms).

---

## 3. Dictation — speak to type

Press **Ctrl + Space**, click into any text field (Notepad, Word, browser, chat…), and speak.

- **Live preview:** interim text appears in the capsule as you talk; finalized words are typed automatically with punctuation.
- **Hands stay free:** say `refine`, `polish`, or `elaborate` mid-flow to rewrite the session (see §6).
- **Multilingual:** auto-detected, SMART transcription locked on.
- **Long sessions:** speech sessions cap previews at ~10 min — SPEAK reconnects automatically on the same key; keep talking.
- **Nothing typed?** Click the target app first (SPEAK never types into itself), check **Verification mode** (§10), and watch the capsule wave bars to confirm the mic is live.

Good first test: open Notepad → **Ctrl + Space** → say *"Meeting moved from 9pm actually 5pm"* → say *"refine"* → you get *“Could we schedule the meeting for 5:00 PM?”* typed in place.

---

## 4. Companion — live voice + screen

Press **Ctrl + /** for a real-time voice conversation (voice `Aoede`, mic uplink + 24 kHz speaker replies). The capsule shows `Companion (…) + Screen` or `— Voice only`.

**Screen sharing (default ON, motion-burst vision):**

1. On first share, approve the OS permission prompt / Settings banner (**Grant Permission**). Voice continues even if screen is blocked.
2. The agent watches the monitor under your cursor (active screen): ~1 JPEG frame/sec when still, reacting within ~0.5 s the moment anything changes. Frames are downscaled (1280 px max, quality 72; MEDIUM detail ≈ 560 tokens each, HIGH ≈ 1120). First live frame confirms `Companion Live + Screen — agent can see`. Vision auto-retries through blips and never quits mid-session — if the AI reports blank, fix permissions first (§14).
3. Toggle vision anytime without killing audio: capsule monitor button, **Preferences → Share live screen**, or just ask (*“turn screen share off”* is voice-only from then on). Frame detail (Medium/High) lives in **Preferences → Live Screen**.
4. Each MEDIUM frame costs ~560 tokens — a busy screen at high rates burns context fast, so static moments are skipped automatically. Watch the token bar on long screen sessions.

**Talk naturally:** interrupt anytime (barge-in flushes stale reply audio), ask follow-ups, dictate messages for it to type.

---

## 5. Typing + sending for you

The companion types at your cursor and sends with Enter — full authority, no confirmation asks. It always confirms verbally what it sent.

**What to say (examples):**

- *“Type the release note draft, friendly tone, and send it.”*
- *“Reply to this email saying I'll join at 5, then send.”*
- *“Type the command and press Enter.”*

**How it works (`typeTextAtCursor`):**

1. You speak — the AI Engine drafts the text (tone adapts: formal docs/mail, friendly chat, concise code).
2. SPEAK types it at the cursor via Unicode injection (no clipboard).
3. **Auto-Send** (default) presses Enter immediately; **Verification Active** (opt-in, Preferences) waits for your Enter.
4. The capsule status + voice confirm what was sent.

Full authority means it acts immediately — say exactly what you want sent.

**Desktop control (Companion):**

The agent also operates your PC by voice — click, type into fields, scroll, drag, hotkeys — acting only on what it sees in the live screen frames, one step at a time, narrating as it goes.

- *“Click the Send button.”* · *“Scroll down twice.”* · *“Open the file menu and click Export.”*
- *“Type hello@acme.com in the email field and press Enter.”* · *“Press Ctrl+S.”*

**Safety governor (always on):** desktop UI actions only (no shell, no background programs); 25-step budget per session; refuses to repeat a failed step (no loops); every action audit-logged; say **stop** (or Esc) to halt instantly. Reasoning depth: **Preferences → Agent Reasoning** (Low/Medium/High, default Medium).

---

## 6. Refine / Polish / Elaborate

Rewrite everything typed **this session** (since dictation start or last purge) with one word or click.

| Action | Say | Does |
|---|---|---|
| **Refine** | *“refine”* | Fixes transcript: resolves self-corrections (keeps final intent only), drops filler, fixes grammar, normalizes times (`500pm` → `5:00 PM`). |
| **Polish** | *“polish”* | Copyedit to publication quality. |
| **Elaborate** | *“elaborate”* (`expand` still works) | Expands with detail, examples, structure. |

**Ways to trigger:** voice mid-dictation · capsule REFINE buttons · tray → Refine submenu.

**Mechanics:** exact measured delete (Backspaces, no clipboard, no Ctrl+A) + retype, run in parallel for speed. Never presses Enter. If the engine fails after deleting, the original is retyped when focus is safe — otherwise you're told it's still in the capsule. Custom vocabulary + signature Mark are honored.

**Custom actions (up to 3):** **Settings → Refine** — name (≤24) + unique trigger (`a-z0-9-`, 2–24 chars) + prompt (≤2000). Appears in capsule + tray + voice instantly after Save. Example: name `Summarize`, trigger `summarize`, prompt `Summarize the following in 3 bullets…`.

**Rewrite engine:** automatic with built-in fallback. No setup needed.

---

## 7. Memory — what SPEAK remembers

The agent keeps small durable facts (name, preferences, project names, vocabulary) across restarts — capped so it stays cheap (~350 tokens max).

- **Teach it:** *“Remember my deploy key is X.” / “Remember I prefer dark mode.”* → `save_memory` (keep under ~20 words). Capsule/tray confirm `Remembered (…)`.
- **Auto-use:** every companion connect prepends your bullet list to its instructions, so replies stay consistent.
- **Forget:** *“Forget dark mode.”* → `forget_memory` (id or keyword). Purge does **not** wipe memory.
- **Storage:** `%APPDATA%\SPEAK_AI\user_memory.json` — max 30 facts × 140 chars, 1500 total, exact-duplicate proof. Delete the file to wipe fully.

---

## 8. Floating capsule (full + mini)

Always-on-top pill centered above the taskbar. Hidden on startup — appears on hotkey / tray / notification. Never slides under the taskbar.

**Full capsule:**

- **Title bar:** status dot + `SPEAK · Ctrl+Space to dictate` + `−` minimise + `✕` close (double-click titlebar also minimizes). Drag by the bar only.
- **Pill row:** status text (full text in tooltip) → 5-bar wave (grey = mic, ice-blue = voice, gentle idle drift) → hint word (`Listening Working Error Refining Ready`) → **Settings / Guide / Hide**.
- **Token bar:** 3 px, green ≤60% → orange ≤85% → red; hover for exact counts + session time.
- **Controls:** Transcript toggle (chevron), screen toggle (monitor / eye-off), live interim line.
- **Transcript sheet:** word count, **Copy** (flips to `Copied ✓`), **Clear**, read-only text, REFINE buttons + trigger hint.
- **Close/Hide** stops the session and hides to tray (app keeps running).

**Mini capsule (`−`, ~330×52, icon-only, no words):**

- 7-bar live wave in the middle — extends up/down while you speak, stills when silent. **Click the wave to expand.**
- Icons only with hover tooltips: Transcript (expands + opens sheet) · Screen toggle (synced) · Settings · Expand · Hide.
- Drag by the background/dot. Ideal while presenting or screen-sharing.

---

## 9. System tray

Home base when windows are closed (tooltip `SPEAK · Ctrl+Space to dictate`).

Menu in order: **Show/Hide capsule · Dictation (Ctrl+Space) · Companion (Ctrl+/) · Purge (Ctrl+Win) · Refine submenu (built-ins + customs, max 6) · Guide · Settings · Exit**. Single/double-click or notification-click toggles the capsule. Balloon notifications confirm saves, refines (`…replaced — N words`), speaker/screen events, sessions, and errors.

---

## 10. Settings guide

Opens **maximized** (native chrome, Aero Snap intact). **Esc** hides to tray. Sidebar collapses 208 px → 58 px.

| Page | Use it for |
|---|---|
| **Setup** | Primary key (paste → **Test** → Save), backup keys (masked `AIzaSy…last4`, auto-switch on quota), free-tier badge. Enter adds. |
| **Guide** | Shortcut cards + capsule behavior reference. |
| **Preferences** | Mic picker + Refresh · custom words + Mark · system prompt · creativity slider (0–2, default 0.30) · **Share live screen** (motion bursts) · startup launch · **Message Verification** (Active = you press Enter / Auto-Send = automatic) · read-only locks (SMART · HIGH · type + memory). |
| **Refine** | Prompts + triggers for Refine/Polish/Elaborate, 3 custom actions, reset defaults. |
| **Sessions** | Max-stored slider (1–20, default 5), live active/stored counts, stored list (`● active` / `○ stored` + mode/words/time), **New Session** button. |
| **Help** | Step-by-step (Screen Share / Transcription / Smart Insertion), shortcut table, troubleshooting. |

**Permission banner** (amber, top of Settings when screen is blocked): **Grant Permission** fires the native OS prompt + retry; **Later** dismisses. **Save & Launch** validates, refreshes capsule + tray immediately, keeps the capsule hidden until hotkey.

---

## 11. Multi-session + purge

- **Ctrl+Tab / Sessions → New Session:** spawns a record, stops current audio/screen, starts a fresh companion. Records hold metadata only (id, mode, timestamps, chars/words, status). Oldest non-active evicts first when over max (active is never evicted). Counts are live from launch.
- **Ctrl+Win purge:** stops everything, clears transcript + injection history + tokens, hard-resets. Use before sensitive dictation. Memory survives purge by design.

---

## 12. AI Engine, tokens & limits

| Job | Engine |
|---|---|
| Dictation (speech-to-text) | AI Engine (auto-reconnects on server close) |
| Companion (voice+screen+PC) | AI Engine with automatic fallback |
| Refine (rewrite) | AI Engine with automatic fallback |
| Type + send | `typeTextAtCursor` with Auto-Send (Enter) |
| Desktop control | `pc_click / pc_type / pc_scroll / pc_key / pc_hotkey / pc_drag / pc_move / pc_wait` (async, governed: 25-step budget, no-loop guard, audit log) |

- **Reasoning:** Low / Medium / High, default Medium (Settings > Preferences > Agent Reasoning).
- **Failover:** tries the engine automatically, then rotates keys (primary → env → backups → embedded). Stops loudly after 3 failures / 30 s instead of looping. Dictation HTTP-400 hints `pip install -U "google-genai>=2.22"`.
- **Context:** 131k window, live bar + hover counts. Audio ≈ `len/320` tokens/chunk; screen ≈ +560/frame (MEDIUM) or +1120 (HIGH); memory ≤ ~350 tokens.
- **Caps:** refine output 4000 chars, deletes 4000, typed history 4000, audio chunk 4 s, queues bounded (mic 200, playback 256, drop-oldest).

---

## 13. Privacy & safety

- Mic + screen stream **only during active sessions** — to Google's AI service only. No analytics, accounts, or other network calls.
- Keys in **Windows Credential Manager** (`SPEAK_AI_App`), never plain files; UI/logs masked (`AIzaSy…last4`, `abc123***wxyz`, `embedded(hidden)`); embedded free-tier key obfuscated (XOR+base64 split).
- Config at `%APPDATA%\SPEAK_AI\config.json`: atomic writes, user-only ACL, every value sanitized/clamped on load.
- Injection: `SendInput` unicode, no clipboard, no Ctrl+A, never Enter (except Auto-Send path), foreground-verified, 4000-char caps, chunked deletes that abort if focus moves.
- Single-instance lock (no double mic/hotkeys). Transcript starts fresh each launch; autosave off by default.

---

## 14. Troubleshooting

| Symptom | Fix |
|---|---|
| Nothing types | Click the target app (not SPEAK) → press Enter if Verification Active → retry. Watch wave bars for mic proof. |
| `Mic silent / Mic Error` | Preferences → Microphone → Refresh → restart dictation. If Windows blocked it: Settings banner → Grant Permission → allow mic → Grant again. |
| Amber screen banner / `Screen blank — voice continues` | Grant Permission → approve OS prompt → Grant again (one click requests mic + screen). Check display/RDP/driver. Voice is unaffected. |
| `Screen hiccup — retrying` | Transient send failure — vision auto-retries with backoff, voice continues. If it persists, check network. |
| `Model unavailable, trying next…` → `Live connect failed` | Setup → Test key; add backup key; check network. |
| Refine warns about focus | Click your document, re-say the trigger (original stays in capsule). |
| Capsule missing | By design — Ctrl+Space or tray Show. |
| `Quota 429` | Add backup keys (auto-switch) or wait; embedded key rotates last. |
| Dictation restarts ~10 min | Normal preview cap — auto-reconnect, keep talking. |
| Shortcuts clash | Use clean single presses; Ctrl+/ avoids Win+Shift Snip conflicts; Esc never steals focus. |

Build/install: `pip install -r requirements.txt` → `python build.py` → `dist\SPEAK.exe` → `iscc installer.iss` → `installer\SPEAK_Setup_v2.1.exe` (needs Inno Setup 6, no admin to install). Details in `HOW_TO_INSTALL.md`.
