from pathlib import Path
import os, sys, time, hashlib, threading

APP_NAME = "ThinAnnotator"


def get_writable_dir():
    # Option A: A hidden folder in the User's Home (Professional way)
    # macOS: /Users/name/.geosam
    # Windows: C:\Users\name\.geosam
    path = Path.home() / ".thinAnnotatorData"
    path.mkdir(parents=True, exist_ok=True)
    return path


def _cache_root():
    if sys.platform == "win32":
        base = os.environ.get("LOCALAPPDATA") or os.path.expanduser("~")
        return os.path.join(base, APP_NAME, "Cache", "png")
    if sys.platform == "darwin":
        return os.path.expanduser(f"~/Library/Caches/{APP_NAME}/png")
    base = os.environ.get("XDG_CACHE_HOME") or os.path.expanduser("~/.cache")
    return os.path.join(base, APP_NAME.lower(), "png")


def get_cache_dir():
    return Path(_cache_root())