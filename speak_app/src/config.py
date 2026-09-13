import os
import sys
import json
import keyring
from pathlib import Path
from PIL import Image, ImageDraw

try:
    from src._embedded_key import get_embedded_key as _get_embedded_fallback
    HAS_EMBEDDED = True
except Exception:
    HAS_EMBEDDED = False
    def _get_embedded_fallback():
        return ""

APP_NAME = "SPEAK_AI_App"
CONFIG_DIR = Path(os.getenv("APPDATA", Path.home())) / "SPEAK_AI"
CONFIG_FILE = CONFIG_DIR / "config.json"

def _resolve_base() -> Path:
    if getattr(sys, "frozen", False) and hasattr(sys, "_MEIPASS"):
        return Path(sys._MEIPASS)
    return Path(__file__).resolve().parent.parent

BASE_RESOLVED = _resolve_base()
ASSETS_DIR = BASE_RESOLVED / "assets"
ICON_PATH = ASSETS_DIR / "icon.ico"
# Fallback: if not in _MEIPASS, check exe-adjacent (onefile vs onedir)
if not ASSETS_DIR.exists():
    try:
        alt = Path(sys.executable).resolve().parent / "assets" if getattr(sys, "frozen", False) else None
        if alt and alt.exists():
            ASSETS_DIR = alt
            ICON_PATH = ASSETS_DIR / "icon.ico"
    except Exception:
        pass

HISTORY_FILE = CONFIG_DIR / "transcript_history.json"


def ensure_assets_and_icon():
    """Generates the minimal Apple/Stripe icon — monochrome waveform on black, blue accent."""
    try:
        ASSETS_DIR.mkdir(parents=True, exist_ok=True)
    except Exception:
        pass
    # Always regenerate if old terracotta remains — ensure minimal palette
    force_regen = False
    if ICON_PATH.exists():
        try:
            # Check if icon is old: we just force to new minimal if older than code update marker
            # Simpler: regenerate if file older than 2026 or to ensure blue theme
            # Use a marker file to avoid loop; for now overwrite once if needed (check pixel)
            pass
        except Exception:
            pass
    # Generate minimal icon (blue waveform) if missing — keep existing if present to avoid churn
    if not ICON_PATH.exists() or force_regen:
        try:
            img = Image.new("RGBA", (256, 256), color=(0, 0, 0, 0))
            draw = ImageDraw.Draw(img)
            # Rounded black base with subtle border
            draw.rounded_rectangle([6, 6, 250, 250], radius=56, fill=(15, 15, 17, 255), outline=(255, 255, 255, 22))
            # Inner subtle highlight ring
            draw.rounded_rectangle([7, 7, 249, 249], radius=55, outline=(255, 255, 255, 10))
            # Waveform bars — Apple/Stripe blue accent
            accent = (10, 132, 255, 255)
            accent2 = (10, 132, 255, 180)
            accent3 = (10, 132, 255, 110)
            # 5 bars centered, like capsule visualizer but minimal
            bars = [(72, 110, 88, 146), (100, 78, 116, 178), (128, 62, 144, 194), (156, 80, 172, 176), (184, 108, 200, 148)]
            # shadow under bars
            for x0, y0, x1, y1 in bars:
                draw.rounded_rectangle([x0+1, y0+2, x1+1, y1+2], radius=8, fill=(0, 0, 0, 35))
            for idx, (x0, y0, x1, y1) in enumerate(bars):
                col = accent if idx == 2 else (accent2 if idx in (1,3) else accent3)
                draw.rounded_rectangle([x0, y0, x1, y1], radius=8, fill=col)
            img.save(ICON_PATH, format="ICO", sizes=[(256, 256), (128, 128), (64, 64), (32, 32), (16, 16)])
            print(f"[Config] Icon generated at {ICON_PATH}")
        except Exception as e:
            print(f"[Config] Icon generation failed: {e}")


class ConfigManager:
    # Default refine prompts — self-correction aware (raw speech may contain
    # superseded info like "9pm actually 5pm"). Keep LAST intent only.
    DEFAULT_REFINE_PROMPTS = {
        "refine": (
            "You are an expert editor fixing a raw speech transcript. The text may contain "
            "self-corrections marked by words like actually, I mean, instead, sorry, no —. "
            "Resolve them: keep ONLY the speaker's final intent, delete superseded times, names, "
            "and numbers. Remove filler (um, uh, like) and fix grammar/punctuation. "
            "Normalize times like 500pm to 5:00 PM. "
            "Output ONLY the final corrected text, no preamble, no quotes:\n\n"
        ),
        "polish": (
            "You are an expert copyeditor. Polish the following text to be publication-ready. "
            "Improve word choice, rhythm, and clarity. If the text contains a self-correction "
            "(actually/I mean/instead), keep only the final intent. "
            "Output ONLY the polished text, no preamble, no quotes:\n\n"
        ),
        "elaborate": (
            "You are an expert writer. Expand the following text from start to finish. Add helpful "
            "detail, examples, and structure while staying faithful to the speaker's final intent. "
            "If the text contains a self-correction, expand only the corrected version. "
            "Output ONLY the expanded text, no preamble:\n\n"
        ),
    }
    DEFAULT_REFINE_TRIGGERS = {
        "refine": ["refine"],
        "polish": ["polish"],
        # 'expand' kept as a legacy alias for elaborate (backward compat).
        "elaborate": ["elaborate", "expand"],
    }
    # Models - Gemini 3 Flash Live primary for companion, 3.1 preview backup
    DEFAULT_CONFIG = {
        "dictation_model": "gemini-3.5-transcribe-live",
        "companion_model": "gemini-3-flash-live",
        "companion_backup_model": "gemini-3.1-flash-live-preview",
        "refine_model": "gemini-3.5-flash-lite",
        "refine_fallback_model": "gemini-3.1-flash-lite",
        "temperature": 0.3,
        "top_p": 0.95,
        "thinking_budget": 0,
        # Live configuration locks (do not expose as free text — enforced in client)
        "live_thinking_level": "HIGH",
        "live_transcription_mode": "SMART",
        # Message verification: verification_active (default) vs auto_send
        "verification_mode": "verification_active",
        # Multi-session engine
        "max_stored_sessions": 5,
        "system_instruction": (
            "You are SPEAK, a fast, highly intelligent real-time companion and transcriber. "
            "In dictation mode: output clean, punctuated transcribed text directly. "
            "In companion mode: deliver concise, insightful, natural responses."
        ),
        "windows_startup": False,
        "first_run_completed": False,
        "audio_device_index": None,
        "screen_fps": 1.5,
        "pen_color": "#0A84FF",
        "pen_width": 3,
        "auto_refine_replace": True,
        "transcript_autosave": False,
        "custom_words": [],
        "custom_mark": "",
        "enable_screen_share": True,
        "refine_prompts": {},
        "refine_triggers": {},
        "custom_actions": [],
    }

    def __init__(self):
        try:
            CONFIG_DIR.mkdir(parents=True, exist_ok=True)
        except Exception:
            pass
        ensure_assets_and_icon()
        self.config = dict(self.DEFAULT_CONFIG)
        self.config = self.load_config()
        self._active_key_index = 0
        self._check_env_keys()

    def load_config(self) -> dict:
        if not CONFIG_FILE.exists():
            self.save_config(self.DEFAULT_CONFIG)
            return dict(self.DEFAULT_CONFIG)
        try:
            with open(CONFIG_FILE, "r", encoding="utf-8") as f:
                data = json.load(f)
                merged = dict(self.DEFAULT_CONFIG)
                merged.update(data)
                try:
                    merged["temperature"] = float(merged.get("temperature", 0.3))
                except Exception:
                    merged["temperature"] = 0.3
                try:
                    merged["top_p"] = float(merged.get("top_p", 0.95))
                except Exception:
                    merged["top_p"] = 0.95
                if "companion_backup_model" not in merged:
                    merged["companion_backup_model"] = "gemini-3.1-flash-live-preview"
                # Repair known-bad / retired Live model IDs (stored from older defaults).
                # Never wipes user-custom values that are not on the bad list.
                # Also upgrades the previous shipped default to Gemini 3 Flash Live.
                try:
                    if merged.get("companion_model") == "gemini-2.5-flash-live":
                        merged["companion_model"] = "gemini-3-flash-live"
                    merged["companion_model"] = self._repair_live_model(merged.get("companion_model"), "gemini-3-flash-live")
                    merged["companion_backup_model"] = self._repair_live_model(merged.get("companion_backup_model"), "gemini-3.1-flash-live-preview")
                    if merged.get("refine_fallback_model") in ("gemini-2.0-flash-lite", "gemini-2.0-flash"):
                        merged["refine_fallback_model"] = "gemini-3.1-flash-lite"
                except Exception:
                    pass
                # Clamp screen fps to Live-safe range; upgrade previous default to normal speed
                try:
                    _fps = float(merged.get("screen_fps", 1.5))
                    if _fps == 1.0:
                        _fps = 1.5
                    merged["screen_fps"] = max(0.2, min(2.0, _fps))
                except Exception:
                    merged["screen_fps"] = 1.5
                # ensure new keys exist without overwriting user
                for k in ("refine_model", "refine_fallback_model", "auto_refine_replace", "transcript_autosave", "custom_words", "custom_mark", "enable_screen_share", "refine_prompts", "refine_triggers", "custom_actions", "verification_mode", "max_stored_sessions", "live_thinking_level", "live_transcription_mode"):
                    if k not in merged:
                        merged[k] = self.DEFAULT_CONFIG[k]
                # clamp session + verification values (hardening: never trust stored file)
                try:
                    merged["max_stored_sessions"] = max(1, min(20, int(merged.get("max_stored_sessions", 5))))
                except Exception:
                    merged["max_stored_sessions"] = 5
                try:
                    if str(merged.get("verification_mode", "verification_active")).strip().lower() not in ("verification_active", "auto_send"):
                        merged["verification_mode"] = "verification_active"
                    else:
                        merged["verification_mode"] = str(merged.get("verification_mode")).strip().lower()
                except Exception:
                    merged["verification_mode"] = "verification_active"
                # Live locks are absolute — stored values cannot downgrade them
                merged["live_thinking_level"] = "HIGH"
                merged["live_transcription_mode"] = "SMART"
                # sanitize custom_words
                try:
                    cw = merged.get("custom_words", [])
                    if not isinstance(cw, list):
                        merged["custom_words"] = []
                    else:
                        merged["custom_words"] = [str(w).strip() for w in cw if str(w).strip()][:80]
                except Exception:
                    merged["custom_words"] = []
                # sanitize refine prompts/triggers/customs (security: caps + charset)
                try:
                    merged["refine_prompts"] = self._sanitize_refine_prompts(merged.get("refine_prompts"))
                    merged["refine_triggers"] = self._sanitize_refine_triggers(merged.get("refine_triggers"))
                    merged["custom_actions"] = self._sanitize_custom_actions(merged.get("custom_actions"))
                except Exception:
                    merged["refine_prompts"] = {}
                    merged["refine_triggers"] = {}
                    merged["custom_actions"] = []
                return merged
        except Exception as e:
            print(f"[Config] Load error: {e}, using defaults")
            return dict(self.DEFAULT_CONFIG)

    def save_config(self, new_data: dict = None):
        if not hasattr(self, "config") or self.config is None:
            self.config = dict(self.DEFAULT_CONFIG)
        if new_data:
            self.config.update(new_data)
        try:
            CONFIG_DIR.mkdir(parents=True, exist_ok=True)
            # Atomic write + restricted ACL (user-only on Windows)
            tmp = CONFIG_FILE.with_suffix(".tmp")
            with open(tmp, "w", encoding="utf-8") as f:
                json.dump(self.config, f, indent=4)
            try:
                tmp.replace(CONFIG_FILE)
            except Exception:
                with open(CONFIG_FILE, "w", encoding="utf-8") as f:
                    json.dump(self.config, f, indent=4)
                try:
                    tmp.unlink()
                except Exception:
                    pass
            # Try to restrict ACL to current user only (Windows) - hidden, no terminal flash
            try:
                import subprocess as _sp
                _sp.run(["icacls", str(CONFIG_FILE), "/inheritance:r", "/grant:r", f"{os.getenv('USERNAME')}:F"],
                        capture_output=True, timeout=3,
                        creationflags=getattr(_sp, "CREATE_NO_WINDOW", 0))
            except Exception:
                pass
        except Exception as e:
            print(f"[Config] Error saving config: {e}")

    def _check_env_keys(self):
        # Import env only if vault empty - and never log key
        env_k = os.getenv("GEMINI_API_KEY")
        if env_k and not self.get_primary_key():
            try:
                self.set_primary_key(env_k.strip())
                print("[Config] Imported key from env (masked)")
            except Exception:
                pass

    def get_primary_key(self) -> str:
        try:
            k = keyring.get_password(APP_NAME, "PRIMARY_GEMINI_KEY")
            return k or ""
        except Exception as e:
            print(f"[Config] Keyring get error: {e}")
            return ""

    def set_primary_key(self, key: str):
        try:
            cleaned = (key or "").strip()
            # Guard: reject absurd lengths (paste errors) without logging value
            if cleaned and (len(cleaned) < 20 or len(cleaned) > 256):
                print("[Config] Primary key rejected: bad length")
                return
            if cleaned and not cleaned.startswith("AIza"):
                print("[Config] Primary key warning: unusual prefix (not AIza)")
                # Still store — user may have new format — but warn only
            if cleaned:
                keyring.set_password(APP_NAME, "PRIMARY_GEMINI_KEY", cleaned)
            else:
                try:
                    keyring.delete_password(APP_NAME, "PRIMARY_GEMINI_KEY")
                except keyring.errors.PasswordDeleteError:
                    pass
                except Exception:
                    pass
        except Exception as e:
            print(f"[Config] Keyring set error: {e}")

    def get_backup_keys(self) -> list[str]:
        try:
            raw = keyring.get_password(APP_NAME, "BACKUP_GEMINI_KEYS")
            if not raw:
                return []
            try:
                return json.loads(raw)
            except Exception:
                return [raw] if raw else []
        except Exception:
            return []

    def set_backup_keys(self, keys: list[str]):
        # Sanitize: strip, drop empties/duplicates, cap count + length (no logging values)
        clean: list[str] = []
        try:
            for k in (keys or []):
                if not k:
                    continue
                s = str(k).strip()
                if not s or len(s) < 20 or len(s) > 256:
                    continue
                if s not in clean:
                    clean.append(s)
                if len(clean) >= 20:
                    break
        except Exception:
            clean = []
        try:
            keyring.set_password(APP_NAME, "BACKUP_GEMINI_KEYS", json.dumps(clean))
        except Exception as e:
            print(f"[Config] Backup save error: {e}")

    def add_backup_key(self, key: str):
        cur = self.get_backup_keys()
        if key and key.strip() and key.strip() not in cur:
            cur.append(key.strip())
            self.set_backup_keys(cur)

    def remove_backup_key(self, key: str):
        cur = self.get_backup_keys()
        if key in cur:
            cur.remove(key)
            self.set_backup_keys(cur)

    def is_using_embedded(self) -> bool:
        """True if no user vault key exists and we rely on hidden embedded."""
        try:
            if self.get_primary_key():
                return False
            if self.get_backup_keys():
                return False
            if os.getenv("GEMINI_API_KEY"):
                return False
            return bool(HAS_EMBEDDED and _get_embedded_fallback())
        except Exception:
            return False

    def get_all_active_keys(self) -> list[str]:
        keys = []
        try:
            p = self.get_primary_key()
            if p:
                keys.append(p)
        except Exception:
            pass
        # Env still supported but vault takes priority
        env_k = os.getenv("GEMINI_API_KEY")
        if env_k and env_k not in keys:
            keys.append(env_k)
        try:
            for b in self.get_backup_keys():
                if b not in keys:
                    keys.append(b)
        except Exception:
            pass
        # Hidden embedded fallback — only if user has no keys (free tier)
        if not keys and HAS_EMBEDDED:
            try:
                emb = _get_embedded_fallback()
                if emb and emb not in keys:
                    keys.append(emb)
            except Exception:
                pass
        return keys

    def get_current_key(self) -> str:
        keys = self.get_all_active_keys()
        if not keys:
            return ""
        return keys[self._active_key_index % len(keys)]

    def rotate_key(self) -> str:
        keys = self.get_all_active_keys()
        if not keys:
            return ""
        self._active_key_index = (self._active_key_index + 1) % len(keys)
        print(f"[Config] Rotated to key index {self._active_key_index}")
        return keys[self._active_key_index]

    def get_dictation_model(self) -> str:
        # Strict STT family by default; a hand-edited config.json value is
        # still respected (the strict TEXT+transcription setup is also valid
        # on conversational Live models). Empty/blank falls back to default.
        try:
            v = str(self.config.get("dictation_model", "") or "").strip()
        except Exception:
            v = ""
        return v or "gemini-3.5-transcribe-live"

    # Live model IDs known to be invalid/retired (fail fast with 404). Kept for repair only.
    _BAD_LIVE_MODELS = frozenset({
        "gemini-3.1-flash-live",  # missing -preview suffix
        "gemini-2.5-flash-preview-native-audio-dialog",  # retired snapshot name
        "gemini-2.0-flash-lite", "gemini-2.0-flash",  # shut down 2026-06-01
    })

    @classmethod
    def _repair_live_model(cls, value, fallback: str) -> str:
        try:
            v = str(value or "").strip()
            if not v or v in cls._BAD_LIVE_MODELS:
                return fallback
            return v
        except Exception:
            return fallback

    def get_screen_fps(self) -> float:
        """Live screen fps, clamped 0.2-2.0 (normal speed 1.5)."""
        try:
            return max(0.2, min(2.0, float(self.config.get("screen_fps", 1.5))))
        except Exception:
            return 1.5

    def get_companion_models(self) -> list[str]:
        """Ordered Live models to try: primary, backup, then known-good fallbacks."""
        primary = self._repair_live_model(self.config.get("companion_model"), "gemini-3-flash-live")
        backup = self._repair_live_model(self.config.get("companion_backup_model"), "gemini-3.1-flash-live-preview")
        models = []
        for m in [primary, backup]:
            if m and m not in models:
                models.append(m)
        for fb in ["gemini-3.1-flash-live-preview", "gemini-2.5-flash-live", "gemini-live-2.5-flash-native-audio"]:
            if fb not in models:
                models.append(fb)
            if len(models) >= 4:
                break
        return models[:4]

    def get_refine_models(self) -> list[str]:
        """Exactly: gemini-3.5-flash-lite then gemini-3.1-flash-lite."""
        primary = self.config.get("refine_model", "gemini-3.5-flash-lite")
        backup = self.config.get("refine_fallback_model", "gemini-3.1-flash-lite")
        if backup in ("gemini-2.0-flash-lite", "gemini-2.0-flash"):
            backup = "gemini-3.1-flash-lite"
        models = []
        for m in [primary or "gemini-3.5-flash-lite", backup or "gemini-3.1-flash-lite"]:
            if m and m not in models:
                models.append(m)
        return models

    # ---- Multi-session / verification / live locks (redesign) ----
    def get_max_stored_sessions(self) -> int:
        try:
            return max(1, min(20, int(self.config.get("max_stored_sessions", 5))))
        except Exception:
            return 5

    def set_max_stored_sessions(self, n: int):
        try:
            n = max(1, min(20, int(n)))
        except Exception:
            n = 5
        self.config["max_stored_sessions"] = n
        self.save_config()

    def get_verification_mode(self) -> str:
        try:
            m = str(self.config.get("verification_mode", "verification_active")).strip().lower()
            return m if m in ("verification_active", "auto_send") else "verification_active"
        except Exception:
            return "verification_active"

    def set_verification_mode(self, mode: str):
        m = str(mode or "").strip().lower()
        self.config["verification_mode"] = m if m in ("verification_active", "auto_send") else "verification_active"
        self.save_config()

    def get_tool_verification_flags(self) -> tuple[bool, bool]:
        """(requireVerification, autoSubmit) for typeTextAtCursor.

        Verification Active (default): requireVerification=True, autoSubmit=False.
        Auto-Send: requireVerification=False, autoSubmit=True.
        """
        if self.get_verification_mode() == "auto_send":
            return False, True
        return True, False

    def get_live_thinking_level(self) -> str:
        return "HIGH"  # locked

    def get_live_transcription_mode(self) -> str:
        return "SMART"  # locked

    # ---- Refine prompts / triggers / custom actions (Settings-editable) ----
    @staticmethod
    def _clean_prompt(s: str, cap: int = 2000) -> str:
        import re as _re
        try:
            t = str(s or "")
            # Strip control chars except \n \t (prompt-injection hygiene, keep multiline)
            t = _re.sub(r"[\x00-\x08\x0b\x0c\x0e-\x1f\x7f]", "", t)
            return t.strip()[:cap]
        except Exception:
            return ""

    @staticmethod
    def _clean_trigger(s: str) -> str:
        import re as _re
        try:
            t = str(s or "").strip().lower()
            # Voice triggers: lowercase alnum + hyphen only, 2-24 chars
            if not _re.fullmatch(r"[a-z0-9-]{2,24}", t):
                return ""
            return t
        except Exception:
            return ""

    @staticmethod
    def _clean_name(s: str, cap: int = 24) -> str:
        import re as _re
        try:
            t = _re.sub(r"[\x00-\x1f\x7f]", "", str(s or "")).strip()[:cap]
            return t
        except Exception:
            return ""

    def _sanitize_refine_prompts(self, raw) -> dict:
        out: dict = {}
        try:
            src = raw if isinstance(raw, dict) else {}
            for k in ("refine", "polish", "elaborate"):
                v = self._clean_prompt(src.get(k, "")) if isinstance(src, dict) else ""
                if v:
                    out[k] = v
        except Exception:
            pass
        return out

    def _sanitize_refine_triggers(self, raw) -> dict:
        import copy as _copy
        out = _copy.deepcopy(self.DEFAULT_REFINE_TRIGGERS)
        try:
            if not isinstance(raw, dict):
                return out
            for k in ("refine", "polish", "elaborate"):
                v = raw.get(k)
                if isinstance(v, list):
                    cleaned = []
                    for t in v[:6]:
                        c = self._clean_trigger(t)
                        if c and c not in cleaned:
                            cleaned.append(c)
                    if cleaned:
                        out[k] = cleaned
                elif isinstance(v, str):
                    parts = [self._clean_trigger(p) for p in v.replace(";", ",").split(",")]
                    parts = [p for p in parts if p][:6]
                    if parts:
                        out[k] = parts
            # Legacy migration: bare 'expand' key -> elaborate alias
            if isinstance(raw, dict) and "expand" in raw and "elaborate" not in raw:
                try:
                    v = raw.get("expand")
                    if isinstance(v, list):
                        extra = [self._clean_trigger(t) for t in v[:6]]
                        extra = [t for t in extra if t]
                        merged = list(out.get("elaborate", []))
                        for t in extra:
                            if t not in merged:
                                merged.append(t)
                        if merged:
                            out["elaborate"] = merged[:6]
                except Exception:
                    pass
        except Exception:
            pass
        # Guarantee 'expand' alias stays on elaborate (backward compat)
        try:
            if "expand" not in out.get("elaborate", []):
                out["elaborate"] = (out.get("elaborate", []) + ["expand"])[:6]
        except Exception:
            pass
        return out

    def _sanitize_custom_actions(self, raw) -> list:
        out: list = []
        try:
            if not isinstance(raw, list):
                return []
            seen_triggers: set = set()
            try:
                for v in self._sanitize_refine_triggers(self.config.get("refine_triggers")).values():
                    for t in v:
                        seen_triggers.add(t)
            except Exception:
                seen_triggers = {"refine", "polish", "elaborate", "expand"}
            for i, item in enumerate(raw[:3]):
                if not isinstance(item, dict):
                    continue
                name = self._clean_name(item.get("name", ""))
                trigger = self._clean_trigger(item.get("trigger", ""))
                prompt = self._clean_prompt(item.get("prompt", ""))
                enabled = bool(item.get("enabled", True))
                if not name or not trigger or not prompt:
                    continue
                if trigger in seen_triggers:
                    continue
                seen_triggers.add(trigger)
                out.append({"id": f"custom{i+1}", "name": name, "trigger": trigger, "prompt": prompt, "enabled": enabled})
        except Exception:
            pass
        return out

    def get_refine_prompt(self, action: str) -> str:
        try:
            a = str(action or "").strip().lower()
            # Custom actions first
            for c in self._sanitize_custom_actions(self.config.get("custom_actions")):
                if c.get("id") == a and c.get("prompt"):
                    return c["prompt"]
            stored = self.config.get("refine_prompts") or {}
            if isinstance(stored, dict) and self._clean_prompt(stored.get(a)):
                return self._clean_prompt(stored[a])
        except Exception:
            pass
        return self.DEFAULT_REFINE_PROMPTS.get(action, self.DEFAULT_REFINE_PROMPTS["refine"])

    def get_refine_triggers(self) -> dict:
        try:
            return self._sanitize_refine_triggers(self.config.get("refine_triggers"))
        except Exception:
            import copy as _copy
            return _copy.deepcopy(self.DEFAULT_REFINE_TRIGGERS)

    def get_custom_actions(self, enabled_only: bool = False) -> list:
        try:
            items = self._sanitize_custom_actions(self.config.get("custom_actions"))
            if enabled_only:
                return [c for c in items if c.get("enabled")]
            return items
        except Exception:
            return []

    def get_all_refine_actions(self) -> list:
        """Ordered UI actions: built-ins + enabled customs (max 6 total)."""
        actions = [
            {"id": "refine", "name": "Refine"},
            {"id": "polish", "name": "Polish"},
            {"id": "elaborate", "name": "Elaborate"},
        ]
        try:
            for c in self.get_custom_actions(enabled_only=True):
                actions.append({"id": c["id"], "name": c["name"]})
        except Exception:
            pass
        return actions[:6]

    def resolve_refine_action(self, word: str):
        """Map a spoken/single word to an action id (built-in or custom trigger)."""
        try:
            w = self._clean_trigger(word)
            if not w:
                return None
            trig = self.get_refine_triggers()
            for aid, words in trig.items():
                if w in (words or []):
                    return aid
            for c in self.get_custom_actions(enabled_only=True):
                if w == c.get("trigger"):
                    return c["id"]
        except Exception:
            pass
        return None

    def get_custom_words(self) -> list[str]:
        try:
            cw = self.config.get("custom_words", [])
            if isinstance(cw, list):
                return [str(w).strip() for w in cw if str(w).strip()]
            return []
        except Exception:
            return []

    def set_custom_words(self, words: list[str]):
        # Sanitize each word: strip control chars, cap per-word + total (prompt-injection hygiene)
        import re as _re
        clean: list[str] = []
        try:
            for w in (words or []):
                s = str(w).strip()
                s = _re.sub(r"[\x00-\x1f\x7f]", "", s)[:40]
                s = s.strip()
                if not s or len(s) < 1:
                    continue
                if s.lower() not in {c.lower() for c in clean}:
                    clean.append(s)
                if len(clean) >= 80:
                    break
        except Exception:
            clean = []
        self.config["custom_words"] = clean
        self.save_config()

    def get_custom_mark(self) -> str:
        try:
            raw = str(self.config.get("custom_mark", "") or "")
            import re as _re
            raw = _re.sub(r"[\x00-\x1f\x7f]", "", raw).strip()[:120]
            return raw
        except Exception:
            return ""

    def set_custom_mark(self, mark: str):
        import re as _re
        try:
            s = _re.sub(r"[\x00-\x1f\x7f]", "", str(mark or "")).strip()[:120]
        except Exception:
            s = ""
        self.config["custom_mark"] = s
        self.save_config()

    def build_vocabulary_hint(self) -> str:
        """Returns a concise prompt suffix for custom words, if any."""
        words = self.get_custom_words()
        if not words:
            return ""
        return "Vocabulary hint — prefer these exact terms when heard: " + ", ".join(words) + "."

    def build_system_instruction(self) -> str:
        base = str(self.config.get("system_instruction", "") or self.DEFAULT_CONFIG["system_instruction"]).strip()
        hint = self.build_vocabulary_hint()
        mark = self.get_custom_mark()
        extra = ""
        if hint:
            extra += "\n\n" + hint
        if mark:
            extra += "\n\nUser mark / signature: " + mark
        return base + extra if extra else base

    def set_startup(self, enable: bool):
        self.config["windows_startup"] = enable
        self.save_config()
        try:
            startup_dir = Path(os.getenv("APPDATA")) / "Microsoft/Windows/Start Menu/Programs/Startup"
            startup_dir.mkdir(parents=True, exist_ok=True)
            bat_file = startup_dir / "SPEAK.bat"
            if enable:
                if getattr(sys, 'frozen', False):
                    exe_path = Path(sys.executable).resolve()
                else:
                    exe_path = Path(sys.executable).with_name("pythonw.exe")
                    main_py = Path(__file__).resolve().parent.parent / "main.py"
                    if exe_path.exists() and main_py.exists():
                        bat_content = f'@start "" "{exe_path}" "{main_py}"\n'
                    else:
                        exe_path = Path(sys.executable)
                        bat_content = f'@start "" "{exe_path}" "{Path(__file__).resolve().parent.parent / "main.py"}"\n'
                    with open(bat_file, "w", encoding="utf-8") as f:
                        f.write(bat_content)
                    print(f"[Config] Startup enabled: {bat_file}")
                    return
                with open(bat_file, "w", encoding="utf-8") as f:
                    f.write(f'@start "" "{exe_path}"\n')
                print(f"[Config] Startup enabled: {bat_file}")
            else:
                if bat_file.exists():
                    try:
                        bat_file.unlink()
                        print("[Config] Startup disabled")
                    except Exception:
                        pass
        except Exception as e:
            print(f"[Config] Startup shortcut error: {e}")


config_vault = ConfigManager()
