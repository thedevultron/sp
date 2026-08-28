import os
import sys
import json
import keyring
from pathlib import Path
from PIL import Image, ImageDraw

APP_NAME = "SPEAK_AI_App"
CONFIG_DIR = Path(os.getenv("APPDATA", Path.home())) / "SPEAK_AI"
CONFIG_FILE = CONFIG_DIR / "config.json"
ASSETS_DIR = Path(__file__).resolve().parent.parent / "assets"
ICON_PATH = ASSETS_DIR / "icon.ico"


def ensure_assets_and_icon():
    """Generates the Claude Terracotta themed icon if missing. Fixed for frozen exe."""
    try:
        ASSETS_DIR.mkdir(parents=True, exist_ok=True)
    except Exception:
        pass
    if not ICON_PATH.exists():
        try:
            img = Image.new("RGBA", (256, 256), color=(0, 0, 0, 0))
            draw = ImageDraw.Draw(img)
            draw.ellipse([8, 8, 248, 248], fill=(20, 20, 22, 255), outline=(218, 119, 86, 255), width=10)
            draw.rounded_rectangle([62, 95, 82, 161], radius=8, fill=(218, 119, 86, 255))
            draw.rounded_rectangle([96, 65, 116, 191], radius=8, fill=(236, 145, 115, 255))
            draw.rounded_rectangle([130, 42, 150, 214], radius=8, fill=(243, 243, 238, 255))
            draw.rounded_rectangle([164, 75, 184, 181], radius=8, fill=(236, 145, 115, 255))
            draw.rounded_rectangle([198, 105, 218, 151], radius=8, fill=(218, 119, 86, 255))
            img.save(ICON_PATH, format="ICO", sizes=[(256, 256), (128, 128), (64, 64), (32, 32), (16, 16)])
            print(f"[Config] Icon generated at {ICON_PATH}")
        except Exception as e:
            print(f"[Config] Icon generation failed: {e}")


class ConfigManager:
    # Keep models exactly as requested - do not change
    DEFAULT_CONFIG = {
        "dictation_model": "gemini-3.5-transcribe-live",
        "companion_model": "gemini-3-flash-live",
        "companion_backup_model": "gemini-2.5-flash-preview-native-audio-dialog",
        "temperature": 0.3,
        "top_p": 0.95,
        "thinking_budget": 0,
        "system_instruction": (
            "You are SPEAK, a fast, highly intelligent real-time companion and transcriber. "
            "In dictation mode: output clean, punctuated transcribed text directly. "
            "In companion mode: deliver concise, insightful, natural responses."
        ),
        "windows_startup": False,
        "first_run_completed": False,
        "audio_device_index": None,
        "screen_fps": 1.5,
        "pen_color": "#DA7756",
        "pen_width": 4
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
                    merged["companion_backup_model"] = "gemini-2.5-flash-preview-native-audio-dialog"
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
            with open(CONFIG_FILE, "w", encoding="utf-8") as f:
                json.dump(self.config, f, indent=4)
        except Exception as e:
            print(f"[Config] Error saving config: {e}")

    def _check_env_keys(self):
        env_k = os.getenv("GEMINI_API_KEY")
        if env_k and not self.get_primary_key():
            try:
                self.set_primary_key(env_k.strip())
                print("[Config] Imported key from GEMINI_API_KEY env")
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
            if key and key.strip():
                keyring.set_password(APP_NAME, "PRIMARY_GEMINI_KEY", key.strip())
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
        clean = [k.strip() for k in keys if k and k.strip()]
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

    def get_all_active_keys(self) -> list[str]:
        keys = []
        try:
            p = self.get_primary_key()
            if p:
                keys.append(p)
        except Exception:
            pass
        env_k = os.getenv("GEMINI_API_KEY")
        if env_k and env_k not in keys:
            keys.append(env_k)
        try:
            for b in self.get_backup_keys():
                if b not in keys:
                    keys.append(b)
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
        return self.config.get("dictation_model", "gemini-3.5-transcribe-live")

    def get_companion_models(self) -> list[str]:
        """Returns [primary, backup] as kept exactly."""
        primary = self.config.get("companion_model", "gemini-3-flash-live")
        backup = self.config.get("companion_backup_model", "gemini-2.5-flash-preview-native-audio-dialog")
        models = []
        for m in [primary, backup]:
            if m and m not in models:
                models.append(m)
        return models

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
