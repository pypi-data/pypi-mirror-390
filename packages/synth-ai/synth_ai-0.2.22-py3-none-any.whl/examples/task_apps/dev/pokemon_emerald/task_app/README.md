# Pokemon Emerald Task App

This directory contains a task app for the PokéAgent Track 2 speedrunning
environment. It wraps the `pokeagent-speedrun` mGBA integration in the Horizons
environment API so agents trained with Synth AI can reset, step, snapshot, and
restore deterministically.

## Local setup (Track 2)

1. Clone and install the **pokeagent-speedrun** project (brings in the mGBA
   Python bindings and emulator helpers). A snapshot of the repository is
   vendored under `examples/task_apps/dev/pokemon_emerald/external/pokeagent-speedrun`,
   but you can also clone a separate working copy if you prefer to track upstream:

   ```bash
   git clone https://github.com/sethkarten/pokeagent-speedrun.git
   cd pokeagent-speedrun
   pip install -r requirements.txt
   ```

   Installing `mgba==0.10.2` may require system packages such as `cmake`,
   `ninja-build`, `pkg-config`, `libpng-dev`, `libzip-dev`, and the FFmpeg
   libraries listed in the repo README.

2. Provide a legal copy of the Pokémon Emerald ROM and any savestate
   checkpoints you wish to use. Place them in a known directory.

3. Export environment variables so the task app can locate both the repository
   and the assets:

   ```bash
   export POKEAGENT_SPEEDRUN_ROOT=/path/to/pokeagent-speedrun  # or the vendored path under examples/task_apps/dev/pokemon_emerald/external
   export POKEMON_EMERALD_ROM=/path/to/emerald.gba
   ```

4. Run a rollout to validate the wiring:

   ```bash
   uv run python -m synth_ai.task.describe pokemon_emerald
   uv run python -m synth_ai.task.rollout pokemon_emerald --seed 4001
   ```

## Modal deployment

`examples/task_apps/pokemon_emerald/modal_app.py` packages the same workflow for
Modal. It clones `pokeagent-speedrun`, installs dependencies (including mGBA),
and mounts a persistent volume (`pokemon-emerald-assets`) where you can upload
the ROM and savestates:

```bash
modal volume put pokemon-emerald-assets /path/to/emerald.gba
modal deploy examples/task_apps/pokemon_emerald/modal_app.py
```

After deployment, point Synth AI workflows at the issued `modal.run` URL.

## Notes (Not Yet Ready)

- The adapter currently requires manual mgba installation (`mgba==0.10.2`),
  which is not automated for Apple Silicon—treat this example as
  **experimental** until we land a turnkey build recipe.
- Dataset entries report savestate availability, but some scenarios may still
  lack assets locally; `/info` will surface this.
- Snapshot/restore wiring is complete, yet we have not validated
  deterministic parity across platforms pending a reliable mgba install flow.
- Actions are exposed as macro buttons; further tuning is needed once the
  runtime environment is stable.

## Status & Next Steps

- **Environment readiness (blocker)**: provide a reproducible mgba installation
  path (possibly via prebaked wheels or containerized build) before relying on
  this adapter.
- **Visual observations**: once runtime is reliable, keep the base64 PNG output
  and validate frame fidelity across platforms.
- **Macro tuning**: calibrate macro durations and add higher-level navigation
  macros.
- **Reward shaping**: extend badge/location bonuses with richer event hooks.
- **Stability checks**: add regression tests for snapshot/restore determinism.
- **Agent integration**: publish rollout scripts after environment setup is
  automated.
