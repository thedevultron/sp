import io
import asyncio
from PIL import Image
import mss


class ScreenEngine:
    """Screen grabber yielding JPEG frames for multimodal companion vision.
    Fixed for HighDPI, multi-monitor, and resource cleanup.

    Permission handshake: every start()/capture path runs through the
    OS permission interceptor FIRST (see src/permission_manager.py).
    If permission is pending/denied, capture returns b"" and surfaces the
    diagnostic for the inline banner instead of silently failing.
    """

    def __init__(self, quality: int = 68, scale_factor: float = 0.6):
        self.quality = quality
        self.scale_factor = scale_factor
        self._sct = None
        self._is_capturing = False
        self._perm_error = ""
        self._perm_status = "unknown"

    # -- Permission interceptor (must run before mss / worker) --
    def check_permission(self) -> str:
        """Programmatically check OS screen-recording grant. Never raises."""
        try:
            from src.permission_manager import permission_manager
            st = permission_manager.check_permission()
            self._perm_status = st
            self._perm_error = permission_manager.last_error
            return st
        except Exception as e:
            self._perm_status = "pending"
            self._perm_error = str(e)[:200]
            return "pending"

    def request_permission(self) -> str:
        """Trigger native OS authorization request directly + re-check."""
        try:
            from src.permission_manager import permission_manager
            st = permission_manager.request_permission()
            self._perm_status = st
            self._perm_error = permission_manager.last_error
            return st
        except Exception as e:
            self._perm_status = "pending"
            self._perm_error = str(e)[:200]
            return "pending"

    def permission_diagnostic(self) -> dict:
        try:
            from src.permission_manager import permission_manager
            return permission_manager.get_diagnostic()
        except Exception:
            return {
                "status": self._perm_status,
                "last_error": self._perm_error,
                "banner_visible": self._perm_status in ("pending", "denied"),
                "banner_text": self._perm_error or "Screen permission check needed.",
            }

    def start(self):
        # Permission interceptor BEFORE mss init
        try:
            st = self.check_permission()
            if st in ("denied", "pending"):
                print(f"[ScreenEngine] start blocked — permission {st}: {self._perm_error[:120]}")
                # Do not init mss; worker will idle and banner shows retry.
                # Still allow _is_capturing so retry can proceed after grant.
                self._is_capturing = False
                return
        except Exception as e:
            print(f"[ScreenEngine] permission pre-check note: {e}")
        if self._sct is None:
            try:
                self._sct = mss.mss()
            except Exception as e:
                print(f"[ScreenEngine] mss init error: {e}")
                self._sct = None
                self._perm_status = "pending"
                self._perm_error = str(e)[:200]
                return
        self._is_capturing = True

    def stop(self):
        self._is_capturing = False
        if self._sct:
            try:
                self._sct.close()
            except Exception:
                pass
            self._sct = None

    def capture_frame_bytes(self, monitor_index: int = 1) -> bytes:
        # Permission gate: never attempt silent grab when denied/pending
        try:
            if getattr(self, "_perm_status", "unknown") in ("denied", "pending"):
                return b""
        except Exception:
            pass
        # Lazy init if needed
        if not self._sct:
            try:
                self._sct = mss.mss()
            except Exception as e:
                print(f"[ScreenEngine] capture init error: {e}")
                return b""

        try:
            monitors = self._sct.monitors
            if not monitors or len(monitors) <= 1:
                target = monitors[1] if len(monitors) > 1 else monitors[0]
            else:
                target = monitors[monitor_index if monitor_index < len(monitors) else 1]

            sct_img = self._sct.grab(target)
            img = Image.frombytes("RGB", sct_img.size, sct_img.bgra, "raw", "BGRX")

            if self.scale_factor != 1.0:
                new_size = (int(img.width * self.scale_factor), int(img.height * self.scale_factor))
                # Clamp minimum size to avoid tiny images
                new_size = (max(640, new_size[0]), max(360, new_size[1]))
                img = img.resize(new_size, Image.Resampling.BILINEAR)
            # Cap pixels for Live uplink (1280w max) — keeps frames fast on HiDPI/4K.
            # NOTE: no optimize=True (CPU-heavy); caller runs this off the event loop.
            try:
                if img.width > 1280:
                    h = max(360, int(img.height * (1280.0 / img.width)))
                    img = img.resize((1280, h), Image.Resampling.BILINEAR)
            except Exception:
                pass

            buf = io.BytesIO()
            img.save(buf, format="JPEG", quality=self.quality, optimize=False)
            # success clears pending flag
            try:
                self._perm_status = "granted"
                self._perm_error = ""
            except Exception:
                pass
            return buf.getvalue()
        except Exception as e:
            print(f"[ScreenEngine] capture error: {e}")
            try:
                low = str(e).lower()
                if any(k in low for k in ("denied", "not allowed", "access is denied", "unauthorized")):
                    self._perm_status = "denied"
                else:
                    self._perm_status = "pending"
                self._perm_error = str(e)[:200]
            except Exception:
                pass
            return b""

    async def stream_frames(self, fps: float = 1.5):
        self.start()
        interval = 1.0 / max(0.2, min(5.0, fps))  # clamp 0.2-5 fps
        while self._is_capturing:
            frame_bytes = self.capture_frame_bytes()
            if frame_bytes:
                yield frame_bytes
            await asyncio.sleep(interval)
        # Ensure cleanup when loop exits
        self.stop()
