// Copies the latest Windows installer next to the built site so the
// Download button serves the actual file. The ~66MB exe is NOT committed:
// it is copied at build time from ../speak_app/installer/ when present.
// Latest = highest SPEAK_Setup_vX.Y.exe version found; older copies in
// public/downloads are pruned so deploys never ship stale installers.
import { copyFileSync, existsSync, mkdirSync, readdirSync, rmSync } from 'node:fs';
import { basename, dirname, resolve } from 'node:path';
import { fileURLToPath } from 'node:url';

const here = dirname(fileURLToPath(import.meta.url));
const root = resolve(here, '..');
const srcDir = resolve(root, '..', 'speak_app', 'installer');
const destDir = resolve(root, 'public', 'downloads');
mkdirSync(destDir, { recursive: true });

function versionOf(name) {
  const m = /^SPEAK_Setup_v(\d+)\.(\d+)\.exe$/i.exec(name);
  return m ? [parseInt(m[1], 10), parseInt(m[2], 10)] : null;
}

let candidates = [];
try {
  candidates = readdirSync(srcDir)
    .filter((n) => versionOf(n) !== null)
    .sort((a, b) => {
      const va = versionOf(a);
      const vb = versionOf(b);
      return vb[0] - va[0] || vb[1] - va[1];
    })
    .map((n) => resolve(srcDir, n));
} catch {
  candidates = [];
}

let copiedName = null;
for (const src of candidates) {
  if (!existsSync(src)) continue;
  try {
    copyFileSync(src, resolve(destDir, basename(src)));
    copiedName = basename(src);
    console.log(`[voxula] installer connected: ${resolve(destDir, copiedName)}`);
    break;
  } catch (err) {
    console.warn(`[voxula] could not copy installer: ${String(err)}`);
  }
}

// Prune older installer copies so only the latest ships.
try {
  for (const n of readdirSync(destDir)) {
    if (versionOf(n) !== null && n !== copiedName) {
      rmSync(resolve(destDir, n));
      console.log(`[voxula] pruned stale installer copy: ${n}`);
    }
  }
} catch {
  /* ignore */
}

if (!copiedName) {
  console.log('[voxula] no local installer found — download modal will offer the quick-start guide fallback.');
}
