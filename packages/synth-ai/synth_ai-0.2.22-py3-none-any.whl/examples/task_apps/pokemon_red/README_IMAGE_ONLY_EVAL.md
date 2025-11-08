# Pokemon Red Image-Only Evaluation Guide

This guide shows you how to run Pokemon Red evaluations with **image-only input** (no text observations) and save traces + rewards to **Turso database**.

## Prerequisites

1. **OpenAI API Key**: Set in your `.env` file
2. **UV Package Manager**: Already installed if you can run `uv run`
3. **Pokemon Red ROM**: Place in `synth_ai/environments/examples/red/roms/pokemon_red.gb`
4. **Synth AI Repository**: Clone and set up per main README

## Quick Start

### 1. Run Image-Only Evaluation (10 Rollouts)

```bash
cd /Users/joshpurtell/Documents/GitHub/synth-ai

# Set up environment for Turso tracing
export TASKAPP_TRACING_ENABLED=1
export TURSO_NATIVE=1
export SQLD_DB_PATH="traces/v3/pokemon_red_eval.db"

# Run evaluation with image-only input
uv run synth-ai eval pokemon_red \
  --config examples/task_apps/pokemon_red/eval_image_only_gpt4o.toml
```

**Expected output**:
- 10 rollouts complete
- Most will stay in Red's bedroom (challenging task!)
- All traces and rewards saved to `traces/v3/pokemon_red_eval.db`

### 2. Check Results

```bash
# View database
ls -lh traces/v3/pokemon_red_eval.db  # Should be ~192KB

# Count sessions
sqlite3 traces/v3/pokemon_red_eval.db \
  "SELECT COUNT(*) FROM session_traces;"

# View all rollouts
sqlite3 -header -column traces/v3/pokemon_red_eval.db \
  "SELECT 
    session_id,
    total_reward, 
    achievements_count,
    json_extract(reward_metadata, '\$.final_map') as map,
    json_extract(reward_metadata, '\$.party_count') as party
   FROM outcome_rewards 
   ORDER BY total_reward DESC;"
```

### 3. Query Statistics

```bash
# Get summary stats
sqlite3 traces/v3/pokemon_red_eval.db \
  "SELECT 
    'Total rollouts' as metric, COUNT(*) as value FROM outcome_rewards
   UNION ALL
   SELECT 
    'With rewards', COUNT(*) FROM outcome_rewards WHERE total_reward > 0
   UNION ALL
   SELECT 
    'Average reward', ROUND(AVG(total_reward), 2) FROM outcome_rewards;"
```

## Configuration File

**Location**: `examples/task_apps/pokemon_red/eval_image_only_gpt4o.toml`

```toml
[eval]
app_id = "pokemon_red"
model = "gpt-4o-mini-2024-07-18"
seeds = [0, 1, 2, 3, 4, 5, 6, 7, 8, 9]  # 10 rollouts
max_turns = 10
concurrency = 1
env_name = "pokemon_red"
policy_name = "pokemon_red_policy"
trace_format = "full"
return_trace = true

[eval.env_config]
max_steps_per_episode = 10

[eval.policy_config]
provider = "openai"
model = "gpt-4o-mini-2024-07-18"
inference_url = "https://api.openai.com"
temperature = 0.7
top_p = 0.95
max_tokens = 512
use_vision = true           # Enable vision mode
image_only_mode = true      # Send ONLY images (no text)
max_llm_calls = 10
```

### Key Configuration Options

| Option | Description | Values |
|--------|-------------|--------|
| `use_vision` | Enable vision/image input | `true` / `false` |
| `image_only_mode` | Send only images (no text) | `true` / `false` |
| `seeds` | Which seeds to run | Array of integers |
| `max_turns` | Max policy calls per rollout | Integer (10-100) |
| `concurrency` | Parallel rollouts | 1-3 recommended |

## Customization

### Run More Steps (Recommended for Pokemon Red)

Pokemon Red needs more steps to make progress:

```toml
[eval.env_config]
env_params = {max_steps_per_episode = 500}  # Full Pallet Town sequence

[eval.policy_config]
max_llm_calls = 100  # Allow more LLM decisions
```

### Enable Text + Images (Recommended)

Image-only is very challenging for Pokemon Red. Try multimodal:

```toml
[eval.policy_config]
use_vision = true
image_only_mode = false  # Send both text AND images
```

This gives the model both:
- Base64-encoded PNG frames (160x144 Game Boy screen)
- Text state (HP, position, party, inventory, etc.)

### Use Better Model

```toml
[eval]
model = "gpt-4o-2024-08-06"  # Full GPT-4o

[eval.policy_config]
model = "gpt-4o-2024-08-06"
temperature = 0.7  # Slightly higher for exploration
```

### Run More Episodes

```toml
[eval]
seeds = [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19]  # 20 rollouts
```

## Database Schema

### outcome_rewards Table

```sql
CREATE TABLE outcome_rewards (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    session_id VARCHAR NOT NULL,
    total_reward INTEGER NOT NULL,
    achievements_count INTEGER NOT NULL,  -- Milestone events
    total_steps INTEGER NOT NULL,
    created_at DATETIME NOT NULL,
    reward_metadata TEXT,  -- JSON with map_id, party_count, badges, etc.
    FOREIGN KEY(session_id) REFERENCES session_traces(session_id)
);
```

### Example Queries

```sql
-- Get statistics
SELECT 
    COUNT(*) as total,
    SUM(CASE WHEN total_reward > 0 THEN 1 ELSE 0 END) as with_rewards,
    AVG(total_reward) as avg_reward,
    MAX(total_reward) as max_reward,
    MAX(achievements_count) as max_achievements
FROM outcome_rewards;

-- Find rollouts that made progress
SELECT 
    session_id,
    total_reward,
    achievements_count,
    json_extract(reward_metadata, '$.final_map') as final_map,
    json_extract(reward_metadata, '$.party_count') as party_count,
    json_extract(reward_metadata, '$.badges') as badges
FROM outcome_rewards 
WHERE total_reward > 0 OR achievements_count > 0
ORDER BY total_reward DESC;

-- Join with session traces
SELECT 
    st.session_id,
    st.created_at,
    st.num_timesteps,
    orw.total_reward,
    orw.achievements_count,
    json_extract(orw.reward_metadata, '$.milestone_events') as milestones
FROM session_traces st
INNER JOIN outcome_rewards orw ON st.session_id = orw.session_id
WHERE orw.total_reward > 0
ORDER BY orw.total_reward DESC;

-- Check which maps were reached
SELECT 
    json_extract(reward_metadata, '$.final_map') as map_id,
    COUNT(*) as count
FROM outcome_rewards
GROUP BY map_id
ORDER BY count DESC;
```

## Understanding Maps

**Common Map IDs**:
- `38`: Red's bedroom (starting location)
- `0`: Pallet Town (outside)
- `40`: Red's house downstairs
- `37`: Oak's Lab

**Goal**: Progress from Map 38 → 40 → 0 → 37 (get starter Pokemon)

## Pallet Town Milestones

The `PalletTownProgressionCompositeReward` tracks these milestones:

| Milestone | Reward | Description |
|-----------|--------|-------------|
| Leave bedroom | +20 | Go downstairs |
| Exit house | +30 | Enter Pallet Town |
| Find Oak's lab | +40 | Discover and enter lab |
| Talk to Oak | +50 | First dialogue |
| Get starter | +100 | Receive your first Pokémon |
| Enter first battle | +75 | Battle rival |
| Win battle | +150 | Defeat rival |

**Total possible**: ~600+ points

## Typical Results

**Expected Performance** (10 rollouts, 10 steps, image-only):

```
Total rollouts: 10
Rollouts with rewards: 0 (0%)  ← Expected! Task is hard
Average reward: 0.0
Final map: 38 (Red's bedroom)
```

**Why Zero Rewards?**
- 10 steps is too few for Pokemon Red
- Image-only mode is very challenging (no HP/inventory text)
- Needs navigation + NPC interaction

**To Get Non-Zero Rewards**:
1. Increase `max_steps_per_episode` to 100-500
2. Enable multimodal: `image_only_mode = false`
3. Use full GPT-4o: `model = "gpt-4o-2024-08-06"`

## Troubleshooting

### No Database Created

**Issue**: `traces/v3/pokemon_red_eval.db` doesn't exist or is 0 bytes

**Fix**: Ensure environment variables are set:
```bash
export TASKAPP_TRACING_ENABLED=1
export TURSO_NATIVE=1
export SQLD_DB_PATH="traces/v3/pokemon_red_eval.db"
```

### ROM Not Found

**Issue**: `FileNotFoundError: pokemon_red.gb`

**Fix**: Place ROM at:
```bash
synth_ai/environments/examples/red/roms/pokemon_red.gb
```

Or set environment variable:
```bash
export POKEMON_RED_ROM_PATH="/path/to/pokemon_red.gb"
```

### 401 Unauthorized Error

**Issue**: OpenAI API returns 401

**Fix**: Check your `.env` file:
```bash
# .env
OPENAI_API_KEY=sk-proj-...your-key-here...
```

### All Rewards are Zero

**Issue**: Agents aren't making progress (expected with image-only + 10 steps)

**Solutions**:

1. **Increase steps**:
```toml
[eval.env_config]
env_params = {max_steps_per_episode = 100}

[eval.policy_config]
max_llm_calls = 100
```

2. **Enable text observations**:
```toml
[eval.policy_config]
image_only_mode = false  # Send both image AND text
```

3. **Use better model**:
```toml
[eval]
model = "gpt-4o-2024-08-06"
```

### PyBoy Not Installed

**Issue**: `ModuleNotFoundError: No module named 'pyboy'`

**Fix**:
```bash
uv add pyboy
```

## Advanced: Export to CSV

```bash
# Export all rollouts to CSV
sqlite3 -header -csv traces/v3/pokemon_red_eval.db \
  "SELECT 
    session_id,
    total_reward,
    achievements_count,
    json_extract(reward_metadata, '$.final_map') as final_map,
    json_extract(reward_metadata, '$.party_count') as party_count,
    json_extract(reward_metadata, '$.badges') as badges,
    json_extract(reward_metadata, '$.milestone_events') as milestones
   FROM outcome_rewards 
   ORDER BY total_reward DESC" \
  > pokemon_red_rewards.csv
```

## Files Overview

```
examples/task_apps/pokemon_red/
├── eval_image_only_gpt4o.toml          # Config file
├── EVAL_IMAGE_ONLY_COMPLETE.md         # Implementation details
├── EVAL_IMAGE_ONLY_STATUS.md           # Status document
├── README_IMAGE_ONLY_EVAL.md           # This file
├── task_app.py                         # Main task app
│   ├── Image-only mode logic
│   ├── SessionTracer integration
│   ├── OpenAI API authentication
│   └── Reward computation
└── pallet_town_rl_config.toml          # RL training config (reference)
```

## Recommended Settings for Success

For best chance of non-zero rewards:

```toml
[eval]
model = "gpt-4o-2024-08-06"  # Full GPT-4o
seeds = [0, 1, 2, 3, 4]       # 5 rollouts
max_turns = 100               # Allow more decisions

[eval.env_config]
env_params = {max_steps_per_episode = 500}  # Full episode

[eval.policy_config]
provider = "openai"
model = "gpt-4o-2024-08-06"
inference_url = "https://api.openai.com"
temperature = 0.7
max_tokens = 512
use_vision = true             # Enable vision
image_only_mode = false       # Send text too (multimodal)
max_llm_calls = 100
```

## See Also

- `EVAL_IMAGE_ONLY_COMPLETE.md` - Full implementation details
- `pallet_town_rl_config.toml` - RL training configuration
- `../crafter/README_IMAGE_ONLY_EVAL.md` - Crafter version

## Summary

1. ✅ Set environment variables for Turso tracing
2. ✅ Run `uv run synth-ai eval pokemon_red --config ...`
3. ✅ Check database: `traces/v3/pokemon_red_eval.db`
4. ✅ Query rewards: `SELECT * FROM outcome_rewards`
5. ✅ For non-zero rewards: increase steps + use multimodal + better model

Pokemon Red is challenging - don't be discouraged by zero rewards with image-only + 10 steps! 🎮








