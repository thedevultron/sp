# SPEAK — Features & Security

> Voice dictation and live AI companion for Windows 11. By Amir Bagawan.

---

## 1. Features

### Live Voice Dictation (`Ctrl + Space`)
- Streams microphone audio (16 kHz mono) to live transcription.
- Transcribed speech is typed **directly at the cursor** in whatever app is focused (Notepad, Word, browser, Discord…), sub-second, with multilingual auto-detect.
- Floating capsule shows live status, sound-wave visualizer (mic vs voice), interim preview, and a token/context bar.

### Multimodal Live Companion (`Win + Shift`)
- Real-time voice conversation with the **AI Engine** (automatic fallback, tried in order automatically).
- Optional **live screen sharing** (~1 fps JPEG frames) so the assistant sees your desktop. Toggle any time via the capsule monitor button or Settings → Live Screen; takes effect mid-session without killing audio.
- Replies play through your speakers; capsule shows `Speaking...` / `Listening...` states.
- Screen-off mode = voice-only companion.

### Refine / Polish / Elaborate (session delete-and-replace)
- Say `refine`, `polish`, or `elaborate` (or tap the capsule buttons / tray menu) to rewrite **everything typed this session** (since purge or dictation start).
- The original text is deleted via measured Backspaces and the rewritten version is typed in its place — no clipboard, no `Ctrl+A`, no `Enter` presses.
- Prompts are **self-correction aware**: *"could you set meeting at 9pm actually 5pm"* → *"Could we schedule the meeting for 5:00 PM?"* (obsolete info dropped, times normalized).
- Old trigger word `expand` still works as an alias for Elaborate.

### Custom refine actions (up to 3)
- Settings → **Refine tab**: edit the Refine/Polish/Elaborate prompts and their voice trigger words, or add your own actions (e.g. name `Summarize`, trigger `summarize`, custom prompt).
- Custom actions appear immediately in the capsule, the tray Refine menu, and voice triggers after Save. Trigger words: `a-z 0-9 -`, 2–24 chars, must be unique.

### Token / context bar
- 3 px bar under the capsule: green (0–60%), orange (61–85%), red (86–100%).
- Hover shows exact token counts, session time, and remaining buffer.

### Purge (`Ctrl + Win`)
- Instantly stops the session, clears transcript + typed history + token counter, and hard-resets the connection.

### Screen drawing canvas
- Fullscreen transparent ink layer (`B`/`1-3` color keys, right-click clears, `Esc` exits) for marking the screen while talking to the companion.

### System tray
- Show/hide capsule, Dictation, Companion, Purge, Refine submenu, Guide, Settings, Exit. Notifications for save/refine/speaker/screen events.

### Settings (main window, native min/max/close, draggable)
- **Setup:** primary + backup API keys (masked display), Test button, free-tier status.
- **Guide:** shortcut reference.
- **Preferences:** microphone select/refresh, custom vocabulary words + signature mark, system prompt, creativity slider, live-screen toggle, Windows startup.
- **Refine:** prompts, triggers, custom actions (see above).

### Design
- Authkit “frosted glass cathedral at midnight”: near-black canvas `#05060f`, frost-glass cards, hairline borders, single Void Violet `#663af3` CTA color, pill buttons, blueprint grid + spotlight backdrop in Settings.

---

## 2. AI Engine

| Use | Engine |
|-----|-----------|
| Dictation | AI Engine (speech-to-text) |
| Companion (Live, audio + screen) | AI Engine with automatic fallback |
| Refine (one-shot edit) | AI Engine with automatic fallback |

- Stored configs with retired IDs are auto-repaired on load; custom engine IDs you entered yourself are never overwritten.
- Companion failover: on connection failure the client rotates API keys and retries; after 3 failures in 30 s it stops loudly with an error instead of hot-looping.

---

## 3. Security

### API key storage
- Keys live in **Windows Credential Manager** (`keyring`, target `SPEAK_AI_App`), never in plain files. The app JSON config holds only non-secret settings.
- UI **masks** keys (`AIza…abcd (39 chars)`); full values stay in Credential Manager and are passed only to Google.
- Logs mask keys (`AIza12***abcd`); length/format validated (20–256 chars, `AIza` prefix warned, never enforced).

### Embedded free-tier key
- A fallback key ships **obfuscated** (XOR + base64 split parts in `src/_embedded_key.py`) and is used only when the user vault is empty. User keys always take priority when present.

### Config file hardening
- Atomic writes (temp file + replace) to `%APPDATA%\SPEAK_AI\config.json`, with `icacls` restricted to the current user.
- All loaded values sanitized: temperatures/fps clamped, engine IDs repaired against a known-bad list, prompts capped at 2000 chars with control characters stripped, trigger words restricted to `[a-z0-9-]{2,24}`, custom names to 24 chars, max 3 customs, duplicate triggers rejected.

### Injection safety
- Typing uses `SendInput` unicode (multilingual-safe); refined text capped at 4000 chars per replace; Backspace deletes capped at 4000; audio playback chunks capped (192 KB) with a bounded 64-slot queue (oldest dropped, loop never blocked).
- Refine refuses to delete while a SPEAK window is focused (tries focus-restore once, else aborts with a warning and keeps history so retry works).
- Clipboard is never used for injection; no `Enter` is ever synthesized.

### Runtime safety
- **Single-instance lock** (`QLOCKFile` in temp): a second launch shows “already running” instead of double mic/hotkeys.
- Hotkeys debounced (600 ms); `Win+Shift` vs `Ctrl+Win` combos are mutually exclusive (three-modifier holds fire nothing); rapid double-press within 1.5 s is ignored rather than restarting the session.
- Failover storm guard, bounded session shutdown (3 s), per-task cancellation that never cancels the caller itself.
- Audio queue bounded (200, oldest dropped); mic-silence watchdog warns instead of hanging; playback runs on a worker thread with throttled warnings.

---

## 4. Privacy

- Microphone and screen frames stream **only** while a dictation/companion session is active, and only to Google's Gemini API.
- Transcript history starts fresh every launch (no restore); autosave off by default.
- No analytics, no accounts, no network calls except to Google APIs.

---

## 5. Build & install

```
cd speak_app
venv\Scripts\activate
pip install -r requirements.txt   # pinned versions
python build.py                   # -> dist\SPEAK.exe (+ SHA256 + SIGNING_NOTE)
python build.py --installer       # -> + installer\SPEAK_Setup_v2.1.exe (needs Inno Setup 6)
```

- Single-file `--windowed --onefile` build, assets bundled, version metadata stamped (Publisher: Amir Bagawan).
- Installer needs no admin rights; optional desktop/startup shortcuts; uninstaller included.

---

## 6. Troubleshooting

| Symptom | Likely cause | Fix |
|---------|--------------|-----|
| Companion shows `Model unavailable, trying next...` then `Live connect failed` | Keys invalid/quota or network | Settings → Setup → Test key; add backup key |
| `Speaker error / reply dropped`, no voice | Output device busy/missing | Check speaker; restart companion |
| `Mic silent / Mic Error` | Wrong input device | Preferences → Microphone → Refresh |
| Refine says `Click your document, then <word>` | Capsule had focus | Click target app, say trigger again (hands-free works best) |
| Capsule hidden | By design (hotkey-only) | `Ctrl+Space`, or tray → Show capsule |
| `Live connect keeps failing` | Bad stored engine IDs | Fixed automatically on load; otherwise check keys/network |
