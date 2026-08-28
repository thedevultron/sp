Auto-Detect & Multi-Backup BYOK Engine: Auto-identifies active system environment keys (Google AI Studio or Vertex AI) and allows adding an unlimited backup API key queue. If a key encounters rate limits or quota errors (HTTP 429), the app seamlessly fails over to the next available backup key without dropping the active WebSocket connection.

Visual Smart Token & Context Bar: A visual percentage bar built into the capsule interface:

🟩 Green (0% – 60%): Optimal context window state.

🟧 Yellow/Orange (61% – 85%): Moderate context usage.

🟥 Red (86% – 100%): Approaching context cap (suggests hitting Ctrl + Win to purge).

Interactive Hover Tooltip: Hovering over the bar reveals a float overlay with exact token counts, session time elapsed, and estimated buffer remaining.

Sound-Wave Reactive Dynamic Audio Pill: 5 vertical animated lines utilizing linear interpolation (Lerp). They expand/contract based on mic RMS volume during dictation, and pulse neon cyan when Gemini responds.

Direct Application Text Injection: Transcribed speech is typed sub-second directly into whichever focused application window or text field currently holds cursor priority.

Canvas Ink Pen Layer: Borderless screen-drawing overlay using freehand QPainter neon red (#FF3B30) or yellow (#FFCC00) ink. Pressing Esc wipes all markings clean instantly.

Global Hardware Hotkeys:

Ctrl + Space: Toggle Live Voice Dictation.

Win + Shift: Toggle Multimodal Live Companion (Simultaneous mic + high-FPS screen streaming).

Ctrl + Win: Purge context memory & hard reset WebSocket session.

Claude & Apple Modern Dark UI: Hardware-accelerated frameless windowing (#0D0D0E surface, #16161A cards, 20px rounded corners, Segoe UI Variable font).

System Architecture & File Map
speak_app/
├── assets/
│   ├── icon.ico                 # App & System Tray icon
│   └── capsule_style.qss        # Custom QSS stylesheet for Claude dark palette
├── src/
│   ├── __init__.py
│   ├── config.py                # Keyring vault, JSON parameters & Key Failover Queue
│   ├── hotkeys.py               # Pynput global background thread listener
│   ├── tray.py                  # Pystray tray icon & quick menu integration
│   ├── audio_engine.py          # Sounddevice mic capture & RMS audio visualizer math
│   ├── screen_engine.py         # MSS screen grabber for live video feeds
│   ├── gemini_client.py         # google-genai live WebSocket connection & key failover manager
│   └── ui/
│       ├── __init__.py
│       ├── floating_capsule.py  # Frameless pill UI, dynamic wave lines & token percent bar
│       ├── screen_canvas.py     # Fullscreen transparent drawing layer (Pen tool)
│       └── settings_dialog.py   # BYOK management (Multi-key list) & hyperparameter sliders
├── build.py                     # PyInstaller single-file binary compilation script
├── installer.iss                # Inno Setup wizard compiler script
├── main.py                      # Application entry point & qasync event loop launcher
└── requirements.txt             # Dependency list
Dependencies & Tech Stack
Plaintext
PySide6>=6.6.0
qasync>=0.27.0
google-genai>=0.1.0
pynput>=1.7.6
pystray>=0.19.5
sounddevice>=0.4.6
numpy>=1.26.0
mss>=9.0.1
pillow>=10.2.0
pywin32>=306
keyring>=24.3.0
pyautogui>=0.9.54
pyinstaller>=6.3.0
User-Friendly Tutorial: How to Use SPEAK
Launch & System Tray: Run SPEAK.exe. The app starts silently in the background. A discrete SPEAK icon appears in your Windows System Tray (near your clock).

API Key Setup: Right-click the tray icon and select Settings.

Primary Key: The app automatically attempts to load local environment keys (GEMINI_API_KEY).

Backup Keys: Click Add Backup Key to append additional fallback keys. If your main key runs out of quota, SPEAK switches to the backup seamlessly.

Live Voice Dictation (Ctrl + Space): Open any app (Notepad, Discord, Word, browser). Press Ctrl + Space. The floating capsule will appear with reactive sound waves. Speak into your microphone, and your words will auto-type into your focused text cursor. Press Ctrl + Space again to stop.

Multimodal Live Companion (Win + Shift): Press Win + Shift to initiate real-time audio and desktop screen sharing with Gemini.

Screen Drawing Tool: Click the Pen Icon on the floating capsule toolbar. Click and drag anywhere on your screen to draw red or yellow highlights for Gemini to analyze. Press Esc to clear all drawings.

Token Monitoring & Session Reset: Look at the visual percentage bar on the capsule.

Green indicates plenty of memory space remaining.

Hover over the bar to see exact token counts and session duration.

If the bar turns Red, press Ctrl + Win to instantly clear memory and start a fresh session.

Phased Build & Implementation Plan
Phase 1: Project Scaffolding & Config Vault: Setup directory structure, keyring API storage, primary key auto-detector, and backup failover queue.

Phase 2: Hardware & Live Streaming Engines: Write audio_engine.py (sounddevice), screen_engine.py (mss), and gemini_client.py using google-genai async WebSockets.

Phase 3: Floating UI & Animations: Build frameless PySide6 windows, implement sound-wave amplitude visualizer, and build the hoverable percentage bar widget.

Phase 4: Global Hotkeys & Direct Injection: Implement pynput listener thread, background system tray hooks, and pyautogui synthetic typing.

Phase 5: Single-Executable & Installer Build: Run build.py to produce SPEAK.exe via PyInstaller, then compile installer.iss with Inno Setup to create SPEAK_Setup_v1.0.exe.You are an expert Senior Windows Desktop Software Engineer and UI/UX Designer. Your task is to write a complete, robust, production-grade Python desktop application named "SPEAK". This application runs natively in the Windows 11 system tray, supports global background keyboard shortcuts, features a fluid, animated floating UI inspired by Claude and modern Apple design, and integrates with the Google Gen AI SDK for live speech-to-text and live multimodal screen-sharing interaction over WebSockets.

You MUST deliver complete, un-truncated, production-ready Python code across a clean multi-file modular architecture. Do NOT use placeholders, shortened code blocks, or comments like "# ... implement rest here".

========================================================================
1. TECH STACK & SYSTEM ENVIRONMENT
========================================================================
- OS & Architecture: Windows 11 64-bit (Compiled via PyInstaller into a standalone executable)
- GUI Framework: PySide6 (Qt for Python) with custom QSS styling and QPainter hardware acceleration
- Async Event Loop: `qasync` (Seamlessly bridges Python asyncio with PySide6 QEventLoop)
- Global Hotkeys: `pynput` (Low-level global system keyboard hook listener thread)
- Tray Integration: `pystray` + `Pillow` (Runs silently in system tray with context menus)
- Live AI Pipeline: `google-genai` SDK using `client.aio.live.connect` WebSockets
- Audio Capturing & Math: `sounddevice` + `numpy` (Direct PCM 16kHz audio capture and RMS volume energy computation)
- Screen Capture: `mss` (Hyper-fast screen buffer streaming for vision features)
- Credential Security: Windows Credential Manager (`keyring`) for encrypted local key storage
- Text Injection: `pyautogui` / synthetic keystrokes for instant cursor insertion

========================================================================
2. SYSTEM FILE MAP & ARCHITECTURE
========================================================================
Write every file completely inside the following project layout:

speak_app/
├── assets/
│   ├── icon.ico                 # App & System Tray icon
│   └── capsule_style.qss        # Custom QSS stylesheet (Claude dark palette)
├── src/
│   ├── __init__.py
│   ├── config.py                # Encrypted keyring vault, JSON parameters & Key Failover Queue
│   ├── hotkeys.py               # Pynput global background thread listener
│   ├── tray.py                  # Pystray tray icon & quick menu integration
│   ├── audio_engine.py          # Sounddevice mic capture & RMS audio visualizer math
│   ├── screen_engine.py         # MSS screen grabber for live video feeds
│   ├── gemini_client.py         # google-genai live WebSocket connection & key failover manager
│   └── ui/
│       ├── __init__.py
│       ├── floating_capsule.py  # Frameless pill UI, dynamic wave lines & token percent bar
│       ├── screen_canvas.py     # Fullscreen transparent drawing layer (Pen tool)
│       └── settings_dialog.py   # BYOK management (Multi-key list) & hyperparameter sliders
├── build.py                     # PyInstaller single-file binary compilation script
├── installer.iss                # Inno Setup wizard compiler script
├── main.py                      # Application entry point & qasync event loop launcher
└── requirements.txt             # Dependency list

========================================================================
3. UI/UX DESIGN SYSTEM (CLAUDE & APPLE DARK DESIGN)
========================================================================
- Aesthetic Style: Frameless, borderless Qt windows with rounded corners (border_radius=20), dark-mode minimalist surface design.
- Color Palette:
  - Surface Background: `#0D0D0E` (Deep Charcoal Black)
  - Card & Container Surface: `#16161A` (Dark Slate)
  - Border Stroke: `#262630` (Subtle 1px stroke)
  - Primary Text: `#F3F3F7` (Off-White)
  - Muted Text: `#8E8EA0` (Claude Text Gray)
  - Accent Pulse: `#00E5FF` (Neon Cyan) & `#7C3AED` (Claude Purple)
- Typography: Native `Segoe UI Variable` (or `Inter`), 13px base text, medium weight, 11px uppercase tracking for badges.

========================================================================
4. FLOATING CAPSULE & VISUAL SMART TOKEN BAR (`ui/floating_capsule.py`)
========================================================================
- Floating Pill Widget: Ultra-thin horizontal pill overlay configured with `Qt.WindowType.FramelessWindowHint | Qt.WindowType.WindowStaysOnTopHint`.
- 5 Sound-Wave Reactive Lines: Centered in the pill. Utilizes linear interpolation (Lerp) to smooth animation transitions.
  - When User Speaks: Lines scale height dynamically based on real-time RMS amplitude from `audio_engine.py` (Glowing White).
  - When Gemini Responds: Lines pulse in neon cyan (`#00E5FF`) dancing to incoming speaker frequency.
- Visual Smart Token Percentage Bar: A discrete horizontal color-coded progress bar embedded into the pill UI:
  - Green (`#34C759`): 0% – 60% token context usage.
  - Yellow/Orange (`#FF9500`): 61% – 85% context usage.
  - Red (`#FF3B30`): 86% – 100% context usage (Warning state).
  - Interactive Hover Tooltip: Hovering over the bar displays a float box with exact token counts, session duration, and remaining capacity.
- Mini Expandable Toolbar: Clicking or hovering over the capsule expands a dock with 3 buttons:
  1. Camera / Monitor Icon: Toggle button to enable/disable screen sharing capture loop.
  2. Canvas Pen Icon: Toggles full-screen drawing layer overlay.
  3. Red Cross "X": Kills active session and hides capsule.

========================================================================
5. KEY ENGINE & FAILOVER AUTOMATION (`config.py` & `gemini_client.py`)
========================================================================
- Environment Auto-Detect: On startup, auto-detect existing OS environment variables (`GEMINI_API_KEY`, `GOOGLE_APPLICATION_CREDENTIALS`).
- Backup API Key Queue: Support adding an unlimited list of backup API keys stored securely via `keyring`.
- Automatic Failover: If the primary key hits rate limits (HTTP 429), quota errors, or WebSocket connection drops, `gemini_client.py` immediately catches the exception, switches to the next available backup key in the queue, and re-establishes the WebSocket session seamlessly without crashing the UI.

========================================================================
6. GLOBAL SHORTCUTS & INTERACTION LOGIC (`hotkeys.py`)
========================================================================
- HOTKEY 1: `Ctrl + Space` -> Dictation Mode
  - Activates `gemini-3.5-transcribe-live`. Streams mic audio over WebSockets. As partial transcripts return sub-second, inject text directly into active Windows app fields using synthetic keystrokes (`pyautogui`).
- HOTKEY 2: `Ctrl + Win` -> Hard Reset Session / Token Purge
  - Immediately terminates active WebSocket session, resets token buffer count to 0%, clears history memory, and restarts clean API session.
- HOTKEY 3: `Win + Shift` -> Multimodal Live Companion Mode
  - Initializes continuous bidirectional audio/video stream using `gemini-3.5-transcribe-live-live`. Streams screen frames (via `mss`) and mic audio, playing generated audio responses back in real-time.

========================================================================
7. TRANSPARENT SCREEN MARKING LAYER (`ui/screen_canvas.py`)
========================================================================
- Transparent Overlay Canvas: Borderless, click-through capable screen overlay covering 100% display coordinates.
- Drawing Engine: Capture left-mouse drag events using `QPainter` to paint freehand neon red (`#FF3B30`) or yellow (`#FFCC00`) ink lines over the desktop.
- Instant Clear: Pressing `Esc` wipes all canvas markings clean instantly.

========================================================================
8. COMPLETE SETTINGS DASHBOARD (`ui/settings_dialog.py`)
========================================================================
- Tabbed Claude UI Interface:
  - Tab 1: BYOK Key Management (Google AI Studio Key, Vertex AI Project ID/Credentials, Multi-Key Backup List addition).
  - Tab 2: Hyperparameters (System Instruction text box, Temperature slider 0.0-2.0, TopP slider 0.0-1.0, Thinking Budget config).
  - Tab 3: System Preferences (Toggle automatic Windows Startup shortcut creation in `%APPDATA%\Microsoft\Windows\Start Menu\Programs\Startup`).

========================================================================
9. PACKAGING AUTOMATION (`build.py` & `installer.iss`)
========================================================================
- Write `build.py` using `PyInstaller` command execution flags: `--noconsole`, `--onefile`, `--add-data`, managing hidden imports for `google-genai`, `PySide6`, and `qasync`.
- Write a complete `installer.iss` script for **Inno Setup** to compile the built binary into `SPEAK_Setup_v1.0.exe` with auto-start tasks and uninstaller support.

Now, write all files in the architecture completely with zero omissions.











