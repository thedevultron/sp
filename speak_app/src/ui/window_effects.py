"""Windows 11 rounded corners + acrylic helpers — no deps.
Uses DwmSetWindowAttribute via ctypes. Safe no-op on non-Windows or older.
Fixes outline/border artifact on frameless translucent windows.
"""
import sys
import ctypes

def _is_windows() -> bool:
    return sys.platform.startswith("win")

def enable_rounded_corners(window) -> bool:
    """Apply Windows 11 rounded corners + remove 1px Win32 border artifact.
    Returns True if applied. Works for frameless WA_TranslucentBackground windows.
    """
    if not _is_windows():
        return False
    try:
        hwnd = int(window.winId())
        if not hwnd:
            return False
        ok = False
        # 1) Corner preference ROUND=2
        try:
            DWMWA_WINDOW_CORNER_PREFERENCE = 33
            DWMWCP_ROUND = 2
            corner = ctypes.c_int(DWMWCP_ROUND)
            ctypes.windll.dwmapi.DwmSetWindowAttribute(
                ctypes.c_void_p(hwnd),
                ctypes.c_int(DWMWA_WINDOW_CORNER_PREFERENCE),
                ctypes.byref(corner),
                ctypes.sizeof(corner),
            )
            ok = True
        except Exception:
            try:
                corner2 = ctypes.c_int(3)  # ROUNDSMALL
                ctypes.windll.dwmapi.DwmSetWindowAttribute(
                    ctypes.c_void_p(hwnd),
                    ctypes.c_int(33),
                    ctypes.byref(corner2),
                    ctypes.sizeof(corner2),
                )
                ok = True
            except Exception:
                pass
        # 2) Remove 1px border artifact: set border color transparent + extend frame
        try:
            # DWMWA_BORDER_COLOR = 34, COLORREF 0x00000000 (transparent)
            DWMWA_BORDER_COLOR = 34
            border = ctypes.c_int(0x00000000)
            # Use COLOR_NONE 0xFFFFFFFE to disable border (Win11 22H2+)
            try:
                COLOR_NONE = ctypes.c_int(0xFFFFFFFE)
                ctypes.windll.dwmapi.DwmSetWindowAttribute(
                    ctypes.c_void_p(hwnd),
                    ctypes.c_int(DWMWA_BORDER_COLOR),
                    ctypes.byref(COLOR_NONE),
                    ctypes.sizeof(COLOR_NONE),
                )
            except Exception:
                # Fallback try black
                ctypes.windll.dwmapi.DwmSetWindowAttribute(
                    ctypes.c_void_p(hwnd),
                    ctypes.c_int(DWMWA_BORDER_COLOR),
                    ctypes.byref(border),
                    ctypes.sizeof(border),
                )
        except Exception:
            pass
        # 3) Extend frame into client area to enable shadow and remove edge line
        try:
            class MARGINS(ctypes.Structure):
                _fields_ = [("cxLeftWidth", ctypes.c_int), ("cxRightWidth", ctypes.c_int),
                            ("cyTopHeight", ctypes.c_int), ("cyBottomHeight", ctypes.c_int)]
            m = MARGINS(-1, -1, -1, -1)
            ctypes.windll.dwmapi.DwmExtendFrameIntoClientArea(ctypes.c_void_p(hwnd), ctypes.byref(m))
        except Exception:
            pass
        return ok
    except Exception:
        return False

def enable_shadow(window) -> bool:
    return enable_rounded_corners(window)

def apply_mica_if_available(window) -> bool:
    if not _is_windows():
        return False
    try:
        hwnd = int(window.winId())
        DWMWA_SYSTEMBACKDROP_TYPE = 38
        DWMSBT_MAINWINDOW = 2
        backdrop = ctypes.c_int(DWMSBT_MAINWINDOW)
        try:
            ctypes.windll.dwmapi.DwmSetWindowAttribute(
                ctypes.c_void_p(hwnd),
                ctypes.c_int(DWMWA_SYSTEMBACKDROP_TYPE),
                ctypes.byref(backdrop),
                ctypes.sizeof(backdrop),
            )
            return True
        except Exception:
            return False
    except Exception:
        return False

def disable_window_border(window) -> bool:
    """Extra helper to ensure no WS_BORDER artifact via SetWindowLong."""
    if not _is_windows():
        return False
    try:
        hwnd = int(window.winId())
        GWL_STYLE = -16
        WS_BORDER = 0x00800000
        WS_THICKFRAME = 0x00040000
        GetWindowLongW = ctypes.windll.user32.GetWindowLongW
        SetWindowLongW = ctypes.windll.user32.SetWindowLongW
        style = GetWindowLongW(ctypes.c_void_p(hwnd), GWL_STYLE)
        style &= ~WS_BORDER
        # Keep thickframe for shadow? Remove if frameless
        try:
            # Only remove border, keep thickframe for resize if needed
            pass
        except Exception:
            pass
        SetWindowLongW(ctypes.c_void_p(hwnd), GWL_STYLE, style)
        # Redraw
        ctypes.windll.user32.SetWindowPos(ctypes.c_void_p(hwnd), None, 0,0,0,0, 0x0027)  # SWP_FRAMECHANGED|SWP_NOMOVE|SWP_NOSIZE|SWP_NOZORDER
        return True
    except Exception:
        return False
