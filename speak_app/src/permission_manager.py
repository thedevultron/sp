"""Proactive Screen Capture & OS Permission Handshake.

Permission Interceptor: must be consulted BEFORE initializing mss or the
screen capture worker. Triggers native OS authorization request directly
rather than letting the worker silently fail. Provides inline diagnostic
state for the main-window banner with a Grant Permission retry action.

Windows: screen capture via mss/DXGI generally needs no explicit consent,
but capture can still fail (secure desktop, RDP, driver, policy). We treat
a successful test-grab as granted, an exception as denied/pending, and the
retry action re-attempts capture + opens the native Privacy settings page
(ms-settings:privacy-screenshot / screenrecording) so the user can grant.
macOS (darwin): uses CGPreflightScreenCaptureAccess / CGRequestScreenCaptureAccess
when available via Quartz; otherwise falls back to test-grab heuristic.
Linux: test-grab heuristic (portal prompt surfaces on first grab).
"""
from __future__ import annotations
import sys
import time

PERMISSION_GRANTED = "granted"
PERMISSION_PENDING = "pending"
PERMISSION_DENIED = "denied"
PERMISSION_UNKNOWN = "unknown"


class ScreenPermissionManager:
    """Stateless-ish helper + cached status for UI banner."""

    def __init__(self):
        self.status: str = PERMISSION_UNKNOWN
        self.last_error: str = ""
        self.last_check_ts: float = 0.0

    # -- core interceptor --
    def check_permission(self) -> str:
        """Programmatically check whether OS granted screen recording.

        Never raises. Returns one of granted/pending/denied/unknown.
        Must be called before mss init / screen worker start.
        """
        plat = sys.platform
        try:
            if plat == "darwin":
                st = self._check_macos()
                self._store(st, "")
                return st
            # Windows + Linux: test-grab heuristic
            ok, err = self._test_grab()
            if ok:
                self._store(PERMISSION_GRANTED, "")
                return PERMISSION_GRANTED
            # Heuristic: distinguish pending vs denied by error text
            low = (err or "").lower()
            if any(k in low for k in ("denied", "not allowed", "access is denied", "unauthorized", "policy", "blocked")):
                self._store(PERMISSION_DENIED, err)
                return PERMISSION_DENIED
            if any(k in low for k in ("timeout", "busy", "temporarily")):
                self._store(PERMISSION_PENDING, err)
                return PERMISSION_PENDING
            # Empty frame / unknown error -> pending so banner offers retry, not dead-end
            self._store(PERMISSION_PENDING if err else PERMISSION_UNKNOWN, err or "")
            return self.status
        except Exception as e:
            self._store(PERMISSION_PENDING, str(e)[:200])
            return PERMISSION_PENDING

    def request_permission(self) -> str:
        """Trigger the native OS authorization request directly.

        - macOS: CGRequestScreenCaptureAccess() (shows system prompt).
        - Windows: open Privacy > Screen recording settings page + re-run test grab.
        - Linux: re-run test grab (portal shows native dialog on Wayland).
        Returns fresh status string.
        """
        plat = sys.platform
        # 1. Fire the native prompt first (best effort, never raises)
        try:
            if plat == "darwin":
                self._request_macos()
            elif plat.startswith("win"):
                self._open_windows_privacy_page()
            # linux: no explicit opener; portal prompt appears on grab
        except Exception as e:
            print(f"[Permission] native request note: {e}")
        # 2. Small settle delay then re-check
        try:
            time.sleep(0.4)
        except Exception:
            pass
        return self.check_permission()

    def get_diagnostic(self) -> dict:
        return {
            "status": self.status,
            "last_error": self.last_error,
            "last_check": self.last_check_ts,
            "banner_visible": self.status in (PERMISSION_PENDING, PERMISSION_DENIED),
            "banner_text": self.banner_text(),
        }

    def banner_text(self) -> str:
        if self.status == PERMISSION_GRANTED:
            return "Screen capture ready."
        if self.status == PERMISSION_DENIED:
            return "Screen recording denied — live vision is paused. Grant permission to resume screen share."
        if self.status == PERMISSION_PENDING:
            return "Screen recording permission pending — waiting for OS approval. Voice continues."
        return "Screen capture status unknown — run a check before sharing."

    # -- internals --
    def _store(self, status: str, err: str):
        self.status = status
        self.last_error = err or ""
        try:
            self.last_check_ts = time.time()
        except Exception:
            pass
        print(f"[Permission] status={status} err={self.last_error[:120]}")

    def _test_grab(self) -> tuple[bool, str]:
        """Single lightweight mss grab. True when OS allowed capture."""
        try:
            import mss as _mss
        except Exception as e:
            return False, f"mss missing: {e}"
        sct = None
        try:
            sct = _mss.mss()
            mons = getattr(sct, "monitors", None) or []
            if not mons:
                return False, "no monitors reported"
            target = mons[1] if len(mons) > 1 else mons[0]
            grab = sct.grab(target)
            # Validate non-blank frame
            try:
                w = int(getattr(grab, "width", 0) or 0)
                h = int(getattr(grab, "height", 0) or 0)
                if w <= 0 or h <= 0:
                    return False, "blank frame (0 size)"
                # sample bytes non-zero?
                try:
                    raw = bytes(grab.bgra or grab.rgb or b"")[:1024]
                    if raw and all(b == 0 for b in raw):
                        return False, "blank frame (all zeros)"
                except Exception:
                    pass
            except Exception:
                pass
            return True, ""
        except Exception as e:
            return False, str(e)[:300]
        finally:
            try:
                if sct is not None:
                    sct.close()
            except Exception:
                pass

    def _check_macos(self) -> str:
        try:
            import Quartz  # type: ignore
            try:
                # 10.15+: returns bool without prompting
                ok = Quartz.CGPreflightScreenCaptureAccess()
                if ok:
                    return PERMISSION_GRANTED
                return PERMISSION_PENDING
            except Exception:
                pass
        except Exception:
            pass
        ok, _ = self._test_grab()
        return PERMISSION_GRANTED if ok else PERMISSION_PENDING

    def _request_macos(self):
        try:
            import Quartz  # type: ignore
            try:
                Quartz.CGRequestScreenCaptureAccess()
                print("[Permission] macOS screen-capture prompt requested")
            except Exception as e:
                print(f"[Permission] macOS request note: {e}")
        except Exception as e:
            print(f"[Permission] macOS Quartz unavailable: {e}")

    def _open_windows_privacy_page(self):
        """Open native Windows Privacy settings (no silent fail)."""
        import subprocess
        candidates = [
            "ms-settings:privacy-screenshot",
            "ms-settings:privacy-screenrecording",
            "ms-settings:privacy",
        ]
        for uri in candidates:
            try:
                # os.startfile handles ms-settings: URIs; fallback to explorer/cmd
                import os as _os
                try:
                    _os.startfile(uri)  # type: ignore[attr-defined]
                    print(f"[Permission] Opened {uri}")
                    return
                except Exception:
                    pass
                subprocess.Popen(["cmd", "/c", "start", "", uri],
                                 stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL,
                                 creationflags=getattr(subprocess, "CREATE_NO_WINDOW", 0))
                print(f"[Permission] Opened {uri} via cmd")
                return
            except Exception as e:
                print(f"[Permission] settings open {uri} note: {e}")
                continue


# Shared singleton for ScreenEngine + UI banner
permission_manager = ScreenPermissionManager()
