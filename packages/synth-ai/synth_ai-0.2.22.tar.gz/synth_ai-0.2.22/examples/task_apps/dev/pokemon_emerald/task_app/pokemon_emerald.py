"""Task App configuration for the PokéAgent Emerald speedrun environment."""

from __future__ import annotations

import base64
import logging
import os
import sys
from dataclasses import dataclass
from io import BytesIO
from pathlib import Path
from typing import Any, Iterable, Sequence

from fastapi import HTTPException, Request

try:  # Optional dependency resolved at runtime during reset()
    from pokemon_env.emulator import EmeraldEmulator  # type: ignore
except Exception:  # pragma: no cover - handled later with explicit error
    EmeraldEmulator = None

from synth_ai.task.apps import ModalDeploymentConfig, TaskAppEntry, register_task_app
from synth_ai.task.contracts import (
    RolloutMetrics,
    RolloutRequest,
    RolloutResponse,
    RolloutStep,
    RolloutTrajectory,
    TaskInfo,
)
from synth_ai.task.datasets import TaskDatasetRegistry, TaskDatasetSpec
from synth_ai.task.server import ProxyConfig, TaskAppConfig

logger = logging.getLogger(__name__)


DATASET_SPEC = TaskDatasetSpec(
    id="pokemon_emerald_objectives",
    name="Pokémon Emerald Speedrun Objectives",
    version="0.1.0",
    splits=["train", "eval"],
    default_split="train",
    description="Savestate checkpoints for the PokéAgent Track 2 Emerald speedrun starter.",
)


def _resolve_repo_root(env_key: str, repo_dir: str) -> Path | None:
    env_path = os.getenv(env_key)
    if env_path:
        candidate = Path(env_path).expanduser()
        if candidate.exists():
            return candidate.resolve()

    here = Path(__file__).resolve()
    candidates: list[Path] = []
    for ancestor in here.parents:
        candidates.append(ancestor / "external" / repo_dir)
        candidates.append(ancestor / repo_dir)
    for candidate in candidates:
        try:
            resolved = candidate.resolve()
        except Exception:  # pragma: no cover - path resolution edge cases
            continue
        if resolved.exists():
            return resolved
    return None


def _ensure_on_path(path: Path | None) -> None:
    if not path:
        return
    path_str = str(path)
    if path_str not in sys.path:
        sys.path.insert(0, path_str)


def _maybe_resolve(path: Path | None) -> Path | None:
    if not path:
        return None
    try:
        return path.resolve()
    except Exception:
        return path


@dataclass(frozen=True)
class EmeraldScenario:
    seed: int
    name: str
    checkpoint_ref: str
    objective: str
    description: str
    timeout_steps: int
    tags: tuple[str, ...]


class PokemonEmeraldDataset:
    """In-memory catalogue of Emerald checkpoints and objectives."""

    def __init__(self, spec: TaskDatasetSpec) -> None:
        self.spec = spec
        self.repo_root = _resolve_repo_root("POKEAGENT_SPEEDRUN_ROOT", "pokeagent-speedrun")
        _ensure_on_path(self.repo_root)

        self._state_roots: list[Path] = []
        self._rom_roots: list[Path] = []
        assets_root_env = os.getenv("POKEMON_EMERALD_ASSETS")
        if assets_root_env:
            assets_path = Path(assets_root_env).expanduser()
            self._state_roots.append(assets_path)
            self._rom_roots.append(assets_path)
        if self.repo_root:
            self._state_roots.extend(
                [
                    self.repo_root / "Emerald-GBAdvance",
                    self.repo_root / "tests" / "states",
                    self.repo_root / "pokemon_env" / "states",
                ]
            )
            self._rom_roots.extend(
                [
                    self.repo_root / "Emerald-GBAdvance",
                    self.repo_root / "roms",
                ]
            )

        scenarios: list[EmeraldScenario] = [
            EmeraldScenario(
                seed=4001,
                name="littleroot_intro",
                checkpoint_ref="Emerald-GBAdvance/truck_start.state",
                objective="Exit the moving truck and meet May.",
                description="Spawn inside the Littleroot truck with dialogue mid-sequence.",
                timeout_steps=1800,
                tags=("tutorial", "movement"),
            ),
            EmeraldScenario(
                seed=4002,
                name="rustboro_split",
                checkpoint_ref="Emerald-GBAdvance/start.state",
                objective="Defeat Roxanne (Badge 1).",
                description="Start at Rustboro gym entrance with levelled Torchic party.",
                timeout_steps=7200,
                tags=("badge", "combat", "routing"),
            ),
            EmeraldScenario(
                seed=4003,
                name="mauville_goal",
                checkpoint_ref="Emerald-GBAdvance/quick_start_save.state",
                objective="Acquire HM06 Rock Smash and return to Wally.",
                description="Begins after Slateport with prepared inventory routing.",
                timeout_steps=5400,
                tags=("hm", "quest"),
            ),
        ]
        self._scenarios: dict[int, EmeraldScenario] = {s.seed: s for s in scenarios}
        self.default_seed = scenarios[0].seed

    @property
    def seeds(self) -> list[int]:
        return sorted(self._scenarios)

    @property
    def count(self) -> int:
        return len(self._scenarios)

    def resolve_seed(self, seed: int | None) -> int:
        if seed is None:
            return self.default_seed
        if seed not in self._scenarios:
            raise KeyError(f"Unknown Emerald seed: {seed}")
        return seed

    def describe_seed(self, seed: int) -> dict[str, Any]:
        scenario = self._scenarios.get(seed)
        if not scenario:
            raise KeyError(f"Unknown Emerald seed: {seed}")
        checkpoint_path = self._resolve_checkpoint(scenario.checkpoint_ref)
        return {
            "seed": seed,
            "name": scenario.name,
            "checkpoint_ref": scenario.checkpoint_ref,
            "checkpoint_path": str(checkpoint_path) if checkpoint_path else None,
            "objective": scenario.objective,
            "description": scenario.description,
            "timeout_steps": scenario.timeout_steps,
            "tags": list(scenario.tags),
            "assets_ready": checkpoint_path is not None,
        }

    def _resolve_checkpoint(self, reference: str) -> Path | None:
        ref = Path(reference)
        candidates: list[Path] = []
        if ref.is_absolute():
            candidates.append(ref)
        if self.repo_root:
            candidates.append(self.repo_root / reference)
        for base in self._state_roots:
            candidates.append(base / ref.name)
            candidates.append(base / reference)
        for candidate in candidates:
            if candidate.exists():
                return _maybe_resolve(candidate)
        return None


def _build_dataset_registry() -> tuple[TaskDatasetRegistry, PokemonEmeraldDataset]:
    registry = TaskDatasetRegistry()
    dataset = PokemonEmeraldDataset(DATASET_SPEC)
    registry.register(DATASET_SPEC, lambda _spec: dataset, cache=True)
    return registry, dataset


def _base_task_info(dataset: PokemonEmeraldDataset) -> TaskInfo:
    return TaskInfo(
        task={"id": "pokemon_emerald", "name": "Pokémon Emerald Speedrun", "version": "0.1.0"},
        environments=["pokemon_emerald"],
        action_space={
            "type": "structured",
            "schema": {
                "type": "object",
                "properties": {
                    "macro": {
                        "enum": [
                            "noop",
                            "step_up",
                            "step_down",
                            "step_left",
                            "step_right",
                            "press_a",
                            "press_b",
                            "press_start",
                            "press_select",
                            "open_menu",
                            "close_menu",
                            "mash_a",
                        ]
                    },
                    "frames": {"type": "integer", "minimum": 1, "maximum": 120},
                    "metadata": {"type": "object"},
                },
                "required": ["macro"],
            },
            "notes": "Macros expand to mGBA button sequences inside the Horizons adapter.",
        },
        observation={
            "summary": "Memory-derived game state plus base64-encoded RGB frame.",
            "keys": ["player_state", "party", "inventory", "flags", "frame_png"],
            "player_state": ["map_id", "x", "y", "facing", "badges"],
        },
        dataset={
            **DATASET_SPEC.model_dump(),
            "seed_count": dataset.count,
            "seeds": dataset.seeds,
            "source_repos": [
                "https://github.com/sethkarten/pokeagent-speedrun",
                "https://pokeagent.github.io/track2.html",
            ],
            "pokeagent_speedrun_root": str(dataset.repo_root) if dataset.repo_root else None,
        },
        rubric={
            "version": "1",
            "criteria_count": 3,
            "source": "inline",
            "summary": "Milestone completion, time penalties, and soft-lock avoidance.",
        },
        inference={
            "supports_proxy": True,
            "tool": {"name": "emerald_macro", "parallel_tool_calls": False},
            "endpoints": {
                "openai": "/proxy/v1/chat/completions",
                "groq": "/proxy/groq/v1/chat/completions",
            },
        },
        capabilities={
            "supports_rollout": True,
            "supports_env_lifecycle": True,
            "requires_api_key_header": True,
        },
        limits={"max_steps": 10000, "max_time_s": 7200, "max_ops": 8192},
        task_metadata={
            "preferred_backend": "pokeagent-speedrun",
            "emulator": "mGBA",
            "documentation": "https://github.com/sethkarten/pokeagent-speedrun",
        },
    )


def describe_taskset(dataset: PokemonEmeraldDataset) -> dict[str, Any]:
    return {
        **DATASET_SPEC.model_dump(),
        "count": dataset.count,
        "seeds": dataset.seeds,
        "assets_ready": all(dataset.describe_seed(seed)["assets_ready"] for seed in dataset.seeds),
    }


def provide_task_instances(
    dataset: PokemonEmeraldDataset, base_info: TaskInfo, seeds: Sequence[int]
) -> Iterable[TaskInfo]:
    infos: list[TaskInfo] = []
    for seed_value in seeds:
        resolved_seed = dataset.resolve_seed(seed_value)
        details = dataset.describe_seed(resolved_seed)
        infos.append(
            TaskInfo(
                task=base_info.task,
                environments=base_info.environments,
                action_space=base_info.action_space,
                observation={
                    **base_info.observation,
                    "seed": resolved_seed,
                    "checkpoint_ref": details["checkpoint_ref"],
                    "objective": details["objective"],
                    "timeout_steps": details["timeout_steps"],
                },
                dataset={**base_info.dataset, "seed": resolved_seed, "scenario": details},
                rubric=base_info.rubric,
                inference=base_info.inference,
                capabilities=base_info.capabilities,
                limits=base_info.limits,
                task_metadata={
                    **base_info.task_metadata,
                    "tags": details["tags"],
                    "assets_ready": details["assets_ready"],
                },
            )
        )
    return infos


class PokemonEmeraldAdapter:
    """Adapter around pokeagent-speedrun's mGBA wrapper with snapshot support."""

    DEFAULT_STEP_PENALTY = 0.01
    BADGE_REWARD = 10.0
    LOCATION_REWARD = 0.5

    MACRO_BUTTONS: dict[str, list[str]] = {
        "noop": [],
        "press_a": ["a"],
        "press_b": ["b"],
        "press_start": ["start"],
        "press_select": ["select"],
        "step_up": ["up"],
        "step_down": ["down"],
        "step_left": ["left"],
        "step_right": ["right"],
        "open_menu": ["start"],
        "close_menu": ["b"],
        "mash_a": ["a"],
    }

    def __init__(
        self,
        *,
        scenario: dict[str, Any],
        rom_path: Path,
        frames_per_step: int = 6,
        step_penalty: float = DEFAULT_STEP_PENALTY,
    ) -> None:
        if EmeraldEmulator is None:
            raise RuntimeError(
                "pokemon_env.emulator.EmeraldEmulator import failed. "
                "Install pokeagent-speedrun with mgba dependencies before running this adapter."
            )

        if not rom_path.exists():
            raise FileNotFoundError(
                f"Pokémon Emerald ROM not found at {rom_path}. "
                "Set POKEMON_EMERALD_ROM or upload emerald.gba to the deployment volume."
            )

        checkpoint_ref = scenario.get("checkpoint_ref")
        checkpoint_path = scenario.get("checkpoint_path")
        if not checkpoint_path or not Path(checkpoint_path).exists():
            raise FileNotFoundError(
                f"Savestate for scenario '{scenario['name']}' not found at {checkpoint_path} "
                f"(reference: {checkpoint_ref})."
            )

        self.scenario = scenario
        self.rom_path = rom_path
        self.checkpoint_path = Path(checkpoint_path)
        self.frames_per_step = frames_per_step
        self.step_penalty = step_penalty
        self.timeout_steps = int(scenario.get("timeout_steps") or 0)

        self._emu: EmeraldEmulator | None = None
        self._step_count = 0
        self._episode_return = 0.0
        self._prev_badges = 0
        self._prev_location: str | None = None

    def reset(self) -> dict[str, Any]:
        self.close()
        self._emu = EmeraldEmulator(str(self.rom_path), headless=True, sound=False)
        self._emu.initialize()
        self._emu.load_state(path=str(self.checkpoint_path))

        self._step_count = 0
        self._episode_return = 0.0

        obs = self._build_observation()
        self._prev_badges = len(obs["player_state"].get("badges", []))
        self._prev_location = obs["player_state"].get("location")
        return obs

    def step(self, action: dict[str, Any]) -> tuple[dict[str, Any], float, bool, dict[str, Any]]:
        if self._emu is None:
            raise RuntimeError("Environment not initialised. Call reset() first.")

        macro = (action or {}).get("macro")
        if macro not in self.MACRO_BUTTONS:
            raise ValueError(
                f"Unsupported macro '{macro}'. "
                f"Valid macros: {sorted(self.MACRO_BUTTONS)}"
            )
        frames = int(action.get("frames") or self.frames_per_step)
        frames = max(1, min(frames, 120))

        buttons = self.MACRO_BUTTONS[macro]
        for _ in range(frames):
            self._emu.run_frame_with_buttons(buttons)

        obs = self._build_observation()
        reward = self._compute_reward(obs, macro)
        self._episode_return += reward
        self._step_count += 1

        done = bool(self.timeout_steps and self._step_count >= self.timeout_steps)
        info = {
            "macro": macro,
            "frames": frames,
            "step_count": self._step_count,
            "episode_return": self._episode_return,
        }
        return obs, reward, done, info

    def snapshot(self) -> bytes:
        if self._emu is None:
            raise RuntimeError("Environment not initialised. Call reset() first.")
        state_bytes = self._emu.save_state()
        if state_bytes is None:
            raise RuntimeError("Failed to capture Emerald savestate bytes.")
        return bytes(state_bytes)

    def restore(self, snapshot_bytes: bytes) -> dict[str, Any]:
        if self._emu is None:
            raise RuntimeError("Environment not initialised. Call reset() first.")
        self._emu.load_state(state_bytes=snapshot_bytes)
        obs = self._build_observation()
        self._prev_badges = len(obs["player_state"].get("badges", []))
        self._prev_location = obs["player_state"].get("location")
        return obs

    def close(self) -> None:
        if self._emu is not None:
            try:
                self._emu.stop()
            except Exception:  # pragma: no cover - best effort clean-up
                pass
        self._emu = None

    # -- helpers -------------------------------------------------------
    def _encode_frame(self, image) -> str | None:
        if image is None:
            return None
        buffer = BytesIO()
        image.save(buffer, format="PNG")
        encoded = base64.b64encode(buffer.getvalue()).decode("ascii")
        return f"data:image/png;base64,{encoded}"

    def _build_observation(self) -> dict[str, Any]:
        if self._emu is None or self._emu.memory_reader is None:
            raise RuntimeError("Emerald emulator not initialised.")

        state = self._emu.get_comprehensive_state()
        player = state.get("player", {})
        game = state.get("game", {})
        visual = state.get("visual", {})
        frame_encoded = self._encode_frame(visual.get("screenshot"))

        badges = game.get("badges") or []
        location = player.get("location")
        coords = player.get("position") or {}

        summary_bits = [
            f"Location: {location}",
            f"Position: ({coords.get('x')}, {coords.get('y')})",
            f"Badges: {len(badges)}",
        ]
        if game.get("game_state"):
            summary_bits.append(f"State: {game['game_state']}")
        if game.get("is_in_battle"):
            summary_bits.append("In battle")

        observation = {
            "player_state": {
                "name": player.get("name"),
                "position": coords,
                "facing": player.get("facing"),
                "location": location,
                "badges": badges,
                "game_time": game.get("time"),
            },
            "party": game.get("party"),
            "inventory": game.get("items"),
            "flags": {
                "game_state": game.get("game_state"),
                "in_battle": bool(game.get("is_in_battle")),
            },
            "frame_png": frame_encoded,
            "text": " | ".join(filter(None, summary_bits)),
        }
        return observation

    def _compute_reward(self, observation: dict[str, Any], macro: str) -> float:
        reward = -self.step_penalty

        badge_count = len(observation["player_state"].get("badges", []))
        if badge_count > self._prev_badges:
            reward += (badge_count - self._prev_badges) * self.BADGE_REWARD

        location = observation["player_state"].get("location")
        if location and location != self._prev_location:
            reward += self.LOCATION_REWARD

        if macro in {"press_a", "open_menu"}:
            reward += 0.02

        self._prev_badges = badge_count
        self._prev_location = location
        return reward


async def rollout_executor(request: RolloutRequest, fastapi_request: Request) -> RolloutResponse:
    dataset: PokemonEmeraldDataset | None = fastapi_request.app.state.get("emerald_dataset")
    if dataset is None:
        raise HTTPException(status_code=500, detail="Emerald dataset missing from app state.")

    seed = dataset.resolve_seed(request.env.seed)
    scenario = dataset.describe_seed(seed)

    rom_candidates: list[Path] = []
    env_rom = os.getenv("POKEMON_EMERALD_ROM")
    if env_rom:
        rom_candidates.append(Path(env_rom).expanduser())

    assets_root = os.getenv("POKEMON_EMERALD_ASSETS")
    if assets_root:
        rom_candidates.append(Path(assets_root).expanduser() / "emerald.gba")

    # Fallback relative to checkpoint directory
    rom_candidates.append(Path(scenario["checkpoint_ref"]).resolve().parent / "rom.gba")

    rom_path = next((candidate for candidate in rom_candidates if candidate.exists()), None)
    if rom_path is None:
        raise HTTPException(
            status_code=500,
            detail=(
                "Unable to locate Pokémon Emerald ROM. "
                "Set POKEMON_EMERALD_ROM or place emerald.gba alongside the savestates."
            ),
        )

    frames_per_step = int(request.env.config.get("frames_per_step", 6))
    adapter = PokemonEmeraldAdapter(
        scenario=scenario,
        rom_path=rom_path,
        frames_per_step=frames_per_step,
    )

    try:
        obs0 = adapter.reset()
        steps: list[RolloutStep] = [
            RolloutStep(
                obs=obs0,
                tool_calls=[],
                reward=0.0,
                done=False,
                info={"available_macros": sorted(PokemonEmeraldAdapter.MACRO_BUTTONS)},
            ),
        ]

        total_reward = 0.0
        done = False

        for op in request.ops or []:
            if done:
                break
            action_payload = op.get("action") if isinstance(op, dict) else op
            if action_payload is None:
                continue
            obs, reward, done, info = adapter.step(action_payload)
            total_reward += reward
            steps.append(
                RolloutStep(obs=obs, tool_calls=[], reward=reward, done=done, info=info),
            )

        final_obs = steps[-1].obs if steps else obs0
        metrics = RolloutMetrics(
            episode_returns=[total_reward],
            mean_return=total_reward,
            num_steps=max(len(steps) - 1, 0),
            num_episodes=1,
            outcome_score=total_reward,
            details={
                "seed": seed,
                "scenario": scenario["name"],
                "checkpoint_ref": scenario["checkpoint_ref"],
                "assets_ready": scenario["assets_ready"],
            },
        )

        trajectory = RolloutTrajectory(
            env_id="pokemon_emerald",
            policy_id=request.policy.policy_id or "policy",
            steps=steps,
            final={"observation": final_obs, "reward": total_reward, "done": done},
            length=len(steps),
        )

        return RolloutResponse(
            run_id=request.run_id,
            trajectories=[trajectory],
            branches={},
            metrics=metrics,
            aborted=False,
            ops_executed=len(request.ops or []),
            trace=None,
        )
    finally:
        adapter.close()


def build_config() -> TaskAppConfig:
    registry, dataset = _build_dataset_registry()
    base_info = _base_task_info(dataset)
    config = TaskAppConfig(
        app_id="pokemon_emerald",
        name="Pokémon Emerald Task App",
        description="Expose Emerald speedrun checkpoints via the Synth AI task framework.",
        base_task_info=base_info,
        describe_taskset=lambda: describe_taskset(dataset),
        provide_task_instances=lambda seeds: provide_task_instances(dataset, base_info, seeds),
        rollout=rollout_executor,
        dataset_registry=registry,
        proxy=ProxyConfig(
            enable_openai=True,
            enable_groq=True,
            system_hint="Respond with Emerald macro actions encoded as JSON.",
        ),
        app_state={"emerald_dataset": dataset},
        require_api_key=True,
        expose_debug_env=True,
        cors_origins=["*"],
    )
    return config


register_task_app(
    entry=TaskAppEntry(
        app_id="pokemon_emerald",
        description="Pokémon Emerald (Track 2) task app skeleton.",
        config_factory=build_config,
        aliases=("pokemon_speedrun", "pokemon_track2"),
        env_files=(),
        modal=ModalDeploymentConfig(
            app_name="pokemon-emerald-task-app",
            python_version="3.11",
            pip_packages=("horizons-ai",),
            extra_local_dirs=(
                ("repo", "/opt/synth_ai_repo"),
                ("pokeagent_speedrun", "/external/pokeagent-speedrun"),
            ),
            secret_names=("ENVIRONMENT_API_KEY", "OPENAI_API_KEY", "GROQ_API_KEY"),
            timeout=900,
            memory=9216,
            cpu=4.0,
        ),
    )
)


__all__ = ["build_config"]
