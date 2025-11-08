# Crafter Image-Only Evaluation Guide

This guide shows you how to run Crafter evaluations with **image-only input** (no text observations) and save traces + rewards to **Turso database**.

## Prerequisites

1. **OpenAI API Key**: Set in your `.env` file
2. **UV Package Manager**: Already installed if you can run `uv run`
3. **Synth AI Repository**: Clone and set up per main README

## Quick Start

### 1. Run Image-Only Evaluation (10 Rollouts)

```bash
cd /Users/joshpurtell/Documents/GitHub/synth-ai

# Set up environment for Turso tracing
export TASKAPP_TRACING_ENABLED=1
export TURSO_NATIVE=1
export SQLD_DB_PATH="traces/v3/crafter_eval.db"

# Run evaluation with image-only input
uv run synth-ai eval grpo-crafter \
  --config examples/task_apps/crafter/eval_image_only_gpt4o.toml
```

**Expected output**:
- 10 rollouts complete
- ~70% will earn achievements (collect_wood, collect_sapling, etc.)
- All traces and rewards saved to `traces/v3/crafter_eval.db`

### 2. Check Results

```bash
# View database
ls -lh traces/v3/crafter_eval.db  # Should be ~1.7MB

# Count sessions
sqlite3 traces/v3/crafter_eval.db \
  "SELECT COUNT(*) FROM session_traces;"

# View all rollouts with rewards
sqlite3 -header -column traces/v3/crafter_eval.db \
  "SELECT 
    json_extract(reward_metadata, '\$.env_seed') as seed,
    total_reward, 
    achievements_count,
    json_extract(reward_metadata, '\$.final_achievements') as achievements
   FROM outcome_rewards 
   ORDER BY total_reward DESC;"
```

### 3. Query Non-Zero Rewards

```bash
# Get rollouts that earned achievements
sqlite3 -header -column traces/v3/crafter_eval.db \
  "SELECT 
    session_id,
    total_reward,
    achievements_count,
    json_extract(reward_metadata, '\$.final_achievements') as achievements
   FROM outcome_rewards 
   WHERE total_reward > 0
   ORDER BY total_reward DESC;"
```

## Configuration File

**Location**: `examples/task_apps/crafter/eval_image_only_gpt4o.toml`

```toml
[eval]
app_id = "grpo-crafter"
model = "gpt-4o-mini-2024-07-18"
seeds = [0, 1, 2, 3, 4, 5, 6, 7, 8, 9]  # 10 rollouts
max_turns = 10
concurrency = 1
env_name = "crafter"
policy_name = "crafter-react"
trace_format = "full"
return_trace = true

[eval.env_config]
env_params = {max_steps_per_episode = 10}

[eval.policy_config]
provider = "openai"
model = "gpt-4o-mini-2024-07-18"
inference_url = "https://api.openai.com"
temperature = 0.6
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
| `concurrency` | Parallel rollouts | 1-5 recommended |

## Customization

### Run More Rollouts

```toml
# Change seeds to run more episodes
seeds = [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19]  # 20 rollouts
```

### Increase Steps Per Episode

```toml
[eval.env_config]
env_params = {max_steps_per_episode = 100}  # Longer episodes

[eval.policy_config]
max_llm_calls = 100
```

### Use Different Model

```toml
[eval]
model = "gpt-4o-2024-08-06"  # Full GPT-4o

[eval.policy_config]
model = "gpt-4o-2024-08-06"
```

### Enable Text + Images (Multimodal)

```toml
[eval.policy_config]
use_vision = true
image_only_mode = false  # Send both text AND images
```

## Database Schema

### outcome_rewards Table

```sql
CREATE TABLE outcome_rewards (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    session_id VARCHAR NOT NULL,
    total_reward INTEGER NOT NULL,
    achievements_count INTEGER NOT NULL,
    total_steps INTEGER NOT NULL,
    created_at DATETIME NOT NULL,
    reward_metadata TEXT,  -- JSON with achievements, seed, etc.
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
    MAX(total_reward) as max_reward
FROM outcome_rewards;

-- Find best performers
SELECT 
    json_extract(reward_metadata, '$.env_seed') as seed,
    total_reward,
    achievements_count,
    json_extract(reward_metadata, '$.final_achievements') as achievements
FROM outcome_rewards 
WHERE achievements_count >= 2
ORDER BY total_reward DESC;

-- Join with session traces
SELECT 
    st.session_id,
    st.created_at,
    st.num_timesteps,
    orw.total_reward,
    orw.achievements_count
FROM session_traces st
INNER JOIN outcome_rewards orw ON st.session_id = orw.session_id
WHERE orw.total_reward > 0
ORDER BY orw.total_reward DESC;

-- Count by achievement level
SELECT 
    achievements_count,
    COUNT(*) as num_rollouts,
    AVG(total_reward) as avg_reward
FROM outcome_rewards
GROUP BY achievements_count
ORDER BY achievements_count DESC;
```

## Typical Results

**Expected Performance** (10 rollouts, 10 steps each, image-only):

```
Total rollouts: 10
Rollouts with rewards: ~7 (70%)
Average reward: ~1.3
Max reward: ~3
```

**Common Achievements**:
- `collect_wood` (most common)
- `collect_sapling` (common)
- `collect_drink` (rare in 10 steps)

## Troubleshooting

### No Database Created

**Issue**: `traces/v3/crafter_eval.db` doesn't exist or is 0 bytes

**Fix**: Ensure environment variables are set:
```bash
export TASKAPP_TRACING_ENABLED=1
export TURSO_NATIVE=1
export SQLD_DB_PATH="traces/v3/crafter_eval.db"
```

### 401 Unauthorized Error

**Issue**: OpenAI API returns 401

**Fix**: Check your `.env` file has valid `OPENAI_API_KEY`:
```bash
# .env file
OPENAI_API_KEY=sk-proj-...your-key-here...
```

### All Rewards are Zero

**Issue**: Agents aren't earning any achievements

**Possible causes**:
1. **Too few steps**: Increase `max_steps_per_episode` to 50-100
2. **Image-only too hard**: Try `image_only_mode = false` for multimodal
3. **Wrong model**: Try full GPT-4o instead of mini

### Database Lock Errors

**Issue**: `SQLITE_BUSY` or `database is locked`

**Fix**: Reduce concurrency in config:
```toml
[eval]
concurrency = 1  # Run sequentially
```

Or use Turso's MVCC mode (already enabled with `TURSO_NATIVE=1`).

## Advanced: Export to CSV

```bash
# Export all rewards to CSV
sqlite3 -header -csv traces/v3/crafter_eval.db \
  "SELECT 
    json_extract(reward_metadata, '$.env_seed') as seed,
    total_reward,
    achievements_count,
    json_extract(reward_metadata, '$.final_achievements') as achievements
   FROM outcome_rewards 
   ORDER BY total_reward DESC" \
  > crafter_rewards.csv
```

## Files Overview

```
examples/task_apps/crafter/
├── eval_image_only_gpt4o.toml          # Config file
├── EVAL_IMAGE_ONLY_RESULTS.md          # Example results
├── QUERY_EXAMPLES.md                   # More SQL queries
├── README_IMAGE_ONLY_EVAL.md           # This file
└── task_app/
    └── synth_envs_hosted/
        ├── envs/crafter/
        │   ├── policy.py                # Image-only mode logic
        │   └── react_agent.py           # Message construction
        ├── rollout.py                   # SessionTracer integration
        └── inference/
            └── openai_client.py         # API authentication
```

## See Also

- `EVAL_IMAGE_ONLY_RESULTS.md` - Example run with detailed results
- `QUERY_EXAMPLES.md` - More SQL query examples
- `../../pokemon_red/README_IMAGE_ONLY_EVAL.md` - Pokemon Red version

## Summary

1. ✅ Set environment variables for Turso tracing
2. ✅ Run `uv run synth-ai eval grpo-crafter --config ...`
3. ✅ Check database: `traces/v3/crafter_eval.db`
4. ✅ Query rewards: `SELECT * FROM outcome_rewards WHERE total_reward > 0`
5. ✅ Customize config for different models/steps

Enjoy running Crafter with vision-only input! 🎮


