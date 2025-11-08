"""
Trace hooks for Pokemon Red environment - v3 version.
Captures reward information and saves to Turso database.
"""

from datetime import datetime
from typing import Any, Dict, Optional

from synth_ai.tracing_v3.abstractions import BaseEvent, EnvironmentEvent
from synth_ai.tracing_v3.hooks import HookManager

# Pokemon Red achievement categories by reward value
EXPLORATION_ACHIEVEMENTS = {
    0.02: "explore_new_area",
    0.04: "explore_multiple_areas",
    1.0: "leave_starting_area",
    1.5: "enter_new_city",
    2.0: "explore_new_route",
    5.0: "enter_gym_building",
}

TRAINING_ACHIEVEMENTS = {
    0.2: "pokemon_level_up",
    0.3: "reach_power_level",
    3.0: "pokemon_ready_for_battle",
}

BATTLE_ACHIEVEMENTS = {
    0.1: "encounter_wild_pokemon",
}

RESOURCE_ACHIEVEMENTS = {
    0.05: "keep_pokemon_healthy",
    0.5: "find_valuable_item",
    0.8: "visit_pokemon_center",
}

MAJOR_ACHIEVEMENTS = {
    50.0: "defeat_brock_win_badge",
}


async def track_pokemon_rewards(event_obj: BaseEvent, **kwargs) -> Optional[Dict[str, Any]]:
    """Hook that captures detailed Pokemon Red reward information."""
    # Only process EnvironmentEvents
    if not isinstance(event_obj, EnvironmentEvent):
        return None

    reward = event_obj.reward
    if reward is None or reward == 0.0:
        return None

    # Determine achievement type based on reward value
    achievement_type = "unknown"
    achievement_category = "other"

    # Check each category
    if reward in EXPLORATION_ACHIEVEMENTS:
        achievement_type = EXPLORATION_ACHIEVEMENTS[reward]
        achievement_category = "exploration"
    elif reward in TRAINING_ACHIEVEMENTS:
        achievement_type = TRAINING_ACHIEVEMENTS[reward]
        achievement_category = "training"
    elif reward in BATTLE_ACHIEVEMENTS:
        achievement_type = BATTLE_ACHIEVEMENTS[reward]
        achievement_category = "battle"
    elif reward in RESOURCE_ACHIEVEMENTS:
        achievement_type = RESOURCE_ACHIEVEMENTS[reward]
        achievement_category = "resource"
    elif reward in MAJOR_ACHIEVEMENTS:
        achievement_type = MAJOR_ACHIEVEMENTS[reward]
        achievement_category = "major"

    return {
        "reward_value": reward,
        "achievement_type": achievement_type,
        "achievement_category": achievement_category,
        "timestamp": datetime.now().isoformat(),
        "system_state_before": event_obj.system_state_before,
        "system_state_after": event_obj.system_state_after,
    }


async def track_pokemon_milestones(event_obj: BaseEvent, **kwargs) -> Optional[Dict[str, Any]]:
    """Hook that tracks significant Pokemon Red milestones."""
    # Only process EnvironmentEvents
    if not isinstance(event_obj, EnvironmentEvent):
        return None

    reward = event_obj.reward
    if reward is None:
        return None

    # Track major milestones
    if reward >= 1.0:  # Significant progress rewards
        return {
            "milestone": "major_progress",
            "reward": reward,
            "timestamp": datetime.now().isoformat(),
        }
    elif reward >= 0.5:  # Moderate rewards
        return {
            "milestone": "moderate_progress",
            "reward": reward,
            "timestamp": datetime.now().isoformat(),
        }

    return None


async def track_pokemon_outcomes(event_obj: BaseEvent, **kwargs) -> Optional[Dict[str, Any]]:
    """Hook that tracks episode outcomes for Pokemon Red."""
    # Only process EnvironmentEvents
    if not isinstance(event_obj, EnvironmentEvent):
        return None

    # Check for termination conditions
    if event_obj.terminated or event_obj.truncated:
        total_reward = getattr(event_obj, 'total_reward', 0.0)
        steps_taken = getattr(event_obj, 'step_count', 0)

        # Extract achievement information from system state
        achievements_count = 0
        if event_obj.system_state_after:
            # Count positive rewards as achievements
            # This is a simplified count - in practice you'd track actual achievements
            achievements_count = max(1, int(total_reward / 0.1))  # Rough estimate

        return {
            "outcome_type": "episode_end",
            "total_reward": total_reward,
            "steps_taken": steps_taken,
            "achievements_count": achievements_count,
            "terminated": event_obj.terminated,
            "truncated": event_obj.truncated,
            "timestamp": datetime.now().isoformat(),
        }

    return None


# Create the global POKEMON_RED_HOOKS instance
POKEMON_RED_HOOKS = HookManager()

# Register all hooks
POKEMON_RED_HOOKS.register(
    "event_recorded",
    track_pokemon_rewards,
    name="pokemon_rewards",
    priority=10,
    event_types=["environment"],
)

POKEMON_RED_HOOKS.register(
    "event_recorded",
    track_pokemon_milestones,
    name="pokemon_milestones",
    priority=5,
    event_types=["environment"],
)

POKEMON_RED_HOOKS.register(
    "event_recorded",
    track_pokemon_outcomes,
    name="pokemon_outcomes",
    priority=5,
    event_types=["environment"],
)
