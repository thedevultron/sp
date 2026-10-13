"""Small local memory — Live agent can save/recall user facts across sessions.
Token-capped: max 30 facts, 140 chars each, total <=1500 chars (~350 tokens).
Stored at %APPDATA%/SPEAK_AI/user_memory.json, atomic write, sanitized.
"""
from __future__ import annotations
import json
import re
import time
import uuid

try:
    from src.config import CONFIG_DIR
except Exception:
    from pathlib import Path as _P
    import os as _os
    CONFIG_DIR = _P(_os.getenv("APPDATA", _P.home())) / "SPEAK_AI"

MEMORY_FILE = CONFIG_DIR / "user_memory.json"
MAX_FACTS = 30
MAX_FACT_CHARS = 140
MAX_TOTAL_CHARS = 1500

def _sanitize_fact(s: str) -> str:
    try:
        t = re.sub(r"[\x00-\x08\x0b\x0c\x0e-\x1f\x7f]", "", str(s or "")).strip()
        t = re.sub(r"\s+", " ", t)
        return t[:MAX_FACT_CHARS].strip()
    except Exception:
        return ""

def _load_raw() -> list:
    try:
        if not MEMORY_FILE.exists():
            return []
        data = json.loads(MEMORY_FILE.read_text(encoding="utf-8"))
        items = data.get("facts", []) if isinstance(data, dict) else []
        out = []
        for it in items:
            if not isinstance(it, dict):
                continue
            txt = _sanitize_fact(it.get("text", ""))
            if not txt:
                continue
            out.append({"id": str(it.get("id", uuid.uuid4().hex[:6])), "text": txt, "ts": float(it.get("ts", time.time()) or time.time())})
        return out[-MAX_FACTS:]
    except Exception:
        return []

def _save_raw(facts: list) -> None:
    try:
        CONFIG_DIR.mkdir(parents=True, exist_ok=True)
        # Enforce caps: newest-first trim to total chars
        facts = facts[-MAX_FACTS:]
        total = 0
        kept_rev = []
        for f in reversed(facts):
            t = _sanitize_fact(f.get("text", ""))
            if not t:
                continue
            if total + len(t) > MAX_TOTAL_CHARS:
                continue
            total += len(t)
            kept_rev.append({"id": str(f.get("id", uuid.uuid4().hex[:6])), "text": t, "ts": float(f.get("ts", time.time()))})
        kept = list(reversed(kept_rev))
        tmp = MEMORY_FILE.with_suffix(".tmp")
        tmp.write_text(json.dumps({"facts": kept, "updated": time.time()}, indent=2, ensure_ascii=False), encoding="utf-8")
        try:
            tmp.replace(MEMORY_FILE)
        except Exception:
            MEMORY_FILE.write_text(json.dumps({"facts": kept}, indent=2, ensure_ascii=False), encoding="utf-8")
    except Exception as e:
        print(f"[Memory] save note: {e}")

def list_facts() -> list:
    return _load_raw()

def add_fact(text: str) -> dict:
    txt = _sanitize_fact(text)
    if not txt:
        return {"ok": False, "reason": "empty"}
    facts = _load_raw()
    # Dedup (case-insensitive exact)
    low = txt.lower()
    for f in facts:
        if str(f.get("text", "")).lower() == low:
            return {"ok": True, "id": f.get("id"), "dedup": True}
    rec = {"id": uuid.uuid4().hex[:6], "text": txt, "ts": time.time()}
    facts.append(rec)
    _save_raw(facts)
    return {"ok": True, "id": rec["id"]}

def forget_fact(query: str) -> dict:
    q = str(query or "").strip().lower()
    if not q:
        return {"ok": False, "reason": "empty query"}
    facts = _load_raw()
    kept = []
    removed = 0
    for f in facts:
        fid = str(f.get("id", "")).lower()
        txt = str(f.get("text", "")).lower()
        if q == fid or q in txt:
            removed += 1
            continue
        kept.append(f)
    if removed:
        _save_raw(kept)
    return {"ok": bool(removed), "removed": removed}

def clear_all() -> None:
    try:
        _save_raw([])
    except Exception:
        pass

def memory_summary_block() -> str:
    facts = _load_raw()
    if not facts:
        return ""
    lines = [f"• {f['text']}" for f in facts[-MAX_FACTS:]]
    block = "User memory (persisted across sessions, keep replies consistent):\n" + "\n".join(lines)
    # Hard cap ~1200 chars so prompt stays small
    return block[:1200]

# ---- Live function declarations (token-cheap, two tools only) ----
# NON_BLOCKING: required by gemini-3.8-live-extended-thinking (async tools).
try:
    from google.genai import types as _types
    try:
        _NB = _types.Behavior.NON_BLOCKING
    except Exception:
        _NB = "NON_BLOCKING"
    MEMORY_TOOLS = [
        _types.Tool(function_declarations=[
            _types.FunctionDeclaration(
                name="save_memory",
                description="Save a small durable fact about the user (name, preference, project, vocabulary). Keep under 20 words.",
                behavior=_NB,
                parameters=_types.Schema(
                    type=_types.Type.OBJECT,
                    properties={"fact": _types.Schema(type=_types.Type.STRING, description="Short fact to remember.")},
                    required=["fact"],
                ),
            )
        ]),
        _types.Tool(function_declarations=[
            _types.FunctionDeclaration(
                name="forget_memory",
                description="Forget a memorized fact by id or keyword.",
                behavior=_NB,
                parameters=_types.Schema(
                    type=_types.Type.OBJECT,
                    properties={"query": _types.Schema(type=_types.Type.STRING, description="Fact id or keyword substring.")},
                    required=["query"],
                ),
            )
        ]),
    ]
except Exception:
    MEMORY_TOOLS = []
