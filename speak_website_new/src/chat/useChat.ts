import { useCallback, useRef, useState } from 'react';
import { answerFromDocs } from './docsEngine';

export interface ChatMsg {
  role: 'user' | 'assistant';
  content: string;
}

const GREETING: ChatMsg = {
  role: 'assistant',
  content: 'Hi — ask me anything about Voxula. Short answers, straight from the Docs.',
};

/** POSTs the conversation to the server proxy (/api/chat), falling back to client-side docs retrieval. */
export function useChat() {
  const [messages, setMessages] = useState<ChatMsg[]>([GREETING]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const historyRef = useRef<ChatMsg[]>([GREETING]);
  const inflightRef = useRef<AbortController | null>(null);

  const post = useCallback(async (history: ChatMsg[]) => {
    const ctrl = new AbortController();
    inflightRef.current = ctrl;
    setLoading(true);
    const timer = window.setTimeout(() => ctrl.abort(), 10000);
    const lastUserQuery = [...history].reverse().find((m) => m.role === 'user')?.content || '';

    try {
      let reply = '';
      try {
        const r = await fetch('/api/chat', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ messages: history.slice(-8) }),
          signal: ctrl.signal,
        });
        if (r.ok) {
          const contentType = r.headers.get('content-type') || '';
          if (contentType.includes('application/json')) {
            const data = (await r.json().catch(() => ({}))) as { reply?: unknown };
            if (typeof data.reply === 'string' && data.reply.trim()) {
              reply = data.reply.trim();
            }
          }
        }
      } catch {
        // Fall back to client-side retrieval
      }

      // If serverless proxy is unavailable or returned empty (e.g. static hosting), answer from Docs
      if (!reply && lastUserQuery) {
        // Brief natural pause
        await new Promise((res) => setTimeout(res, 350));
        reply = answerFromDocs(lastUserQuery);
      }

      if (!reply) {
        throw new Error("I couldn't find an answer to that right now. Please check the Docs tab.");
      }

      const assistantMsg: ChatMsg = { role: 'assistant', content: reply };
      historyRef.current = [...history, assistantMsg].slice(-30);
      setMessages([...historyRef.current]);
      setError(null);
    } catch (e) {
      if (e instanceof DOMException && e.name === 'AbortError') {
        const fallback = answerFromDocs(lastUserQuery);
        const assistantMsg: ChatMsg = { role: 'assistant', content: fallback };
        historyRef.current = [...history, assistantMsg].slice(-30);
        setMessages([...historyRef.current]);
        setError(null);
      } else {
        setError(e instanceof Error ? e.message : 'Something went wrong.');
      }
    } finally {
      window.clearTimeout(timer);
      inflightRef.current = null;
      setLoading(false);
    }
  }, []);

  const send = useCallback(
    (raw: string) => {
      const content = raw.trim().slice(0, 2000);
      if (!content || inflightRef.current) return;
      setError(null);
      const userMsg: ChatMsg = { role: 'user', content };
      const next: ChatMsg[] = [...historyRef.current, userMsg].slice(-30);
      historyRef.current = next;
      setMessages([...next]);
      void post(next);
    },
    [post]
  );

  /** Re-sends the current history (last message is the unanswered user turn). */
  const retry = useCallback(() => {
    if (inflightRef.current) return;
    const last = historyRef.current[historyRef.current.length - 1];
    if (!last || last.role !== 'user') return;
    setError(null);
    void post(historyRef.current);
  }, [post]);

  return { messages, loading, error, send, retry };
}
