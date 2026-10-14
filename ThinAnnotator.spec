# -*- mode: python ; coding: utf-8 -*-
# Build with scripts/build.py, or directly: pyinstaller --noconfirm ThinAnnotator.spec
# THINANNOTATOR_MODEL selects the bundled checkpoint (tiny, small, base_plus, large).
import os
import re
import sys
from pathlib import Path

from PyInstaller.utils.hooks import collect_all

ROOT = Path(SPECPATH)
IS_MAC = sys.platform == "darwin"

CHECKPOINTS = {
    "tiny": "sam2.1_hiera_tiny.pt",
    "small": "sam2.1_hiera_small.pt",
    "base_plus": "sam2.1_hiera_base_plus.pt",
    "large": "sam2.1_hiera_large.pt",
}
MODEL = os.environ.get("THINANNOTATOR_MODEL", "base_plus")
if MODEL not in CHECKPOINTS:
    raise SystemExit(f"Unknown THINANNOTATOR_MODEL '{MODEL}'. Use one of: {', '.join(CHECKPOINTS)}")
checkpoint = ROOT / "checkpoints" / CHECKPOINTS[MODEL]
if not checkpoint.is_file():
    raise SystemExit(f"Missing checkpoint {checkpoint}. Run scripts/build.py to download it.")

VERSION = re.search(r'^version = "([^"]+)"', (ROOT / "pyproject.toml").read_text(), re.M).group(1)

# The frozen app reads MODEL_SIZE at startup; this hook sets it to the bundled checkpoint.
runtime_hook = Path(workpath) / "rthook_model_size.py"
runtime_hook.parent.mkdir(parents=True, exist_ok=True)
runtime_hook.write_text(f'import os\nos.environ.setdefault("MODEL_SIZE", "{MODEL}")\n')

datas = [
    ("frontend_payload", "frontend_payload"),
    (str(checkpoint), "checkpoints"),
    ("assets", "assets"),
    ("docs", "docs"),
]
# sam2 configs, submodules and .py sources come from pyinstaller-hooks-contrib's hook-sam2.
binaries = []
hiddenimports = []
tmp_ret = collect_all("torch")
datas += tmp_ret[0]; binaries += tmp_ret[1]; hiddenimports += tmp_ret[2]

icon = "assets/ThinAnnotator.icns" if IS_MAC else "assets/ThinAnnotator.ico"

a = Analysis(
    ["launcher.py"],
    pathex=[],
    binaries=binaries,
    datas=datas,
    hiddenimports=hiddenimports,
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[str(runtime_hook)],
    excludes=[],
    noarchive=False,
    optimize=0,
)
pyz = PYZ(a.pure)

exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name="ThinAnnotator",
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon=icon,
)
coll = COLLECT(
    exe,
    a.binaries,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name="ThinAnnotator",
)
if IS_MAC:
    app = BUNDLE(
        coll,
        name="ThinAnnotator.app",
        icon=icon,
        bundle_identifier=None,
        version=VERSION,
        info_plist={
            "CFBundleShortVersionString": VERSION,
            "CFBundleVersion": VERSION,
            "NSHighResolutionCapable": True,
        },
    )
