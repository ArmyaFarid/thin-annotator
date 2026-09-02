#!/usr/bin/env python3
"""
Locate every FOV folder under a root directory.

An FOV folder is any directory holding at least one thin-section image whose
filename follows the pattern:

    T_017_proj-PI-99-3_tsn-TS-03_mod-PPL_rot-0_comp-na.<ext>

A callback is then run on each folder found.
"""

from __future__ import annotations

import argparse
import os
import re
from collections import Counter
from pathlib import Path
from typing import Callable, Iterator, Sequence

# --------------------------------------------------------------------------
# Configuration
# --------------------------------------------------------------------------

#: Extensions treated as "image". Lowercase, leading dot.
IMAGE_EXTENSIONS: frozenset[str] = frozenset({
    ".jpg", ".jpeg", ".png", ".tif", ".tiff",
    ".bmp", ".webp", ".exr", ".tga", ".dpx",
})

#: Filename stem pattern (extension excluded).
#: Token values may contain letters, digits and internal hyphens; the
#: underscore is reserved as the token separator.
STEM_PATTERN: re.Pattern[str] = re.compile(
    r"^T_(?P<index>\d+)"
    r"_proj-(?P<proj>[A-Za-z0-9]+(?:-[A-Za-z0-9]+)*)"
    r"_tsn-(?P<tsn>[A-Za-z0-9]+(?:-[A-Za-z0-9]+)*)"
    r"_mod-(?P<mod>[A-Za-z0-9]+)"
    r"_rot-(?P<rot>-?\d+)"
    r"_comp-(?P<comp>[A-Za-z0-9]+)$"
)


# --------------------------------------------------------------------------
# Core
# --------------------------------------------------------------------------

def iter_matching_files(
    root: str | os.PathLike[str],
    *,
    extensions: frozenset[str] | set[str] = IMAGE_EXTENSIONS,
    pattern: re.Pattern[str] = STEM_PATTERN,
    follow_symlinks: bool = False,
) -> Iterator[Path]:
    """Yield every file under `root` matching `pattern` + an image extension."""
    for dirpath, _dirnames, filenames in os.walk(root, followlinks=follow_symlinks):
        for name in filenames:
            stem, ext = os.path.splitext(name)
            if ext.lower() not in extensions:
                continue
            if pattern.match(stem):
                yield Path(dirpath) / name


def find_fov_folders(
    root: str | os.PathLike[str],
    *,
    extensions: frozenset[str] | set[str] = IMAGE_EXTENSIONS,
    pattern: re.Pattern[str] = STEM_PATTERN,
    dominant_extension_only: bool = False,
    follow_symlinks: bool = False,
) -> list[Path]:
    """
    Return the sorted, de-duplicated list of FOV folders (>= 1 matching image).

    Parameters
    ----------
    dominant_extension_only:
        False (default) -> any extension in `extensions` counts.
        True            -> count extensions across all matches, keep only the
                           single most frequent one, then derive the folders.
                           Ties are broken by first-seen order (Counter rule).
    follow_symlinks:
        Off by default; enabling it can loop on cyclic symlinks.
    """
    root_path = Path(root)
    if not root_path.is_dir():
        raise NotADirectoryError(f"Not a directory: {root_path}")

    matches = list(
        iter_matching_files(
            root_path,
            extensions=extensions,
            pattern=pattern,
            follow_symlinks=follow_symlinks,
        )
    )

    if dominant_extension_only and matches:
        counts = Counter(p.suffix.lower() for p in matches)
        top_ext, _ = counts.most_common(1)[0]
        matches = [p for p in matches if p.suffix.lower() == top_ext]

    return sorted({p.parent for p in matches})


# --------------------------------------------------------------------------
# Action hook
# --------------------------------------------------------------------------

def process_folder(folder: Path) -> None:
    """Placeholder action. Replace the body with the real work."""
    print(folder)


def apply_to_folders(
    folders: Sequence[Path],
    action: Callable[[Path], object] = process_folder,
) -> list[object]:
    """Run `action` on every folder, collecting return values."""
    return [action(folder) for folder in folders]


# --------------------------------------------------------------------------
# CLI
# --------------------------------------------------------------------------

def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("root", help="root folder to scan recursively for FOV folders")
    parser.add_argument(
        "--dominant-ext-only",
        action="store_true",
        help="keep only the most frequent image extension found",
    )
    parser.add_argument(
        "--follow-symlinks",
        action="store_true",
        help="descend into symlinked directories (risk of cycles)",
    )
    args = parser.parse_args(argv)

    folders = find_fov_folders(
        args.root,
        dominant_extension_only=args.dominant_ext_only,
        follow_symlinks=args.follow_symlinks,
    )
    apply_to_folders(folders)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())