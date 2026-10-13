import { GITHUB_REPO_URL, INSTALLER_FILE, INSTALLER_SIZE } from "../site";

interface Canned {
  match: RegExp;
  answer: string;
}

const CANNED: Canned[] = [
  {
    match: /install|download|setup|set up|get started|installer/i,
    answer: `Four steps: 1) Download ${INSTALLER_FILE} (${INSTALLER_SIZE}) from GitHub using the download button. 2) Run the setup wizard — no admin rights needed. 3) Bring a free Google AI Studio key, or set GEMINI_API_KEY and it's auto-detected. 4) Put your cursor in any app and press Ctrl+Space.`,
  },
  {
    match: /refine|polish|elaborate|rewrite|expand/i,
    answer:
      "Refine is a hands-free rewriter. Say refine, polish, or elaborate and Voxula deletes what you typed this session with measured Backspaces, then retypes a cleaner version at your cursor. You can add up to 3 custom actions with your own prompts in Settings → Refine.",
  },
  {
    match: /privat|secur|safe|key|encrypt|telemetry|track|record/i,
    answer:
      "Your API keys are stored in Windows Credential Manager with DPAPI encryption. Audio and screen frames stream only during an active session, and only to Google's AI service. There is zero telemetry, no proxy and no analytics.",
  },
  {
    match: /companion|screen|vision|see|win\s*\+?\s*shift/i,
    answer:
      "Press Win+Shift to start the multimodal companion. It's a real-time voice conversation on the AI Engine that speaks through your speakers. Optional ~1 fps desktop sharing lets it see your screen, and you can toggle that mid-session.",
  },
  {
    match: /click|control|agent|operate|desktop|scroll/i,
    answer:
      'Voice desktop control lets you say things like "click Send", "scroll down", "type hello…" or "press Ctrl+S". It acts one step at a time and narrates as it goes. Reasoning depth (Low / Medium / High) lives in Preferences → Agent Reasoning, a governor caps runs at 25 steps with no loops, and saying stop halts it instantly.',
  },
  {
    match: /model|engine|gemini/i,
    answer:
      "Voxula runs on the AI Engine with automatic fallback. You can set reasoning depth in Preferences, and the full table of what runs where is in Docs → AI Engine.",
  },
  {
    match: /shortcut|hotkey|keyboard|ctrl|esc/i,
    answer:
      "Ctrl+Space toggles dictation. Win+Shift starts the companion. Ctrl+Win purges the session and token counter. Esc dismisses to the tray. And just say refine to rewrite your session.",
  },
  {
    match: /free|cost|price|pricing|subscription|pay|money/i,
    answer:
      "Voxula is 100% free with no subscription. You bring a free Google key, and a free-tier fallback key is included so you can start immediately.",
  },
  {
    match: /github|source|code|repo/i,
    answer: `The project lives at ${GITHUB_REPO_URL.replace("https://github.com/", "")}. You can inspect the repo or download ${INSTALLER_FILE} straight from there.`,
  },
  {
    match: /mac|linux|ios|android|mobile|phone/i,
    answer:
      "Voxula AI is a native Windows app (Windows 10 Build 19041+ or Windows 11, 64-bit). A mobile companion for voice notes is mentioned on the site, but there is no Mac, Linux or mobile download.",
  },
];

const CORPUS: { t: string; body: string }[] = [
  { t: "Dictation", body: "Ctrl+Space toggles dictation. Mic audio streams at 16 kHz mono and words are typed directly at the cursor in whatever app is focused — multilingual auto-detect, sub-second. The capsule shows live status, a visualizer, interim preview and a token bar." },
  { t: "Context", body: "A 3px token bar sits under the capsule: green 0–60%, orange 61–85%, red 86–100%. Hover for exact counts. Ctrl+Win instantly stops the session and clears transcript, typed history and the token counter." },
  { t: "Canvas & tray", body: "The screen canvas is a fullscreen transparent ink layer: B and 1–3 pick colors, right-click clears, Esc exits. The system tray shows or hides the capsule and has Dictation, Companion, Purge, Refine, Guide, Settings and Exit." },
  { t: "Settings", body: "Four tabs: Setup (primary and backup keys, Test button), Guide (shortcut reference), Preferences (microphone, vocabulary, system prompt, creativity, live-screen, agent reasoning, Windows startup) and Refine (prompts, triggers, up to 3 custom actions)." },
  { t: "Troubleshooting", body: "If the companion says Live connect failed, test your key in Settings → Setup and add a backup key. If the mic is silent, refresh Preferences → Microphone. If refine says click your document, click the target app and say the trigger again. If the capsule is hidden, press Ctrl+Space or use tray → Show capsule." },
  { t: "System requirements", body: "DirectX 11+, Windows 10 Build 19041+ or Windows 11, 64-bit. The installer needs no admin rights and includes an uninstaller." },
  { t: "Keys", body: "Primary and backup keys are kept in Windows Credential Manager. On rate limits or drops, Voxula rotates keys and reconnects. After 3 failures in 30 seconds it stops rather than looping." },
];

function tokens(s: string) {
  return s.toLowerCase().replace(/[^a-z0-9\s]/g, " ").split(/\s+/).filter((w) => w.length > 2);
}

export function answerLocal(question: string): string {
  const hit = CANNED.find((c) => c.match.test(question));
  if (hit) return hit.answer;
  const q = new Set(tokens(question));
  const ranked = CORPUS.map((c) => ({
    c,
    score: tokens(c.t + " " + c.body).reduce((n, w) => n + (q.has(w) ? 1 : 0), 0),
  }))
    .filter((r) => r.score > 1)
    .sort((a, b) => b.score - a.score);
  if (ranked.length) return `${ranked[0].c.body} (Docs → ${ranked[0].c.t})`;
  return "I couldn't find that in the docs. Please check the Docs (#/docs) or the GitHub repository for more.";
}
