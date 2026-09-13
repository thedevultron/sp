/**
 * Single source of truth for the downloadable installer.
 * The file lives in `speak_website/public/` (copied from
 * `speak_app/installer/SPEAK_Setup_v2.1.exe`) so Vite emits it
 * next to `dist/index.html`. Keep version + size in sync when
 * the installer is rebuilt.
 */
export const INSTALLER_FILE = "SPEAK-Setup-v2.1-x64.exe";
export const INSTALLER_VERSION = "2.1";
export const INSTALLER_SIZE_MB = 100.4;
export const INSTALLER_URL = `./${INSTALLER_FILE}`;
