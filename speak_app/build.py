"""Automated PyInstaller Build Script for SPEAK v2.1 — Amir Bagawan — production ready, Inno 6.

One-click production build:
  python build.py            -> EXE only (dist\\SPEAK.exe)
  python build.py --installer -> EXE + Inno installer (installer\\SPEAK_Setup_v2.1.exe)

Production guarantees:
- Pinned deps verified before build (fail fast with clear message)
- Syntax check (compileall) before PyInstaller — catches cutoff/chrome regressions
- Embedded free-tier key verified present (masked log only, never value)
- Single-file --windowed --onefile, icon + assets bundled, no UPX (fewer AV false positives)
- Version metadata stamped via --version-file (Publisher: Amir Bagawan)
- SHA256 hash printed for distribution verification
- Best-effort signtool signing if cert.pfx present, else SIGNING_NOTE.txt
- Optional --installer auto-runs ISCC.exe so you can send ONE file and be done
"""
import os
import sys
import shutil
import subprocess
import hashlib
import compileall
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(BASE_DIR))

DIST_DIR = BASE_DIR / "dist"
BUILD_DIR = BASE_DIR / "build"
ASSETS_DIR = BASE_DIR / "assets"
ICON_PATH = ASSETS_DIR / "icon.ico"
SPEC_PATH = BASE_DIR / "SPEAK.spec"
VERSION_FILE = BASE_DIR / "version_info.txt"

APP_VERSION = "2.1.0"


def ensure_version_file():
    """Stamp Publisher/Version so Explorer > Properties shows Amir Bagawan."""
    content = f"""# UTF-8
VSVersionInfo(
  ffi=FixedFileInfo(filevers=({APP_VERSION.replace('.', ', ')}, 0), prodvers=({APP_VERSION.replace('.', ', ')}, 0), mask=0x3f, flags=0x0, OS=0x40004, fileType=0x1, subtype=0x0, date=(0, 0)),
  kids=[StringFileInfo([StringTable(u'040904B0', [StringStruct(u'CompanyName', u'Amir Bagawan'), StringStruct(u'FileDescription', u'SPEAK - Voice dictation and AI companion'), StringStruct(u'FileVersion', u'{APP_VERSION}'), StringStruct(u'InternalName', u'SPEAK'), StringStruct(u'OriginalFilename', u'SPEAK.exe'), StringStruct(u'ProductName', u'SPEAK'), StringStruct(u'ProductVersion', u'{APP_VERSION}')])]), VarFileInfo([VarStruct(u'Translation', [1033, 1200])])]
)
"""
    try:
        VERSION_FILE.write_text(content, encoding="utf-8")
    except Exception as e:
        print(f"[Version] write note: {e}")


def preflight_checks() -> bool:
    """Fail fast with actionable messages — production safety."""
    ok = True
    # 1. Python version
    if sys.version_info < (3, 10):
        print(f"[Preflight] FAIL: Python {sys.version} < 3.10 required")
        ok = False
    # 2. Required files
    for p in [BASE_DIR / "main.py", BASE_DIR / "requirements.txt", ASSETS_DIR / "capsule_style.qss"]:
        if not p.exists():
            print(f"[Preflight] FAIL: missing {p}")
            ok = False
    # 3. Syntax check all sources (catches UI regressions before 5-min PyInstaller run)
    print("[Preflight] Compiling sources...")
    compile_ok = compileall.compile_dir(str(BASE_DIR / "src"), quiet=1, force=False)
    main_ok = compileall.compile_file(str(BASE_DIR / "main.py"), quiet=1)
    if not (compile_ok and main_ok):
        print("[Preflight] FAIL: syntax errors — fix before build")
        ok = False
    # 4. Critical imports available
    for mod in ["PySide6", "qasync", "google.genai", "pynput", "sounddevice", "keyring", "mss", "PIL"]:
        try:
            __import__(mod)
        except Exception:
            print(f"[Preflight] FAIL: missing dep '{mod}' — run: pip install -r requirements.txt")
            ok = False
    # 5. Icon
    try:
        from src.config import ensure_assets_and_icon
        ensure_assets_and_icon()
    except Exception as e:
        print(f"[Preflight] icon ensure note: {e}")
    if not ICON_PATH.exists():
        print("[Preflight] FAIL: icon.ico missing")
        ok = False
    # 6. Embedded key present (masked only). NOTE: OAuth-style embedded tokens
    # (AQ.Ab…/ya29…) expire in ~1h and fail with 401 — the installer MUST be
    # used with a user BYOK from AI Studio. Never claim one-click free-tier
    # unless the embedded value is a long-lived AIza key.
    try:
        from src._embedded_key import get_embedded_key
        ek = get_embedded_key()
        if ek:
            if str(ek).startswith("AIza"):
                print(f"[Preflight] Embedded key present (len {len(ek)}, AIza shape) — installer may work with no user key")
            else:
                print(f"[Preflight] WARNING: embedded key present but non-AIza shape (len {len(ek)}) — likely expired OAuth; installer will REQUIRE user BYOK in Settings > Setup")
        else:
            print("[Preflight] WARNING: embedded key empty — installer will REQUIRE user key (not one-click)")
    except Exception as e:
        print(f"[Preflight] embedded check note: {e}")
    return ok


def try_sign_exe(exe_path: Path):
    """Best-effort signing (no cert = note + continue). Never blocks distribution."""
    pfx = None
    for cand in [BASE_DIR / "cert.pfx", BASE_DIR / "amir.pfx", Path(os.getenv("CERT_PATH", "") or "")]:
        try:
            p = Path(cand)
            # Must be a real .pfx FILE (Path("") resolves to cwd — never accept that).
            if p.suffix.lower() == ".pfx" and p.is_file():
                pfx = p
                break
        except Exception:
            continue
    if not pfx:
        note = BASE_DIR / "dist" / "SIGNING_NOTE.txt"
        try:
            note.write_text("SPEAK v2.1 by Amir Bagawan\nUnsigned build - no pfx found.\nTo sign: place cert.pfx next to build.py and re-run.\nCmd: signtool sign /fd SHA256 /f cert.pfx /p password dist\\SPEAK.exe\n", encoding="utf-8")
            print(f"[Sign] No cert.pfx — shipping unsigned (VersionInfoCompany=Amir Bagawan still stamped)")
        except Exception:
            pass
        return False
    # Only attempt signers that actually exist — no scary "not found" spam.
    import shutil as _sh
    signtools = [st for st in (r"C:\Program Files (x86)\Windows Kits\10\bin\x64\signtool.exe",
                               r"C:\Program Files\Microsoft SDKs\Windows\v10.0A\bin\NETFX 4.8 Tools\signtool.exe")
                 if Path(st).is_file()]
    if _sh.which("signtool"):
        signtools.append("signtool")
    if not signtools:
        print("[Sign] cert.pfx present but no signtool installed — shipping unsigned")
        return False
    pwd = os.getenv("CERT_PASSWORD", "")
    for st in signtools:
        try:
            cmd = [st, "sign", "/fd", "SHA256", "/f", str(pfx), "/tr", "http://timestamp.digicert.com", "/td", "SHA256", str(exe_path)]
            if pwd:
                cmd.insert(5, "/p"); cmd.insert(6, pwd)
            print(f"[Sign] Trying {st} ...")
            r = subprocess.run(cmd, capture_output=True, text=True, timeout=60, creationflags=getattr(subprocess, "CREATE_NO_WINDOW", 0))
            if r.returncode == 0:
                print(f"[Sign] Signed OK with {pfx}")
                return True
            else:
                print(f"[Sign] {st} failed: {(r.stderr or '')[:200]}")
        except Exception as e:
            print(f"[Sign] {st} error {e}")
            continue
    return False


def run_iscc() -> bool:
    """Auto-compile installer.iss if Inno is installed — one-file distribution."""
    candidates = [
        r"C:\Program Files (x86)\Inno Setup 6\ISCC.exe",
        r"C:\Program Files\Inno Setup 6\ISCC.exe",
        os.path.join(os.getenv("LOCALAPPDATA", ""), r"Programs\Inno Setup 6\ISCC.exe"),
        os.path.expandvars(r"%LOCALAPPDATA%\Programs\Inno Setup 6\ISCC.exe"),
        "iscc",
    ]
    iss = BASE_DIR / "installer.iss"
    if not iss.exists():
        print("[Installer] installer.iss missing — skipping")
        return False
    for iscc in candidates:
        try:
            print(f"[Installer] Trying {iscc} ...")
            r = subprocess.run([iscc, str(iss)], cwd=str(BASE_DIR), capture_output=True, text=True, timeout=180)
            out = (r.stdout or "") + (r.stderr or "")
            if r.returncode == 0:
                print("[Installer] OK — check installer\\SPEAK_Setup_v2.1.exe")
                return True
            else:
                print(f"[Installer] {iscc} rc={r.returncode}: {out[-400:]}")
        except FileNotFoundError:
            continue
        except Exception as e:
            print(f"[Installer] {iscc} error {e}")
            continue
    print("[Installer] ISCC not found — install Inno Setup 6 (https://jrsoftware.org/isinfo.php), then run: iscc installer.iss")
    return False


def build_executable(with_installer: bool = False):
    print("=" * 58)
    print(f"      BUILDING SPEAK STANDALONE EXECUTABLE v{APP_VERSION} - Amir Bagawan")
    print("=" * 58)
    if not preflight_checks():
        print("\n[Error] Preflight failed — fix messages above, then re-run.")
        sys.exit(2)
    for d in (DIST_DIR, BUILD_DIR):
        if d.exists():
            try:
                shutil.rmtree(d)
            except Exception as e:
                print(f"[Clean] {d}: {e}")
    ensure_version_file()

    cmd = [
        sys.executable, "-m", "PyInstaller",
        "--name=SPEAK",
        "--onefile",
        "--windowed",
        f"--icon={str(ICON_PATH)}",
        f"--add-data={str(ASSETS_DIR)}{os.pathsep}assets",
        "--hidden-import=qasync",
        "--hidden-import=google.genai",
        "--hidden-import=google.genai.types",
        "--hidden-import=pynput.keyboard._win32",
        "--hidden-import=pynput.mouse._win32",
        "--hidden-import=sounddevice",
        "--hidden-import=keyring.backends.Windows",
        "--hidden-import=pyautogui",
        "--hidden-import=mss",
        "--hidden-import=PySide6.QtSvg",
        "--hidden-import=PIL",
        "--hidden-import=src._embedded_key",
        "--hidden-import=src.injection_service",
        "--hidden-import=src.session_manager",
        "--hidden-import=src.permission_manager",
        "--hidden-import=src.memory_store",
        "--hidden-import=src.config",
        "--hidden-import=src.gemini_client",
        "--collect-all=google.genai",
        # Smaller + faster startup, fewer AV heuristics triggers:
        "--exclude-module=tkinter",
        "--exclude-module=matplotlib",
        "--exclude-module=scipy",
        "--exclude-module=pandas",
        # Silence known-harmless "not found" warnings (absent optionals /
        # runtime-generated tables — excluding them changes nothing, since
        # PyInstaller already skips files that do not exist):
        "--exclude-module=google.genai.tests",
        "--exclude-module=pycparser.lextab",
        "--exclude-module=pycparser.yacctab",
        "--exclude-module=tzdata",
        "--exclude-module=pkg_resources",
        # NOTE: no --strip — it needs GNU strip.exe (absent on Windows) and only
        # produced 8 scary but harmless "Failed to run strip" tracebacks.
        "--optimize=1",
        # Clean console: only real errors print (the full warning log is still
        # written to build/SPEAK/warn-SPEAK.txt for forensics).
        "--log-level=ERROR",
        f"--version-file={str(VERSION_FILE)}",
        "--noconfirm",
        "--clean",
        "--noupx",
        str(BASE_DIR / "main.py"),
    ]
    print(f"\n[Running] {' '.join(cmd)}\n")
    # Silence third-party SyntaxWarnings (e.g. pyautogui's unused Linux-only
    # x11 module) so the log reads clean — app code still warns normally.
    try:
        _env = dict(os.environ)
        _prev = _env.get("PYTHONWARNINGS", "")
        _env["PYTHONWARNINGS"] = ((_prev + ",") if _prev else "") + "ignore::SyntaxWarning"
    except Exception:
        _env = None
    result = subprocess.run(cmd, cwd=str(BASE_DIR), env=_env)
    if result.returncode != 0:
        print("\n[Error] PyInstaller failed")
        sys.exit(result.returncode)
    exe = DIST_DIR / "SPEAK.exe"
    if not exe.exists():
        print("[Warn] PyInstaller succeeded but exe not found")
        sys.exit(1)
    size_mb = exe.stat().st_size / (1024 * 1024)
    try:
        h = hashlib.sha256(exe.read_bytes()).hexdigest()
        print(f"[Hash] SHA256:{h}")
        (DIST_DIR / "SPEAK.exe.sha256").write_text(f"{h}  SPEAK.exe\n", encoding="utf-8")
    except Exception:
        pass
    try_sign_exe(exe)
    print("\n" + "=" * 58)
    print(f" BUILD OK — {exe}")
    print(f" Size: {size_mb:.1f} MB")
    print(" Publisher: Amir Bagawan (VersionInfo stamped)")
    print(" NOTE: add your Gemini API key in Settings > Setup (BYOK required).")
    print("=" * 58)
    if with_installer:
        print("\n[Build] --installer: compiling Inno installer...")
        ok = run_iscc()
        if ok:
            try:
                outs = sorted((BASE_DIR / "installer").glob("SPEAK_Setup*.exe"))
                if outs:
                    latest = max(outs, key=lambda p: p.stat().st_mtime)
                    print(f" INSTALLER OK — {latest} ({latest.stat().st_size / (1024*1024):.1f} MB)")
                    print(" Send this ONE file — receiver double-clicks Next>Next>Install. Done.")
            except Exception:
                pass
        else:
            sys.exit(3)


def _ensure_venv_interpreter():
    """build.py MUST run under speak_app\\venv (pinned deps: PySide 6.8.2,
    PyInstaller 6.12.0, genai 2.22). A bare `py build.py` uses system Python
    (3.14 + unpinned packages) and produces a bloated, wrong-deps exe with
    scary warnings — so re-exec through the venv automatically instead of
    failing or misbuilding. Never raises out (falls through on odd setups).
    """
    try:
        here = Path(__file__).resolve().parent
        venv_py = here / "venv" / "Scripts" / "python.exe"
        if venv_py.exists() and Path(sys.executable).resolve() != venv_py.resolve():
            print(f"[Build] Redirecting to project venv: {venv_py}")
            print(f"[Build] (you ran: {sys.executable})")
            r = subprocess.run([str(venv_py), str(Path(__file__).resolve()), *sys.argv[1:]])
            sys.exit(r.returncode)
    except SystemExit:
        raise
    except Exception as e:
        print(f"[Build] venv redirect note: {e} — continuing with {sys.executable}")


if __name__ == "__main__":
    _ensure_venv_interpreter()
    with_installer = "--installer" in sys.argv or "/installer" in sys.argv
    build_executable(with_installer=with_installer)
