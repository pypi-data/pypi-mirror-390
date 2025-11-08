"""Modal deployment helper for the Pokémon Emerald speedrun task app example.

This reproduces the manual setup described in the README:

- Clone `pokeagent-speedrun` and install its Python (and mGBA) dependencies.
- Mount the Synth AI repository so the task app can be imported directly.
- Mount a Modal volume that stores the ROM and savestates used by the environment.

Deploy with:

```
modal deploy examples/task_apps/pokemon_emerald/modal_app.py
```

Before deploying, upload `emerald.gba` and any required savestate files to the
`pokemon-emerald-assets` volume (see the README for `modal volume put` examples).
"""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path

import modal

REPO_ROOT = Path(__file__).resolve().parents[3]
POKEAGENT_SPEEDRUN_REPO = "https://github.com/sethkarten/pokeagent-speedrun.git"

app = modal.App("pokemon-emerald-task-app-example")

BASE_IMAGE = (
    modal.Image.debian_slim(python_version="3.11")
    .apt_install(
        "git",
        "cmake",
        "ninja-build",
        "build-essential",
        "pkg-config",
        "libpng-dev",
        "libzip-dev",
        "libepoxy-dev",
        "libavcodec-dev",
        "libavformat-dev",
        "libavutil-dev",
        "libswscale-dev",
        "zlib1g-dev",
        "libgles2-mesa-dev",
        "libegl1-mesa-dev",
    )
    .pip_install(["uvicorn[standard]", "fastapi", "httpx", "horizons-ai"])
    .run_commands(
        [
            "mkdir -p /external",
            f"if [ ! -d /external/pokeagent-speedrun ]; then git clone --depth 1 {POKEAGENT_SPEEDRUN_REPO} /external/pokeagent-speedrun; fi",
            "pip install --no-cache-dir -r /external/pokeagent-speedrun/requirements.txt",
        ]
    )
)

REPO_MOUNT = modal.Mount.from_local_dir(REPO_ROOT, remote_path="/workspace/synth-ai")
ASSET_VOLUME = modal.Volume.from_name("pokemon-emerald-assets", create_if_missing=True)


@app.function(
    image=BASE_IMAGE,
    mounts=[REPO_MOUNT],
    volumes={"/assets": ASSET_VOLUME},
    timeout=900,
    memory=9216,
    cpu=4.0,
    secrets=[modal.Secret.from_name("environment-api-key")],
    keep_warm=1,
)
@modal.asgi_app()
def fastapi_app():
    """Serve the Synth task app via Modal."""

    import os

    repo_path = Path("/workspace/synth-ai").resolve()
    if str(repo_path) not in sys.path:
        sys.path.insert(0, str(repo_path))

    marker = Path("/tmp/.synth_ai_editable")
    if not marker.exists():
        subprocess.check_call([sys.executable, "-m", "pip", "install", "-e", str(repo_path)])
        marker.touch()

    os.environ.setdefault("POKEAGENT_SPEEDRUN_ROOT", "/external/pokeagent-speedrun")
    os.environ.setdefault("POKEMON_EMERALD_ASSETS", "/assets")

    rom_path = Path(os.getenv("POKEMON_EMERALD_ROM", "/assets/emerald.gba"))
    if not rom_path.exists():
        raise RuntimeError(
            f"Missing ROM at {rom_path}. Upload it with "
            "\"modal volume put pokemon-emerald-assets emerald.gba\" before deployment."
        )

    from examples.task_apps.pokemon_emerald.task_app.pokemon_emerald import build_config
    from synth_ai.task.server import create_task_app

    return create_task_app(build_config())


@app.local_entrypoint()
def main():
    """Print usage hints for local operators."""

    print("Pokémon Emerald task app Modal helper")
    print("Upload assets: modal volume put pokemon-emerald-assets /path/to/emerald.gba")
    print("Optional savestates can also be uploaded to the same volume.")
    print("Deploy with: modal deploy examples/task_apps/pokemon_emerald/modal_app.py")
    print("Test locally: modal serve examples/task_apps/pokemon_emerald/modal_app.py")
