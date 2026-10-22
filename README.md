# ThinAnnotator

Desktop annotation tool for thin-section images, based on SAM 2.

## Requirements

- [uv](https://docs.astral.sh/uv/). uv installs Python 3.10 and all dependencies from `uv.lock`.
  - macOS: `curl -LsSf https://astral.sh/uv/install.sh | sh`
  - Windows (PowerShell): `powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"`
- About 1 GB of free disk space for the environment and one model checkpoint.

## Run from source

1. Run `uv sync --locked`.
   uv creates `.venv` with the exact versions in `uv.lock`.
2. Put a SAM 2.1 checkpoint in `checkpoints/`.
   The default model is `base_plus`:
   ```bash
   mkdir -p checkpoints
   curl -L -o checkpoints/sam2.1_hiera_base_plus.pt \
     https://dl.fbaipublicfiles.com/segment_anything_2/092824/sam2.1_hiera_base_plus.pt
   ```
   To use another model, download its checkpoint and set `MODEL_SIZE` to `tiny`, `small` or `large`.
3. Run `uv run python launcher.py`.
   The control panel opens.
4. Click **Start Server**.
   The server listens on `http://127.0.0.1:7263/`.

| Page | URL |
|---|---|
| Editor | http://127.0.0.1:7263/ |
| User guide | http://127.0.0.1:7263/docs/user-guide/ |
| User guide (FR) | http://127.0.0.1:7263/docs/user-guide/index.fr.html |

## Build the desktop app

Build on the target OS: build on a Mac for macOS and on Windows for Windows.

1. Run `uv sync --locked`.
2. Run `uv run --locked python scripts/build.py`.
   The script downloads the checkpoint if `checkpoints/` does not have it, verifies its SHA-256, runs PyInstaller and packages the app.
3. Find the result in `dist/`:
   - macOS: `ThinAnnotator-<version>-macos-<arch>.dmg`
   - Windows: `ThinAnnotator-<version>-windows-<arch>.zip`

Options:

- `--model tiny|small|base_plus|large`: the checkpoint to bundle. The default is `base_plus`. The app bundles only this checkpoint.
- `--frontend-dist PATH`: copy a new editor build into `frontend_payload/` before the build. Without this option, the build uses the committed `frontend_payload/`.

To include a new editor build:

```bash
cd ../thin-annotator-editor
yarn build
cd ../thin-annotator
uv run --locked python scripts/build.py --frontend-dist ../thin-annotator-editor/dist
```

The version comes from `version` in `pyproject.toml`.

The macOS app is not signed. On another Mac, Gatekeeper blocks the first launch. Right-click the app and select **Open** to start it.

## Dependencies

- Change dependencies in `pyproject.toml`, then run `uv lock` and commit `uv.lock`.
- `constraint-dependencies` in `pyproject.toml` holds some transitive packages at tested versions.
- `sam2/` is vendored SAM 2 source with local changes. See `NOTICE`.
