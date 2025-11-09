# -*- coding: utf-8 -*-
"""
🛡️ Safety Guard — Protects the Awa
Blocks destructive ops (delete/rename) across .mauri, .env, supabase/, migrations/, and config files.
Enable/disable safely; integrates with FastAPI lifespan.
"""

from __future__ import annotations
import os
import pathlib
import contextlib
from typing import Callable, Optional

# Absolute-protected anchors (directory names or files)
PROTECTED_ANCHORS = {".mauri", ".env", "supabase", "migrations", "backend/config.yaml"}

# Optional dev override: set TI_ALLOW_DESTRUCTIVE=1 to bypass protections.
DEV_BYPASS_ENV = "TI_ALLOW_DESTRUCTIVE"

# Keep originals so we can restore cleanly
_ORIG_REMOVE: Optional[Callable] = None
_ORIG_RMDIR: Optional[Callable] = None
_ORIG_RENAME: Optional[Callable] = None

def _is_protected(path: str) -> bool:
    """True if path or any ancestor is under a protected anchor."""
    if os.environ.get(DEV_BYPASS_ENV) == "1":
        return False
    p = pathlib.Path(path).resolve()
    # direct file match first
    for anchor in PROTECTED_ANCHORS:
        if p.as_posix().endswith(anchor):
            return True
    # ancestor directory match
    for parent in [p] + list(p.parents):
        if parent.name in PROTECTED_ANCHORS:
            return True
    return False

def _block(msg: str):
    try:
        from Te_Po.utils.logger import get_logger  # optional
        get_logger(__name__).warning(msg)
    except Exception:
        print(msg)

def _safe_remove(path: str):
    if _is_protected(path):
        _block(f"⚠️  SafetyGuard: blocked os.remove('{path}')")
        return
    return _ORIG_REMOVE(path)

def _safe_rmdir(path: str):
    if _is_protected(path):
        _block(f"⚠️  SafetyGuard: blocked os.rmdir('{path}')")
        return
    return _ORIG_RMDIR(path)

def _safe_rename(src: str, dst: str):
    if _is_protected(src) or _is_protected(dst):
        _block(f"⚠️  SafetyGuard: blocked os.rename('{src}', '{dst}')")
        return
    return _ORIG_RENAME(src, dst)

def enable() -> None:
    """Monkey-patch os destructive calls (idempotent)."""
    global _ORIG_REMOVE, _ORIG_RMDIR, _ORIG_RENAME
    if _ORIG_REMOVE is not None:
        return  # already enabled
    _ORIG_REMOVE = os.remove
    _ORIG_RMDIR = os.rmdir
    _ORIG_RENAME = os.rename
    os.remove = _safe_remove  # type: ignore[assignment]
    os.rmdir = _safe_rmdir    # type: ignore[assignment]
    os.rename = _safe_rename  # type: ignore[assignment]
    _block("🛡️  SafetyGuard active — destructive ops blocked.")

def disable() -> None:
    """Restore original os functions (idempotent)."""
    global _ORIG_REMOVE, _ORIG_RMDIR, _ORIG_RENAME
    if _ORIG_REMOVE is None:
        return
    os.remove = _ORIG_REMOVE  # type: ignore[assignment]
    os.rmdir  = _ORIG_RMDIR   # type: ignore[assignment]
    os.rename = _ORIG_RENAME  # type: ignore[assignment]
    _ORIG_REMOVE = _ORIG_RMDIR = _ORIG_RENAME = None
    _block("🛡️  SafetyGuard disabled — destructive ops restored.")

@contextlib.contextmanager
def safety_guard():
    """Context-manager for temporary protection."""
    enable()
    try:
        yield
    finally:
        disable()

# Optional convenience wrappers for callers (e.g., carver.py)
def safe_remove(path: str): return _safe_remove(path)
def safe_rmdir(path: str):  return _safe_rmdir(path)
def safe_rename(src: str, dst: str): return _safe_rename(src, dst)
# Enable by default
enable()