# SPEAK v2.0 — Production Installer Guide — Amir Bagawan
Free + BYOK — premium rounded UI — injection fix

## What changed in v2.0 final
- **Free tier + BYOK:** Hidden embedded fallback key (obfuscated in `src/_embedded_key.py`, XOR+base64, never shown/logged). User vault keys take priority. UI shows "Free tier active" when using embedded.
- **Injection fix:** `src/injection_service.py` replaces `pyautogui.write` + `Ctrl+A` hack with `SendInput` unicode + clipboard `Ctrl+V`. No `Enter` press, error-free multilingual (SMART `language_codes=[]`), refine replaces buffer correctly and copies to clipboard.
- **Premium rounded UI:** `src/ui/window_effects.py` now removes 1px Win32 border (`DWMWA_BORDER_COLOR` + `DwmExtendFrameIntoClientArea`) + `disable_window_border`, capsule `paintEvent` single rounded rect 16px + shadow, no double hairline outline. Settings & capsule use delayed `_apply` timers for HWND validity.
- **Security hardening:** `config.py` atomic write + `icacls` ACL, masked logs (`_key_label`), bounded audio queue (200), default free tier.
- **Publisher:** Amir Bagawan — `installer.iss` VersionInfoCompany, `LICENSE.txt`, `installer/README.txt`, `build.py` signing workaround (`cert.pfx` or `SIGNING_NOTE.txt`).
- **Deps pinned:** `requirements.txt` now `==` exact (PySide6 6.8.2, google-genai 1.21.0, etc.)

---

## One-time setup

### 1) Python environment
```
cd speak_app
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
```

### 2) Install Inno Setup 6
- https://jrsoftware.org/isinfo.php (6.2+)
- Provides `ISCC.exe` (`C:\Program Files (x86)\Inno Setup 6\ISCC.exe`)

---

## Build

### A) Build EXE
```
cd C:\Users\Amir\SPEAK\speak_app
venv\Scripts\activate
python build.py
```
- Runs PyInstaller `--onefile --windowed --icon=assets/icon.ico --add-data=assets --hidden-import=src._embedded_key --hidden-import=src.injection_service --collect-all=google.genai`
- Output: `dist\SPEAK.exe` (~90-130 MB), `dist/SIGNING_NOTE.txt` if no cert
- Embedded key is already in `src/_embedded_key.py` (hidden, obfuscated). Do not commit plain key.

If you need to update the hidden key: edit `src/_embedded_key.py` `_P1/_P2/_P3` (generate via `scripts/gen_key.py` or manual XOR+base64).

### B) Compile installer
```
"C:\Program Files (x86)\Inno Setup 6\ISCC.exe" installer.iss
# or iscc installer.iss if in PATH
```
- Output: `installer\SPEAK_Setup_v2.0.exe` (Publisher: Amir Bagawan)

### C) Test locally
- Double-click `installer\SPEAK_Setup_v2.0.exe` (check Desktop/Startup options).
- Launch: Settings should show "Free tier active" (green) if no user key, rounded corners, no outline, shadow under capsule.
- Ctrl+Space: capsule above taskbar, blue wave, type in Notepad — verify multilingual + refine.
- Refine: dictate 2 sentences, say "refine" or tap Refine — should delete what was typed in focused field and paste refined (copied), no Enter.

### D) Distribute
- Send `installer\SPEAK_Setup_v2.0.exe`. Receiver double-clicks Next>Next>Install. Free works immediately; they can add their key in Setup for unlimited.

---

## Troubleshooting
- Capsule outline still: ensure `window_effects.py` is updated + reboot Windows Explorer; Win10 shows square (no DWM 33).
- Mic: Settings > Preferences > Refresh
- Quota 429: user should add backup key; embedded hidden fallback rotates last.
- Installer fail: ensure `dist\SPEAK.exe` exists before ISCC.

## Versioning
- Bump `MyAppVersion` in `installer.iss`, re-run build + ISCC.
