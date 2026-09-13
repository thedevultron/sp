"""InjectionService - precise measured typing & refine replacement.

Guarantees:
- No Enter pressing.
- Measures EXACT words/chars typed via safe_type and stores per-session.
- On refine: deletes EXACTLY that many chars via Backspace SendInput, then types refined via unicode SendInput (no clipboard, no Ctrl+A).
- Verifies foreground window != SPEAK before injecting.
- Fallback to pyautogui only if ctypes unavailable.
"""
import time
import asyncio

try:
    import win32clipboard
    import win32con
    HAS_WIN32 = True
except Exception:
    HAS_WIN32 = False

try:
    import ctypes
    from ctypes import wintypes
    HAS_CTYPES = True
except Exception:
    HAS_CTYPES = False

try:
    import pyautogui
    pyautogui.FAILSAFE = False
    pyautogui.PAUSE = 0.0
except Exception:
    pyautogui = None

try:
    from pynput.keyboard import Controller as _PynputController, Key as _PynputKey
    HAS_PYNPUT = True
except Exception:
    HAS_PYNPUT = False
    _PynputController = None
    _PynputKey = None


def _pynput_backspaces(count: int) -> int:
    """Press BackSpace `count` times via pynput (count = transcript chars). Returns sent."""
    count = max(0, min(int(count), 4000))
    if count <= 0 or not HAS_PYNPUT:
        return 0
    sent = 0
    try:
        kb = _PynputController()
        for _ in range(count):
            # Abort mid-flood if focus moved (never delete the wrong window to completion)
            if sent % 200 == 0 and sent > 0 and not _is_injection_safe():
                print(f"[Injection] pynput backspace abort at {sent}/{count} - focus moved")
                break
            kb.press(_PynputKey.backspace)
            kb.release(_PynputKey.backspace)
            sent += 1
        return int(sent)
    except Exception as e:
        print(f"[Injection] pynput backspace fail {e}")
        return int(sent)


def _get_foreground_hwnd():
    try:
        if HAS_CTYPES:
            return ctypes.windll.user32.GetForegroundWindow()
    except Exception:
        pass
    return 0


def _get_speak_hwnds():
    try:
        from PySide6.QtWidgets import QApplication
        app = QApplication.instance()
        if not app:
            return set()
        hwnds = set()
        for w in app.topLevelWidgets():
            try:
                hwnds.add(int(w.winId()))
            except Exception:
                pass
        return hwnds
    except Exception:
        return set()


def _is_injection_safe() -> bool:
    try:
        fg = _get_foreground_hwnd()
        speak_hwnds = _get_speak_hwnds()
        if fg and fg in speak_hwnds:
            return False
        return True
    except Exception:
        return True


def _ctypes_unicode_send(text: str):
    if not HAS_CTYPES:
        raise RuntimeError("ctypes not available")
    PUL = ctypes.POINTER(ctypes.c_ulong)
    class KEYBDINPUT(ctypes.Structure):
        _fields_ = [("wVk", wintypes.WORD),
                    ("wScan", wintypes.WORD),
                    ("dwFlags", wintypes.DWORD),
                    ("time", wintypes.DWORD),
                    ("dwExtraInfo", PUL)]
    class MOUSEINPUT(ctypes.Structure):
        _fields_ = [("dx", wintypes.LONG),
                    ("dy", wintypes.LONG),
                    ("mouseData", wintypes.DWORD),
                    ("dwFlags", wintypes.DWORD),
                    ("time", wintypes.DWORD),
                    ("dwExtraInfo", PUL)]
    class HARDWAREINPUT(ctypes.Structure):
        _fields_ = [("uMsg", wintypes.DWORD),
                    ("wParamL", wintypes.WORD),
                    ("wParamH", wintypes.WORD)]
    class INPUT_I(ctypes.Union):
        _fields_ = [("ki", KEYBDINPUT),
                    ("mi", MOUSEINPUT),
                    ("hi", HARDWAREINPUT)]
    class INPUT(ctypes.Structure):
        _fields_ = [("type", wintypes.DWORD),
                    ("ii", INPUT_I)]
    KEYEVENTF_UNICODE = 0x0004
    KEYEVENTF_KEYUP = 0x0002
    INPUT_KEYBOARD = 1
    extra = ctypes.c_ulong(0)
    inputs = []
    for ch in text:
        ki_down = KEYBDINPUT(wVk=0, wScan=ord(ch), dwFlags=KEYEVENTF_UNICODE, time=0, dwExtraInfo=ctypes.pointer(extra))
        inp_down = INPUT(type=INPUT_KEYBOARD, ii=INPUT_I(ki=ki_down))
        inputs.append(inp_down)
        ki_up = KEYBDINPUT(wVk=0, wScan=ord(ch), dwFlags=KEYEVENTF_UNICODE | KEYEVENTF_KEYUP, time=0, dwExtraInfo=ctypes.pointer(extra))
        inp_up = INPUT(type=INPUT_KEYBOARD, ii=INPUT_I(ki=ki_up))
        inputs.append(inp_up)
    n = len(inputs)
    arr = (INPUT * n)(*inputs)
    ctypes.windll.user32.SendInput(n, arr, ctypes.sizeof(INPUT))


def _send_backspaces(count: int, chunk: int = 120) -> int:
    """Send `count` Backspace presses via SendInput (or pyautogui fallback).
    Returns chars actually sent (0 when focus-unsafe or no backend)."""
    if count <= 0:
        return 0
    if not _is_injection_safe():
        print("[Injection] Backspace skip - SPEAK focused")
        return 0
    if HAS_CTYPES:
        try:
            PUL = ctypes.POINTER(ctypes.c_ulong)
            class KBD(ctypes.Structure):
                _fields_ = [("wVk", wintypes.WORD), ("wScan", wintypes.WORD), ("dwFlags", wintypes.DWORD), ("time", wintypes.DWORD), ("dwExtraInfo", PUL)]
            class INP_I(ctypes.Union):
                _fields_ = [("ki", KBD)]
            class INP(ctypes.Structure):
                _fields_ = [("type", wintypes.DWORD), ("ii", INP_I)]
            VK_BACK = 0x08
            extra = ctypes.c_ulong(0)
            def kd(vk): return INP(type=1, ii=INP_I(ki=KBD(wVk=vk, wScan=0, dwFlags=0, time=0, dwExtraInfo=ctypes.pointer(extra))))
            def ku(vk): return INP(type=1, ii=INP_I(ki=KBD(wVk=vk, wScan=0, dwFlags=2, time=0, dwExtraInfo=ctypes.pointer(extra))))
            # Chunk to avoid huge SendInput arrays
            remaining = count
            while remaining > 0:
                cur = min(remaining, chunk)
                n = cur * 2
                arr = (INP * n)()
                idx = 0
                for _ in range(cur):
                    arr[idx] = kd(VK_BACK); idx += 1
                    arr[idx] = ku(VK_BACK); idx += 1
                ctypes.windll.user32.SendInput(n, arr, ctypes.sizeof(INP))
                remaining -= cur
                if remaining > 0:
                    time.sleep(0.015)
            print(f"[Injection] Sent {count} Backspaces")
            return int(count)
        except Exception as e:
            print(f"[Injection] Backspace SendInput fail {e}")
            return 0
    # Fallback pyautogui
    if pyautogui:
        try:
            # pyautogui.press in loop chunked
            sent_pg = 0
            for _ in range(count):
                pyautogui.press("backspace")
                sent_pg += 1
            print(f"[Injection] Sent {count} Backspaces via pyautogui")
            return int(sent_pg)
        except Exception as e:
            print(f"[Injection] pyautogui backspace fail {e}")
            return 0
    return 0


class InjectionService:
    """Tracks exact typed content for session delete-and-replace."""
    _segments: list[str] = []
    _total_len: int = 0
    _lock = None  # lazy init
    # Last known non-SPEAK target (for focus restore on refine). 0 = unknown.
    _last_target_hwnd: int = 0

    @classmethod
    def _ensure_lock(cls):
        if cls._lock is None:
            try:
                import threading
                cls._lock = threading.Lock()
            except Exception:
                cls._lock = None

    @classmethod
    def clear_history(cls):
        cls._ensure_lock()
        try:
            if cls._lock:
                with cls._lock:
                    cls._segments.clear()
                    cls._total_len = 0
            else:
                cls._segments.clear()
                cls._total_len = 0
        except Exception:
            cls._segments = []
            cls._total_len = 0
        print("[Injection] History cleared")

    @classmethod
    def _remember_target(cls, hwnd: int):
        try:
            hwnd = int(hwnd or 0)
            if hwnd > 0:
                cls._ensure_lock()
                if cls._lock:
                    with cls._lock:
                        cls._last_target_hwnd = hwnd
                else:
                    cls._last_target_hwnd = hwnd
        except Exception:
            pass

    @classmethod
    def _restore_last_target(cls) -> bool:
        """If SPEAK is focused, try to restore the last typing target. Returns True if safe now."""
        try:
            if _is_injection_safe():
                return True
            hwnd = int(getattr(cls, "_last_target_hwnd", 0) or 0)
            if hwnd <= 0 or not HAS_CTYPES:
                return False
            try:
                ctypes.windll.user32.SetForegroundWindow(ctypes.c_void_p(hwnd))
            except Exception:
                return False
            time.sleep(0.25)
            return bool(_is_injection_safe())
        except Exception:
            return False

    @classmethod
    def get_typed_length(cls) -> int:
        cls._ensure_lock()
        try:
            if cls._lock:
                with cls._lock:
                    return cls._total_len
            return cls._total_len
        except Exception:
            return cls._total_len

    @classmethod
    def get_typed_text(cls) -> str:
        try:
            return "".join(cls._segments)
        except Exception:
            return ""

    @classmethod
    def get_segment_count(cls) -> int:
        try:
            return len(cls._segments)
        except Exception:
            return 0

    @classmethod
    def _record(cls, text: str):
        # Central cap: history length drives delete counts, never store unbounded text
        try:
            text = str(text or "")[:4000]
        except Exception:
            return
        if not text:
            return
        cls._ensure_lock()
        try:
            if cls._lock:
                with cls._lock:
                    cls._segments.append(text)
                    cls._total_len += len(text)
            else:
                cls._segments.append(text)
                cls._total_len += len(text)
        except Exception:
            cls._segments.append(text)
            cls._total_len += len(text)

    @staticmethod
    def safe_type(text: str, interval: float = 0.001):
        """Type `text` exactly and measure it (session scope)."""
        if not text:
            return
        if not _is_injection_safe():
            print("[Injection] Skip safe_type - SPEAK focused")
            return
        # Remember target HWND for later focus restore on refine
        try:
            InjectionService._remember_target(_get_foreground_hwnd())
        except Exception:
            pass
        # Send
        sent_ok = False
        if len(text) < 180:
            try:
                if HAS_CTYPES:
                    _ctypes_unicode_send(text)
                    sent_ok = True
                elif pyautogui:
                    pyautogui.write(text, interval=interval)
                    sent_ok = True
            except Exception as e:
                print(f"[Injection] unicode send fallback {e}")
        if not sent_ok:
            try:
                if pyautogui:
                    pyautogui.write(text, interval=interval)
                    sent_ok = True
                elif HAS_CTYPES:
                    _ctypes_unicode_send(text)
                    sent_ok = True
            except Exception as e:
                print(f"[Injection] safe_type fallback {e}")
        # Record only if sent
        if sent_ok:
            InjectionService._record(text)
            # tiny throttle to keep cursor in sync
            if len(text) > 80:
                time.sleep(0.01)

    @staticmethod
    def _ensure_target() -> bool:
        """Focus guard: restore last target once. True when safe to inject."""
        if _is_injection_safe():
            return True
        try:
            return bool(InjectionService._restore_last_target())
        except Exception:
            return False

    @staticmethod
    def delete_chars(count: int) -> int:
        """Delete `count` transcript chars via pynput BackSpace (SendInput fallback).
        Returns chars deleted (0 when focus-unsafe — history kept for retry)."""
        try:
            count = max(0, min(int(count), 4000))
        except Exception:
            return 0
        if count <= 0:
            return 0
        if not InjectionService._ensure_target():
            print("[Injection] delete_chars skip - SPEAK focused, no delete (history kept)")
            return 0
        time.sleep(0.10)
        sent = _pynput_backspaces(count)
        if sent < count:
            # pynput unavailable/partial — finish the remainder via SendInput (honest count)
            try:
                sent += int(_send_backspaces(count - sent) or 0)
            except Exception:
                pass
        time.sleep(0.03)
        return int(sent)

    @staticmethod
    def type_text(text: str) -> int:
        """Type `text` exactly (unicode SendInput, chunked) + record history. Returns typed."""
        try:
            capped = str(text or "")[:4000]
        except Exception:
            capped = str(text or "")
        if not capped:
            return 0
        try:
            chunk_size = 800
            if len(capped) > chunk_size:
                for i in range(0, len(capped), chunk_size):
                    part = capped[i:i+chunk_size]
                    if HAS_CTYPES:
                        _ctypes_unicode_send(part)
                    elif pyautogui:
                        pyautogui.write(part, interval=0.001)
                    time.sleep(0.01)
            else:
                if HAS_CTYPES:
                    _ctypes_unicode_send(capped)
                elif pyautogui:
                    pyautogui.write(capped, interval=0.001)
        except Exception as e:
            print(f"[Injection] type_text fail {e}")
            try:
                if pyautogui:
                    pyautogui.write(capped, interval=0.001)
            except Exception:
                pass
        try:
            InjectionService._record(capped)
        except Exception:
            pass
        return int(len(capped))

    @staticmethod
    def _delete_count(fallback_len: int = 0) -> int:
        """How many chars to delete: measured history wins, else transcript snapshot."""
        try:
            n = int(InjectionService.get_typed_length() or 0)
        except Exception:
            n = 0
        if n > 0:
            return max(0, min(n, 4000))
        try:
            fb = max(0, min(int(fallback_len or 0), 4000))
        except Exception:
            fb = 0
        if fb > 0:
            print(f"[Injection] History empty, using transcript count delete_len={fb}")
        return fb

    @staticmethod
    def precise_replace(refined: str, fallback_len: int = 0):
        """Session delete-and-replace: pynput-Backspace transcript count, then type refined.
        No clipboard, no Ctrl+A. Returns (deleted, typed). Keeps history on focus-skip
        so a retry after focusing the document still deletes correctly."""
        if not refined:
            return 0, 0
        delete_len = InjectionService._delete_count(fallback_len)
        if delete_len <= 0:
            print("[Injection] No history to delete, just typing refined")
            typed = InjectionService.type_text(refined)
            try:
                InjectionService.clear_history()
                InjectionService._record(str(refined or "")[:4000])
            except Exception:
                pass
            return 0, typed
        deleted = InjectionService.delete_chars(delete_len)
        if deleted <= 0:
            return 0, 0
        typed = InjectionService.type_text(refined)
        print(f"[Injection] precise_replace typed refined {typed} chars (deleted {deleted})")
        # Reset history to refined so next refine deletes exactly refined
        try:
            InjectionService.clear_history()
            InjectionService._record(str(refined or "")[:4000])
        except Exception:
            pass
        return int(deleted), int(typed)

    @staticmethod
    def replace_all(refined: str, fallback_len: int = 0):
        """Legacy alias -> precise_replace (no clipboard)."""
        return InjectionService.precise_replace(refined, fallback_len)

    @staticmethod
    async def replace_all_async(refined: str, fallback_len: int = 0):
        loop = asyncio.get_running_loop()
        return await loop.run_in_executor(None, lambda: InjectionService.precise_replace(refined, int(fallback_len or 0)))

    @staticmethod
    async def precise_replace_async(refined: str, fallback_len: int = 0):
        loop = asyncio.get_running_loop()
        return await loop.run_in_executor(None, lambda: InjectionService.precise_replace(refined, int(fallback_len or 0)))
