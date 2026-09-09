import io
import os
import threading
import time

from PIL import Image

from system.disk_caching.host_caching import _key_path, TTL_SECONDS, _lock_for

# Pillow modes that PNG can carry with no pixel loss.
LOSSLESS_PNG_MODES = {"1", "L", "LA", "I;16", "I;16B", "I;16L", "P", "RGB", "RGBA"}


class LossyConversion(Exception):
    pass


def to_png_bytes(path, allow_lossy=False):
    with Image.open(path) as img:
        img.load()  # force decode while the file handle is open

        if getattr(img, "n_frames", 1) > 1 and not allow_lossy:
            raise LossyConversion(f"{img.n_frames} frames; PNG will keep only the first")

        mode = img.mode
        if mode not in LOSSLESS_PNG_MODES:
            if not allow_lossy:
                raise LossyConversion(f"mode {mode!r} has no lossless PNG representation")
            # CMYK -> RGB is a colorimetric conversion, not a re-container.
            img = img.convert("RGBA" if "A" in mode else "RGB")

        buf = io.BytesIO()
        img.save(
            buf,
            format="PNG",
            compress_level=9,
            icc_profile=img.info.get("icc_profile"),
        )
    buf.seek(0)
    return buf


def cached_png_path(src, mtime_ns, size):
    dst = _key_path(src, mtime_ns, size)

    try:
        age = time.time() - os.stat(dst).st_mtime
        if age < TTL_SECONDS:
            os.utime(dst, None)      # touch: extend lifetime on use
            return dst
    except OSError:
        pass

    with _lock_for(dst):
        try:                          # re-check: another thread may have built it
            if time.time() - os.stat(dst).st_mtime < TTL_SECONDS:
                return dst
        except OSError:
            pass

        data = to_png_bytes(src).getvalue()
        os.makedirs(os.path.dirname(dst), exist_ok=True)
        tmp = f"{dst}.{os.getpid()}.{threading.get_ident()}.tmp"
        with open(tmp, "wb") as f:
            f.write(data)
            f.flush()
            os.fsync(f.fileno())
        os.replace(tmp, dst)
        return dst