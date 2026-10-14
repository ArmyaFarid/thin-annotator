"""Build the ThinAnnotator desktop app for the current OS.

Usage:
    uv run --locked python scripts/build.py [--model base_plus] [--frontend-dist PATH]

Output in dist/: ThinAnnotator-<version>-macos-<arch>.dmg on macOS,
ThinAnnotator-<version>-windows-<arch>.zip on Windows.
"""
import argparse
import hashlib
import os
import platform
import re
import shutil
import subprocess
import sys
import tempfile
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
CHECKPOINT_DIR = ROOT / "checkpoints"
CHECKPOINT_URL = "https://dl.fbaipublicfiles.com/segment_anything_2/092824/{}"
# SHA-256 of the SAM 2.1 checkpoints released 2024-09-28.
CHECKPOINTS = {
    "tiny": ("sam2.1_hiera_tiny.pt", "7402e0d864fa82708a20fbd15bc84245c2f26dff0eb43a4b5b93452deb34be69"),
    "small": ("sam2.1_hiera_small.pt", "6d1aa6f30de5c92224f8172114de081d104bbd23dd9dc5c58996f0cad5dc4d38"),
    "base_plus": ("sam2.1_hiera_base_plus.pt", "a2345aede8715ab1d5d31b4a509fb160c5a4af1970f199d9054ccfb746c004c5"),
    "large": ("sam2.1_hiera_large.pt", "2647878d5dfa5098f2f8649825738a9345572bae2d4350a2468587ece47dd318"),
}


def fail(message):
    print(f"error: {message}", file=sys.stderr)
    sys.exit(1)


def step(message):
    print(f"\n==> {message}", flush=True)


def check_environment():
    if sys.platform not in ("darwin", "win32"):
        fail(f"unsupported OS '{sys.platform}'. Build on macOS or Windows.")
    if sys.version_info[:2] != (3, 10):
        fail(f"Python 3.10 required, found {platform.python_version()}. Run through 'uv run'.")
    if Path(sys.prefix).resolve() != (ROOT / ".venv").resolve():
        fail(f"not running in the project environment ({sys.prefix}). Run 'uv run --locked python scripts/build.py'.")
    try:
        import PyInstaller  # noqa: F401
    except ImportError:
        fail("PyInstaller is missing. Run 'uv sync --locked'.")


def sha256(path):
    digest = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            digest.update(chunk)
    return digest.hexdigest()


def ensure_checkpoint(model):
    name, expected = CHECKPOINTS[model]
    path = CHECKPOINT_DIR / name
    if path.is_file():
        if sha256(path) == expected:
            print(f"{name}: cached, checksum OK")
            return
        print(f"{name}: checksum mismatch, downloading again")
    CHECKPOINT_DIR.mkdir(exist_ok=True)
    partial = path.with_suffix(".part")
    url = CHECKPOINT_URL.format(name)
    print(f"downloading {url}")
    with urllib.request.urlopen(url) as response, open(partial, "wb") as out:
        shutil.copyfileobj(response, out, 1 << 20)
    if sha256(partial) != expected:
        partial.unlink()
        fail(f"downloaded {name} does not match the expected checksum")
    partial.replace(path)
    print(f"{name}: downloaded, checksum OK")


def copy_frontend(dist):
    dist = Path(dist).resolve()
    if not (dist / "index.html").is_file():
        fail(f"{dist} has no index.html. Run 'yarn build' in the editor project first.")
    payload = ROOT / "frontend_payload"
    shutil.rmtree(payload, ignore_errors=True)
    shutil.copytree(dist, payload)
    print(f"copied {dist} -> frontend_payload/")


def run_pyinstaller(model):
    env = {**os.environ, "THINANNOTATOR_MODEL": model}
    subprocess.run(
        [sys.executable, "-m", "PyInstaller", "--noconfirm", "--clean", "ThinAnnotator.spec"],
        cwd=ROOT,
        env=env,
        check=True,
    )


def package(version):
    arch = platform.machine().lower().replace("amd64", "x64").replace("x86_64", "x64")
    dist = ROOT / "dist"
    if sys.platform == "darwin":
        output = dist / f"ThinAnnotator-{version}-macos-{arch}.dmg"
        output.unlink(missing_ok=True)
        with tempfile.TemporaryDirectory() as staging:
            shutil.copytree(dist / "ThinAnnotator.app", Path(staging) / "ThinAnnotator.app", symlinks=True)
            (Path(staging) / "Applications").symlink_to("/Applications")
            subprocess.run(
                ["hdiutil", "create", "-volname", "ThinAnnotator", "-srcfolder", staging,
                 "-format", "UDZO", "-ov", str(output)],
                check=True,
            )
    else:
        output = dist / f"ThinAnnotator-{version}-windows-{arch}.zip"
        output.unlink(missing_ok=True)
        shutil.make_archive(str(output.with_suffix("")), "zip", dist, "ThinAnnotator")
    return output


def main():
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--model", choices=CHECKPOINTS, default="base_plus",
                        help="SAM 2.1 checkpoint to bundle (default: base_plus)")
    parser.add_argument("--frontend-dist", metavar="PATH",
                        help="editor build output to copy into frontend_payload/ (default: keep the committed one)")
    args = parser.parse_args()

    version = re.search(r'^version = "([^"]+)"', (ROOT / "pyproject.toml").read_text(), re.M).group(1)

    step("Checking environment")
    check_environment()
    step(f"Checkpoint: {args.model}")
    ensure_checkpoint(args.model)
    if args.frontend_dist:
        step("Frontend")
        copy_frontend(args.frontend_dist)
    step("PyInstaller")
    run_pyinstaller(args.model)
    step("Packaging")
    output = package(version)
    print(f"\nBuilt {output} ({output.stat().st_size / 1e6:.0f} MB)")


if __name__ == "__main__":
    main()
