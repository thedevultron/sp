"""Multi-Session Engine — hot-swappable live sessions with FIFO eviction.

Keeps full compatibility with existing GeminiLiveManager / AudioLoop worker tasks.
Each stored session is lightweight metadata + transcript snapshot; live handles
stay in the owning GeminiLiveManager. FIFO eviction enforces Max Stored Sessions.
"""
from __future__ import annotations
import time
import uuid
from dataclasses import dataclass, field, asdict
from typing import List, Dict, Any
from PySide6.QtCore import QObject, Signal


@dataclass
class SessionRecord:
    session_id: str = field(default_factory=lambda: uuid.uuid4().hex[:8])
    mode: str = "companion"  # dictation | companion | none
    model: str = ""
    created_ts: float = field(default_factory=time.time)
    last_active_ts: float = field(default_factory=time.time)
    transcript_chars: int = 0
    transcript_words: int = 0
    status: str = "stored"  # active | stored | evicted
    note: str = ""

    def to_dict(self) -> Dict[str, Any]:
        d = asdict(self)
        try:
            d["created"] = time.strftime("%H:%M:%S", time.localtime(self.created_ts))
            d["last_active"] = time.strftime("%H:%M:%S", time.localtime(self.last_active_ts))
        except Exception:
            d["created"] = ""
            d["last_active"] = ""
        return d


class SessionManager(QObject):
    """Owns session metadata list + FIFO eviction. Emits Qt signals for UI."""

    sessions_changed = Signal()
    active_session_changed = Signal(str)  # session_id

    def __init__(self, max_stored: int = 5, parent=None):
        super().__init__(parent)
        self._max_stored = max(1, min(20, int(max_stored or 5)))
        self._sessions: List[SessionRecord] = []
        self._active_id: str = ""
        self._counter = 0

    # -- config --
    @property
    def max_stored(self) -> int:
        return self._max_stored

    def set_max_stored(self, n: int):
        try:
            n = max(1, min(20, int(n)))
        except Exception:
            n = 5
        self._max_stored = n
        self._enforce_fifo()
        try:
            self.sessions_changed.emit()
        except Exception:
            pass

    # -- lifecycle --
    def spawn_session(self, mode: str = "companion", model: str = "") -> SessionRecord:
        """Create + activate a new live session record. Evicts oldest if over threshold."""
        self._counter += 1
        # mark previous active as stored
        for s in self._sessions:
            if s.session_id == self._active_id and s.status == "active":
                s.status = "stored"
                s.last_active_ts = time.time()
        rec = SessionRecord(mode=mode or "companion", model=model or "", status="active")
        try:
            rec.note = f"Session #{self._counter}"
        except Exception:
            pass
        self._sessions.append(rec)
        self._active_id = rec.session_id
        self._enforce_fifo()
        try:
            self.sessions_changed.emit()
            self.active_session_changed.emit(self._active_id)
        except Exception:
            pass
        print(f"[Sessions] Spawned {rec.session_id} mode={rec.mode} total={len(self._sessions)}")
        return rec

    def switch_to(self, session_id: str) -> bool:
        found = False
        for s in self._sessions:
            if s.session_id == session_id:
                found = True
                s.status = "active"
                s.last_active_ts = time.time()
                self._active_id = session_id
            elif s.status == "active":
                s.status = "stored"
                s.last_active_ts = time.time()
        if found:
            try:
                self.sessions_changed.emit()
                self.active_session_changed.emit(session_id)
            except Exception:
                pass
        return found

    def mark_stored(self, session_id: str = ""):
        sid = session_id or self._active_id
        for s in self._sessions:
            if s.session_id == sid:
                s.status = "stored"
                s.last_active_ts = time.time()
        if sid == self._active_id:
            self._active_id = ""
        try:
            self.sessions_changed.emit()
        except Exception:
            pass

    def update_transcript_stats(self, session_id: str, chars: int, words: int):
        for s in self._sessions:
            if s.session_id == session_id:
                s.transcript_chars = int(chars or 0)
                s.transcript_words = int(words or 0)
                break

    def _enforce_fifo(self):
        """FIFO eviction when stored sessions exceed threshold (oldest first)."""
        # Only evict stored (non-active) first; if still over, evict oldest overall except active
        while len(self._sessions) > self._max_stored:
            # find oldest stored
            oldest_idx = -1
            oldest_ts = None
            for i, s in enumerate(self._sessions):
                if s.session_id == self._active_id:
                    continue
                if oldest_ts is None or s.created_ts < oldest_ts:
                    oldest_ts = s.created_ts
                    oldest_idx = i
            if oldest_idx < 0:
                # all are active (single) — drop oldest non-active fallback: drop index 0 if not active
                if self._sessions and self._sessions[0].session_id != self._active_id:
                    oldest_idx = 0
                else:
                    break
            try:
                evicted = self._sessions.pop(oldest_idx)
                print(f"[Sessions] FIFO evicted {evicted.session_id} (max={self._max_stored})")
            except Exception:
                break

    # -- queries for UI --
    def active_count(self) -> int:
        return sum(1 for s in self._sessions if s.status == "active")

    def stored_count(self) -> int:
        return len(self._sessions)

    def active_id(self) -> str:
        return self._active_id

    def list_metadata(self) -> List[Dict[str, Any]]:
        return [s.to_dict() for s in reversed(self._sessions)]  # newest first for UI

    def clear_all(self):
        self._sessions.clear()
        self._active_id = ""
        try:
            self.sessions_changed.emit()
        except Exception:
            pass
