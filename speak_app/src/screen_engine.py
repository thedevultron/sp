import io
import asyncio
from PIL import Image
import mss


class ScreenEngine:
    """Screen grabber yielding JPEG frames for multimodal companion vision.
    Fixed for HighDPI, multi-monitor, and resource cleanup.
    """

    def __init__(self, quality: int = 68, scale_factor: float = 0.6):
        self.quality = quality
        self.scale_factor = scale_factor
        self._sct = None
        self._is_capturing = False

    def start(self):
        if self._sct is None:
            try:
                self._sct = mss.mss()
            except Exception as e:
                print(f"[ScreenEngine] mss init error: {e}")
                self._sct = None
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

            buf = io.BytesIO()
            img.save(buf, format="JPEG", quality=self.quality, optimize=True)
            return buf.getvalue()
        except Exception as e:
            print(f"[ScreenEngine] capture error: {e}")
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
