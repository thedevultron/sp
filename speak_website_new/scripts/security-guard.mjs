// React2Shell (CVE-2025-55182 / CVE-2025-66478) build guard.
// This site is a static Vite SPA: it must NEVER depend on React Server
// Components. Fail the build if any RSC-capable package (or Next.js, which
// bundles it) appears in package.json, package-lock.json, or node_modules.
// Offline and deterministic - runs in prebuild. Usage: node scripts/security-guard.mjs [projectRoot]
import { existsSync, readdirSync, readFileSync } from 'node:fs';
import { dirname, join, resolve } from 'node:path';
import { fileURLToPath } from 'node:url';

const ROOT = resolve(process.argv[2] || join(dirname(fileURLToPath(import.meta.url)), '..'));

// Exact package names that bring a Server Function / RSC deserialization
// endpoint with them. Any version (patched or not) is a build failure here:
// this project has no server to run them on, so their presence can only be
// a supply-chain mistake.
const BANNED = [
  'react-server-dom-webpack',
  'react-server-dom-parcel',
  'react-server-dom-turbopack',
  'next',
];

const failures = [];
const notes = [];

const pkgPath = join(ROOT, 'package.json');
const pkg = JSON.parse(readFileSync(pkgPath, 'utf8'));
for (const field of ['dependencies', 'devDependencies', 'peerDependencies', 'optionalDependencies']) {
  for (const name of Object.keys(pkg[field] || {})) {
    if (BANNED.includes(name)) failures.push(`${field}.${name}@${pkg[field][name]} (declared in package.json)`);
  }
}
notes.push(`package.json declares react@${pkg.dependencies?.react || '?'} react-dom@${pkg.dependencies?.['react-dom'] || '?'}`);

const lockPath = join(ROOT, 'package-lock.json');
if (existsSync(lockPath)) {
  const lock = JSON.parse(readFileSync(lockPath, 'utf8'));
  const entries = Object.keys(lock.packages || {});
  for (const key of entries) {
    const name = key.replace(/^node_modules\//, '');
    if (BANNED.includes(name)) failures.push(`lockfile entry ${key}@${lock.packages[key].version} (transitive or direct)`);
  }
  // Belt-and-braces: raw text scan catches renamed/shadowed entries.
  const raw = readFileSync(lockPath, 'utf8');
  for (const name of BANNED) {
    if (raw.includes(`"node_modules/${name}"`) && !entries.some((k) => k === `node_modules/${name}`)) {
      failures.push(`lockfile raw match for ${name} (unparsed entry)`);
    }
  }
  notes.push(`package-lock scanned (${entries.length} entries)`);
} else {
  notes.push('no package-lock.json (skipped lockfile scan)');
}

const nm = join(ROOT, 'node_modules');
if (existsSync(nm)) {
  for (const name of BANNED) {
    if (existsSync(join(nm, name))) failures.push(`node_modules/${name} is installed on disk`);
  }
  notes.push('node_modules scanned');
} else {
  notes.push('no node_modules (skipped disk scan)');
}

// Static-output sanity: the shipped bundle must not contain an RSC runtime.
const distIndex = join(ROOT, 'dist', 'index.html');
if (existsSync(distIndex)) {
  const html = readFileSync(distIndex, 'utf8');
  for (const marker of ['react-server-dom', 'text/x-component']) {
    if (html.includes(marker)) failures.push(`dist/index.html contains RSC marker "${marker}"`);
  }
  notes.push('dist/index.html scanned for RSC markers');
} else {
  notes.push('no dist yet (bundle scan runs after first build)');
}

for (const n of notes) console.log(`[guard] ${n}`);
if (failures.length) {
  console.error('[guard] BLOCKED - React2Shell surface detected:');
  for (const f of failures) console.error(`[guard]  - ${f}`);
  console.error('[guard] This static site must not include React Server Components. Remove the package and rebuild.');
  process.exit(1);
}
console.log('[guard] OK - no React Server Components / Next.js in the dependency tree.');
