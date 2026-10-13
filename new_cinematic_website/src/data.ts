export type AppKey = "vscode" | "slack" | "notion";

export const SCRIPTS: Record<AppKey, { raw: string; polish: string }> = {
  vscode: {
    raw: `// get the users that are active and sort by name
const activeUsers = users
  .filter(user => user.isActive)
  .sort((a, b) => a.name.localeCompare(b.name));`,
    polish: `// Return active users, alphabetically by name.
const getActiveUsers = (users: User[]): User[] => {
  return users
    .filter(({ isActive }) => isActive)
    .sort((a, b) => a.name.localeCompare(b.name));
};`,
  },
  slack: {
    raw: `hey team so the voice integration is ready and um latency is looking really good. can someone take a look at the pull request before we ship tomorrow?`,
    polish: `Hey team — the voice integration is ready for review.

Latency is consistently under 200ms, and all tests are passing. Please review the pull request before tomorrow's release.

Thanks for helping us ship something great.`,
  },
  notion: {
    raw: `okay so the idea is to make a voice first workflow and not have to switch apps. we need global shortcuts, live transcription and maybe screen sharing too.`,
    polish: `# A voice-first workflow

Build a companion that turns thoughts into action, without switching apps.

## Core priorities
• System-wide keyboard shortcuts
• Real-time, low-latency transcription
• Multimodal screen understanding

Less friction. More flow.`,
  },
};

export const HERO_PHRASES = [
  "Hey team — the build is green, shipping this afternoon.",
  "Remind me to send the invoice before Friday.",
  "Let's move the standup to ten and keep it short.",
  "Draft a reply: thanks, that works for me.",
];

export const PILLARS_ORDER = ["voice", "vision", "keys", "context", "custom", "refine"] as const;

export const SHORTCUTS = [
  { keys: ["Ctrl", "Space"], title: "Global dictation", body: "Your voice, typed wherever your cursor is." },
  { keys: ["Win", "Shift"], title: "Screen companion", body: "Voice + live screen, together." },
  { keys: ["Ctrl", "Win"], title: "Fresh start", body: "Purge transcript and token counter." },
  { keys: ["Esc"], title: "Back to focus", body: "Clear the canvas and dismiss to tray." },
];

export const FAQ = [
  {
    q: "Dictation isn't appearing",
    a: "Make sure your cursor is in an editable field, microphone permissions are granted, and your API key is active.",
  },
  {
    q: "API key reached limit",
    a: "Add a backup key in Settings. Failover rotates between keys automatically. Google quotas apply.",
  },
  {
    q: "How does refine work?",
    a: "Say refine, polish, or elaborate (or use the capsule or tray). The session is deleted with Backspaces and retyped cleanly. If Voxula had focus, click your document first, then say it again.",
  },
  {
    q: "Does this website record my microphone?",
    a: "No. The simulator streams pre-written sample text locally. There is no mic, screen, or account access.",
  },
];
