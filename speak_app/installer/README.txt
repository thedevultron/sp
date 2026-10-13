SPEAK — Voice Dictation & Companion
Version 2.1 — Amir Bagawan — Minimalist fullscreen

FREE TO USE — ONE FILE, DONE
SPEAK works out of the box — no key needed (free tier active). For unlimited usage,
add your own Gemini API key in Settings > Setup > Primary API key.

QUICK START
0. WINDOWS MAY WARN "Unknown publisher" — this build is unsigned (normal for
   new independent software). Click "More info" > "Run anyway", once per
   version. Nothing is installed silently: Start Menu + optional Desktop icons.
1. Double-click SPEAK_Setup_v2.1.exe and follow the wizard (no admin needed).
2. Launch SPEAK from Start Menu or Desktop (if you checked the box).
   Settings opens natively fullscreen with a collapsible sidebar.
3. OPTIONAL: Paste your Google Gemini API key (AIzaSy...) and click Test, then Save.
   Get a key at https://aistudio.google.com/app/apikey
   If you add your key, SPEAK uses yours. Otherwise free tier is used silently.
4. Press Ctrl + Space to dictate — text types at your cursor in any app.
   Press Ctrl + Space again to stop.
5. Press Ctrl + Tab to spawn + switch to a new live session instantly.
   Sessions tab shows active count + stored metadata; oldest evicts first (FIFO, default Max 5).
6. Press Ctrl + / for companion (voice + optional screen). Toggle screen in the capsule.
7. Press Ctrl + Win to clear memory. Press Esc to stop live only (app keeps running).

PERMISSIONS (asked on first run — installer cannot grant these, Windows requires in-app approval)
- MICROPHONE: on launch SPEAK checks mic access. If blocked you get a tray
  alert + Settings banner. Click Grant Permission (opens Windows Privacy >
  Microphone), allow access, then Grant again to retry.
- SCREEN: on first screen share, SPEAK checks OS permission BEFORE starting capture.
  If pending/denied, a banner appears in Settings with a Grant Permission button.
  Click it to trigger the native OS prompt, approve, then click again to retry.
  One Grant click requests BOTH mic and screen.
- Voice continues even when screen is blocked. Dictation needs the mic.
- Blank frames from the AI means permission is still blocked — fix it here first.

MESSAGE VERIFICATION (Settings > Preferences)
- Auto-Send (default): requireVerification=False, autoSubmit=True — type + Enter automatically.
- Verification Active (opt-in): requireVerification=True, autoSubmit=False — type, wait for Enter.
- Agent reasoning: Low / Medium (default) / High (Settings > Preferences > Agent Reasoning).
- Live locks enforced: Transcription SMART, tool typeTextAtCursor.

SELF-TESTS (Settings > Preferences)
- Microphone card > Test speaker: plays a two-tone beep through the real
  reply path. Clear beep = speaker wiring correct.
- Live Screen card > Test capture: grabs one frame, shows KB size + tokens.
  Proves vision frames actually flow. Blank = permission still blocked.
- If anything misbehaves, open %APPDATA%\SPEAK_AI\logs\ and send the newest
  speak-*.log — it records every session event.

CAPSULE
- Hotkeys open the mini pill first. Click it (or the maximize button) to expand
  the full capsule. Close-only, stays on top. Appears only on hotkey. Find SPEAK in tray near the clock.
- Transcript panel: copy, clear, refine/polish/elaborate + customs. Screen button toggles vision.
- Status text elides gracefully, full text in tooltip. Panel never slides under taskbar.

REFINE
- Say "refine", "polish", "elaborate" (or old "expand") or tap capsule buttons.
- Refined text replaces what was just typed — no extra Enter needed.
- Works multilingual (auto-detect).

HELP TAB
- Settings > Help: step-by-step for Screen Share / Transcription / Smart Insertion,
  shortcut cheat sheet table, and quick fixes for cursor focus + permissions.

TIPS
- The floating capsule appears only when you use a hotkey.
- In Settings > Preferences add Custom words (names, products) and your Mark.
- Backup keys: Settings > Setup — auto switches on quota. List shows masked previews only.
- Publisher: Amir Bagawan

PRIVACY & SAFETY
- Keys in Windows Credential Manager (never plain files). Only sent to Google.
- Single-instance guard prevents double mic/hotkeys. Injection never types when SPEAK is focused.
- No admin install. Startup launch is opt-in only.

UNINSTALL
Settings > Apps > SPEAK > Uninstall.
