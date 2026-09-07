import os, sys, time, hashlib, threading

from system.disk_caching.host_caching import CACHE_DIR, TTL_SECONDS, MAX_BYTES, SWEEP_EVERY


def sweep():
    now = time.time()
    entries = []
    print(CACHE_DIR)
    for root, _, files in os.walk(CACHE_DIR):
        for name in files:
            p = os.path.join(root, name)
            try:
                st = os.stat(p)
            except OSError:
                continue
            if name.endswith(".tmp") and now - st.st_mtime > 3600:
                _unlink(p)                      # orphaned from a crash
                continue
            if now - st.st_mtime > TTL_SECONDS:
                _unlink(p)
                continue
            entries.append((st.st_mtime, st.st_size, p))

    if MAX_BYTES is not None:
        total = sum(e[1] for e in entries)
        entries.sort()                          # oldest touch first
        for mtime, size, p in entries:
            if total <= MAX_BYTES:
                break
            if _unlink(p):
                total -= size


def _unlink(p):
    try:
        os.remove(p)
        return True
    except OSError:
        return False


def start_sweeper():
    def loop():
        while True:
            try:
                sweep()
            except Exception:
                pass
            time.sleep(SWEEP_EVERY)
    threading.Thread(target=loop, daemon=True).start()