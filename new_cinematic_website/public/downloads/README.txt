The real Windows Setup installer is NOT committed to git (~100MB).

Serve the installer wizard (SPEAK_Setup_*.exe) here — never the portable SPEAK.exe.

Before `npm run build`, place the built installer here:

  downloads/SPEAK_Setup_v2.1.exe

Or just run the build — `scripts/copy-installer.mjs` copies it automatically
from `../../speak_app/installer/SPEAK_Setup_v2.1.exe` when present.

The Download modal links to `downloads/SPEAK_Setup_v2.1.exe` (relative URL,
so it works from any static host or a single-file preview folder). If the file
is missing, the modal falls back to the quick-start guide download.
