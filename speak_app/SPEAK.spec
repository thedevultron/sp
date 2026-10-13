# -*- mode: python ; coding: utf-8 -*-
from PyInstaller.utils.hooks import collect_all

datas = [('C:\\Users\\Amir\\SPEAK\\speak_app\\assets', 'assets')]
binaries = []
hiddenimports = ['qasync', 'google.genai', 'google.genai.types', 'pynput.keyboard._win32', 'pynput.mouse._win32', 'sounddevice', 'keyring.backends.Windows', 'pyautogui', 'mss', 'PySide6.QtSvg', 'PIL', 'src._embedded_key', 'src.injection_service', 'src.session_manager', 'src.permission_manager', 'src.memory_store', 'src.config', 'src.gemini_client']
tmp_ret = collect_all('google.genai')
datas += tmp_ret[0]; binaries += tmp_ret[1]; hiddenimports += tmp_ret[2]


a = Analysis(
    ['C:\\Users\\Amir\\SPEAK\\speak_app\\main.py'],
    pathex=[],
    binaries=binaries,
    datas=datas,
    hiddenimports=hiddenimports,
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=['tkinter', 'matplotlib', 'scipy', 'pandas', 'google.genai.tests', 'pycparser.lextab', 'pycparser.yacctab', 'tzdata', 'pkg_resources'],
    noarchive=False,
    optimize=1,
)
pyz = PYZ(a.pure)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.datas,
    [('O', None, 'OPTION')],
    name='SPEAK',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=False,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    version='C:\\Users\\Amir\\SPEAK\\speak_app\\version_info.txt',
    icon=['C:\\Users\\Amir\\SPEAK\\speak_app\\assets\\icon.ico'],
)
