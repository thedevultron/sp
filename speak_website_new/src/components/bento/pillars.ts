export type PillarKey = 'voice' | 'vision' | 'keys' | 'context' | 'custom' | 'refine';

export interface Pillar {
  key: PillarKey;
  tag: string;
  title: string;
  text: string;
  foot: string;
  span: string;
}

export const PILLARS: Pillar[] = [
  {
    key: 'voice',
    tag: 'INSTANT DICTATION',
    title: 'Your voice. Direct to cursor.',
    text: 'Live dictation streamed at 16 kHz and typed at your cursor — any app, sub-second, multilingual auto-detect.',
    foot: 'Ctrl + Space',
    span: 'vox-span-4',
  },
  {
    key: 'vision',
    tag: 'MULTIMODAL COMPANION',
    title: 'An AI that sees — and acts.',
    text: 'A voice companion on the AI Engine: optional ~1 fps screen share plus voice desktop control — "click Send", "scroll down" — narrated step by step.',
    foot: 'Win + Shift',
    span: 'vox-span-2',
  },
  {
    key: 'keys',
    tag: 'MULTI-KEY ENGINE',
    title: 'Stay in flow. Never in a queue.',
    text: 'Primary + backup keys in Windows Credential Manager. On rate limits or drops, Voxula AI rotates keys and reconnects.',
    foot: 'Always connected',
    span: 'vox-span-2',
  },
  {
    key: 'context',
    tag: 'SMART CONTEXT',
    title: 'Full context. Full control.',
    text: 'Live token bar: green 0–60%, orange 61–85%, red 86–100%. Hover for exact tokens and session time. Purge anytime.',
    foot: 'Ctrl + Win',
    span: 'vox-span-4',
  },
  {
    key: 'custom',
    tag: 'CUSTOM ACTIONS',
    title: 'Teach it your own words.',
    text: 'Up to 3 custom refine actions with your own trigger words — say "summarize" and the whole session obeys. Craft them in Settings → Refine.',
    foot: 'Settings → Refine',
    span: 'vox-span-3',
  },
  {
    key: 'refine',
    tag: 'REFINE & POLISH',
    title: 'Say “refine” — it refines.',
    text: 'Say refine, polish, or elaborate and the whole session is deleted and retyped, cleaner. Self-correction aware, plus 3 custom actions.',
    foot: 'Say “refine”',
    span: 'vox-span-3',
  },
];
