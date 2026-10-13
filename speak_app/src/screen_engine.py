import io
import time
import asyncio
from PIL import Image
import mss


class ScreenEngine:
    """Screen grabber yielding JPEG frames for multimodal companion vision.
    Fixed for HighDPI, multi-monitor, and resource cleanup.

    Permission handshake: start() runs through the OS permission
    interceptor FIRST (see src/permission_manager.py) so the banner can
    offer Grant Permission. capture_frame_bytes() NEVER latches a stale
    denied/pending forever — it re-checks (throttled) so one transient
    failure can't blank the whole session.

    Targeting: grabs the monitor under the mouse cursor (the screen the
    user is actually looking at), falling back to primary.
    """

    def __init__(self, quality: int = 72, scale_factor: float = 0.6):
        self.quality = quality
        self.scale_factor = scale_factor
        self._sct = None
        self._is_capturing = False
        self._perm_error = ""
        self._perm_status = "unknown"
        self._last_perm_retry_ts = 0.0
        self._last_frame_hash = None
        self.last_frame_info = ""

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
        # NOTE: no shared mss instance here on purpose — every capture opens
        # its own (see _new_mss). A shared handle goes stale across threads.
        self._is_capturing = True

    def stop(self):
        self._is_capturing = False
        if self._sct:
            try:
                self._sct.close()
            except Exception:
                pass
            self._sct = None

    def _new_mss(self):
        """Fresh mss instance PER CALL — mss handles live in thread-local
        storage, so a shared instance crashes with '_thread._local ... has no
        attribute srcdc' when the executor pool touches it from another
        thread. mss() init costs ~1-5 ms; at ~1 fps capture it is negligible
        and makes every capture thread-safe by construction."""
        try:
            import mss as _mss
            try:
                return _mss.MSS()
            except Exception:
                return _mss.mss()
        except Exception:
            return None

    def _active_monitor(self, sct=None):
        """Monitor under the mouse cursor (active screen), else primary.
        Uses the caller-supplied per-call instance (thread-safe)."""
        try:
            monitors = (sct.monitors if sct is not None else None) or []
        except Exception:
            monitors = []
        if not monitors:
            return None
        if len(monitors) <= 2:
            # monitors[0] = virtual all-monitors; [1] = primary
            return monitors[1] if len(monitors) > 1 else monitors[0]
        # Multi-monitor: pick the monitor containing the cursor
        try:
            import ctypes
            pt = ctypes.wintypes.POINT()
            ctypes.windll.user32.GetCursorPos(ctypes.byref(pt))
            cx, cy = int(pt.x), int(pt.y)
            for m in monitors[1:]:
                try:
                    if m["left"] <= cx < m["left"] + m["width"] and m["top"] <= cy < m["top"] + m["height"]:
                        return m
                except Exception:
                    continue
        except Exception:
            pass
        return monitors[1]

    def _maybe_refresh_permission(self):
        """Throttled re-check so a stale pending/denied can't blank forever."""
        try:
            if getattr(self, "_perm_status", "unknown") not in ("denied", "pending"):
                return
            now = time.monotonic()
            if now - float(getattr(self, "_last_perm_retry_ts", 0.0) or 0.0) < 5.0:
                return
            self._last_perm_retry_ts = now
            self.check_permission()
        except Exception:
            pass

    @staticmethod
    def frame_changed(thumb_a, thumb_b, threshold: int = 12) -> bool:
        """Cheap sudden-change detector on 32x18 grayscale thumbnails.
        Returns True when mean absolute pixel difference >= threshold (0-255).
        Never raises — unknown means 'changed' (send, don't drop)."""
        try:
            if thumb_a is None or thumb_b is None:
                return True
            if len(thumb_a) != len(thumb_b) or not thumb_a:
                return True
            diff = sum(abs(a - b) for a, b in zip(thumb_a, thumb_b)) / len(thumb_a)
            return diff >= threshold
        except Exception:
            return True

    def capture_frame_bytes(self, monitor_index: int = -1) -> bytes:
        # Retry a stale gate (throttled) instead of returning blank forever
        self._maybe_refresh_permission()
        try:
            if getattr(self, "_perm_status", "unknown") in ("denied", "pending"):
                return b""
        except Exception:
            pass
        # Per-call mss instance (thread-safe by construction — never share
        # one handle across executor threads; see _new_mss).
        sct = self._new_mss()
        if sct is None:
            try:
                self._perm_status = "pending"
                self._perm_error = "screen backend unavailable"
            except Exception:
                pass
            return b""

        try:
            if monitor_index is None or int(monitor_index) < 0:
                target = self._active_monitor(sct)
            else:
                monitors = sct.monitors
                if not monitors or len(monitors) <= 1:
                    target = monitors[1] if len(monitors) > 1 else monitors[0]
                else:
                    target = monitors[monitor_index if monitor_index < len(monitors) else 1]
            if not target:
                return b""

            sct_img = sct.grab(target)
            img = Image.frombytes("RGB", sct_img.size, sct_img.bgra, "raw", "BGRX")

            if self.scale_factor != 1.0:
                new_size = (int(img.width * self.scale_factor), int(img.height * self.scale_factor))
                # Clamp minimum size to avoid tiny images
                new_size = (max(640, new_size[0]), max(360, new_size[1]))
                img = img.resize(new_size, Image.Resampling.BILINEAR)
            # Cap pixels for Live uplink (1280w max) — keeps frames fast on HiDPI/4K.
            # Frame token cost follows Settings screen detail (Gemini 3:
            # MEDIUM 560 / HIGH 1120 tokens per frame).
            # NOTE: no optimize=True (CPU-heavy); caller runs this off the event loop.
            try:
                if img.width > 1280:
                    h = max(360, int(img.height * (1280.0 / img.width)))
                    img = img.resize((1280, h), Image.Resampling.BILINEAR)
            except Exception:
                pass

            buf = io.BytesIO()
            img.save(buf, format="JPEG", quality=self.quality, optimize=False)
            try:
                self.last_frame_info = f"{img.width}x{img.height} q{self.quality}"
            except Exception:
                pass
            # success clears pending flag
            try:
                self._perm_status = "granted"
                self._perm_error = ""
            except Exception:
                pass
            try:
                return buf.getvalue()
            finally:
                try:
                    sct.close()
                except Exception:
                    pass
        except Exception as e:
            try:
                sct.close()
            except Exception:
                pass
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

    def capture_frame(self, monitor_index: int = -1) -> tuple:
        """(jpeg_bytes, thumb) — thumb is a 32x18 grayscale bytes sample for
        sudden-change detection. jpeg is b"" when capture is unavailable."""
        jpeg = self.capture_frame_bytes(monitor_index=monitor_index)
        if not jpeg:
            return b"", None
        try:
            img = Image.open(io.BytesIO(jpeg)).convert("L").resize((32, 18), Image.Resampling.BILINEAR)
            return jpeg, img.tobytes()
        except Exception:
            return jpeg, None

    async def stream_frames(self, fps: float = 3.0):
        self.start()
        interval = 1.0 / max(0.2, min(15.0, fps))  # clamp 0.2-15 fps
        while self._is_capturing:
            frame_bytes = self.capture_frame_bytes()
            if frame_bytes:
                yield frame_bytes
            await asyncio.sleep(interval)
        # Ensure cleanup when loop exits
        self.stop()
