"""Automated PyInstaller Build Script for SPEAK Executable."""

import os
import sys
import shutil
import subprocess
from pathlib import Path

# Add project root to sys.path so modules resolve correctly
BASE_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(BASE_DIR))

DIST_DIR = BASE_DIR / "dist"
BUILD_DIR = BASE_DIR / "build"
ASSETS_DIR = BASE_DIR / "assets"
ICON_PATH = ASSETS_DIR / "icon.ico"


def build_executable():
    print("==================================================")
    print("      BUILDING SPEAK STANDALONE EXECUTABLE        ")
    print("==================================================")

    # 1. Clean previous build directories
    if DIST_DIR.exists():
        try:
            shutil.rmtree(DIST_DIR)
        except Exception:
            pass
    if BUILD_DIR.exists():
        try:
            shutil.rmtree(BUILD_DIR)
        except Exception:
            pass

    # 2. Ensure Claude icon exists
    from src.config import ensure_assets_and_icon
    ensure_assets_and_icon()

    # 3. PyInstaller build flags
    cmd = [
        sys.executable,
        "-m",
        "PyInstaller",
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
        "--noconfirm",
        "--clean",
        str(BASE_DIR / "main.py")
    ]

    print(f"\n[Running Command] {' '.join(cmd)}\n")
    result = subprocess.run(cmd)

    if result.returncode == 0:
        exe_file = DIST_DIR / "SPEAK.exe"
        print("\n==================================================")
        print(f" BUILD COMPLETE! Binary ready at:\n {exe_file}")
        print("==================================================")
    else:
        print("\n[ERROR] PyInstaller compilation failed.")
        sys.exit(1)


if __name__ == "__main__":
    build_executable()