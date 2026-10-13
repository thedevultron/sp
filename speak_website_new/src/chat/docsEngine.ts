import corpusData from './corpus.json';
import { INSTALLER_FILE, INSTALLER_SIZE, SITE_VERSION } from '../site';

interface CorpusChunk {
  id: number;
  source: string;
  text: string;
  weight: number;
}

const docs = corpusData as CorpusChunk[];

const STOP_WORDS = new Set([
  'the', 'a', 'an', 'and', 'or', 'but', 'is', 'are', 'was', 'were', 'be', 'to',
  'of', 'in', 'on', 'for', 'with', 'how', 'what', 'does', 'do', 'it', 'my',
  'your', 'voxula', 'ai', 'app', 'can', 'use', 'using', 'this', 'that', 'have',
  'has', 'will', 'would', 'should', 'could', 'there', 'their', 'they', 'them',
  'from', 'about', 'into', 'over', 'you', 'please', 'tell', 'show', 'get', 'i',
  'me', 'any', 'where', 'which', 'who', 'when', 'why'
]);

function extractTokens(str: string): string[] {
  return str
    .toLowerCase()
    .replace(/[^a-z0-9+\s#._-]/g, ' ')
    .split(/\s+/)
    .filter((t) => t.length > 1 && !STOP_WORDS.has(t));
}

export function answerFromDocs(query: string): string {
  const qLower = query.toLowerCase().trim();

  // Instant answers for primary questions
  if (qLower.includes('install') || qLower.includes('download') || qLower.includes('setup') || qLower.includes('get started')) {
    return `To install Voxula AI (${SITE_VERSION}):\n1. Download the Windows installer (${INSTALLER_FILE}, ${INSTALLER_SIZE}) from our GitHub repository or the download button.\n2. Run the setup wizard — no administrator rights needed; uninstaller included.\n3. Bring a free API key from Google AI Studio (or set GEMINI_API_KEY).\n4. Place your cursor in any app and press Ctrl + Space to dictate!`;
  }

  if (qLower.includes('refine') || qLower.includes('polish') || qLower.includes('elaborate')) {
    return `Refine is Voxula AI's hands-free session rewriter. Say "refine", "polish", or "elaborate" (or tap the capsule buttons), and the app measures Backspaces to delete your draft and retypes a clean, structured version directly at your cursor. You can also customize prompts and triggers in Settings → Refine.`;
  }

  if (qLower.includes('private') || qLower.includes('privacy') || qLower.includes('security') || qLower.includes('telemetry') || qLower.includes('key')) {
    return `Voxula AI is private by design. Your API keys are encrypted locally with Windows Credential Manager (DPAPI). Microphone and screen frames stream only during active sessions directly to Google's AI service — zero telemetry, no proxy servers, and no analytics.`;
  }

  if (qLower.includes('companion') || qLower.includes('screen') || qLower.includes('vision') || qLower.includes('see')) {
    return `Press Win + Shift to start the Multimodal Live Companion, powered by the AI Engine. It speaks aloud through your speakers and can optionally see your active desktop (~1 fps) so you can brainstorm, debug code, or dictate with full visual context. You can toggle screen vision anytime mid-session.`;
  }

  if (qLower.includes('click') || qLower.includes('control') || (qLower.includes('agent') && !qLower.includes('key')) || qLower.includes('operate') || qLower.includes('desktop') || qLower.includes('thinking')) {
    return `The companion is a full voice agent: tell it "click Send", "scroll down", "type hello in the email field", or "press Ctrl+S" and it operates your desktop step by step, narrating as it goes. Reasoning depth (Low / Medium / High, default Medium) lives in Settings → Preferences → Agent Reasoning. Safety governor: desktop UI actions only, 25-step budget, no loops — say "stop" to halt instantly.`;
  }

  if (qLower.includes('model')) {
    return `Voxula AI runs on the AI Engine with automatic fallback for the companion, dictation, and refine. Reasoning depth (Low / Medium / High, default Medium) lives in Settings → Preferences → Agent Reasoning. Full table in Docs → AI Engine.`;
  }

  if (qLower.includes('shortcut') || qLower.includes('hotkey') || qLower.includes('keys')) {
    return `Global shortcuts:\n• Ctrl + Space: Toggle live voice dictation (types at cursor)\n• Win + Shift: Toggle multimodal live companion (voice + screen)\n• Ctrl + Win: Purge session (transcript, typed history, tokens)\n• Esc: Clear canvas and dismiss capsule to tray\n• Say "refine": Instant delete-and-rewrite`;
  }

  if (qLower.includes('free') || qLower.includes('cost') || qLower.includes('price') || qLower.includes('subscription')) {
    return `Voxula AI is 100% free with no subscriptions. You bring your own free API key from Google AI Studio. The app also includes a free-tier fallback key so you can start right away.`;
  }

  if (qLower.includes('github') || qLower.includes('source') || qLower.includes('code') || qLower.includes('repo')) {
    return `The official installer and repository are hosted on GitHub at codedebuggalt/voxula_ai_installer. You can inspect the release files or download SPEAK_Setup_v2.1.exe directly.`;
  }

  // Fallback: Ranked keyword overlap retrieval across documentation chunks
  const qTokens = extractTokens(query);
  if (!qTokens.length) {
    return "Hi — ask me anything about Voxula AI: installation, dictation, companion, shortcuts, privacy, or refine. You can also check the full guide in the Docs page.";
  }

  const scored = docs
    .map((chunk) => {
      const cTokens = extractTokens(chunk.text);
      const cSet = new Set(cTokens);
      let matches = 0;
      for (const t of qTokens) {
        if (cSet.has(t)) matches += 1;
      }
      return { chunk, score: matches * (chunk.weight || 1) };
    })
    .filter((s) => s.score > 0)
    .sort((a, b) => b.score - a.score);

  if (scored.length > 0) {
    const topChunk = scored[0].chunk.text;
    // Clean up markdown/tokens into plain readable sentences
    const cleanSentence = topChunk
      .replace(/\[([^\]]+)\]\([^)]+\)/g, '$1')
      .replace(/[#*`>]/g, '')
      .replace(/\s+/g, ' ')
      .trim();

    return `${cleanSentence.slice(0, 320)}...\n\nFor more details, open the full guide in the Docs tab.`;
  }

  return "I couldn't find a direct answer to that in the quick guide, but you can find the complete reference in the Docs section (#/docs) or visit our GitHub repository.";
}
