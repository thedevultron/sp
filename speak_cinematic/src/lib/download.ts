export const INSTALLER_FILE = 'SPEAK_Setup_v2.1.exe';
export const INSTALLER_SIZE = '64.3 MB';
export const GITHUB_INSTALLER_DOWNLOAD_URL =
  'https://github.com/codedebuggalt/voxula_ai_installer/raw/main/SPEAK_Setup_v2.1.exe';

export function startDownload(): void {
  const a = document.createElement('a');
  a.href = GITHUB_INSTALLER_DOWNLOAD_URL;
  a.download = INSTALLER_FILE;
  a.rel = 'noopener';
  document.body.appendChild(a);
  a.click();
  a.remove();
}
