"""Embedded fallback key - obfuscated. Never log, never display.
This key is used ONLY if user has no vault key. User BYOK always takes priority.
Key is split + XOR + base64 to avoid trivial strings dump.
Publisher: Amir Bagawan
"""
import base64

# XOR key derived from app identity (not secret, just obfuscation)
_XOR = b"SPEAK_AI_App_v2_AmirBagawan_2026"

# Key fragments (base64 of XORed original). Reassemble at runtime only.
_P1 = "EgFrAClnEwdpCAFIDQ5iFw5Z"
_P2 = "HhhwPlk9NikCJUBXR2YnNBMK"
_P3 = "BSgGLQUjJTM8AmhqMAhQKzU="


def _decode_embedded() -> str:
    try:
        raw = base64.b64decode(_P1 + _P2 + _P3)
        decoded = bytes(b ^ _XOR[i % len(_XOR)] for i, b in enumerate(raw))
        return decoded.decode("utf-8").strip()
    except Exception:
        return ""


_cached = None

def get_embedded_key() -> str:
    global _cached
    if _cached is not None:
        return _cached
    _cached = _decode_embedded()
    return _cached


def clear_cache():
    global _cached
    _cached = None
