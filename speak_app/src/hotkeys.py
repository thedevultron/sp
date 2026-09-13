import time
from pynput import keyboard
from PySide6.QtCore import QObject, Signal, QTimer


class GlobalHotkeyListener(QObject):
    """Background keyboard listener for global system shortcuts.
    Fixed: debounce, WIN detection on Windows, thread-safe signals, no spam.
    """

    sig_toggle_dictation = Signal()  # Ctrl + Space
    sig_toggle_companion = Signal()  # Win + Shift
    sig_purge_reset = Signal()       # Ctrl + Win
    sig_new_session = Signal()       # Ctrl + Tab — spawn + switch live session

    def __init__(self):
        super().__init__()
        self._listener = None
        self._pressed = set()
        self._is_running = False
        self._last_emit = {"dictation": 0, "companion": 0, "purge": 0, "new_session": 0}
        self._debounce_ms = 600  # prevent double-fire when holding keys

    def start(self):
        if self._is_running:
            return
        self._is_running = True
        self._pressed.clear()
        try:
            self._listener = keyboard.Listener(
                on_press=self._on_press,
                on_release=self._on_release,
                suppress=False
            )
            self._listener.daemon = True
            self._listener.start()
            print("[Hotkeys] Listener started")
        except Exception as e:
            print(f"[Hotkeys] Failed to start: {e}")
            self._is_running = False

    def stop(self):
        self._is_running = False
        self._pressed.clear()
        if self._listener:
            try:
                self._listener.stop()
                # Don't wait indefinitely
                self._listener.join(timeout=1.0)
            except Exception:
                pass
            self._listener = None
            print("[Hotkeys] Listener stopped")

    def _normalize(self, key):
        # Handle special keys
        try:
            if key in (keyboard.Key.ctrl, keyboard.Key.ctrl_l, keyboard.Key.ctrl_r):
                return "CTRL"
            if key in (keyboard.Key.cmd, keyboard.Key.cmd_l, keyboard.Key.cmd_r):
                return "WIN"
            # Windows key may also be reported as 'cmd' via cmd key
            if key == keyboard.Key.alt or key == keyboard.Key.alt_l or key == keyboard.Key.alt_r:
                return "ALT"
            if key in (keyboard.Key.shift, keyboard.Key.shift_l, keyboard.Key.shift_r):
                return "SHIFT"
            if key == keyboard.Key.space:
                return "SPACE"
            if key == keyboard.Key.tab:
                return "TAB"
            if key == keyboard.Key.esc:
                return "ESC"
            # For char keys, normalize case
            if hasattr(key, 'char') and key.char:
                return key.char.lower()
            if hasattr(key, 'vk') and key.vk == 91:  # VK_LWIN
                return "WIN"
            if hasattr(key, 'vk') and key.vk == 92:  # VK_RWIN
                return "WIN"
        except Exception:
            pass
        return key

    def _should_emit(self, action: str) -> bool:
        now = time.time() * 1000
        last = self._last_emit.get(action, 0)
        if now - last < self._debounce_ms:
            return False
        self._last_emit[action] = now
        return True

    def _on_press(self, key):
        try:
            norm = self._normalize(key)
        except Exception:
            return
        try:
            self._pressed.add(norm)
        except Exception:
            return

        # Ctrl + Tab = NEW live session (spawn + switch). Tab alone is still
        # focus navigation and is ignored; only the explicit Ctrl+Tab chord fires.
        try:
            if "CTRL" in self._pressed and "TAB" in self._pressed and "SPACE" not in self._pressed:
                if self._should_emit("new_session"):
                    print("[Hotkeys] Ctrl+Tab -> new session")
                    try:
                        self.sig_new_session.emit()
                    except Exception as e:
                        print(f"[Hotkeys] emit new_session failed: {e}")
                    self._pressed.discard("TAB")
                return
        except Exception:
            pass

        # Use set checks; ensure we don't emit spuriously on key repeat
        # 1. Ctrl + Space (Dictation) - highest priority
        if "CTRL" in self._pressed and "SPACE" in self._pressed:
            if self._should_emit("dictation"):
                print("[Hotkeys] Ctrl+Space -> dictation")
                try:
                    self.sig_toggle_dictation.emit()
                except Exception as e:
                    print(f"[Hotkeys] emit dictation failed: {e}")
                # Clear to prevent repeat firing while holding
                self._pressed.discard("SPACE")
            return

        # 2. Win + Shift (Companion) — only without Ctrl (avoids Ctrl+Win purge misfire)
        if "WIN" in self._pressed and "SHIFT" in self._pressed and "CTRL" not in self._pressed:
            if self._should_emit("companion"):
                print("[Hotkeys] Win+Shift -> companion")
                try:
                    self.sig_toggle_companion.emit()
                except Exception as e:
                    print(f"[Hotkeys] emit companion failed: {e}")
                self._pressed.discard("SHIFT")
            return

        # 3. Ctrl + Win (Purge & Reset) — only without Shift (avoids Win+Shift misfire)
        if "CTRL" in self._pressed and "WIN" in self._pressed and "SHIFT" not in self._pressed:
            if self._should_emit("purge"):
                print("[Hotkeys] Ctrl+Win -> purge")
                try:
                    self.sig_purge_reset.emit()
                except Exception as e:
                    print(f"[Hotkeys] emit purge failed: {e}")
                # Don't discard WIN immediately: Win key sticky on Windows
            return

    def _on_release(self, key):
        norm = self._normalize(key)
        # pynput may send different object for release; ensure string match
        try:
            self._pressed.discard(norm)
            # Also discard variations
            if norm == "CTRL":
                self._pressed.discard("CTRL")
            elif norm == "WIN":
                self._pressed.discard("WIN")
            elif norm == "SHIFT":
                self._pressed.discard("SHIFT")
            elif norm == "SPACE":
                self._pressed.discard("SPACE")
            elif norm == "TAB":
                self._pressed.discard("TAB")
        except Exception:
            pass
