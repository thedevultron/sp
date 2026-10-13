import asyncio
import queue
import threading
import time
import numpy as np
import sounddevice as sd
from PySide6.QtCore import QObject, Signal


class AudioEngine(QObject):
    """Audio stream processor with RMS calculation and auto-gain.
    Fixed for Python 3.14 / sounddevice / asyncio compatibility.
    """

    amplitude_changed = Signal(float)  # Emits normalized amplitude (0.0 to 1.0)
    gemini_output_amplitude = Signal(float)

    def __init__(self, sample_rate: int = 16000, chunk_size: int = 512):
        super().__init__()
        self.sample_rate = sample_rate
        self.chunk_size = chunk_size
        self._stream = None
        self._output_stream = None
        self._is_recording = False
        self._audio_queue: asyncio.Queue = asyncio.Queue(maxsize=200)
        self._loop = None
        # Non-blocking playback: producer (event loop) -> queue -> worker thread (blocking write).
        # Sized for ~25s of 24kHz mono headroom so bursts never cut audio (drop-oldest is last resort).
        self._play_queue: queue.Queue = queue.Queue(maxsize=256)
        self._play_thread: threading.Thread | None = None
        self._play_stop = threading.Event()
        self._play_drop_warns = 0
        self._play_start_warned = False
        # Monotonic timestamp of the last speaker write (feedback guard).
        self._last_play_ts = 0.0

    def set_loop(self, loop):
        self._loop = loop
        # Re-create queue bound to this loop if needed (py 3.14), bounded
        try:
            self._audio_queue = asyncio.Queue(maxsize=200)
        except Exception:
            pass

    @staticmethod
    def get_input_devices():
        devices = []
        try:
            for idx, dev in enumerate(sd.query_devices()):
                if dev.get("max_input_channels", 0) > 0:
                    name = dev.get("name", f"Microphone {idx}")
                    devices.append((idx, name))
        except Exception as e:
            print(f"[AudioEngine] Device query error: {e}")
        return devices

    def _audio_callback(self, indata, frames, time_info, status):
        if status:
            # Don't spam on overflow
            pass
        try:
            # Python 3.14 / CFFI buffer fix: indata is cffi buffer -> bytes
            # bytes(indata) works for numpy/raw, fallback to tobytes
            try:
                raw_bytes = bytes(indata)
            except Exception:
                try:
                    raw_bytes = indata.tobytes()
                except Exception:
                    raw_bytes = bytes(bytearray(indata))

            if len(raw_bytes) == 0:
                return

            # RMS for visualizer
            try:
                audio_data = np.frombuffer(raw_bytes, dtype=np.int16)
            except Exception:
                audio_data = np.array([], dtype=np.int16)

            if len(audio_data) == 0:
                return

            rms = float(np.sqrt(np.mean(audio_data.astype(np.float32) ** 2)))

            if rms < 55.0:
                norm = 0.05
            else:
                norm = min(1.0, float((rms - 55.0) / 4000.0) + 0.15)

            # Emit on Qt thread
            try:
                self.amplitude_changed.emit(norm)
            except Exception:
                pass

            if self._loop and self._is_recording:
                try:
                    # Bounded queue: drop oldest if full
                    if self._audio_queue.qsize() >= 190:
                        try:
                            self._audio_queue.get_nowait()
                        except Exception:
                            pass
                    if self._loop.is_running():
                        self._loop.call_soon_threadsafe(self._audio_queue.put_nowait, raw_bytes)
                    else:
                        try:
                            self._audio_queue.put_nowait(raw_bytes)
                        except Exception:
                            pass
                except Exception:
                    pass
        except Exception as e:
            print(f"[AudioEngine] Callback error: {e}")

    def start_recording(self, device_index=None) -> bool:
        """Start mic capture. Returns True when actually recording."""
        if self._is_recording:
            return True
        # Drain queue safely (fix QueueEmpty bug - use queue.Empty / asyncio.QueueEmpty)
        while True:
            try:
                if self._audio_queue.empty():
                    break
                self._audio_queue.get_nowait()
            except (queue.Empty, asyncio.QueueEmpty, asyncio.queues.QueueEmpty, Exception):
                break

        self._is_recording = True
        try:
            # Validate device_index
            if device_index is not None:
                try:
                    devs = sd.query_devices()
                    if device_index < 0 or device_index >= len(devs):
                        print(f"[AudioEngine] Invalid device {device_index}, falling back to default")
                        device_index = None
                except Exception:
                    device_index = None

            self._stream = sd.RawInputStream(
                samplerate=self.sample_rate,
                blocksize=self.chunk_size,
                device=device_index,
                channels=1,
                dtype="int16",
                callback=self._audio_callback
            )
            self._stream.start()
            print(f"[AudioEngine] Recording started on device={device_index}")
            return True
        except Exception as e:
            print(f"[AudioEngine] Recording start error: {e}")
            self._is_recording = False
            # Try fallback to default device
            if device_index is not None:
                print("[AudioEngine] Retrying with default device...")
                try:
                    self._stream = sd.RawInputStream(
                        samplerate=self.sample_rate,
                        blocksize=self.chunk_size,
                        device=None,
                        channels=1,
                        dtype="int16",
                        callback=self._audio_callback
                    )
                    self._stream.start()
                    self._is_recording = True
                    print("[AudioEngine] Fallback recording started")
                    return True
                except Exception as e2:
                    print(f"[AudioEngine] Fallback also failed: {e2}")
                    self._is_recording = False
            return False

    def stop_recording(self):
        self._is_recording = False
        if self._stream:
            try:
                self._stream.stop()
                self._stream.close()
            except Exception:
                pass
            self._stream = None
        try:
            self.amplitude_changed.emit(0.0)
        except Exception:
            pass

    async def get_audio_chunk(self, timeout: float | None = None) -> bytes:
        """Next mic chunk. timeout=None blocks (legacy); pass seconds to detect a dead mic."""
        if timeout is None:
            return await self._audio_queue.get()
        try:
            return await asyncio.wait_for(self._audio_queue.get(), timeout=timeout)
        except asyncio.TimeoutError:
            raise

    def start_playback_stream(self, output_sample_rate: int = 24000) -> bool:
        """Start speaker output + worker thread. Returns True only when audible path is live."""
        if self._output_stream is not None:
            try:
                if self._output_stream.active:
                    self._ensure_play_thread()
                    return True
            except Exception:
                pass
            # Recreate if inactive
            self.stop_playback_stream()
        try:
            self._output_stream = sd.RawOutputStream(
                samplerate=output_sample_rate,
                channels=1,
                dtype="int16",
                blocksize=1024
            )
            self._output_stream.start()
            self._play_start_warned = False
            self._ensure_play_thread()
            print("[AudioEngine] Playback stream started")
            return True
        except Exception as e:
            print(f"[AudioEngine] Playback start error: {e}")
            self._output_stream = None
            return False

    def _ensure_play_thread(self):
        """Idempotent worker starter, pinned to the current stream.

        If a stale worker from a previous stream is still alive, it is asked
        to stop and reaped (briefly) before a fresh worker starts — two
        workers must never write to two devices at once (overlap = garble).
        """
        try:
            cur = self._output_stream
            th = self._play_thread
            if th is not None and th.is_alive():
                try:
                    pinned = getattr(th, "_pinned_stream", None)
                except Exception:
                    pinned = None
                if pinned is cur:
                    return
                try:
                    self._play_stop.set()
                    th.join(timeout=1.0)
                except Exception:
                    pass
                self._play_thread = None
            self._play_stop.clear()
            # Drain stale audio so a restart never blurts old speech
            try:
                while True:
                    self._play_queue.get_nowait()
            except queue.Empty:
                pass
            except Exception:
                pass
            t = threading.Thread(target=self._play_worker, name="speak-playback",
                                 args=(cur,), daemon=True)
            try:
                t._pinned_stream = cur
            except Exception:
                pass
            self._play_thread = t
            t.start()
        except Exception as e:
            print(f"[AudioEngine] Play worker start error: {e}")

    def _play_worker(self, stream=None):
        """Dedicated thread: blocking stream.write must never run on the asyncio loop."""
        while not self._play_stop.is_set():
            try:
                cur = self._output_stream
                if stream is not None and cur is not None and cur is not stream:
                    break  # restarted elsewhere; the fresh worker owns the new stream
                if stream is None:
                    stream = cur
                    try:
                        threading.current_thread()._pinned_stream = stream
                    except Exception:
                        pass
            except Exception:
                pass
            try:
                raw = self._play_queue.get(timeout=0.25)
            except queue.Empty:
                continue
            except Exception:
                continue
            try:
                if stream is None:
                    continue
                try:
                    if not stream.active:
                        continue
                except Exception:
                    continue
                stream.write(raw)
                try:
                    self._last_play_ts = time.monotonic()
                except Exception:
                    pass
                try:
                    audio_data = np.frombuffer(raw, dtype=np.int16)
                    if len(audio_data) > 0:
                        rms = float(np.sqrt(np.mean(audio_data.astype(np.float32) ** 2)))
                        norm = min(1.0, float(rms / 5000.0) + 0.1)
                        self.gemini_output_amplitude.emit(norm)
                except Exception:
                    pass
            except Exception as e:
                if "underflow" not in str(e).lower():
                    print(f"[AudioEngine] Playback write error: {e}")

    def play_audio_chunk(self, pcm_bytes: bytes) -> bool:
        """Enqueue speaker audio (non-blocking). Returns False only when audibly dropped."""
        try:
            raw = bytes(pcm_bytes) if not isinstance(pcm_bytes, (bytes, bytearray)) else bytes(pcm_bytes)
        except Exception:
            return False
        if len(raw) == 0:
            return True
        # Cap single-chunk size (security: no megabyte queue bursts)
        if len(raw) > 192000:  # 4s @ 24kHz mono int16
            raw = raw[:192000]
        stream = self._output_stream
        if stream is None:
            # Lazy restart, throttled warn so logs stay readable
            if not self._play_start_warned:
                print("[AudioEngine] Playback chunk dropped — no output stream (retrying start)")
                self._play_start_warned = True
            try:
                if self.start_playback_stream():
                    stream = self._output_stream
                else:
                    return False
            except Exception:
                return False
            if stream is None:
                return False
        try:
            if not stream.active:
                if self._play_drop_warns % 50 == 0:
                    print("[AudioEngine] Playback chunk dropped — stream inactive")
                self._play_drop_warns += 1
                return False
        except Exception:
            return False
        try:
            self._play_queue.put_nowait(raw)
            return True
        except queue.Full:
            # Drop oldest, keep live speech (never block the event loop)
            try:
                self._play_queue.get_nowait()
            except Exception:
                pass
            try:
                self._play_queue.put_nowait(raw)
            except Exception:
                pass
            if self._play_drop_warns % 25 == 0:
                print("[AudioEngine] Playback queue full — dropped oldest chunk")
            self._play_drop_warns += 1
            return True
        except Exception:
            return False

    def played_recently(self, window_s: float = 0.25) -> bool:
        """True if speaker audio was written within the last window.

        The companion uses this as a feedback guard: while our own reply is
        audible, mic uplink of room tone would feed the model its own voice.
        """
        try:
            return (time.monotonic() - float(getattr(self, "_last_play_ts", 0.0) or 0.0)) < max(0.05, float(window_s))
        except Exception:
            return False

    def flush_playback(self) -> int:
        """Drop queued (not-yet-played) reply audio. Returns chunks dropped."""
        dropped = 0
        try:
            while True:
                self._play_queue.get_nowait()
                dropped += 1
        except queue.Empty:
            pass
        except Exception:
            pass
        return dropped

    def stop_playback_stream(self):
        try:
            self._play_stop.set()
        except Exception:
            pass
        if self._play_thread is not None:
            try:
                self._play_thread.join(timeout=1.0)
            except Exception:
                pass
            self._play_thread = None
        try:
            while True:
                self._play_queue.get_nowait()
        except queue.Empty:
            pass
        except Exception:
            pass
        if self._output_stream:
            try:
                self._output_stream.stop()
                self._output_stream.close()
            except Exception:
                pass
            self._output_stream = None
        self._play_drop_warns = 0
        try:
            self.gemini_output_amplitude.emit(0.0)
        except Exception:
            pass
