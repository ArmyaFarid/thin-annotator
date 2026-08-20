import io
from PIL import Image

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


