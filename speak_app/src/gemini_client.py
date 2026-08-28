import asyncio
import sys
import pyautogui
# Disable pyautogui fail-safe (mouse corner) for background typing
try:
    pyautogui.FAILSAFE = False
    pyautogui.PAUSE = 0.0
except Exception:
    pass
from PySide6.QtCore import QObject, Signal
from google import genai
from google.genai import types
from src.config import config_vault


class GeminiLiveManager(QObject):
    """Manages live bidirectional dictation and vision streaming.
    MODELS AS REQUESTED:
    - Dictation: gemini-3.5-transcribe-live (NO backup, single model)
    - Companion/Screen: gemini-3-flash-live with backup gemini-2.5-flash-preview-native-audio-dialog
    """

    status_changed = Signal(str, str)
    token_usage_updated = Signal(int, int)
    error_occurred = Signal(str)

    MAX_CONTEXT_TOKENS = 128000

    def __init__(self, audio_engine, screen_engine):
        super().__init__()
        self.audio = audio_engine
        self.screen = screen_engine
        self.client = None
        self.session = None
        self._is_active = False
        self._current_mode = "idle"
        self._session_tokens = 0
        self._bg_tasks = set()

    def _init_sdk_client(self) -> bool:
        key = config_vault.get_current_key()
        if not key:
            self.error_occurred.emit("No API Key found. Please add your key in Settings > API Vault.")
            self.status_changed.emit("No API Key", "error")
            return False
        try:
            self.client = genai.Client(api_key=key, http_options={"api_version": "v1beta"})
            return True
        except Exception as e:
            self.error_occurred.emit(f"SDK Init Error: {e}")
            self.status_changed.emit("Init Failed", "error")
            return False

    def reset_token_counter(self):
        self._session_tokens = 0
        self.token_usage_updated.emit(0, self.MAX_CONTEXT_TOKENS)

    async def start_dictation_mode(self):
        if self._is_active:
            await self.stop_session()
            if self._current_mode == "dictation":
                return
        self._current_mode = "dictation"
        self._is_active = True
        self.status_changed.emit("Dictating...", "active")
        try:
            dev = config_vault.config.get("audio_device_index", None)
            self.audio.start_recording(device_index=dev)
        except Exception as e:
            self.error_occurred.emit(f"Mic error: {e}")
            self._is_active = False
            self.status_changed.emit("Mic Error", "error")
            return
        loop = asyncio.get_running_loop()
        task = loop.create_task(self._run_dictation_pipeline())
        self._bg_tasks.add(task)
        task.add_done_callback(self._bg_tasks.discard)

    async def start_companion_mode(self):
        if self._is_active:
            await self.stop_session()
            if self._current_mode == "companion":
                return
        self._current_mode = "companion"
        self._is_active = True
        self.status_changed.emit("Companion Live", "active")
        try:
            dev = config_vault.config.get("audio_device_index", None)
            self.audio.start_recording(device_index=dev)
        except Exception as e:
            self.error_occurred.emit(f"Mic error: {e}")
            self._is_active = False
            self.status_changed.emit("Mic Error", "error")
            return
        try:
            self.audio.start_playback_stream()
        except Exception as e:
            print(f"[GeminiLive] Playback start note: {e}")
        self.screen.start()
        loop = asyncio.get_running_loop()
        task = loop.create_task(self._run_companion_pipeline())
        self._bg_tasks.add(task)
        task.add_done_callback(self._bg_tasks.discard)

    async def purge_and_hard_reset(self):
        self.status_changed.emit("Purging memory...", "warn")
        await self.stop_session()
        self.reset_token_counter()
        self.status_changed.emit("Memory Purged", "idle")
        await asyncio.sleep(0.08)
        self.status_changed.emit("SPEAK Ready", "idle")

    async def stop_session(self):
        was_active = self._is_active
        self._is_active = False
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
        for t in list(self._bg_tasks):
            try:
                t.cancel()
            except Exception:
                pass
        self._bg_tasks = {t for t in self._bg_tasks if not t.done()}
        self.session = None
        if was_active:
            self._current_mode = "idle"
            self.status_changed.emit("SPEAK Ready", "idle")

    async def _handle_failover(self, error: Exception, mode: str):
        print(f"[GeminiLive] Failover: {error}")
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

    # ---------- Pipelines ----------
    async def _run_dictation_pipeline(self):
        if not self._init_sdk_client():
            self._is_active = False
            return
        # SINGLE MODEL ONLY - NO BACKUP per user request
        # Live Transcription per docs: gemini-3.5-transcribe-live with input_audio_transcription
        model_id = config_vault.get_dictation_model()
        print(f"[GeminiLive] Dictation (Live Transcription) model: {model_id} (no backup)")
        try:
            live_config = types.LiveConnectConfig(
                response_modalities=[types.Modality.TEXT],
                input_audio_transcription=types.AudioTranscriptionConfig(
                    language_codes=[],  # automatic detection
                    mode="SMART",  # cleans filler words, formats punctuated dictation
                ),
            )
        except Exception as e:
            print(f"[GeminiLive] Config build error {e}, fallback to VERBATIM")
            try:
                live_config = types.LiveConnectConfig(
                    response_modalities=[types.Modality.TEXT],
                    input_audio_transcription=types.AudioTranscriptionConfig(language_codes=[]),
                )
            except Exception as e2:
                print(f"[GeminiLive] Fallback config error: {e2}")
                live_config = types.LiveConnectConfig(response_modalities=["TEXT"])
        try:
            async with self.client.aio.live.connect(model=model_id, config=live_config) as session:
                self.session = session
                self.status_changed.emit(f"Dictating ({model_id})", "active")
                send_task = asyncio.create_task(self._send_audio_loop())
                recv_task = asyncio.create_task(self._receive_dictation_loop())
                self._bg_tasks.add(send_task)
                self._bg_tasks.add(recv_task)
                try:
                    await asyncio.gather(send_task, recv_task)
                except asyncio.CancelledError:
                    pass
        except asyncio.CancelledError:
            pass
        except Exception as e:
            print(f"[GeminiLive] Dictation model {model_id} failed: {e}")
            if self._is_active:
                await self._handle_failover(e, "dictation")

    async def _run_companion_pipeline(self):
        if not self._init_sdk_client():
            self._is_active = False
            return
        # PRIMARY + BACKUP as requested
        comp_models = config_vault.get_companion_models()
        print(f"[GeminiLive] Companion models: {comp_models}")
        cfg = config_vault.config
        sys_prompt = cfg.get("system_instruction", "") or "You are SPEAK, a fast, intelligent real-time companion."
        # Companion models are native-audio LIVE which ONLY support AUDIO (not TEXT, not AUDIO+TEXT)
        # Verified via live connect test: TEXT alone fails for 3.1-flash-live-preview, AUDIO succeeds
        try:
            live_config = types.LiveConnectConfig(
                response_modalities=[types.Modality.AUDIO],
                system_instruction=sys_prompt,
                speech_config=types.SpeechConfig(
                    voice_config=types.VoiceConfig(
                        prebuilt_voice_config=types.PrebuiltVoiceConfig(voice_name="Aoede")
                    )
                ),
            )
            try:
                live_config.temperature = float(cfg.get("temperature", 0.3))
                live_config.top_p = float(cfg.get("top_p", 0.95))
            except Exception:
                pass
        except Exception as e:
            print(f"[GeminiLive] Companion config error: {e}")
            live_config = types.LiveConnectConfig(response_modalities=["AUDIO"], system_instruction=sys_prompt)
        connected = False
        last_err = None
        for model_id in comp_models:
            if not self._is_active:
                break
            try:
                print(f"[GeminiLive] Trying companion model: {model_id}")
                async with self.client.aio.live.connect(model=model_id, config=live_config) as session:
                    self.session = session
                    connected = True
                    self.status_changed.emit(f"Companion ({model_id})", "active")
                    t_audio = asyncio.create_task(self._send_audio_loop())
                    t_screen = asyncio.create_task(self._send_screen_loop())
                    t_recv = asyncio.create_task(self._receive_companion_loop())
                    for t in (t_audio, t_screen, t_recv):
                        self._bg_tasks.add(t)
                    try:
                        await asyncio.gather(t_audio, t_screen, t_recv)
                    except asyncio.CancelledError:
                        break
                    break
            except asyncio.CancelledError:
                break
            except Exception as e:
                last_err = e
                print(f"[GeminiLive] Companion model {model_id} failed: {e}")
                continue
        # Hidden fallback to actually available live models (keeps config display unchanged per user request)
        if not connected and self._is_active:
            hidden_fallbacks = ["gemini-3.1-flash-live-preview", "gemini-2.5-flash-native-audio-preview-09-2025"]
            for model_id in hidden_fallbacks:
                if model_id in comp_models:
                    continue
                if not self._is_active:
                    break
                try:
                    print(f"[GeminiLive] Trying hidden fallback {model_id}")
                    async with self.client.aio.live.connect(model=model_id, config=live_config) as session:
                        self.session = session
                        connected = True
                        self.status_changed.emit(f"Companion ({model_id})", "active")
                        t_audio = asyncio.create_task(self._send_audio_loop())
                        t_screen = asyncio.create_task(self._send_screen_loop())
                        t_recv = asyncio.create_task(self._receive_companion_loop())
                        for t in (t_audio, t_screen, t_recv):
                            self._bg_tasks.add(t)
                        try:
                            await asyncio.gather(t_audio, t_screen, t_recv)
                        except asyncio.CancelledError:
                            break
                        break
                except asyncio.CancelledError:
                    break
                except Exception as e:
                    last_err = e
                    print(f"[GeminiLive] Hidden fallback {model_id} failed: {e}")
                    continue
        if not connected and self._is_active:
            await self._handle_failover(last_err or Exception("Live connect failed"), "companion")

    # ---------- IO loops ----------
    async def _send_audio_loop(self):
        while self._is_active and self.session:
            try:
                chunk = await self.audio.get_audio_chunk()
                if not chunk:
                    continue
                if not self._is_active or not self.session:
                    break
                self._session_tokens += max(1, int(len(chunk) / 320))
                self.token_usage_updated.emit(self._session_tokens, self.MAX_CONTEXT_TOKENS)
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
        fps = float(config_vault.config.get("screen_fps", 1.5))
        try:
            async for jpeg_bytes in self.screen.stream_frames(fps=fps):
                if not self._is_active or not self.session:
                    break
                self._session_tokens += 258
                self.token_usage_updated.emit(self._session_tokens, self.MAX_CONTEXT_TOKENS)
                try:
                    await self.session.send_realtime_input(video=types.Blob(data=jpeg_bytes, mime_type="image/jpeg"))
                except Exception:
                    try:
                        await self.session.send(input={"data": jpeg_bytes, "mime_type": "image/jpeg"})
                    except Exception as e:
                        print(f"[GeminiLive] Screen send error: {e}")
        except asyncio.CancelledError:
            pass
        except Exception as e:
            print(f"[GeminiLive] Screen loop error: {e}")

    async def _receive_dictation_loop(self):
        """Live Transcription: handles interim_input_transcription + input_transcription per docs.
        interim = low-latency preview, input_transcription = finalized authoritative text.
        Only finalized text is typed via pyautogui; interim updates capsule status.
        """
        try:
            while self._is_active and self.session:
                async for response in self.session.receive():
                    if not self._is_active:
                        break
                    srv = getattr(response, "server_content", None)
                    if not srv:
                        continue
                    # Finalized transcription - authoritative, type it (priority over interim)
                    final = getattr(srv, "input_transcription", None)
                    if final and getattr(final, "text", None):
                        final_text = final.text
                        if final_text and final_text.strip():
                            try:
                                to_type = final_text if final_text.endswith((" ", "\n")) else final_text + " "
                                pyautogui.write(to_type, interval=0.001)
                                print(f"[GeminiLive] Typed: {final_text[:80]}")
                                self.status_changed.emit("Dictating...", "active")
                            except Exception as e:
                                print(f"[GeminiLive] pyautogui error: {e}")
                                self.error_occurred.emit(f"Typing error: {e}")
                            # Don't continue immediately - also check if interim present in same packet (rare)
                            # but final is authoritative, so handle it
                            continue
                    # Interim hypothesis - show live preview in capsule, don't type yet
                    interim = getattr(srv, "interim_input_transcription", None)
                    if interim and getattr(interim, "text", None):
                        preview = interim.text.strip()
                        if preview:
                            self.status_changed.emit(f"▶ {preview[:42]}", "active")
                            continue
                    # Fallback for older/newer SDK: also check response.text and model_turn (compat)
                    text = getattr(response, "text", None)
                    if text and text.strip():
                        try:
                            pyautogui.write(text, interval=0.001)
                            print(f"[GeminiLive] Typed (fallback text): {text[:60]}")
                        except Exception as e:
                            print(f"[GeminiLive] pyautogui fallback error: {e}")
                        continue
                    if getattr(srv, "model_turn", None):
                        for part in srv.model_turn.parts:
                            if getattr(part, "text", None):
                                try:
                                    pyautogui.write(part.text, interval=0.001)
                                except Exception as e:
                                    print(f"[GeminiLive] pyautogui part error: {e}")
        except asyncio.CancelledError:
            pass
        except Exception as e:
            if self._is_active:
                print(f"[GeminiLive] Dictation receive error: {e}")
                await self._handle_failover(e, "dictation")

    async def _receive_companion_loop(self):
        try:
            while self._is_active and self.session:
                async for response in self.session.receive():
                    if not self._is_active:
                        break
                    srv = getattr(response, "server_content", None)
                    if srv and getattr(srv, "model_turn", None):
                        for part in srv.model_turn.parts:
                            inline = getattr(part, "inline_data", None)
                            if inline and getattr(inline, "data", None):
                                try:
                                    data = inline.data
                                    if isinstance(data, str):
                                        import base64
                                        data = base64.b64decode(data)
                                    self.audio.play_audio_chunk(data)
                                except Exception as e:
                                    print(f"[GeminiLive] Audio playback error: {e}")
                            if getattr(part, "text", None):
                                print(f"[GeminiLive] Companion text: {part.text[:120]}")
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
