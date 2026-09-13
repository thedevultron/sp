"""TranscriptBuffer: additive history for refine workflow — non-breaking."""
import json
import time
from PySide6.QtCore import QObject, Signal
from src.config import HISTORY_FILE, CONFIG_DIR

class TranscriptBuffer(QObject):
    text_changed = Signal(str)
    interim_changed = Signal(str)
    refined = Signal(str, str)

    def __init__(self, autosave: bool = False):
        super().__init__()
        self._full = ""
        self._interim = ""
        self._history = []
        self._autosave = autosave
        # Do not restore previous session on startup — fresh each launch
        self._clear_persisted()

    def _clear_persisted(self):
        try:
            if HISTORY_FILE.exists():
                HISTORY_FILE.unlink()
        except Exception:
            pass
        self._full = ""
        self._history = []

    def _load(self):
        # Intentionally no-op — fresh start each launch per user request
        return

    def _save(self):
        if not self._autosave:
            return
        try:
            CONFIG_DIR.mkdir(parents=True, exist_ok=True)
            with open(HISTORY_FILE, "w", encoding="utf-8") as f:
                json.dump({"full_text": self._full, "history": self._history[-200:]}, f, indent=2, ensure_ascii=False)
        except Exception as e:
            print(f"[Buffer] save {e}")

    @property
    def full_text(self): return self._full
    @property
    def interim(self): return self._interim

    def _clean(self, text: str) -> str:
        import re
        t = text.strip()
        t = re.sub(r'^[—–\-•▶>]+\s*', '', t.lstrip())
        t = re.sub(r'^[*+]+\s+', '', t)
        return t

    def append_final(self, text: str):
        if not text or not text.strip():
            return
        clean = self._clean(text)
        if self._full and not self._full.endswith((" ", "\n", "\t")):
            self._full += " "
        self._full += clean + " "
        self._history.append({"ts": time.time(), "type": "final", "text": clean})
        self.text_changed.emit(self._full)
        self._save()

    def set_interim(self, text: str):
        self._interim = text.strip() if text else ""
        self.interim_changed.emit(self._interim)

    def clear_interim(self):
        self._interim = ""
        self.interim_changed.emit("")

    def clear_all(self):
        self._full = ""
        self._interim = ""
        self._history.clear()
        self.text_changed.emit("")
        self.interim_changed.emit("")
        self._save()

    def replace_full(self, new_text: str, action="refine"):
        self._full = self._clean(new_text).strip() + (" " if new_text and not new_text.endswith("\n") else "")
        self._history.append({"ts": time.time(), "type": f"refined:{action}", "text": new_text[:200]})
        self.text_changed.emit(self._full)
        self.refined.emit(action, new_text)
        self._save()

    def get_for_refine(self): return self._full.strip()
    def has_content(self): return bool(self._full.strip())
    def word_count(self): return len(self._full.strip().split()) if self._full.strip() else 0
