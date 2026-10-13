// Single source of truth for release wiring. UI unchanged — text only.
export const SITE_VERSION = 'v2.1';
export const APP_NAME = 'Voxula AI';
export const APP_SHORT = 'VOXULA';
export const INSTALLER_FILE = 'SPEAK_Setup_v2.1.exe';
export const INSTALLER_SIZE = '64.3 MB';
export const INSTALLER_PATH = `downloads/${INSTALLER_FILE}`;
export const INSTALLER_FALLBACK_FILE = 'SPEAK_Setup_v2.0.exe';
export const GITHUB_REPO_URL = 'https://github.com/codedebuggalt/voxula_ai_installer';
export const GITHUB_INSTALLER_DOWNLOAD_URL = 'https://github.com/codedebuggalt/voxula_ai_installer/raw/main/SPEAK_Setup_v2.1.exe';
export const DOCS_HASH = '#/docs';
export const GEMINI_KEY_URL = 'https://aistudio.google.com/apikey';
// Brand gradient artwork as inline SVG data URIs (no asset files needed).
export const MASKED_GRADIENT_SRC =
  "data:image/svg+xml,<svg xmlns='http://www.w3.org/2000/svg' width='800' height='450'><defs><linearGradient id='g' x1='0' y1='0' x2='1' y2='1'><stop offset='0' stop-color='%23663af3'/><stop offset='.55' stop-color='%23799fd6'/><stop offset='1' stop-color='%23b6d9fc'/></linearGradient><radialGradient id='r' cx='.7' cy='.3' r='.85'><stop offset='0' stop-color='%23b6d9fc' stop-opacity='.9'/><stop offset='1' stop-color='%23b6d9fc' stop-opacity='0'/></radialGradient></defs><rect width='800' height='450' fill='url(%23g)'/><rect width='800' height='450' fill='url(%23r)'/></svg>";
export const SCROLL_FRAME_SRC =
  "data:image/svg+xml,<svg xmlns='http://www.w3.org/2000/svg' width='1600' height='900'><defs><radialGradient id='v' cx='.5' cy='.42' r='.75'><stop offset='0' stop-color='%237a52f5'/><stop offset='.45' stop-color='%23271f66'/><stop offset='1' stop-color='%2305060f'/></radialGradient><linearGradient id='b' x1='0' y1='0' x2='1' y2='0'><stop offset='0' stop-color='%23b6d9fc' stop-opacity='0'/><stop offset='.5' stop-color='%23b6d9fc' stop-opacity='.55'/><stop offset='1' stop-color='%23b6d9fc' stop-opacity='0'/></linearGradient></defs><rect width='1600' height='900' fill='%2305060f'/><rect width='1600' height='900' fill='url(%23v)'/><g stroke='url(%23b)' stroke-width='1.5' opacity='.5'><path d='M0 620 Q 400 560 800 620 T 1600 620' fill='none'/><path d='M0 660 Q 400 590 800 660 T 1600 660' fill='none'/><path d='M0 700 Q 400 620 800 700 T 1600 700' fill='none'/></g><ellipse cx='800' cy='380' rx='420' ry='150' fill='none' stroke='%23b6d9fc' stroke-opacity='.5' stroke-width='2'/><ellipse cx='800' cy='380' rx='300' ry='105' fill='none' stroke='%23663af3' stroke-opacity='.6' stroke-width='2'/></svg>";
