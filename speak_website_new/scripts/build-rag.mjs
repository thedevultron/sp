// Builds api/corpus.json — the chatbot's retrieval corpus.
// Sources: website truth (llms.txt, DocsPage, pillars, guide copy) +
// desktop truth (speak_app docs). Deterministic, offline, no dependencies.
// Usage: node scripts/build-rag.mjs
import { mkdirSync, readFileSync, writeFileSync } from 'node:fs';
import { dirname, join, resolve } from 'node:path';
import { fileURLToPath } from 'node:url';

const ROOT = resolve(join(dirname(fileURLToPath(import.meta.url)), '..'));
const APP_ROOT = resolve(join(ROOT, '..', 'speak_app'));

const SOURCES = [
  { file: join(ROOT, 'public', 'llms.txt'), label: 'overview', weight: 3 },
  { file: join(ROOT, 'src', 'components', 'docs', 'DocsPage.tsx'), label: 'docs', weight: 3, tsx: true },
  { file: join(ROOT, 'src', 'components', 'bento', 'pillars.ts'), label: 'features', weight: 2, tsx: true },
  { file: join(APP_ROOT, 'DOCS.md'), label: 'desktop-docs', weight: 2 },
  { file: join(APP_ROOT, 'FEATURES_AND_SECURITY.md'), label: 'desktop-features', weight: 2 },
];

const MAX_CHUNK = 700;

function stripTsx(raw) {
  return raw
    .replace(/^import[^;]*;/gm, '')
    .replace(/<[^>]*>/g, ' ')
    .replace(/[{}\[\]()'"`;=>]/g, ' ')
    .replace(/className|onClick|onChange|onSubmit|aria-[a-z]+|http[s]?/g, ' ')
    .replace(/[ \t]+/g, ' ');
}

function chunkText(text, label) {
  const paras = text
    .replace(/\r/g, '')
    .split(/\n{2,}/)
    .map((p) => p.replace(/\s+/g, ' ').trim())
    .filter((p) => p.length > 40);
  const chunks = [];
  for (const p of paras) {
    if (p.length <= MAX_CHUNK) {
      chunks.push(p);
    } else {
      // Hard-split long paragraphs on sentence boundaries.
      const sentences = p.split(/(?<=[.!?])\s+/);
      let cur = '';
      for (const s of sentences) {
        if ((cur + ' ' + s).trim().length > MAX_CHUNK && cur) {
          chunks.push(cur.trim());
          cur = s;
        } else {
          cur += ' ' + s;
        }
      }
      if (cur.trim()) chunks.push(cur.trim());
    }
  }
  return chunks.map((text) => ({ source: label, text }));
}

const corpus = [];
for (const src of SOURCES) {
  let raw;
  try {
    raw = readFileSync(src.file, 'utf8');
  } catch {
    console.warn(`[rag] missing ${src.file} — skipped`);
    continue;
  }
  const clean = src.tsx ? stripTsx(raw) : raw;
  const chunks = chunkText(clean, src.label);
  for (const c of chunks) corpus.push({ ...c, weight: src.weight });
  console.log(`[rag] ${src.label}: ${chunks.length} chunks`);
}

mkdirSync(join(ROOT, 'api'), { recursive: true });
mkdirSync(join(ROOT, 'src', 'chat'), { recursive: true });
const out = corpus.map((c, i) => ({ id: i, ...c }));
writeFileSync(join(ROOT, 'api', 'corpus.json'), JSON.stringify(out));
writeFileSync(join(ROOT, 'src', 'chat', 'corpus.json'), JSON.stringify(out));
console.log(`[rag] wrote api/corpus.json and src/chat/corpus.json (${out.length} chunks)`);
