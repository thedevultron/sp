# -*- mode: python ; coding: utf-8 -*-


a = Analysis(
    ['C:/Users/Amir/SPEAK/speak_app/main.py'],
    pathex=[],
    binaries=[],
    datas=[('C:/Users/Amir/SPEAK/speak_app/assets', 'assets')],
    hiddenimports=['qasync', 'google.genai', 'google.genai.types', 'pynput.keyboard._win32', 'pynput.mouse._win32', 'sounddevice', 'keyring.backends.Windows', 'pyautogui', 'mss'],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    noarchive=False,
    optimize=0,
)
pyz = PYZ(a.pure)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.datas,
    [],
    name='SPEAK',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon=['C:/Users/Amir/SPEAK/speak_app/assets/icon.ico'],
)
