import asyncio
import sys
import re
from PySide6.QtCore import QObject, Signal
from google import genai
from google.genai import types
from src.config import config_vault
try:
    from src.injection_service import InjectionService
    HAS_INJECTION = True
except Exception:
    HAS_INJECTION = False
    InjectionService = None
# Fallback pyautogui only if injection not available
try:
    import pyautogui
    pyautogui.FAILSAFE = False
    pyautogui.PAUSE = 0.0
except Exception:
    pyautogui = None

try:
    from src.transcript_buffer import TranscriptBuffer
except Exception:
    TranscriptBuffer = None

# Fallback prompts (Settings-editable copies live in config; these are last-resort).
# Self-correction aware: raw speech may contain superseded info ("9pm actually 5pm").
REFINE_PROMPTS = {
    "refine": ("You are an expert editor fixing a raw speech transcript. The text may contain self-corrections "
        "marked by words like actually, I mean, instead, sorry, no \u2014. Resolve them: keep ONLY the speaker's "
        "final intent, delete superseded times, names, and numbers. Remove filler (um, uh, like) and fix "
        "grammar/punctuation. Normalize times like 500pm to 5:00 PM. Output ONLY the final corrected text, no preamble, no quotes:\n\n"),
    "polish": ("You are an expert copyeditor. Polish the following text to be publication-ready. Improve word choice, "
        "rhythm, and clarity. If the text contains a self-correction (actually/I mean/instead), keep only the final intent. "
        "Output ONLY the polished text, no preamble, no quotes:\n\n"),
    "elaborate": ("You are an expert writer. Expand the following text from start to finish. Add helpful detail, examples, "
        "and structure while staying faithful to the speaker's final intent. If the text contains a self-correction, "
        "expand only the corrected version. Output ONLY the expanded text, no preamble:\n\n"),
    # Legacy alias: old 'expand' id maps to elaborate prompt.
    "expand": ("You are an expert writer. Expand the following text from start to finish. Add helpful detail, examples, "
        "and structure while staying faithful to the speaker's final intent. If the text contains a self-correction, "
        "expand only the corrected version. Output ONLY the expanded text, no preamble:\n\n"),
}
BUILTIN_REFINE_IDS = ("refine", "polish", "elaborate")

# ---- typeTextAtCursor tool schema (locked — do not alter shape) ----
# Drafts and types structured message content into the user's active cursor.
# All typing actions bind directly to this schema. Verification flags are
# driven by Settings > Message Verification (see ConfigManager).
TYPE_TEXT_TOOL = types.Tool(
    function_declarations=[
        types.FunctionDeclaration(
            name="typeTextAtCursor",
            description=(
                "Drafts and types structured message content or text into the user's "
                "active cursor/focused input field. Automatically formats message "
                "based on intent and settings."
            ),
            parameters=types.Schema(
                type=types.Type.OBJECT,
                properties={
                    "content": types.Schema(
                        type=types.Type.STRING,
                        description="The drafted text to insert at the cursor position.",
                    ),
                    "requireVerification": types.Schema(
                        type=types.Type.BOOLEAN,
                        description="Set to true if user verification/confirmation is required before sending/pressing Enter. Set to false for instant submission.",
                    ),
                    "autoSubmit": types.Schema(
                        type=types.Type.BOOLEAN,
                        description="Set to true if the model should automatically press Enter after typing when verification is satisfied or skipped.",
                    ),
                    "tone": types.Schema(
                        type=types.Type.STRING,
                        description="Tone applied to the message (e.g., formal, friendly, casual, concise).",
                    ),
                },
                required=["content", "requireVerification", "autoSubmit"],
            ),
        )
    ]
)

# Verbal-confirmation + cursor-aware tone suffix. Appended to (never replacing)
# the user's stored system instruction so existing behavior is retained.
_VERBAL_CONFIRM_SUFFIX = (
    "\n\nTool behavior: when you call typeTextAtCursor, always provide a brief verbal "
    "confirmation of what was drafted before or while typing (never type silently). "
    "Adapt tone to the cursor context when a tone hint is available "
    "(formal for documents/mail, friendly for chat, concise for code/commands)."
)

_LOCKED_THINKING_LEVEL = "HIGH"
_LOCKED_TRANSCRIPTION_MODE = "SMART"


def _locked_thinking_config():
    """thinking_level HIGH — locked for high-accuracy context awareness.

    Spec requires thinking_level="HIGH". Installed SDK (1.21.0) only exposes
    thinking_budget/include_thoughts, so we attempt HIGH first (forward-compat
    with newer Gemini Live API) and fall back to a high budget which is the
    equivalent HIGH-effort setting on this SDK. Returns None only if neither
    shape is supported — callers must guard LiveConnectConfig field existence.
    """
    try:
        return types.ThinkingConfig(thinking_level=_LOCKED_THINKING_LEVEL)
    except Exception:
        pass
    try:
        # HIGH ≈ maximum reasoning effort on budget-based SDKs
        return types.ThinkingConfig(thinking_budget=2048)
    except Exception:
        return None


def _supports_live_field(name: str) -> bool:
    try:
        fields = getattr(types.LiveConnectConfig, "model_fields", {}) or {}
        return name in fields
    except Exception:
        return False


def _locked_transcription_config(custom_vocabulary=None):
    """Strict STT-only transcription config — SMART, auto-detect, custom vocab.

    Version-tolerant: SDKs >= 2.19 accept language_codes/mode/custom_vocabulary;
    older SDKs (e.g. 1.21.0) only accept an empty config (server then defaults
    to VERBATIM). Probes richest-first, degrades gracefully. Never raises —
    returns None only if the type itself is unavailable.
    """
    try:
        vocab = [str(w).strip() for w in (custom_vocabulary or []) if str(w).strip()][:100]
    except Exception:
        vocab = []
    attempts: list[dict] = []
    if vocab:
        attempts.append({"language_codes": [], "mode": _LOCKED_TRANSCRIPTION_MODE, "custom_vocabulary": vocab})
    attempts.append({"language_codes": [], "mode": _LOCKED_TRANSCRIPTION_MODE})
    attempts.append({"language_codes": []})
    attempts.append({})
    for kwargs in attempts:
        try:
            return types.AudioTranscriptionConfig(**kwargs)
        except Exception:
            continue
    return None


def _dictation_sdk_status() -> tuple[bool, bool, bool]:
    """(smart_ok, vocab_ok, interim_ok) capability probe for Settings UI."""
    smart_ok = vocab_ok = interim_ok = False
    try:
        types.AudioTranscriptionConfig(language_codes=[], mode=_LOCKED_TRANSCRIPTION_MODE)
        smart_ok = True
    except Exception:
        pass
    try:
        types.AudioTranscriptionConfig(custom_vocabulary=["probe"])
        vocab_ok = True
    except Exception:
        pass
    try:
        srv_fields = getattr(types.LiveServerContent, "model_fields", {}) or {}
        interim_ok = "interim_input_transcription" in srv_fields
    except Exception:
        pass
    return smart_ok, vocab_ok, interim_ok


def _build_dictation_config():
    """Strict STT-only LiveConnectConfig for gemini-3.5-transcribe-live.

    Contract (official live-transcribe guide): response_modalities TEXT +
    input_audio_transcription ONLY. No tools (function calling unsupported on
    this model), no thinking_config (thinking unsupported), no
    system_instruction / speech_config / temperature — the server rejects the
    connect with 400 INVALID_ARGUMENT when any of those are present, which is
    why dictation kept failing while companion worked.
    """
    try:
        vocab = config_vault.get_custom_words()[:100]
    except Exception:
        vocab = []
    trans = _locked_transcription_config(vocab)
    if trans is None:
        try:
            trans = types.AudioTranscriptionConfig()
        except Exception:
            trans = None
    kwargs: dict = {"response_modalities": [types.Modality.TEXT]}
    if trans is not None:
        kwargs["input_audio_transcription"] = trans
    return types.LiveConnectConfig(**kwargs)


def _classify_live_error(error: Exception) -> str:
    """Short actionable bucket for capsule status (never includes key text)."""
    try:
        s = f"{type(error).__name__}: {error}"
    except Exception:
        return "connect-error"
    low = s.lower()
    if "429" in s or "resource_exhausted" in low or "quota" in low:
        return "quota/rate-limit"
    if "404" in s or "not_found" in low:
        return "model-not-found"
    if "400" in s or "invalid_argument" in low:
        return "bad-request (config rejected)"
    if "api_key_invalid" in low or "api key" in low or "401" in s or "403" in s:
        return "auth/key"
    if "unavailable" in low or "500" in s or "503" in s:
        return "server-unavailable"
    return "connect-error"

class GeminiLiveManager(QObject):
    status_changed = Signal(str, str)
    token_usage_updated = Signal(int, int)
    error_occurred = Signal(str)
    transcript_updated = Signal(str)
    interim_updated = Signal(str)
    refine_started = Signal(str)
    refine_completed = Signal(str, str)
    refine_failed = Signal(str)

    MAX_CONTEXT_TOKENS = 128000

    def __init__(self, audio_engine, screen_engine, transcript_buffer=None):
        super().__init__()
        self.audio = audio_engine
        self.screen = screen_engine
        self._screen_enabled = bool(config_vault.config.get("enable_screen_share", True))
        if transcript_buffer is not None:
            self.transcript = transcript_buffer
        elif TranscriptBuffer is not None:
            try:
                self.transcript = TranscriptBuffer(autosave=config_vault.config.get("transcript_autosave", True))
            except Exception:
                self.transcript = None
        else:
            self.transcript = None
        self.current_transcript_buffer = ""
        if self.transcript is not None:
            try:
                self.transcript.text_changed.connect(self._on_buffer_update)
                self.transcript.interim_changed.connect(self.interim_updated.emit)
                self.current_transcript_buffer = self.transcript.full_text
            except Exception:
                pass
        self.client = None
        self.session = None
        self._is_active = False
        self._current_mode = "idle"
        self._session_tokens = 0
        self._bg_tasks = set()
        self._refine_in_progress = False
        # Live-screen task handle — restartable mid-session (voice-only <-> +Screen)
        self._screen_task = None
        # Companion lifecycle guards (double-fire, toggle races, failover storms)
        self._screen_gen = 0
        self._last_mode_start_ts = 0.0
        self._loop = None
        self._failover_count = 0
        self._failover_window_ts = 0.0
        self._speak_last_emit = 0.0
        self._audio_bytes_out = 0
        self._mic_silent_warns = 0
        self._dictation_clean_close = None

    def _on_buffer_update(self, text: str):
        self.current_transcript_buffer = text
        try:
            self.transcript_updated.emit(text)
        except Exception:
            pass

    def _key_label(self, key: str) -> str:
        """Masked label for logging without exposing key."""
        if not key:
            return "none"
        if config_vault.is_using_embedded():
            return "embedded(hidden)"
        return f"{key[:6]}***{key[-4:]}" if len(key) > 10 else "***"

    def _init_sdk_client(self) -> bool:
        key = config_vault.get_current_key()
        if not key:
            self.error_occurred.emit("No API Key found. Please add your key in Settings > API Vault or use free tier.")
            self.status_changed.emit("No API Key", "error")
            return False
        # Never log raw key
        try:
            self.client = genai.Client(api_key=key, http_options={"api_version": "v1beta"})
            print(f"[Gemini] Client init key={self._key_label(key)}")
            return True
        except Exception as e:
            # Mask key in error
            msg = str(e).replace(key[:10], "***") if len(key) > 10 else str(e)
            self.error_occurred.emit(f"SDK Init Error: {msg[:120]}")
            self.status_changed.emit("Init Failed", "error")
            return False

    def reset_token_counter(self):
        self._session_tokens = 0
        self.token_usage_updated.emit(0, self.MAX_CONTEXT_TOKENS)

    def _preempt_for_mode(self, mode: str) -> str:
        """Decide what a start request means while a session may be active.
        Returns 'fresh' (start now), 'ignore' (accidental double-fire), or
        'toggle-off' (caller already stopped; do not restart).
        """
        try:
            import time as _time
            now = _time.monotonic()
        except Exception:
            now = 0.0
        try:
            if self._is_active:
                if self._current_mode == mode and (now - float(getattr(self, "_last_mode_start_ts", 0.0) or 0.0)) < 1.5:
                    return "ignore"
                return "toggle-off" if self._current_mode == mode else "switch"
        except Exception:
            pass
        return "fresh"

    def _emit_companion_status(self, model_id=None):
        """Single source of truth for companion status (never loses screen state)."""
        try:
            screen = " + Screen" if getattr(self, "_screen_enabled", True) else " \u2014 Voice only"
            if model_id:
                short = str(model_id).replace("gemini-", "")[:28]
                self.status_changed.emit(f"Companion ({short}){screen}", "active")
            else:
                self.status_changed.emit(f"Companion Live{screen}", "active")
        except Exception:
            pass

    # ---- Message Verification + typeTextAtCursor binding (redesign, core-safe) ----
    def get_verification_flags(self) -> tuple[bool, bool]:
        """Current (requireVerification, autoSubmit) from Settings toggle."""
        try:
            return config_vault.get_tool_verification_flags()
        except Exception:
            return True, False

    def build_locked_system_instruction(self, base: str = "") -> str:
        """Base instruction + retained verbal-confirmation / cursor-tone suffix."""
        try:
            b = (base or "").strip() or config_vault.build_system_instruction()
        except Exception:
            b = base or ""
        if _VERBAL_CONFIRM_SUFFIX.strip() not in b:
            b = (b + _VERBAL_CONFIRM_SUFFIX) if b else _VERBAL_CONFIRM_SUFFIX.strip()
        return b

    def _apply_tone(self, content: str, tone: str = "") -> str:
        """Cursor-aware tone adaptation (lightweight, preserves content)."""
        try:
            t = str(tone or "").strip().lower()
            c = str(content or "")
            if not t or not c:
                return c
            # Concise trims whitespace runs; formal ensures terminal punctuation.
            if t == "concise":
                import re as _re
                c = _re.sub(r"\s+", " ", c).strip()
            elif t in ("formal", "friendly", "casual"):
                c = c.strip()
                if c and c[-1] not in ".!?":
                    c = c + "."
            return c
        except Exception:
            return str(content or "")

    async def handle_type_text_tool_call(self, tool_call) -> None:
        """Bind ALL typing actions to typeTextAtCursor schema.

        Honors Settings > Message Verification:
          Verification Active: requireVerification=True, autoSubmit=False
          Auto-Send: requireVerification=False, autoSubmit=True
        Model-supplied flags win when present; Settings defaults fill gaps.
        Core AudioLoop worker tasks are untouched — this only routes typing.
        """
        try:
            calls = getattr(tool_call, "function_calls", None) or []
        except Exception:
            return
        for call in calls:
            try:
                if getattr(call, "name", "") != "typeTextAtCursor":
                    continue
                args = getattr(call, "args", {}) or {}
                if isinstance(args, str):
                    try:
                        import json as _j
                        args = _j.loads(args)
                    except Exception:
                        args = {}
                content = str(args.get("content", "") or "")
                tone = str(args.get("tone", "") or "")
                def_req, def_auto = self.get_verification_flags()
                require_verif = args.get("requireVerification", def_req)
                auto_submit = args.get("autoSubmit", def_auto)
                try:
                    require_verif = bool(require_verif)
                except Exception:
                    require_verif = def_req
                try:
                    auto_submit = bool(auto_submit)
                except Exception:
                    auto_submit = def_auto
                content = self._apply_tone(content, tone)
                print(f"[Tool Execution] typeTextAtCursor len={len(content)} tone={tone or '-'} verify={require_verif} auto={auto_submit}")
                # Execute automated typing at current cursor position
                try:
                    if HAS_INJECTION and InjectionService:
                        InjectionService.safe_type(content)
                    elif pyautogui:
                        pyautogui.write(content, interval=0.01)
                except Exception as e:
                    print(f"[Tool] typing note: {e}")
                if auto_submit and not require_verif:
                    try:
                        if HAS_INJECTION and InjectionService:
                            # InjectionService never presses Enter by design; use fallback
                            if pyautogui:
                                pyautogui.press("enter")
                        elif pyautogui:
                            pyautogui.press("enter")
                    except Exception:
                        pass
                    status = "Typed and sent automatically."
                elif require_verif:
                    status = "Typed text at cursor. Awaiting user verification before hitting enter."
                else:
                    status = "Typed text at cursor."
                # Verbal confirmation is emitted via status so UI/tray can speak it
                try:
                    self.status_changed.emit(f"Drafted ({tone or 'neutral'}): {content[:60]}", "active")
                except Exception:
                    pass
                if self.session is not None:
                    try:
                        await self.session.send(
                            input=types.LiveClientToolResponse(
                                function_responses=[
                                    types.FunctionResponse(
                                        name="typeTextAtCursor",
                                        id=getattr(call, "id", "id"),
                                        response={"status": status},
                                    )
                                ]
                            )
                        )
                    except Exception:
                        # SDK variant: send_tool_response
                        try:
                            await self.session.send_tool_response(
                                function_responses=types.FunctionResponse(
                                    id=getattr(call, "id", "id"),
                                    name="typeTextAtCursor",
                                    response={"status": status},
                                )
                            )
                        except Exception as e:
                            print(f"[Tool] response note: {e}")
            except Exception as e:
                print(f"[Tool] handle note: {e}")
                continue

    async def start_dictation_mode(self):
        decision = self._preempt_for_mode("dictation")
        if decision == "ignore":
            return
        if decision in ("toggle-off", "switch"):
            await self.stop_session()
            if decision == "toggle-off":
                return
        self._current_mode = "dictation"
        self._is_active = True
        try:
            import time as _time
            self._last_mode_start_ts = _time.monotonic()
        except Exception:
            pass
        try:
            self._loop = asyncio.get_running_loop()
        except Exception:
            pass
        # New convo -> reset measured history so refine deletes only this session
        try:
            self._sync_injection_clear_on_new_session()
        except Exception:
            pass
        self.status_changed.emit("Dictating...", "active")
        try:
            dev = config_vault.config.get("audio_device_index", None)
            mic_ok = self.audio.start_recording(device_index=dev)
        except Exception as e:
            self.error_occurred.emit(f"Mic error: {e}")
            self._is_active = False
            self.status_changed.emit("Mic Error", "error")
            return
        if mic_ok is False:
            self.error_occurred.emit("Mic error: recording failed to start. Check Settings > Preferences > Microphone.")
            self._is_active = False
            self._current_mode = "idle"
            self.status_changed.emit("Mic Error", "error")
            return
        loop = asyncio.get_running_loop()
        task = loop.create_task(self._run_dictation_pipeline())
        self._bg_tasks.add(task)
        task.add_done_callback(self._bg_tasks.discard)

    def set_screen_enabled(self, enabled: bool):
        """Toggle live screen share for companion — idle or live.
        Production: restartable mid-session. Enabling mid-session spawns a new
        send-loop if the session is live; disabling cancels it and stops MSS.
        """
        self._screen_enabled = bool(enabled)
        config_vault.config["enable_screen_share"] = self._screen_enabled
        try:
            config_vault.save_config()
        except Exception:
            pass
        if self._is_active and self._current_mode == "companion":
            if self._screen_enabled:
                try:
                    self.screen.start()
                except Exception:
                    pass
                # Spawn send-loop if live and not already running (generation-guarded)
                self._screen_gen += 1
                my_gen = self._screen_gen
                try:
                    running = self._screen_task is not None and not self._screen_task.done()
                except Exception:
                    running = False
                if not running and self.session is not None and self._is_active:
                    try:
                        loop = asyncio.get_running_loop()
                    except RuntimeError:
                        loop = getattr(self, "_loop", None)
                    spawned = False
                    if loop is not None:
                        try:
                            def _spawn():
                                if my_gen != self._screen_gen or not self._is_active:
                                    return
                                try:
                                    already = self._screen_task is not None and not self._screen_task.done()
                                except Exception:
                                    already = False
                                if already or self.session is None:
                                    return
                                t = loop.create_task(self._send_screen_loop())
                                self._screen_task = t
                                self._bg_tasks.add(t)
                                t.add_done_callback(self._bg_tasks.discard)
                                print("[GeminiLive] Screen loop (re)started mid-session")
                            try:
                                running_loop = asyncio.get_running_loop()
                            except RuntimeError:
                                running_loop = None
                            if running_loop is loop:
                                _spawn()
                            else:
                                try:
                                    loop.call_soon_threadsafe(_spawn)
                                except Exception:
                                    pass
                            spawned = True
                        except Exception as e:
                            print(f"[GeminiLive] Screen restart note: {e}")
                    if not spawned:
                        self.error_occurred.emit("Screen restart needs the event loop — toggle again while companion is live.")
                self._emit_companion_status()
            else:
                # Cancel loop first (bump generation so late spawns abort), then stop MSS.
                # The session gather only waits on audio+receive, so this never kills audio.
                self._screen_gen += 1
                try:
                    if self._screen_task is not None and not self._screen_task.done():
                        self._screen_task.cancel()
                except Exception:
                    pass
                self._screen_task = None
                try:
                    self.screen.stop()
                except Exception:
                    pass
                self._emit_companion_status()
        print(f"[GeminiLive] Screen share {'enabled' if self._screen_enabled else 'disabled'}")

    async def start_companion_mode(self):
        decision = self._preempt_for_mode("companion")
        if decision == "ignore":
            return
        if decision in ("toggle-off", "switch"):
            await self.stop_session()
            if decision == "toggle-off":
                return
        self._current_mode = "companion"
        self._is_active = True
        try:
            import time as _time
            self._last_mode_start_ts = _time.monotonic()
        except Exception:
            pass
        try:
            self._loop = asyncio.get_running_loop()
        except Exception:
            pass
        # Sync with config at start
        self._screen_enabled = bool(config_vault.config.get("enable_screen_share", True))
        self._emit_companion_status()
        try:
            dev = config_vault.config.get("audio_device_index", None)
            mic_ok = self.audio.start_recording(device_index=dev)
        except Exception as e:
            self.error_occurred.emit(f"Mic error: {e}")
            self._is_active = False
            self.status_changed.emit("Mic Error", "error")
            return
        if mic_ok is False:
            self.error_occurred.emit("Mic error: recording failed to start. Check Settings > Preferences > Microphone.")
            self._is_active = False
            self._current_mode = "idle"
            self.status_changed.emit("Mic Error", "error")
            return
        try:
            play_ok = self.audio.start_playback_stream()
        except Exception as e:
            play_ok = False
            print(f"[GeminiLive] Playback start note: {e}")
        if play_ok is False:
            self.error_occurred.emit("Speaker error: output failed to start. You can still talk, but replies may be silent. Check speaker.")
            self.status_changed.emit("Speaker issue — listening", "warn")
        if self._screen_enabled:
            try:
                self.screen.start()
            except Exception as e:
                print(f"[GeminiLive] Screen start note: {e}")
        loop = asyncio.get_running_loop()
        task = loop.create_task(self._run_companion_pipeline())
        self._bg_tasks.add(task)
        task.add_done_callback(self._bg_tasks.discard)

    async def purge_and_hard_reset(self):
        self.status_changed.emit("Purging memory...", "warn")
        await self.stop_session()
        if self.transcript is not None:
            try:
                self.transcript.clear_all()
                self.current_transcript_buffer = ""
            except Exception:
                pass
        # Clear precise injection history so next refine has fresh measurement
        try:
            if HAS_INJECTION and InjectionService:
                InjectionService.clear_history()
        except Exception:
            pass
        self.reset_token_counter()
        self.status_changed.emit("Memory Purged", "idle")
        await asyncio.sleep(0.08)
        self.status_changed.emit("SPEAK Ready", "idle")

    async def stop_session(self):
        was_active = self._is_active
        self._is_active = False
        # Bump generation so late screen spawns abort; clear handle so toggles cannot respawn mid-stop
        try:
            self._screen_gen = int(getattr(self, "_screen_gen", 0) or 0) + 1
        except Exception:
            pass
        try:
            self._screen_task = None
        except Exception:
            pass
        try:
            self.audio.stop_recording()
        except Exception:
            pass
        try:
            self.audio.stop_playback_stream()
        except Exception:
            pass
        try:
            self.screen.stop()
        except Exception:
            pass
        # Never cancel/await ourselves: failover runs inside a _bg_tasks member, and
        # self-cancel would abort the failover before its sleep/restart (CancelledError
        # is BaseException, not caught by `except Exception`).
        try:
            cur = asyncio.current_task()
        except Exception:
            cur = None
        for t in list(self._bg_tasks):
            try:
                if cur is not None and t is cur:
                    continue
                t.cancel()
            except Exception:
                pass
        # Let cancellations deliver (bounded) so a restart never overlaps a dying connect
        try:
            pending = [t for t in list(self._bg_tasks) if t is not cur and not t.done()]
            if pending:
                await asyncio.wait_for(asyncio.gather(*pending, return_exceptions=True), timeout=3.0)
        except Exception:
            pass
        self._bg_tasks = {t for t in self._bg_tasks if not t.done()}
        self.session = None
        if was_active:
            self._current_mode = "idle"
            self.status_changed.emit("SPEAK Ready", "idle")
        if self.transcript is not None:
            try:
                self.transcript.clear_interim()
            except Exception:
                pass

    async def _handle_failover(self, error: Exception, mode: str):
        print(f"[GeminiLive] Failover: {error}")
        # Dictation uses a strict STT-only config. A 400/INVALID_ARGUMENT here
        # means the server rejected the setup itself — rotating keys and
        # retrying the identical setup would hot-loop, so stop loudly with an
        # actionable message instead.
        if mode == "dictation" and _classify_live_error(error).startswith("bad-request"):
            self.error_occurred.emit("Dictation rejected by API (400). Upgrade the SDK: pip install -U \"google-genai>=2.19\" then retry.")
            self.status_changed.emit("Dictation rejected (400)", "error")
            await self.stop_session()
            return
        # Storm guard: 3+ failovers in 30s means models/keys are bad — stop loudly, no hot loop.
        try:
            import time as _time
            now = _time.monotonic()
            if now - float(getattr(self, "_failover_window_ts", 0.0) or 0.0) > 30.0:
                self._failover_count = 0
                self._failover_window_ts = now
            self._failover_count = int(getattr(self, "_failover_count", 0) or 0) + 1
        except Exception:
            pass
        try:
            if int(getattr(self, "_failover_count", 0) or 0) >= 3:
                self.error_occurred.emit("Live connect keeps failing — check API keys and companion model IDs in Settings.")
                self.status_changed.emit("Live connect failed", "error")
                await self.stop_session()
                return
        except Exception:
            pass
        self.status_changed.emit("Switching to backup key...", "warn")
        new_key = config_vault.rotate_key()
        if not new_key:
            self.error_occurred.emit("API quota exhausted across all keys. Add backup key in Settings.")
            await self.stop_session()
            return
        await self.stop_session()
        await asyncio.sleep(0.5)
        if mode == "dictation":
            await self.start_dictation_mode()
        elif mode == "companion":
            await self.start_companion_mode()

    def _sanitize_transcript_text(self, text: str) -> str:
        """Strip leading em dashes/bullets that appear before live text."""
        if not text:
            return text
        t = text.lstrip()
        t = re.sub(r'^[—–\-•▶>]+\s*', '', t)
        t = re.sub(r'^[*+]+\s+', '', t)
        return t

    def _sync_injection_clear_on_new_session(self):
        """Clear injection history at session start so refine measures only current convo."""
        try:
            if HAS_INJECTION and InjectionService:
                InjectionService.clear_history()
        except Exception:
            pass

    def _detect_action_keyword(self, text: str):
        """Map spoken text to a refine action id via Settings triggers (built-ins + customs).
        Exact single-word match first, then short-phrase contains (<=8 words). Longest trigger wins."""
        try:
            t = (text or "").strip().lower()
            if not t:
                return None
            clean = re.sub(r"[^\w\s-]", "", t).strip()
            if not clean:
                return None
            # Exact match via config resolver (handles custom triggers + expand alias)
            try:
                direct = config_vault.resolve_refine_action(clean)
                if direct:
                    return direct
            except Exception:
                pass
            words = clean.split()
            if len(words) > 8:
                return None
            # Collect all known triggers, longest first for specificity
            candidates: list[tuple[str, str]] = []
            try:
                trig = config_vault.get_refine_triggers()
                for aid, lst in trig.items():
                    for kw in (lst or []):
                        if kw:
                            candidates.append((kw, aid))
            except Exception:
                candidates = [("refine", "refine"), ("polish", "polish"), ("elaborate", "elaborate"), ("expand", "elaborate")]
            try:
                for c in config_vault.get_custom_actions(enabled_only=True):
                    if c.get("trigger"):
                        candidates.append((c["trigger"], c["id"]))
            except Exception:
                pass
            candidates.sort(key=lambda kv: -len(kv[0]))
            for kw, aid in candidates:
                if re.search(rf"\b{re.escape(kw)}\b", clean):
                    return aid
        except Exception:
            pass
        return None

    def _sanitize_refined_output(self, text: str) -> str:
        """Strip model preamble/quotes/fences so only final text is typed."""
        try:
            t = str(text or "").strip()
            # Code fences — remove anywhere (a language tag like ```json would otherwise
            # eat the first word via [a-zA-Z]* matching prose, e.g. ```Refined -> 'text: ...')
            t = t.replace("```", "").strip()
            # Leading labels like 'Refined text:' / 'Output:'
            t = re.sub(r"^(refined( text)?|polished( text)?|elaborated( text)?|expanded( text)?|output|result)\s*[:\-\u2014]\s*", "", t, flags=re.IGNORECASE)
            # Surrounding quotes (single attempt, balanced only)
            if len(t) >= 2 and ((t[0] == t[-1] == '"') or (t[0] == t[-1] == "'")):
                t = t[1:-1].strip()
            # Collapse 3+ newlines to 2 (keep paragraphs, avoid wall)
            t = re.sub(r"\n{3,}", "\n\n", t)
            return t.strip()[:4000]
        except Exception:
            return str(text or "").strip()[:4000]

    def _display_name(self, action_type: str) -> str:
        try:
            a = str(action_type or "").strip().lower()
            if a in ("refine", "polish", "elaborate", "expand"):
                return "Elaborate" if a in ("elaborate", "expand") else a.title()
            for c in config_vault.get_custom_actions(enabled_only=False):
                if c.get("id") == a:
                    return str(c.get("name") or a).title()
        except Exception:
            pass
        return str(action_type or "refine").title()

    async def trigger_refine(self, action_type: str):
        if self._refine_in_progress:
            return
        if self.transcript is None or not self.transcript.has_content():
            self.status_changed.emit("Nothing to refine yet", "warn")
            try:
                self.refine_failed.emit("No transcript")
            except Exception:
                pass
            return
        # Normalize: legacy 'expand' -> 'elaborate'; validate customs; unknown -> fail loudly
        raw = str(action_type or "").lower().strip()
        if raw == "expand":
            action_type = "elaborate"
        elif raw in BUILTIN_REFINE_IDS:
            action_type = raw
        else:
            try:
                valid_ids = {"refine", "polish", "elaborate"} | {c.get("id") for c in config_vault.get_custom_actions(enabled_only=True)}
            except Exception:
                valid_ids = {"refine", "polish", "elaborate"}
            if raw in valid_ids:
                action_type = raw
            else:
                try:
                    self.refine_failed.emit(f"Unknown action: {raw[:24]}")
                except Exception:
                    pass
                self.status_changed.emit("Unknown refine action", "error")
                return
        disp = self._display_name(action_type)
        self._refine_in_progress = True
        try:
            self.refine_started.emit(action_type)
        except Exception:
            pass
        try:
            self.status_changed.emit(f"{disp}ing...", "warn")
            snapshot = self.transcript.get_for_refine()
        except Exception as e:
            print(f"[Gemini] Refine failed {e}")
            try:
                self.refine_failed.emit(str(e)[:300])
            except Exception:
                pass
            self._refine_in_progress = False
            return
        except BaseException:
            self._refine_in_progress = False
            raise
        # Session delete scope: transcript char count (+1 trailing space)
        try:
            fallback_len = len(snapshot) + 1 if snapshot else 0
        except Exception:
            fallback_len = 0
        # Fast path: delete old text WHILE the model rewrites (parallel, not serial).
        # Count comes from measured history first, else the transcript snapshot.
        try:
            loop = asyncio.get_running_loop()
        except Exception:
            loop = None
        use_fast = bool(HAS_INJECTION and InjectionService and loop is not None)
        if use_fast:
            try:
                delete_len = InjectionService._delete_count(fallback_len)
            except Exception:
                delete_len = int(fallback_len or 0)
            try:
                api_task = loop.create_task(self._call_flash_lite(snapshot, action_type))
                del_task = loop.run_in_executor(None, InjectionService.delete_chars, int(delete_len or 0))
            except Exception as e:
                print(f"[Gemini] Refine failed {e}")
                try:
                    self.refine_failed.emit(str(e)[:300])
                except Exception:
                    pass
                self._refine_in_progress = False
                return
            except BaseException:
                try:
                    _t = locals().get("api_task")
                    if _t is not None:
                        _t.cancel()
                except Exception:
                    pass
                self._refine_in_progress = False
                raise
            try:
                api_res, del_res = await asyncio.gather(api_task, del_task, return_exceptions=True)
            except BaseException:
                # Outer cancellation: never leave the flag stuck (would block all future refines)
                self._refine_in_progress = False
                raise
            deleted = int(del_res) if isinstance(del_res, int) else 0
            if isinstance(api_res, BaseException):
                # Model failed but old text may already be gone — restore it, then fail loudly.
                try:
                    if deleted > 0 and snapshot and InjectionService._ensure_target():
                        await loop.run_in_executor(None, InjectionService.type_text, snapshot)
                        try:
                            InjectionService.clear_history()
                            InjectionService._record(snapshot)
                        except Exception:
                            pass
                    elif deleted > 0 and snapshot:
                        # Focus moved mid-refine: old text already deleted, restore unsafe — stay loud.
                        print("[Gemini] Refine restore skipped - focus moved during rewrite")
                        try:
                            self.error_occurred.emit("Refine restore skipped — focus moved during rewrite. Original text is in the capsule.")
                        except Exception:
                            pass
                except Exception:
                    pass
                print(f"[Gemini] Refine failed {api_res}")
                try:
                    self.refine_failed.emit(str(api_res)[:300])
                except Exception:
                    pass
                try:
                    self.status_changed.emit(f"{self._display_name(action_type)} failed", "error")
                except Exception:
                    pass
                try:
                    self.error_occurred.emit(f"Refine error: {str(api_res)[:160]}")
                except Exception:
                    pass
                self._refine_in_progress = False
                return
            refined = api_res
            if not refined or not str(refined).strip():
                try:
                    if deleted > 0 and snapshot and InjectionService._ensure_target():
                        await loop.run_in_executor(None, InjectionService.type_text, snapshot)
                        try:
                            InjectionService.clear_history()
                            InjectionService._record(snapshot)
                        except Exception:
                            pass
                    elif deleted > 0 and snapshot:
                        print("[Gemini] Refine restore skipped - focus moved during rewrite")
                        try:
                            self.error_occurred.emit("Refine restore skipped — focus moved during rewrite. Original text is in the capsule.")
                        except Exception:
                            pass
                except Exception:
                    pass
                print("[Gemini] Refine failed Empty response")
                try:
                    self.refine_failed.emit("Empty response")
                except Exception:
                    pass
                try:
                    self.status_changed.emit(f"{self._display_name(action_type)} failed", "error")
                except Exception:
                    pass
                self._refine_in_progress = False
                return
            refined = self._sanitize_refined_output(refined)
            if not refined:
                try:
                    if deleted > 0 and snapshot and InjectionService._ensure_target():
                        await loop.run_in_executor(None, InjectionService.type_text, snapshot)
                        try:
                            InjectionService.clear_history()
                            InjectionService._record(snapshot)
                        except Exception:
                            pass
                    elif deleted > 0 and snapshot:
                        print("[Gemini] Refine restore skipped - focus moved during rewrite")
                        try:
                            self.error_occurred.emit("Refine restore skipped — focus moved during rewrite. Original text is in the capsule.")
                        except Exception:
                            pass
                except Exception:
                    pass
                print("[Gemini] Refine failed Empty response after sanitize")
                try:
                    self.refine_failed.emit("Empty response after sanitize")
                except Exception:
                    pass
                try:
                    self.status_changed.emit(f"{self._display_name(action_type)} failed", "error")
                except Exception:
                    pass
                self._refine_in_progress = False
                return
            try:
                if deleted <= 0:
                    # Focus was unsafe during early delete — full path retries (restore-aware).
                    deleted, typed = await self._apply_refined_text(refined, fallback_len)
                else:
                    typed = await loop.run_in_executor(None, InjectionService.type_text, refined)
                    try:
                        InjectionService.clear_history()
                        InjectionService._record(str(refined or "")[:4000])
                    except Exception:
                        pass
                self.transcript.replace_full(refined, action_type)
                self.current_transcript_buffer = refined
                try:
                    self.refine_completed.emit(action_type, refined)
                except Exception:
                    pass
                try:
                    self.status_changed.emit(f"{disp}d \u2014 replaced {deleted} chars", "active")
                except Exception:
                    pass
                await asyncio.sleep(0.05)
                self.status_changed.emit("SPEAK Ready", "idle")
                self._refine_in_progress = False
            except Exception as e:
                print(f"[Gemini] Refine failed {e}")
                try:
                    self.refine_failed.emit(str(e)[:300])
                except Exception:
                    pass
                try:
                    self.status_changed.emit(f"{self._display_name(action_type)} failed", "error")
                except Exception:
                    pass
                self._refine_in_progress = False
            except BaseException:
                for _t in (locals().get("api_task"), locals().get("del_task")):
                    try:
                        if _t is not None:
                            _t.cancel()
                    except Exception:
                        pass
                self._refine_in_progress = False
                raise
            return
        try:
            refined = await self._call_flash_lite(snapshot, action_type)
            if not refined or not refined.strip():
                raise RuntimeError("Empty response")
            refined = self._sanitize_refined_output(refined)
            if not refined:
                raise RuntimeError("Empty response after sanitize")
            self.transcript.replace_full(refined, action_type)
            self.current_transcript_buffer = refined
            try:
                self.refine_completed.emit(action_type, refined)
            except Exception:
                pass
            self.status_changed.emit(f"{disp}d", "active")
            deleted, typed = await self._apply_refined_text(refined, fallback_len)
            try:
                self.status_changed.emit(f"{disp}d \u2014 replaced {deleted} chars", "active")
            except Exception:
                pass
            await asyncio.sleep(0.05)
            self.status_changed.emit("SPEAK Ready", "idle")
        except Exception as e:
            print(f"[Gemini] Refine failed {e}")
            import traceback; traceback.print_exc()
            try:
                self.refine_failed.emit(str(e)[:300])
            except Exception:
                pass
            try:
                self.status_changed.emit(f"{self._display_name(action_type)} failed", "error")
            except Exception:
                pass
            try:
                self.error_occurred.emit(f"Refine error: {str(e)[:160]}")
            except Exception:
                pass
        finally:
            self._refine_in_progress = False

    async def _call_flash_lite(self, text: str, action_type: str):
        if not self.client and not self._init_sdk_client():
            raise RuntimeError("No client")
        # Settings-editable prompt wins; REFINE_PROMPTS is fallback only.
        try:
            base_prompt = config_vault.get_refine_prompt(action_type)
            if not base_prompt or not str(base_prompt).strip():
                raise ValueError("empty")
        except Exception:
            base_prompt = REFINE_PROMPTS.get(action_type, REFINE_PROMPTS["refine"])
        # Inject custom mark and vocabulary hint into refine
        try:
            mark = config_vault.get_custom_mark()
            vocab = config_vault.build_vocabulary_hint()
            suffix = ""
            if vocab:
                suffix += "\n" + vocab
            if mark:
                suffix += f"\nPreserve user mark if appropriate: {mark}"
            if suffix:
                base_prompt = base_prompt.rstrip() + suffix + "\n\n"
        except Exception:
            pass
        prompt = base_prompt + text
        last_err = None
        for model_id in config_vault.get_refine_models():
            try:
                print(f"[Gemini] FlashLite {model_id}")
                loop = asyncio.get_running_loop()
                def _call():
                    return self.client.models.generate_content(model=model_id, contents=prompt)
                resp = await loop.run_in_executor(None, _call)
                out = getattr(resp, "text", None)
                if out and out.strip():
                    return out
                try:
                    cands = getattr(resp, "candidates", None)
                    if cands:
                        parts = getattr(cands[0].content, "parts", None) if hasattr(cands[0], "content") else None
                        if parts:
                            txt = "".join(getattr(p,"text","") or "" for p in parts)
                            if txt.strip():
                                return txt
                except Exception:
                    pass
                raise RuntimeError(f"Empty {model_id}")
            except Exception as e:
                last_err = e
                print(f"[Gemini] FlashLite {model_id} fail {e}")
                continue
        raise RuntimeError(f"All refine models failed: {last_err}")

    async def _apply_refined_text(self, refined: str, fallback_len: int = 0):
        # Session delete-and-replace: delete everything typed this session, then type refined.
        # No clipboard, no Ctrl+A — InjectionService precise history (+ fallback_len when history empty).
        # Returns (deleted, typed) counts for status/notify (never raises).
        try:
            await asyncio.sleep(0.10)
            if HAS_INJECTION and InjectionService:
                try:
                    result = await InjectionService.precise_replace_async(refined, int(fallback_len or 0))
                    if isinstance(result, tuple) and len(result) == 2:
                        deleted, typed = int(result[0]), int(result[1])
                    else:
                        deleted, typed = int(fallback_len or 0), len(refined or "")
                except TypeError:
                    # Old signature compat (should not happen post-upgrade)
                    await InjectionService.precise_replace_async(refined)
                    deleted, typed = int(fallback_len or 0), len(refined or "")
                print(f"[Gemini] Precise refined replace done (deleted {deleted}, typed {typed})")
                return deleted, typed
            else:
                if pyautogui:
                    try:
                        n = 0
                        try:
                            if InjectionService:
                                n = int(InjectionService.get_typed_length() or 0)
                        except Exception:
                            n = 0
                        if n <= 0:
                            n = int(fallback_len or 0)
                        for _ in range(max(0, min(n, 4000))):
                            pyautogui.press("backspace")
                        pyautogui.write(refined, interval=0.001)
                        return n, len(refined or "")
                    except Exception:
                        try:
                            pyautogui.write(refined, interval=0.001)
                        except Exception:
                            pass
                        return 0, len(refined or "")
        except Exception as e:
            print(f"[Gemini] apply {e}")
        return 0, len(refined or "")

    def request_refine(self, action="refine"):
        asyncio.create_task(self.trigger_refine(action))
    def get_buffer(self):
        return self.transcript.get_for_refine() if self.transcript else ""

    async def _run_dictation_pipeline(self):
        if not self._init_sdk_client():
            self._is_active = False
            return
        try:
            self._loop = asyncio.get_running_loop()
        except Exception:
            pass
        model_id = config_vault.get_dictation_model()
        print(f"[GeminiLive] Dictation model: {model_id}")
        # Strict STT-only config (no tools/thinking/system prompt — server 400s them).
        try:
            live_config = _build_dictation_config()
        except Exception as e:
            print(f"[GeminiLive] Dictation config build error: {e}")
            self.error_occurred.emit(f"Dictation config error: {e}")
            self.status_changed.emit("Dictation config error", "error")
            self._is_active = False
            return
        try:
            smart_ok, vocab_ok, _ = _dictation_sdk_status()
            if not smart_ok:
                print("[GeminiLive] SDK predates SMART transcription (need google-genai>=2.19) — running VERBATIM fallback")
        except Exception:
            pass
        attempt = 0
        # Reconnect loop: the Preview STT model caps sessions (~10 min) and the
        # server then closes cleanly. Reconnect on the SAME key/config without
        # burning key rotation; key rotation stays reserved for real errors.
        while self._is_active and self._current_mode == "dictation":
            attempt += 1
            try:
                self._dictation_clean_close = asyncio.Event()
            except Exception:
                self._dictation_clean_close = None
            try:
                async with self.client.aio.live.connect(model=model_id, config=live_config) as session:
                    self.session = session
                    self.status_changed.emit(f"Dictating ({model_id})", "active")
                    send_task = asyncio.create_task(self._send_audio_loop(stop_event=getattr(self, "_dictation_clean_close", None)))
                    recv_task = asyncio.create_task(self._receive_dictation_loop())
                    self._bg_tasks.add(send_task)
                    self._bg_tasks.add(recv_task)
                    try:
                        await asyncio.gather(send_task, recv_task)
                    except asyncio.CancelledError:
                        raise
                    except Exception as e:
                        # Sibling-task failure (sendLoop recvLoop already
                        # failovers internally) — classify loudly, then failover.
                        kind = _classify_live_error(e)
                        print(f"[GeminiLive] Dictation model {model_id} failed (attempt {attempt}, {kind}): {e}")
                        try:
                            self.status_changed.emit(f"Dictation {kind} — retrying...", "warn")
                        except Exception:
                            pass
                        if self._is_active:
                            await self._handle_failover(e, "dictation")
                        return
            except asyncio.CancelledError:
                break
            except Exception as e:
                kind = _classify_live_error(e)
                print(f"[GeminiLive] Dictation model {model_id} failed (attempt {attempt}, {kind}): {e}")
                try:
                    self.status_changed.emit(f"Dictation {kind} — retrying...", "warn")
                except Exception:
                    pass
                if self._is_active:
                    await self._handle_failover(e, "dictation")
                return
            # Clean server close (e.g. 10-min Preview cap, GoAway): reconnect
            # same key/config if the user is still dictating.
            try:
                clean = bool(getattr(self, "_dictation_clean_close", None) is not None and self._dictation_clean_close.is_set())
            except Exception:
                clean = False
            if not self._is_active or self._current_mode != "dictation":
                break
            if clean:
                print(f"[GeminiLive] Dictation session closed by server (attempt {attempt}) — reconnecting same key")
                try:
                    self.status_changed.emit("Reconnecting dictation...", "warn")
                except Exception:
                    pass
                await asyncio.sleep(1.0)
                continue
            break

    async def _run_companion_pipeline(self):
        if not self._init_sdk_client():
            self._is_active = False
            return
        comp_models = config_vault.get_companion_models()
        print(f"[GeminiLive] Companion models: {comp_models}  screen={self._screen_enabled}")
        cfg = config_vault.config
        # Use vault helper that injects custom words/mark + locked verbal-confirm suffix
        try:
            sys_prompt = self.build_locked_system_instruction(config_vault.build_system_instruction())
        except Exception:
            try:
                sys_prompt = self.build_locked_system_instruction(cfg.get("system_instruction", "") or "You are SPEAK, a fast, intelligent real-time companion.")
            except Exception:
                sys_prompt = cfg.get("system_instruction", "") or "You are SPEAK, a fast, intelligent real-time companion."
        try:
            _think = _locked_thinking_config()
            _kwargs: dict = {
                "response_modalities": [types.Modality.AUDIO],
                "system_instruction": sys_prompt,
                "speech_config": types.SpeechConfig(
                    voice_config=types.VoiceConfig(
                        prebuilt_voice_config=types.PrebuiltVoiceConfig(voice_name="Aoede")
                    )
                ),
                "tools": [TYPE_TEXT_TOOL],
            }
            if _think is not None and _supports_live_field("thinking_config"):
                _kwargs["thinking_config"] = _think
            elif _think is not None:
                print("[GeminiLive] thinking_config HIGH requested but SDK LiveConnectConfig lacks field — running without (SDK 1.21 compat)")
            live_config = types.LiveConnectConfig(**_kwargs)
            # Ask for transcriptions alongside audio (observability + UI proof-of-life).
            # LOCKED to SMART mode — never fail the build on older SDKs.
            # Best-effort: older SDKs may not accept these fields — never fail the build.
            try:
                live_config.output_audio_transcription = _locked_transcription_config() or types.AudioTranscriptionConfig()
            except Exception:
                pass
            try:
                live_config.input_audio_transcription = _locked_transcription_config() or types.AudioTranscriptionConfig()
            except Exception:
                pass
            try:
                live_config.temperature = float(cfg.get("temperature", 0.3))
                live_config.top_p = float(cfg.get("top_p", 0.95))
            except Exception:
                pass
            # Re-assert HIGH thinking after temperature/top_p (some SDKs reset extras)
            try:
                if _think is not None and _supports_live_field("thinking_config"):
                    live_config.thinking_config = _think
            except Exception:
                pass
        except Exception as e:
            print(f"[GeminiLive] Companion config error: {e}")
            live_config = types.LiveConnectConfig(response_modalities=["AUDIO"], system_instruction=sys_prompt)
        connected = False
        last_err = None
        tried: list[str] = []
        for model_id in comp_models:
            if not self._is_active:
                break
            try:
                print(f"[GeminiLive] Trying companion model: {model_id}")
                tried.append(str(model_id))
                async with self.client.aio.live.connect(model=model_id, config=live_config) as session:
                    self.session = session
                    connected = True
                    # A working connect resets the failover storm counter
                    try:
                        self._failover_count = 0
                    except Exception:
                        pass
                    self._emit_companion_status(model_id)
                    t_audio = asyncio.create_task(self._send_audio_loop())
                    t_recv = asyncio.create_task(self._receive_companion_loop())
                    t_screen = None
                    self._screen_task = None
                    if self._screen_enabled:
                        t_screen = asyncio.create_task(self._send_screen_loop())
                        self._screen_task = t_screen
                        self._bg_tasks.add(t_screen)
                        # Screen failures must never kill audio: log only, session survives.
                        try:
                            t_screen.add_done_callback(lambda _t: print(f"[GeminiLive] Screen task ended (ok={not _t.cancelled()})"))
                        except Exception:
                            pass
                    for t in (t_audio, t_recv):
                        self._bg_tasks.add(t)
                    try:
                        # Session-critical tasks only — screen is supervised separately above.
                        await asyncio.gather(t_audio, t_recv)
                    except asyncio.CancelledError:
                        break
                    finally:
                        # Tear down the supervised screen task with the session (awaited, quiet).
                        try:
                            if t_screen is not None and not t_screen.done():
                                t_screen.cancel()
                                try:
                                    await asyncio.gather(t_screen, return_exceptions=True)
                                except Exception:
                                    pass
                        except Exception:
                            pass
                        try:
                            if getattr(self, "_screen_task", None) is t_screen:
                                self._screen_task = None
                        except Exception:
                            pass
                    break
            except asyncio.CancelledError:
                break
            except Exception as e:
                last_err = e
                print(f"[GeminiLive] Companion model {model_id} failed: {e}")
                try:
                    self.status_changed.emit(f"Model unavailable, trying next...", "warn")
                except Exception:
                    pass
                continue
        if not connected and self._is_active:
            try:
                self.error_occurred.emit(f"Live connect failed ({', '.join(tried) or 'no models'}). Check keys/models.")
            except Exception:
                pass
            await self._handle_failover(last_err or Exception("Live connect failed"), "companion")

    async def _send_audio_loop(self, stop_event=None):
        while self._is_active and self.session:
            try:
                if stop_event is not None and stop_event.is_set():
                    break
            except Exception:
                pass
            try:
                try:
                    chunk = await self.audio.get_audio_chunk(timeout=3.0)
                except asyncio.TimeoutError:
                    # Dead mic (callback stopped feeding) — warn throttled, keep session alive
                    try:
                        self._mic_silent_warns = int(getattr(self, "_mic_silent_warns", 0) or 0) + 1
                        if self._mic_silent_warns % 5 == 1:
                            self.status_changed.emit("Mic silent — check microphone", "warn")
                    except Exception:
                        pass
                    continue
                if not chunk:
                    continue
                if not self._is_active or not self.session:
                    break
                self._session_tokens += max(1, int(len(chunk) / 320))
                try:
                    self.token_usage_updated.emit(self._session_tokens, self.MAX_CONTEXT_TOKENS)
                except Exception:
                    pass
                try:
                    await self.session.send_realtime_input(audio=types.Blob(data=chunk, mime_type="audio/pcm;rate=16000"))
                except Exception:
                    await self.session.send(input={"data": chunk, "mime_type": "audio/pcm;rate=16000"})
            except asyncio.CancelledError:
                break
            except Exception as e:
                print(f"[GeminiLive] Audio send error: {e}")
                await asyncio.sleep(0.05)

    async def _send_screen_loop(self):
        # Voice-only companion: exit immediately (no dangling sleep task).
        # Mid-session re-enable spawns a fresh task via set_screen_enabled().
        if not getattr(self, "_screen_enabled", True):
            print("[GeminiLive] Screen loop skipped — voice only")
            return
        try:
            fps = config_vault.get_screen_fps()
        except Exception:
            fps = 1.5
        send_failures = 0
        frames_sent = 0
        empty_streak = 0
        blank_warned = False
        try:
            # Drive pacing here; capture offloaded so the event loop never blocks on
            # mss grab + PIL resize + JPEG encode (HiDPI/4K can cost 50-400ms/frame).
            interval = 1.0 / max(0.2, min(2.0, float(fps)))
            try:
                self.screen.start()
            except Exception:
                pass
            loop = asyncio.get_running_loop()
            while self._is_active and self.session and self._screen_enabled:
                try:
                    jpeg_bytes = await loop.run_in_executor(None, self.screen.capture_frame_bytes)
                except Exception as e:
                    print(f"[GeminiLive] Screen capture error: {e}")
                    await asyncio.sleep(interval)
                    continue
                if not self._is_active or not self.session or not self._screen_enabled:
                    break
                if not jpeg_bytes:
                    empty_streak += 1
                    if empty_streak >= 10 and not blank_warned:
                        blank_warned = True
                        try:
                            self.error_occurred.emit("Screen capture is returning blank frames — check display connection/permissions. Voice continues.")
                            self.status_changed.emit("Screen blank — voice continues", "warn")
                        except Exception:
                            pass
                    await asyncio.sleep(interval)
                    continue
                empty_streak = 0
                self._session_tokens += 258
                try:
                    self.token_usage_updated.emit(self._session_tokens, self.MAX_CONTEXT_TOKENS)
                except Exception:
                    pass
                try:
                    await self.session.send_realtime_input(video=types.Blob(data=jpeg_bytes, mime_type="image/jpeg"))
                    send_failures = 0
                    frames_sent += 1
                    if frames_sent == 1 or frames_sent % 45 == 0:
                        print(f"[GeminiLive] Screen frames sent: {frames_sent} ({len(jpeg_bytes)} bytes last)")
                except Exception:
                    try:
                        await self.session.send(input={"data": jpeg_bytes, "mime_type": "image/jpeg"})
                        send_failures = 0
                        frames_sent += 1
                    except Exception as e:
                        send_failures += 1
                        print(f"[GeminiLive] Screen send error ({send_failures}): {e}")
                        if send_failures >= 20:
                            # Give up on video, keep voice alive — never kill the session over screen.
                            try:
                                self.status_changed.emit("Screen unavailable — voice continues", "warn")
                            except Exception:
                                pass
                            return
                        await asyncio.sleep(0.25)
                        continue
                await asyncio.sleep(interval)
        except asyncio.CancelledError:
            raise
        except Exception as e:
            print(f"[GeminiLive] Screen loop error: {e}")
        finally:
            try:
                if getattr(self, "_screen_task", None) is asyncio.current_task():
                    self._screen_task = None
            except Exception:
                pass

    async def _receive_dictation_loop(self):
        """Live Transcription: handles interim_input_transcription + input_transcription.
        STT-only model: no tools/thinking — server sends transcription events.
        GoAway / clean server close (e.g. ~10-min Preview cap) signals the
        pipeline to reconnect on the SAME key instead of key-rotation failover."""
        try:
            while self._is_active and self.session:
                async for response in self.session.receive():
                    if not self._is_active:
                        break
                    # Server-initiated end-of-session (Preview time cap): exit
                    # cleanly so the pipeline reconnects same key/config.
                    try:
                        if getattr(response, "go_away", None) is not None:
                            print("[GeminiLive] Dictation GoAway from server — clean reconnect")
                            try:
                                ev = getattr(self, "_dictation_clean_close", None)
                                if ev is not None:
                                    ev.set()
                            except Exception:
                                pass
                            return
                    except Exception:
                        pass
                    try:
                        if getattr(response, "session_resumption_update", None) is not None:
                            print("[GeminiLive] Dictation session_resumption_update noted")
                    except Exception:
                        pass
                    # Handle tool calls if present (optional, not required for typing)
                    tool_call = getattr(response, "tool_call", None)
                    if tool_call and getattr(tool_call, "function_calls", None):
                        for fc in tool_call.function_calls:
                            name = getattr(fc, "name", "") or ""
                            fid = getattr(fc, "id", "") or "id"
                            args = getattr(fc, "args", {}) or {}
                            if isinstance(args, str):
                                try:
                                    import json as _j
                                    args = _j.loads(args)
                                except Exception:
                                    args = {}
                            print(f"[Gemini] ToolCall {name} id={fid} args={args}")
                            if name == "typeTextAtCursor":
                                # All typing binds to typeTextAtCursor (verification-aware)
                                try:
                                    await self.handle_type_text_tool_call(tool_call)
                                except Exception as e:
                                    print(f"[Gemini] typeTextAtCursor note: {e}")
                                continue
                            if name == "refine_document":
                                action = args.get("action_type","refine") if isinstance(args, dict) else "refine"
                                try:
                                    await self.session.send_tool_response(function_responses=types.FunctionResponse(id=fid, name=name, response={"status":"processing","action":action}))
                                except Exception as e:
                                    print(f"[Gemini] ack {e}")
                                try:
                                    norm = str(action or "refine").strip().lower()
                                    if norm == "expand":
                                        norm = "elaborate"
                                except Exception:
                                    norm = "refine"
                                asyncio.create_task(self.trigger_refine(norm))
                                continue
                    srv = getattr(response, "server_content", None)
                    if not srv:
                        continue
                    final = getattr(srv, "input_transcription", None)
                    if final and getattr(final, "text", None):
                        final_text = final.text
                        if final_text and final_text.strip():
                            stripped = self._sanitize_transcript_text(final_text.strip())
                            if not stripped:
                                continue
                            det = self._detect_action_keyword(stripped)
                            if det and self.transcript is not None and self.transcript.has_content():
                                print(f"[Gemini] Keyword refine {stripped} -> {det}")
                                try:
                                    self.transcript.clear_interim()
                                except Exception:
                                    pass
                                try:
                                    self.status_changed.emit(f"{self._display_name(det)} requested...", "warn")
                                except Exception:
                                    pass
                                asyncio.create_task(self.trigger_refine(det))
                                continue
                            if self.transcript is not None:
                                try:
                                    self.transcript.append_final(stripped)
                                except Exception:
                                    pass
                            try:
                                to_type = stripped if stripped.endswith((" ", "\n")) else stripped + " "
                                if HAS_INJECTION and InjectionService:
                                    InjectionService.safe_type(to_type)
                                elif pyautogui:
                                    pyautogui.write(to_type, interval=0.001)
                                print(f"[GeminiLive] Typed: {stripped[:80]}")
                                self.status_changed.emit("Dictating...", "active")
                                if self.transcript is not None:
                                    try:
                                        self.transcript.clear_interim()
                                    except Exception:
                                        pass
                            except Exception as e:
                                print(f"[GeminiLive] typing error: {e}")
                                self.error_occurred.emit(f"Typing error: {e}")
                            continue
                    interim = getattr(srv, "interim_input_transcription", None)
                    if interim and getattr(interim, "text", None):
                        preview = interim.text.strip()
                        if preview:
                            det = self._detect_action_keyword(preview)
                            if det and self.transcript is not None and self.transcript.has_content():
                                try:
                                    self.status_changed.emit(f"{self._display_name(det)}...", "warn")
                                except Exception:
                                    pass
                                try:
                                    self.transcript.set_interim(f"-> {self._display_name(det)}...")
                                except Exception:
                                    pass
                            else:
                                self.status_changed.emit(f"▶ {preview[:42]}", "active")
                                if self.transcript is not None:
                                    try:
                                        self.transcript.set_interim(preview)
                                    except Exception:
                                        pass
                            continue
                    text = getattr(response, "text", None)
                    if text and text.strip():
                        cleaned = self._sanitize_transcript_text(text.strip())
                        if not cleaned:
                            continue
                        _det2 = self._detect_action_keyword(cleaned)
                        if _det2 and self.transcript is not None and self.transcript.has_content():
                            asyncio.create_task(self.trigger_refine(_det2))
                            continue
                        if self.transcript is not None:
                            try:
                                self.transcript.append_final(cleaned)
                            except Exception:
                                pass
                        try:
                            if HAS_INJECTION and InjectionService:
                                InjectionService.safe_type(cleaned)
                            elif pyautogui:
                                pyautogui.write(cleaned, interval=0.001)
                            print(f"[GeminiLive] Typed (fallback): {cleaned[:60]}")
                        except Exception as e:
                            print(f"[GeminiLive] fallback {e}")
                        continue
                    if getattr(srv, "model_turn", None):
                        for part in srv.model_turn.parts:
                            if getattr(part, "text", None):
                                txt_raw = part.text.strip()
                                txt = self._sanitize_transcript_text(txt_raw)
                                if not txt:
                                    continue
                                _det3 = self._detect_action_keyword(txt)
                                if _det3 and self.transcript is not None and self.transcript.has_content():
                                    asyncio.create_task(self.trigger_refine(_det3))
                                    continue
                                if self.transcript is not None:
                                    try:
                                        self.transcript.append_final(txt)
                                    except Exception:
                                        pass
                                try:
                                    if HAS_INJECTION and InjectionService:
                                        InjectionService.safe_type(txt)
                                    elif pyautogui:
                                        pyautogui.write(txt, interval=0.001)
                                except Exception as e:
                                    print(f"[GeminiLive] part {e}")
        except asyncio.CancelledError:
            pass
        except Exception as e:
            if self._is_active:
                kind = _classify_live_error(e)
                print(f"[GeminiLive] Dictation receive error ({kind}): {e}")
                import traceback; traceback.print_exc()
                try:
                    self.status_changed.emit(f"Dictation {kind} — retrying...", "warn")
                except Exception:
                    pass
                await self._handle_failover(e, "dictation")

    def _on_spoken_audio(self, nbytes: int):
        """Proof-of-life for exe users: throttled Speaking status + byte counter."""
        try:
            self._audio_bytes_out = int(getattr(self, "_audio_bytes_out", 0) or 0) + max(0, int(nbytes))
        except Exception:
            pass
        try:
            import time as _time
            now = _time.monotonic()
            if now - float(getattr(self, "_speak_last_emit", 0.0) or 0.0) >= 2.0:
                self._speak_last_emit = now
                self.status_changed.emit("Speaking...", "active")
        except Exception:
            pass

    def _play_response_audio(self, data) -> bool:
        """Decode one audio payload and enqueue it. Returns True if heard-able.
        Dedupes: the SDK may surface the same bytes as top-level `data` AND per-part
        `inline_data`, and the server may resend chunks — replaying either sounds
        like echo/repeat. Recently-played digests (10s window) are skipped."""
        try:
            if isinstance(data, str):
                import base64
                data = base64.b64decode(data)
            raw = bytes(data) if not isinstance(data, (bytes, bytearray)) else bytes(data)
        except Exception as e:
            print(f"[GeminiLive] Audio decode error: {e}")
            return False
        if not raw:
            return True
        try:
            import hashlib as _hl
            import time as _time
            digest = _hl.sha1(raw).digest()
            now = _time.monotonic()
            seen = getattr(self, "_played_hashes", None)
            if seen is None:
                seen = []
                self._played_hashes = seen
            # Trim entries older than the window first (bounded list)
            try:
                self._played_hashes = [(d, t) for (d, t) in seen if now - t < 10.0][-32:]
                seen = self._played_hashes
            except Exception:
                pass
            for d, t in seen:
                if d == digest and now - t < 10.0:
                    print("[GeminiLive] Duplicate reply chunk skipped (echo guard)")
                    return True
            seen.append((digest, now))
            self._played_hashes = seen[-32:]
        except Exception:
            pass
        try:
            ok = self.audio.play_audio_chunk(raw)
        except Exception as e:
            print(f"[GeminiLive] Audio playback error: {e}")
            return False
        if ok:
            self._on_spoken_audio(len(raw))
        else:
            try:
                self.error_occurred.emit("Speaker error: dropping reply audio. Check speaker.")
                self.status_changed.emit("Speaker issue — reply dropped", "warn")
            except Exception:
                pass
        return bool(ok)

    async def _receive_companion_loop(self):
        try:
            while self._is_active and self.session:
                async for response in self.session.receive():
                    if not self._is_active:
                        break
                    try:
                        self._handle_companion_response(response)
                    except Exception as e:
                        print(f"[GeminiLive] Companion response error: {e}")
                    usage = getattr(response, "usage_metadata", None)
                    if usage:
                        try:
                            total = getattr(usage, "total_token_count", None)
                            if total:
                                self._session_tokens = int(total)
                                self.token_usage_updated.emit(self._session_tokens, self.MAX_CONTEXT_TOKENS)
                        except Exception:
                            pass
        except asyncio.CancelledError:
            pass
        except Exception as e:
            if self._is_active:
                print(f"[GeminiLive] Companion receive error: {e}")
                await self._handle_failover(e, "companion")

    def _handle_companion_response(self, response):
        """Route one Live response: audio -> speaker, text -> status (never silent)."""
        # Tool calls (typeTextAtCursor) can arrive top-level or inside server_content.
        # Schedule async handler without blocking the audio path.
        try:
            tc = getattr(response, "tool_call", None)
            if tc and getattr(tc, "function_calls", None):
                try:
                    loop = asyncio.get_running_loop()
                    loop.create_task(self.handle_type_text_tool_call(tc))
                except RuntimeError:
                    loop2 = getattr(self, "_loop", None)
                    if loop2 is not None:
                        try:
                            asyncio.run_coroutine_threadsafe(self.handle_type_text_tool_call(tc), loop2)
                        except Exception:
                            pass
        except Exception:
            pass
        # Top-level raw audio payload (SDK variant)
        try:
            raw_data = getattr(response, "data", None)
            if raw_data:
                self._play_response_audio(raw_data)
        except Exception:
            pass
        srv = getattr(response, "server_content", None)
        if srv is None:
            return
        # Transcribed speech (when output_audio_transcription negotiated)
        for attr in ("output_transcription", "input_transcription"):
            try:
                tr = getattr(srv, attr, None)
                txt = getattr(tr, "text", None) if tr is not None else None
                if txt and str(txt).strip():
                    self.status_changed.emit(f"{'Speaking' if attr == 'output_transcription' else 'Hearing'}...", "active")
            except Exception:
                pass
        model_turn = getattr(srv, "model_turn", None)
        if model_turn and getattr(model_turn, "parts", None):
            for part in model_turn.parts:
                try:
                    inline = getattr(part, "inline_data", None)
                    if inline and getattr(inline, "data", None):
                        self._play_response_audio(inline.data)
                except Exception as e:
                    print(f"[GeminiLive] Audio playback error: {e}")
                try:
                    if getattr(part, "text", None) and str(part.text).strip():
                        print(f"[GeminiLive] Companion text: {part.text[:120]}")
                        self.status_changed.emit("Speaking...", "active")
                except Exception:
                    pass
        # Server interruptions / turn-complete: return status to listening
        try:
            if getattr(srv, "interrupted", False):
                # Drop not-yet-played stale audio so the old turn never overlaps
                # the new one (sounds like repeat/cut glitching).
                try:
                    dropped = self.audio.flush_playback()
                    if dropped:
                        print(f"[GeminiLive] Flushed {dropped} stale audio chunks on interrupt")
                except Exception:
                    pass
                try:
                    self._played_hashes = []
                except Exception:
                    pass
                self.status_changed.emit("Listening...", "active")
            elif getattr(srv, "turn_complete", False):
                self._emit_companion_status()
        except Exception:
            pass
