"""Lucide icons provider — renders Lucide SVG paths into QIcon/QPixmap via QSvgRenderer.
Apple/Stripe minimal: stroke-based, 1.75px, rounded caps.
No emojis. Colors are monochrome, tinted via currentColor.
"""
from PySide6.QtGui import QIcon, QPixmap, QPainter
from PySide6.QtCore import QByteArray, QSize
from PySide6.QtSvg import QSvgRenderer

# Lucide stroke SVGs — 24x24 viewBox, strokeWidth 2, round caps
# extracted & simplified from https://lucide.dev
_ICON_PATHS = {
    # settings
    "settings": '<path d="M12 15a3 3 0 1 0 0-6 3 3 0 0 0 0 6z"/><path d="M19.4 15a1.65 1.65 0 0 0 .33 1.82l.06.06a2 2 0 0 1-2.83 2.83l-.06-.06A1.65 1.65 0 0 0 15 19.4a1.65 1.65 0 0 0-1 1.51V21a2 2 0 0 1-4 0v-.09a1.65 1.65 0 0 0-1-1.51 1.65 1.65 0 0 0-1.82-.33l-.06.06a2 2 0 0 1-2.83-2.83l.06-.06A1.65 1.65 0 0 0 4.6 15a1.65 1.65 0 0 0-1.51-1H3a2 2 0 0 1 0-4h.09a1.65 1.65 0 0 0 1.51-1 1.65 1.65 0 0 0-.33-1.82l-.06-.06a2 2 0 0 1 2.83-2.83l.06.06A1.65 1.65 0 0 0 9 4.6a1.65 1.65 0 0 0 1-1.51V3a2 2 0 0 1 4 0v.09a1.65 1.65 0 0 0 1 1.51 1.65 1.65 0 0 0 1.82.33l.06-.06a2 2 0 0 1 2.83 2.83l-.06.06A1.65 1.65 0 0 0 19.4 9a1.65 1.65 0 0 0 1.51 1H21a2 2 0 0 1 0 4h-.09a1.65 1.65 0 0 0-1.51 1z"/>',
    "book-open": '<path d="M2 3h6a4 4 0 0 1 4 4v14a3 3 0 0 0-3-3H2z"/><path d="M22 3h-6a4 4 0 0 0-4 4v14a3 3 0 0 1 3-3h7z"/>',
    "mic": '<path d="M12 14a3 3 0 0 0 3-3V5a3 3 0 0 0-6 0v6a3 3 0 0 0 3 3z"/><path d="M19 10a7 7 0 0 1-14 0"/><line x1="12" y1="19" x2="12" y2="23"/><line x1="8" y1="23" x2="16" y2="23"/>',
    "monitor": '<rect x="2" y="3" width="20" height="14" rx="2"/><line x1="8" y1="21" x2="16" y2="21"/><line x1="12" y1="17" x2="12" y2="21"/>',
    "eye": '<path d="M1 12s4-8 11-8 11 8 11 8-4 8-11 8-11-8-11-8z"/><circle cx="12" cy="12" r="3"/>',
    "eye-off": '<path d="M9.88 9.88a3 3 0 1 0 4.24 4.24"/><path d="M10.73 5.08A10.94 10.94 0 0 1 12 5c7 0 11 8 11 8a13.39 13.39 0 0 1-1.67 2.68"/><path d="M6.61 6.61A13.52 13.52 0 0 0 1 12s4 8 11 8a9.08 9.08 0 0 0 5.39-1.61"/><line x1="2" y1="2" x2="22" y2="22"/>',
    "pen-tool": '<path d="M12 19l7-7a1.5 1.5 0 0 0-3-3L9 16l-4 1 1-4 7-7"/><path d="M12 19H5"/>',
    "x": '<line x1="18" y1="6" x2="6" y2="18"/><line x1="6" y1="6" x2="18" y2="18"/>',
    "copy": '<rect x="9" y="9" width="13" height="13" rx="2"/><path d="M5 15H4a2 2 0 0 1-2-2V4a2 2 0 0 1 2-2h9a2 2 0 0 1 2 2v3"/>',
    "trash-2": '<polyline points="3 6 5 6 21 6"/><path d="M19 6v14a2 2 0 0 1-2 2H7a2 2 0 0 1-2-2V6m3 0V4a2 2 0 0 1 2-2h4a2 2 0 0 1 2 2v2"/><line x1="10" y1="11" x2="10" y2="17"/><line x1="14" y1="11" x2="14" y2="17"/>',
    "plus": '<line x1="12" y1="5" x2="12" y2="19"/><line x1="5" y1="12" x2="19" y2="12"/>',
    "layers": '<polygon points="12 2 2 7 12 12 22 7 12 2"/><polyline points="2 17 12 22 22 17"/><polyline points="2 12 12 17 22 12"/>',
    "sparkles": '<path d="M12 3l1.88 5.12L19 10l-5.12 1.88L12 17l-1.88-5.12L5 10l5.12-1.88z"/><path d="M19 14l1 2 2 1-2 1-1 2-1-2-2-1 2-1z"/><path d="M5 14l1 2 2 1-2 1-1 2-1-2-2-1 2-1z"/>',
    "zap": '<polygon points="13 2 3 14 12 14 11 22 21 10 12 10 13 2"/>',
    "keyboard": '<rect x="2" y="4" width="20" height="16" rx="2"/><path d="M6 8h4"/><path d="M8 12h8"/><path d="M6 12h.01"/><path d="M10 16h6"/>',
    "shield": '<path d="M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10z"/>',
    "check": '<polyline points="20 6 9 17 4 12"/>',
    "alert-circle": '<circle cx="12" cy="12" r="10"/><line x1="12" y1="8" x2="12" y2="12"/><line x1="12" y1="16" x2="12.01" y2="16"/>',
    "info": '<circle cx="12" cy="12" r="10"/><line x1="12" y1="16" x2="12" y2="12"/><line x1="12" y1="8" x2="12.01" y2="8"/>',
    "chevron-down": '<polyline points="6 9 12 15 18 9"/>',
    "chevron-up": '<polyline points="18 15 12 9 6 15"/>',
    "maximize-2": '<polyline points="15 3 21 3 21 9"/><polyline points="9 21 3 21 3 15"/><line x1="21" y1="3" x2="14" y2="10"/><line x1="3" y1="21" x2="10" y2="14"/>',
    "more-horizontal": '<circle cx="12" cy="12" r="1"/><circle cx="19" cy="12" r="1"/><circle cx="5" cy="12" r="1"/>',
    "volume-2": '<polygon points="11 5 6 9 2 9 2 15 6 15 11 19 11 5"/><path d="M15.54 8.46a5 5 0 0 1 0 7.07"/><path d="M19.07 4.93a10 10 0 0 1 0 14.14"/>',
    "activity": '<polyline points="22 12 18 12 15 21 9 3 6 12 2 12"/>',
    "clock": '<circle cx="12" cy="12" r="10"/><polyline points="12 6 12 12 16 14"/>',
    "sliders": '<line x1="4" y1="21" x2="4" y2="14"/><line x1="4" y1="10" x2="4" y2="3"/><line x1="12" y1="21" x2="12" y2="12"/><line x1="12" y1="8" x2="12" y2="3"/><line x1="20" y1="21" x2="20" y2="16"/><line x1="20" y1="12" x2="20" y2="3"/><line x1="1" y1="14" x2="7" y2="14"/><line x1="9" y1="8" x2="15" y2="8"/><line x1="17" y1="16" x2="23" y2="16"/>',
    "hash": '<line x1="4" y1="9" x2="20" y2="9"/><line x1="4" y1="15" x2="20" y2="15"/><line x1="10" y1="3" x2="8" y2="21"/><line x1="16" y1="3" x2="14" y2="21"/>',
    "type": '<polyline points="4 7 4 4 20 4 20 7"/><line x1="9" y1="20" x2="15" y2="20"/><line x1="12" y1="4" x2="12" y2="20"/>',
    "wand": '<path d="M15 4V2"/><path d="M15 22v-2"/><path d="M4 15H2"/><path d="M22 15h-2"/><path d="M4.93 4.93l1.41 1.41"/><path d="M17.66 17.66l1.41 1.41"/><path d="M4.93 19.07l1.41-1.41"/><path d="M17.66 6.34l1.41-1.41"/><path d="M12 8a4 4 0 1 0 0 8 4 4 0 0 0 0-8z"/>',
    "refresh": '<polyline points="23 4 23 10 17 10"/><path d="M20.49 15a9 9 0 1 1-2.12-9.36L23 10"/>',
    "external": '<path d="M18 13v6a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2V8a2 2 0 0 1 2-2h6"/><polyline points="15 3 21 3 21 9"/><line x1="10" y1="14" x2="21" y2="3"/>',
    "lock": '<rect x="3" y="11" width="18" height="11" rx="2"/><path d="M7 11V7a5 5 0 0 1 10 0v4"/>',
    "unlock": '<rect x="3" y="11" width="18" height="11" rx="2"/><path d="M7 11V7a5 5 0 0 1 9.9-1"/>',
    "minus": '<line x1="5" y1="12" x2="19" y2="12"/>',
    "square": '<rect x="3" y="3" width="18" height="18" rx="2"/>',
    "minimize-2": '<polyline points="4 14 10 14 10 20"/><polyline points="20 10 14 10 14 4"/><line x1="10" y1="14" x2="21" y2="3"/><line x1="14" y1="10" x2="3" y2="21"/>',
    "chevrons-left": '<polyline points="11 17 6 12 11 7"/><polyline points="18 17 13 12 18 7"/>',
    "chevrons-right": '<polyline points="13 17 18 12 13 7"/><polyline points="6 17 11 12 6 7"/>',
    "shield-check": '<path d="M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10z"/><polyline points="9 12 11 14 15 10"/>',
    "circle-help": '<circle cx="12" cy="12" r="10"/><path d="M9.09 9a3 3 0 0 1 5.83 1c0 2-3 3-3 3"/><line x1="12" y1="17" x2="12.01" y2="17"/>',
    "help-circle": '<circle cx="12" cy="12" r="10"/><path d="M9.09 9a3 3 0 0 1 5.83 1c0 2-3 3-3 3"/><line x1="12" y1="17" x2="12.01" y2="17"/>',
}

_SVG_TEMPLATE = """<svg xmlns="http://www.w3.org/2000/svg" width="{size}" height="{size}" viewBox="0 0 24 24" fill="none" stroke="{color}" stroke-width="{stroke}" stroke-linecap="round" stroke-linejoin="round">{paths}</svg>"""

_DEFAULT_COLOR = "#C7D3EA"  # Authkit Moon Mist (monochrome frost)
_DEFAULT_STROKE = "1.85"

def _build_svg(name: str, color: str, stroke: str) -> bytes:
    inner = _ICON_PATHS.get(name, _ICON_PATHS["info"])
    svg = _SVG_TEMPLATE.format(paths=inner, size=24, color=color, stroke=stroke)
    return svg.encode("utf-8")

def icon(name: str, size: int = 16, color: str = None, stroke: str = None) -> QIcon:
    """Return QIcon for lucide name at requested pixel size."""
    c = color or _DEFAULT_COLOR
    s = stroke or _DEFAULT_STROKE
    pix = pixmap(name, size, c, s)
    ic = QIcon(pix)
    return ic

def pixmap(name: str, size: int = 16, color: str = None, stroke: str = None) -> QPixmap:
    c = color or _DEFAULT_COLOR
    s = stroke or _DEFAULT_STROKE
    svg_bytes = _build_svg(name, c, s)
    renderer = QSvgRenderer(QByteArray(svg_bytes))
    pm = QPixmap(size, size)
    pm.fill(0x00000000)  # transparent
    painter = QPainter(pm)
    painter.setRenderHint(QPainter.RenderHint.Antialiasing, True)
    renderer.render(painter)
    painter.end()
    return pm

def colored(icon_name: str, color: str, size: int = 16) -> QIcon:
    return icon(icon_name, size=size, color=color)
