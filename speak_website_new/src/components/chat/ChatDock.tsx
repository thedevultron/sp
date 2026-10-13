import { useEffect, useRef, useState } from 'react';
import { LayoutGroup, motion, useReducedMotion } from 'motion/react';
import { ArrowUp, MessageCircle, X } from 'lucide-react';
import { useChat } from '../../chat/useChat';

const SUGGESTIONS = ['How do I install it?', 'What does refine do?', 'Is my voice private?'];

function ChatBody({
  docked,
  onFirstType,
  onClose,
}: {
  docked: boolean;
  onFirstType: () => void;
  onClose: () => void;
}) {
  const { messages, loading, error, send, retry } = useChat();
  const [draft, setDraft] = useState('');
  const listRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    const el = listRef.current;
    if (el) el.scrollTop = el.scrollHeight;
  }, [messages, loading]);

  useEffect(() => {
    const onKey = (e: KeyboardEvent) => {
      if (e.key === 'Escape') onClose();
    };
    window.addEventListener('keydown', onKey);
    return () => window.removeEventListener('keydown', onKey);
  }, [onClose]);

  return (
    <>
      <div className="chat-head">
        <span className="chat-head-icon">
          <MessageCircle size={15} />
        </span>
        <div>
          <strong>Ask Voxula</strong>
          <span>Answers from the Docs</span>
        </div>
        <button type="button" className="chat-close" onClick={onClose} aria-label="Close chat">
          <X size={16} />
        </button>
      </div>
      <div className="chat-list" ref={listRef} role="log" aria-live="polite" aria-label="Chat messages">
        {messages.map((m, i) => (
          <div key={i} className={m.role === 'user' ? 'chat-msg is-user' : 'chat-msg is-bot'}>
            <p>{m.content}</p>
          </div>
        ))}
        {messages.length <= 1 && (
          <div className="chat-suggest">
            {SUGGESTIONS.map((s) => (
              <button
                key={s}
                type="button"
                onClick={() => {
                  onFirstType();
                  send(s);
                }}
              >
                {s}
              </button>
            ))}
          </div>
        )}
        {loading && (
          <div className="chat-msg is-bot">
            <p className="chat-typing" aria-label="Assistant is typing">
              <i />
              <i />
              <i />
            </p>
          </div>
        )}
        {error && (
          <div className="chat-error" role="alert">
            <span>{error}</span>
            <button type="button" onClick={retry}>
              Try again
            </button>
          </div>
        )}
      </div>
      <form
        className="chat-form"
        onSubmit={(e) => {
          e.preventDefault();
          if (!draft.trim()) return;
          onFirstType();
          send(draft);
          setDraft('');
        }}
      >
        <input
          // eslint-disable-next-line jsx-a11y/no-autofocus
          autoFocus={!docked}
          type="text"
          value={draft}
          onChange={(e) => {
            if (e.target.value.length === 1) onFirstType();
            setDraft(e.target.value);
          }}
          placeholder="Ask about Voxula…"
          aria-label="Ask about Voxula"
          maxLength={2000}
          autoComplete="off"
        />
        <button type="submit" aria-label="Send message" disabled={!draft.trim() || loading}>
          <ArrowUp size={16} />
        </button>
      </form>
    </>
  );
}

/**
 * ChatDock — quiet until invited. The CTA lives at the end of the page;
 * opening shows a centered card, and the first keystroke animates it into
 * a small docked window on the right. No model names anywhere.
 */
export default function ChatDock({ onClose }: { onClose: () => void }) {
  const [docked, setDocked] = useState(false);
  const reduced = useReducedMotion();
  const firstType = () => setDocked(true);

  if (reduced) {
    return (
      <div className={docked ? 'chat-root is-docked' : 'chat-root is-open'}>
        <div className={docked ? 'chat-panel is-docked' : 'chat-panel is-open'}>
          <ChatBody docked={docked} onFirstType={firstType} onClose={onClose} />
        </div>
      </div>
    );
  }

  return (
    <LayoutGroup>
      <div className={docked ? 'chat-root is-docked' : 'chat-root is-open'}>
        {!docked && (
          <motion.div
            className="chat-scrim"
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            transition={{ duration: 0.25 }}
            onClick={onClose}
          />
        )}
        <motion.div
          layoutId="voxula-chat-panel"
          className={docked ? 'chat-panel is-docked' : 'chat-panel is-open'}
          transition={{ type: 'spring', stiffness: 380, damping: 34 }}
          onClick={(e) => e.stopPropagation()}
        >
          <ChatBody docked={docked} onFirstType={firstType} onClose={onClose} />
        </motion.div>
      </div>
    </LayoutGroup>
  );
}
