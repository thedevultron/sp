import asyncio
import queue
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
        self._audio_queue: asyncio.Queue = asyncio.Queue()
        self._loop = None

    def set_loop(self, loop):
        self._loop = loop
        # Re-create queue bound to this loop if needed (py 3.14)
        try:
            # If queue was created on different loop, recreate
            self._audio_queue = asyncio.Queue()
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
                    if self._loop.is_running():
                        self._loop.call_soon_threadsafe(self._audio_queue.put_nowait, raw_bytes)
                    else:
                        # Loop not running yet (early callback) - try direct put
                        try:
                            self._audio_queue.put_nowait(raw_bytes)
                        except Exception:
                            pass
                except Exception:
                    pass
        except Exception as e:
            print(f"[AudioEngine] Callback error: {e}")

    def start_recording(self, device_index=None):
        if self._is_recording:
            return
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
                except Exception as e2:
                    print(f"[AudioEngine] Fallback also failed: {e2}")
                    self._is_recording = False

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

    async def get_audio_chunk(self) -> bytes:
        return await self._audio_queue.get()

    def start_playback_stream(self, output_sample_rate: int = 24000):
        if self._output_stream is not None:
            try:
                if self._output_stream.active:
                    return
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
            print("[AudioEngine] Playback stream started")
        except Exception as e:
            print(f"[AudioEngine] Playback start error: {e}")
            self._output_stream = None

    def play_audio_chunk(self, pcm_bytes: bytes):
        if not self._output_stream:
            return
        try:
            if not self._output_stream.active:
                return
        except Exception:
            return
        try:
            raw = bytes(pcm_bytes) if not isinstance(pcm_bytes, (bytes, bytearray)) else bytes(pcm_bytes)
            if len(raw) == 0:
                return
            self._output_stream.write(raw)
            try:
                audio_data = np.frombuffer(raw, dtype=np.int16)
                if len(audio_data) > 0:
                    rms = float(np.sqrt(np.mean(audio_data.astype(np.float32) ** 2)))
                    norm = min(1.0, float(rms / 5000.0) + 0.1)
                    self.gemini_output_amplitude.emit(norm)
            except Exception:
                pass
        except Exception as e:
            # Don't crash on underrun
            if "underflow" not in str(e).lower():
                print(f"[AudioEngine] Playback write error: {e}")

    def stop_playback_stream(self):
        if self._output_stream:
            try:
                self._output_stream.stop()
                self._output_stream.close()
            except Exception:
                pass
            self._output_stream = None
            try:
                self.gemini_output_amplitude.emit(0.0)
            except Exception:
                pass
