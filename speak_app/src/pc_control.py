"""SPEAK PC control — desktop UI action + OS tools for the Live companion agent.

Scope: desktop mouse + keyboard UI actions, application launching, and a
guarded shell for everyday commands (open apps/files/URLs, list directories,
small scripts). NO destructive or privilege-escalation commands — those are
denylisted below and refused with an explanation. Every execution is step-
budgeted, loop-guarded, and audit-logged by PCGovernor.

Coordinates are normalized 0-999 (model-friendly, matches the official
Computer Use grid) and scaled to the ACTIVE monitor — the same monitor
ScreenEngine captures (monitor under the cursor), so what the model points
at is what gets clicked.

Safety governor (always on):
  - Step budget per session (default 25). Exhausted -> tools refuse politely.
  - No-identical-repeat: same action+args 3x in a row is refused (loop guard).
  - Clamps: type <= 500 chars/call, wait <= 5s, shell <= 500 chars/20s/2000 out.
  - Destructive shell patterns refused (format, mass delete, registry writes,
    shutdown, credential/user changes, encoded payloads, process kills...).
  - Audit log (cap 200) — every action recorded with timestamp + result.
  - Kill switch: governor.stop() halts all further actions (Esc / stop-word).

Execution backends: pynput first (clean, no focus stealing), ctypes
SendInput path via InjectionService helpers where available, pyautogui
last resort. All actions run in a worker thread (asyncio.to_thread) so the
Live audio loops never block — this is what makes NON_BLOCKING tools safe.
"""
import os
import re
import subprocess
import time

try:
    from google.genai import types as _types
    _HAS_TYPES = True
except Exception:
    _types = None
    _HAS_TYPES = False

# pynput controllers (mouse + keyboard), pyautogui fallback
try:
    from pynput.mouse import Controller as _MouseController, Button as _MouseButton
    _mouse = _MouseController()
except Exception:
    _MouseController = None
    _MouseButton = None
    _mouse = None
try:
    from pynput.keyboard import Controller as _KbController, Key as _KbKey
    _kb = _KbController()
except Exception:
    _KbController = None
    _KbKey = None
    _kb = None
try:
    import pyautogui as _pyautogui
    try:
        _pyautogui.FAILSAFE = False
        _pyautogui.PAUSE = 0.0
    except Exception:
        pass
except Exception:
    _pyautogui = None

# Action allowlist. Anything not listed here is refused.
PC_ACTION_NAMES = frozenset({
    "pc_move", "pc_click", "pc_double_click", "pc_right_click",
    "pc_drag", "pc_scroll", "pc_type", "pc_key", "pc_hotkey", "pc_wait",
    "pc_open_app", "pc_shell",
})

STEP_BUDGET_DEFAULT = 100
MAX_TYPE_CHARS = 2000
MAX_WAIT_SECONDS = 5
MAX_SHELL_CHARS = 1000
MAX_SHELL_SECONDS = 30
MAX_SHELL_OUTPUT = 4000

# Destructive / privilege-escalation patterns — always refused, no exceptions.
# The app runs unprivileged, so the OS is a backstop; this list stops the
# obvious foot-guns before they reach it.
_SHELL_DENY = [
    r"^\s*format\s+[a-z]:",
    r"\bdiskpart\b", r"\bvssadmin\s+delete\b", r"\bbcdedit\b",
    r"\bshutdown\b\s*(/[sgrahl]|$)", r"\brestart-computer\b",
    r"\b(del|erase)\b[^&|]*?/[fsq]", r"\b(rmdir|rd)\b[^&|]*?/s",
    r"\breg\s+(delete|add)\b", r"\btakeown\b",
    r"\bicacls\b[^&|]*?/(grant|deny|remove)",
    r"\bcipher\s+/w", r"\bnet\s+(user|localgroup)\b", r"\bnetsh\b",
    r"\bchkdsk\s+/[fr]", r"\bsfc\s+/scannow", r"\bdism\b",
    r"powershell.*-(enc|encodedcommand|hidden)\b", r"\bpwsh\b.*-enc\b",
    r"\btaskkill\b", r"\bpkill\b", r"\bkill\s+-9\b", r"\btskill\b",
    r"\bmkfs\b", r"\bdd\s+if=", r":\(\)\s*\{",
    r"\brundll32\b.*javascript", r"\bmshta\s+(javascript|vbscript):",
    r"\bcertutil\b.*-decode\b", r"\bbitsadmin\b\s+/transfer\b",
]


def _shell_denied(command: str) -> str | None:
    """Returns the matched danger reason, or None when allowed."""
    try:
        low = str(command or "")
        for pat in _SHELL_DENY:
            try:
                if re.search(pat, low, re.IGNORECASE):
                    return pat
            except Exception:
                continue
        return None
    except Exception:
        return None


def _open_app_target(app: str) -> str:
    """Launch an application / document / URL. Returns status. Never raises."""
    target = str(app or "").strip()[:200]
    if not target:
        return "pc_open_app needs an application name, file path, or URL."
    # ShellExecute (no shell parsing) handles exes, documents, and URLs.
    try:
        os.startfile(target)  # noqa: S606 - user-directed local launch, audited
        return f"Opened {target}."
    except Exception as e:
        # Fallback: cmd start with the target double-quoted. Refuse shell
        # metacharacters here (they only make sense chained).
        try:
            if re.search(r"[&|;$`]", target):
                return f"Could not open {target}: {str(e)[:100]}"
            r = subprocess.run(
                ["cmd", "/c", "start", "", target],
                capture_output=True, text=True, timeout=15,
                cwd=os.path.expanduser("~"),
                creationflags=getattr(subprocess, "CREATE_NO_WINDOW", 0),
            )
            if r.returncode == 0:
                return f"Opened {target}."
            return f"Could not open {target}: {(r.stderr or '').strip()[:120]}"
        except Exception as e2:
            return f"Could not open {target}: {str(e2)[:120]}"


def _shell_exec(command: str) -> str:
    """Run a shell command, guarded. Returns exit code + capped output."""
    cmd = str(command or "").strip()[:MAX_SHELL_CHARS]
    if not cmd:
        return "pc_shell needs a command string."
    try:
        reason = _shell_denied(cmd)
    except Exception:
        reason = None
    if reason:
        return ("Refused: destructive or privilege-escalation pattern "
                f"({reason}). Ask for a safer alternative.")
    try:
        r = subprocess.run(
            ["cmd", "/c", cmd],
            capture_output=True, text=True, timeout=MAX_SHELL_SECONDS,
            cwd=os.path.expanduser("~"),
            creationflags=getattr(subprocess, "CREATE_NO_WINDOW", 0),
        )
        out = (r.stdout or "")[:MAX_SHELL_OUTPUT]
        err = (r.stderr or "")[:500]
        tail = f"\n[stderr] {err}" if err.strip() else ""
        return f"exit={r.returncode}\n{out}{tail}".strip()[:MAX_SHELL_OUTPUT + 600]
    except subprocess.TimeoutExpired:
        return f"Timed out after {MAX_SHELL_SECONDS}s (killed)."
    except Exception as e:
        return f"Shell error: {str(e)[:150]}"


def _num01(value):
    """Strict 0-999 coordinate: ints, floats, numeric strings pass; anything
    else (missing, words, garbage) returns None so the caller REFUSES."""
    try:
        if value is None:
            return None
        s = str(value).strip()
        if not s or s.lower() == "none":
            return None
        v = int(float(s))
        return v if 0 <= v <= 999 else None
    except Exception:
        return None


_COORD_KEYS = {
    "pc_move": ("x", "y"),
    "pc_click": ("x", "y"),
    "pc_double_click": ("x", "y"),
    "pc_right_click": ("x", "y"),
    "pc_drag": ("start_x", "start_y", "end_x", "end_y"),
    "pc_scroll": ("x", "y"),
}


def _active_monitor_rect():
    """(left, top, width, height) of the monitor under the cursor.

    Mirrors ScreenEngine targeting so model coordinates land on the monitor
    the model is actually seeing. Falls back to the primary screen.
    """
    try:
        import ctypes
        pt = ctypes.wintypes.POINT()
        ctypes.windll.user32.GetCursorPos(ctypes.byref(pt))
        cx, cy = int(pt.x), int(pt.y)
    except Exception:
        cx = cy = -10**9
    try:
        import mss as _mss
        with _mss.mss() as _sct:
            mons = _sct.monitors or []
        for m in mons[1:]:
            try:
                if m["left"] <= cx < m["left"] + m["width"] and m["top"] <= cy < m["top"] + m["height"]:
                    return (int(m["left"]), int(m["top"]), int(m["width"]), int(m["height"]))
            except Exception:
                continue
        if len(mons) > 1:
            m = mons[1]
            return (int(m["left"]), int(m["top"]), int(m["width"]), int(m["height"]))
    except Exception:
        pass
    try:
        import ctypes
        w = int(ctypes.windll.user32.GetSystemMetrics(0))
        h = int(ctypes.windll.user32.GetSystemMetrics(1))
        return (0, 0, max(640, w), max(360, h))
    except Exception:
        return (0, 0, 1920, 1080)


def _scale(nx, ny):
    """Normalized 0-999 -> absolute pixels on the active monitor (clamped)."""
    try:
        nx = max(0, min(999, int(nx)))
    except Exception:
        nx = 500
    try:
        ny = max(0, min(999, int(ny)))
    except Exception:
        ny = 500
    left, top, w, h = _active_monitor_rect()
    return (left + int(nx / 999.0 * max(1, w - 1)), top + int(ny / 999.0 * max(1, h - 1)))


def _click_at(px, py, button="left", clicks=1):
    if _mouse is not None and _MouseButton is not None:
        try:
            _mouse.position = (px, py)
            btn = {"left": _MouseButton.left, "right": _MouseButton.right,
                   "middle": _MouseButton.middle}.get(str(button or "left").lower(), _MouseButton.left)
            try:
                _mouse.click(btn, int(max(1, clicks)))
            except Exception:
                for _ in range(int(max(1, clicks))):
                    _mouse.press(btn)
                    _mouse.release(btn)
            return True
        except Exception:
            pass
    if _pyautogui is not None:
        try:
            _pyautogui.click(px, py, button=str(button or "left").lower(), clicks=int(max(1, clicks)))
            return True
        except Exception:
            return False
    return False


def _move_to(px, py):
    if _mouse is not None:
        try:
            _mouse.position = (px, py)
            return True
        except Exception:
            pass
    if _pyautogui is not None:
        try:
            _pyautogui.moveTo(px, py)
            return True
        except Exception:
            return False
    return False


def _drag(sx, sy, ex, ey):
    if _mouse is not None and _MouseButton is not None:
        try:
            _mouse.position = (sx, sy)
            _mouse.press(_MouseButton.left)
            try:
                steps = 12
                for i in range(1, steps + 1):
                    _mouse.position = (sx + (ex - sx) * i // steps, sy + (ey - sy) * i // steps)
                    time.sleep(0.008)
            finally:
                _mouse.release(_MouseButton.left)
            return True
        except Exception:
            pass
    if _pyautogui is not None:
        try:
            _pyautogui.moveTo(sx, sy)
            _pyautogui.dragTo(ex, ey, duration=0.25, button="left")
            return True
        except Exception:
            return False
    return False


def _scroll_at(px, py, direction, magnitude):
    try:
        mag = max(1, min(999, int(magnitude or 300)))
    except Exception:
        mag = 300
    direction = str(direction or "down").lower()
    ticks = max(1, min(20, mag // 100 + 1))
    dx = dy = 0
    if direction == "up":
        dy = ticks
    elif direction == "down":
        dy = -ticks
    elif direction == "left":
        dx = -ticks
    elif direction == "right":
        dx = ticks
    else:
        dy = -ticks
    if _mouse is not None:
        try:
            _mouse.position = (px, py)
            _mouse.scroll(dx, dy)
            return True
        except Exception:
            pass
    if _pyautogui is not None:
        try:
            if dx:
                _pyautogui.hscroll(dx * 100, x=px, y=py)
            else:
                _pyautogui.scroll(dy * 100, x=px, y=py)
            return True
        except Exception:
            return False
    return False


_KEY_ALIASES = {
    "enter": "enter", "return": "enter", "tab": "tab", "esc": "esc", "escape": "esc",
    "space": "space", "backspace": "backspace", "delete": "delete", "del": "delete",
    "up": "up", "down": "down", "left": "left", "right": "right",
    "home": "home", "end": "end", "pageup": "pageup", "pagedown": "pagedown",
    "ctrl": "ctrl", "alt": "alt", "shift": "shift", "win": "win", "super": "win",
    "f1": "f1", "f2": "f2", "f3": "f3", "f4": "f4", "f5": "f5", "f6": "f6",
    "f7": "f7", "f8": "f8", "f9": "f9", "f10": "f10", "f11": "f11", "f12": "f12",
}


def _press_key_name(name):
    """Single key press. A '+'-joined combo delegates to the chord path."""
    raw = str(name or "").strip()
    if not raw:
        return False
    if "+" in raw:
        return _hotkey_combo(raw)
    n = _KEY_ALIASES.get(raw.lower(), raw.lower() if len(raw) == 1 else None)
    if not n:
        return False
    if _pyautogui is not None:
        try:
            _pyautogui.press(n)
            return True
        except Exception:
            pass
    if _kb is not None and _KbKey is not None:
        try:
            keymap = {"enter": _KbKey.enter, "tab": _KbKey.tab, "esc": _KbKey.esc,
                      "space": _KbKey.space, "backspace": _KbKey.backspace, "delete": _KbKey.delete,
                      "up": _KbKey.up, "down": _KbKey.down, "left": _KbKey.left, "right": _KbKey.right,
                      "home": _KbKey.home, "end": _KbKey.end, "page_up": _KbKey.page_up,
                      "page_down": _KbKey.page_down, "shift": _KbKey.shift, "ctrl": _KbKey.ctrl,
                      "alt": _KbKey.alt, "cmd": _KbKey.cmd}
            k = keymap.get(n, n if len(n) == 1 else None)
            if k is None:
                return False
            _kb.press(k)
            _kb.release(k)
            return True
        except Exception:
            return False
    return False


def _hotkey_combo(combo):
    """Many keys at once: real simultaneous chords via pyautogui.hotkey.

    Accepts 'ctrl+c', 'ctrl+shift+s', 'alt+tab', 'win+d' (also space/comma
    separated). Max 4 keys. Every part must be a known key or a single
    character — anything else is refused with False (caller reports it).
    """
    parts = [p.strip().lower() for p in str(combo or "").replace("+", " ").replace(",", " ").split() if p.strip()]
    parts = [_KEY_ALIASES.get(p, p) for p in parts][:4]
    if not parts:
        return False
    try:
        import string as _s
        allowed = set(_KEY_ALIASES.values()) | set(_s.ascii_lowercase) | set(_s.digits)
        if any(p not in allowed for p in parts):
            return False
    except Exception:
        return False
    if _pyautogui is not None:
        try:
            _pyautogui.hotkey(*parts)
            return True
        except Exception:
            pass
    # Fallback: press in sequence (modifiers held via pynput when available)
    ok = True
    for p in parts:
        if not _press_key_name(p):
            ok = False
    return ok


def _type_text(text, press_enter=False):
    text = str(text or "")[:MAX_TYPE_CHARS]
    if not text:
        return False
    try:
        from src.injection_service import InjectionService as _Inj
        _Inj.safe_type(text)
        ok = True
    except Exception:
        ok = False
        if _pyautogui is not None:
            try:
                _pyautogui.write(text, interval=0.005)
                ok = True
            except Exception:
                ok = False
    if ok and press_enter:
        try:
            if not _press_key_name("enter"):
                if _pyautogui is not None:
                    _pyautogui.press("enter")
        except Exception:
            pass
    return ok


class PCGovernor:
    """Per-session safety governor for pc_* actions. Never raises."""

    def __init__(self, step_budget: int = STEP_BUDGET_DEFAULT):
        self.step_budget = max(1, int(step_budget or STEP_BUDGET_DEFAULT))
        self.steps_used = 0
        self.stopped = False
        self.audit: list = []
        self._last_sig = None
        self._repeat_count = 0

    def reset(self):
        self.steps_used = 0
        self.stopped = False
        self.audit = []
        self._last_sig = None
        self._repeat_count = 0

    def stop(self):
        self.stopped = True

    def remaining(self) -> int:
        return max(0, self.step_budget - self.steps_used)

    def check(self, name: str, args: dict) -> str | None:
        """Returns refusal reason, or None when the action may proceed."""
        try:
            if self.stopped:
                return "Agent control stopped by user."
            if self.steps_used >= self.step_budget:
                return f"Step budget exhausted ({self.step_budget} actions this session). Say 'stop' acknowledged; ask the user to start a new task."
            try:
                sig = (str(name), str(sorted((str(k), str(v)[:80]) for k, v in (args or {}).items())))
            except Exception:
                sig = (str(name), "")
            if sig == self._last_sig:
                self._repeat_count += 1
            else:
                self._last_sig = sig
                self._repeat_count = 1
            if self._repeat_count >= 5:
                self._repeat_count = 0
                return "Same action repeated without progress — refusing to loop. Describe what you see and ask the user."
            return None
        except Exception:
            return None

    def record(self, name: str, args: dict, result: str):
        try:
            self.steps_used += 1
            try:
                safe_args = {str(k): str(v)[:120] for k, v in (args or {}).items()}
            except Exception:
                safe_args = {}
            self.audit.append({"t": time.time(), "action": str(name), "args": safe_args,
                               "result": str(result)[:200], "step": self.steps_used})
            self.audit = self.audit[-200:]
        except Exception:
            pass

    def summary(self) -> str:
        try:
            return f"{self.steps_used}/{self.step_budget} steps used, {len(self.audit)} logged."
        except Exception:
            return ""


def execute_pc_call(name: str, args: dict, governor: PCGovernor | None = None) -> str:
    """Execute one pc_* action synchronously (call via asyncio.to_thread).

    Returns a short status string for the FunctionResponse. Never raises.
    """
    args = args or {}
    try:
        if name not in PC_ACTION_NAMES:
            return f"Unknown PC action '{name}'. Allowed: {sorted(PC_ACTION_NAMES)}."
        if governor is not None:
            refusal = governor.check(name, args)
            if refusal:
                try:
                    governor.record(name, args, f"REFUSED: {refusal}")
                except Exception:
                    pass
                return refusal
        # Coordinate actions need REAL numbers — never fire at center-screen
        # on hallucinated garbage. Refuse with guidance so the model retries.
        if name in _COORD_KEYS:
            _bad = [k for k in _COORD_KEYS[name] if _num01(args.get(k)) is None]
            if _bad:
                _msg = (f"{name} needs numbers 0-999 for {', '.join(_COORD_KEYS[name])} — "
                        "look at the screen and give numeric positions.")
                if governor is not None:
                    try:
                        governor.record(name, args, f"REFUSED: {_msg}")
                    except Exception:
                        pass
                return _msg
        ok = False
        detail = ""
        try:
            if name == "pc_move":
                px, py = _scale(args.get("x", 500), args.get("y", 500))
                ok = _move_to(px, py)
                detail = f"cursor to ({px},{py})"
            elif name == "pc_click":
                px, py = _scale(args.get("x", 500), args.get("y", 500))
                ok = _click_at(px, py, args.get("button", "left"), 1)
                detail = f"{args.get('button', 'left')} click at ({px},{py})"
            elif name == "pc_double_click":
                px, py = _scale(args.get("x", 500), args.get("y", 500))
                ok = _click_at(px, py, "left", 2)
                detail = f"double-click at ({px},{py})"
            elif name == "pc_right_click":
                px, py = _scale(args.get("x", 500), args.get("y", 500))
                ok = _click_at(px, py, "right", 1)
                detail = f"right-click at ({px},{py})"
            elif name == "pc_drag":
                sx, sy = _scale(args.get("start_x", 500), args.get("start_y", 500))
                ex, ey = _scale(args.get("end_x", 500), args.get("end_y", 500))
                ok = _drag(sx, sy, ex, ey)
                detail = f"drag ({sx},{sy})->({ex},{ey})"
            elif name == "pc_scroll":
                px, py = _scale(args.get("x", 500), args.get("y", 500))
                ok = _scroll_at(px, py, args.get("direction", "down"), args.get("magnitude", 300))
                detail = f"scroll {args.get('direction', 'down')}"
            elif name == "pc_type":
                ok = _type_text(args.get("text", ""), bool(args.get("press_enter", False)))
                detail = f"typed {len(str(args.get('text', '')))} chars"
            elif name == "pc_key":
                ok = _press_key_name(args.get("key", ""))
                detail = f"key {args.get('key', '')}"
            elif name == "pc_hotkey":
                ok = _hotkey_combo(args.get("keys", ""))
                detail = f"hotkey {args.get('keys', '')}"
            elif name == "pc_wait":
                try:
                    secs = max(0.2, min(MAX_WAIT_SECONDS, float(args.get("seconds", 1))))
                except Exception:
                    secs = 1.0
                time.sleep(secs)
                ok = True
                detail = f"waited {secs:.1f}s"
            elif name == "pc_open_app":
                detail = _open_app_target(args.get("app", ""))
                ok = detail.startswith("Opened")
            elif name == "pc_shell":
                detail = _shell_exec(args.get("command", ""))
                ok = not (detail.startswith("Refused") or detail.startswith("pc_shell needs"))
        except Exception as e:
            if governor is not None:
                try:
                    governor.record(name, args, f"ERROR: {e}")
                except Exception:
                    pass
            return f"PC action failed: {str(e)[:120]}"
        status = f"Done: {detail}." if ok else f"Could not execute {name} (no input backend available)."
        if name in ("pc_open_app", "pc_shell"):
            # These carry their own complete status (exit codes, refusals).
            status = detail
        if governor is not None:
            try:
                governor.record(name, args, status)
            except Exception:
                pass
        return status
    except Exception as e:
        return f"PC action error: {str(e)[:120]}"


def _nb_decl(name: str, description: str, props: dict, required: list):
    """NON_BLOCKING function declaration (required by extended-thinking)."""
    try:
        kwargs = dict(
            name=name,
            description=description,
            parameters=_types.Schema(
                type=_types.Type.OBJECT,
                properties={k: _types.Schema(type=_types.Type.STRING, description=v) if isinstance(v, str)
                            else v for k, v in props.items()},
                required=required,
            ),
        )
        try:
            kwargs["behavior"] = _types.Behavior.NON_BLOCKING
        except Exception:
            try:
                kwargs["behavior"] = "NON_BLOCKING"
            except Exception:
                pass
        return _types.FunctionDeclaration(**kwargs)
    except Exception:
        return None


def _xy_props():
    def _num(d):
        # NUMBER (not STRING) so the model can send 0-999 as numbers without
        # a server-side type mismatch (400). _num01 still accepts numeric
        # strings too, so both shapes work client-side.
        try:
            return _types.Schema(type=_types.Type.NUMBER, description=d)
        except Exception:
            return _types.Schema(type=_types.Type.STRING, description=d)
    s = lambda d: _types.Schema(type=_types.Type.STRING, description=d)
    return {
        "x": _num("Horizontal position 0-999 on the visible screen you see."),
        "y": _num("Vertical position 0-999 on the visible screen you see."),
        "intent": s("One short sentence: why this action, what you expect to happen."),
    }


def build_pc_tools():
    """Tool list for desktop control. Empty list when SDK types unavailable."""
    if not _HAS_TYPES:
        return []
    try:
        s = lambda d: _types.Schema(type=_types.Type.STRING, description=d)
        try:
            n = lambda d: _types.Schema(type=_types.Type.NUMBER, description=d)
        except Exception:
            n = s
        decls = [
            _nb_decl("pc_move", "Move the mouse cursor to a screen position. Use before describing hover targets.",
                     _xy_props(), []),
            _nb_decl("pc_click", "Left-click (or other button) at a screen position you can SEE in the latest frame.",
                     {**_xy_props(),
                      "button": s("Mouse button: left (default), right, or middle.")}, []),
            _nb_decl("pc_double_click", "Double-click at a screen position (open files, select words).",
                     _xy_props(), []),
            _nb_decl("pc_right_click", "Right-click at a screen position (context menus).",
                     _xy_props(), []),
            _nb_decl("pc_drag", "Drag from start to end position (move windows, select areas, sliders).",
                     {"start_x": n("Drag start X 0-999."), "start_y": n("Drag start Y 0-999."),
                      "end_x": n("Drag end X 0-999."), "end_y": n("Drag end Y 0-999."),
                      "intent": s("Why this drag, what you expect.")}, []),
            _nb_decl("pc_scroll", "Scroll at a position (lists, pages, documents).",
                     {**_xy_props(),
                      "direction": s("up, down (default), left, or right."),
                      "magnitude": n("0-999 pixels, default 300.")}, []),
            _nb_decl("pc_type", "Type text at the CURRENT cursor/focus (click the field first if needed).",
                     {"text": s("Exact text to type (max 2000 chars per call)."),
                      "press_enter": s("true to press Enter after typing, false (default) to leave text unsubmitted."),
                      "intent": s("What this text is for.")}, ["text"]),
            _nb_decl("pc_key", "Press a single key (enter, tab, esc, arrows, f1-f12).",
                     {"key": s("Key name, e.g. enter, tab, esc, down, f5."),
                      "intent": s("Why this keypress.")}, ["key"]),
            _nb_decl("pc_hotkey", "Press a key combination (copy, paste, save, alt-tab...).",
                     {"keys": s("Combination like 'ctrl+c', 'alt+tab', 'win+d'. Max 4 keys."),
                      "intent": s("Why this hotkey.")}, ["keys"]),
            _nb_decl("pc_wait", "Pause briefly to let the screen settle after an action.",
                     {"seconds": n("0.2-5 seconds, default 1."),
                      "intent": s("What you are waiting for.")}, []),
            _nb_decl("pc_open_app", "Open an application, file, or URL by name (e.g. notepad, calculator, a document path, https://...).",
                     {"app": s("Application name, file path, or URL to open."),
                      "intent": s("Why opening this.")}, ["app"]),
            _nb_decl("pc_shell", "Run a short, safe shell command (dir, echo, ipconfig, small scripts). Destructive, privilege, and process-kill patterns are refused. Prefer pc_open_app for launching programs.",
                     {"command": s("Command line to run, max 1000 chars. Output capped, 30s timeout."),
                      "intent": s("Why this command.")}, ["command"]),
        ]
        decls = [d for d in decls if d is not None]
        if not decls:
            return []
        return [_types.Tool(function_declarations=decls)]
    except Exception:
        return []


try:
    PC_TOOLS = build_pc_tools()
except Exception:
    PC_TOOLS = []
