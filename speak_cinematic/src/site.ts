// Single source of truth — Voxula AI v2.1 (marketing cinematic)
export const SITE_VERSION = 'v2.1';
export const APP_NAME = 'Voxula AI';
export const APP_SHORT = 'VOXULA';
export const INSTALLER_FILE = 'SPEAK_Setup_v2.1.exe';
export const INSTALLER_SIZE = '64.3 MB';
export const GITHUB_REPO_URL = 'https://github.com/codedebuggalt/voxula_ai_installer';
export const GITHUB_INSTALLER_DOWNLOAD_URL =
  'https://github.com/codedebuggalt/voxula_ai_installer/raw/main/SPEAK_Setup_v2.1.exe';
export const GEMINI_KEY_URL = 'https://aistudio.google.com/apikey';
export const DOCS_URL = 'https://github.com/codedebuggalt/voxula_ai_installer#readme';

export const CHAPTERS = [
  { id: 'overview', label: 'Opening', title: 'Your Voice. Everywhere.' },
  { id: 'how-it-works', label: 'Chapter I', title: 'Instant execution. Zero friction.' },
  { id: 'features', label: 'Chapter II', title: 'Quietly powerful.' },
  { id: 'why', label: 'Chapter III', title: 'Built because the alternatives cost too much.' },
  { id: 'privacy', label: 'Chapter IV', title: 'Your words are yours.' },
  { id: 'finale', label: 'Finale', title: 'Find your voice. Get into flow.' },
] as const;
