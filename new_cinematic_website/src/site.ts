export const APP_NAME = "Voxula AI";
export const APP_SHORT = "VOXULA";
export const SITE_VERSION = "v2.1";
export const AUTHOR = "Amir Bagawan";
export const INSTALLER_FILE = "SPEAK_Setup_v2.1.exe";
export const INSTALLER_SIZE = "64.3 MB";
export const INSTALLER_PATH = `downloads/${INSTALLER_FILE}`;
export const INSTALLER_FALLBACK_FILE = "SPEAK_Setup_v2.0.exe";
export const GITHUB_REPO_URL = "https://github.com/codedebuggalt/voxula_ai_installer";
export const GITHUB_INSTALLER_DOWNLOAD_URL =
  "https://github.com/codedebuggalt/voxula_ai_installer/raw/main/SPEAK_Setup_v2.1.exe";
export const GEMINI_KEY_URL = "https://aistudio.google.com/apikey";
export const DOCS_HASH = "#/docs";

export const QUICK_START_TEXT = `Voxula AI v2.1 — Quick Start (Amir Bagawan, 2026)

SYSTEM REQUIREMENTS
Windows 10 Build 19041+ or Windows 11, 64-bit, DirectX 11+.

INSTALL
1. Run the installer SPEAK_Setup_v2.1.exe (Setup wizard, no admin needed).
   Direct Download: ${GITHUB_INSTALLER_DOWNLOAD_URL}
   GitHub: ${GITHUB_REPO_URL}
2. Launch Voxula AI from the tray icon.

SETUP
1. Get a free API key at ${GEMINI_KEY_URL}
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
`;

export type ModalKind = "settings" | "guide" | "download" | "support" | null;
export interface DemoState {
  active: boolean;
  text: string;
  progress: number;
}
