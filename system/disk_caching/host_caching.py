import os, sys, time, hashlib, threading

APP_NAME = "FOVViewer"
TTL_SECONDS = 24 * 3600
MAX_BYTES = 2 * 1024 * 1024 * 1024   # None to disable the cap
SWEEP_EVERY = 600


def _cache_root():
    if sys.platform == "win32":
        base = os.environ.get("LOCALAPPDATA") or os.path.expanduser("~")
        return os.path.join(base, APP_NAME, "Cache", "png")
    if sys.platform == "darwin":
        return os.path.expanduser(f"~/Library/Caches/{APP_NAME}/png")
    base = os.environ.get("XDG_CACHE_HOME") or os.path.expanduser("~/.cache")
    return os.path.join(base, APP_NAME.lower(), "png")


CACHE_DIR = _cache_root()
_locks = {}
_locks_guard = threading.Lock()


def _key_path(src, mtime_ns, size):
    h = hashlib.sha256(f"{src}|{mtime_ns}|{size}".encode()).hexdigest()
    return os.path.join(CACHE_DIR, h[:2], h + ".png")


def _lock_for(path):
    with _locks_guard:
        lk = _locks.get(path)
        if lk is None:
            lk = _locks[path] = threading.Lock()
        return lk