# Crafter Image-Only Eval Results

## Summary
Successfully ran 10 rollouts of the Crafter task app using **image-only input** (no text observations), with full tracing and rewards saved to Turso database.

## Configuration
- **Model**: `gpt-4o-mini-2024-07-18`
- **Input Mode**: Image-only (vision enabled, text observations disabled)
- **Max Steps**: 10 per episode
- **Max LLM Calls**: 10 per rollout
- **Seeds**: 0-9 (10 rollouts)
- **Tracing**: Enabled with Turso/libsql (MVCC concurrent writes)
- **Database**: `traces/v3/crafter_eval.db` (1.7MB)

## Results

### Overall Performance
- **Total Rollouts**: 10
- **Success Rate**: 100% (10/10 completed)
- **Mean Official Score**: 0.700 (70%)
- **Rollouts with Achievements**: 7/10 (70%)

### Achievement Distribution
| Achievements Count | Number of Rollouts |
|-------------------|-------------------|
| 3                 | 1                 |
| 2                 | 4                 |
| 1                 | 2                 |
| 0                 | 3                 |

### Top Performing Rollouts
1. **Seed 0** - 3 achievements: `collect_drink`, `collect_sapling`, `collect_wood` (reward: 3)
2. **Seed 1** - 2 achievements: `collect_sapling`, `collect_wood` (reward: 2)
3. **Seed 3** - 2 achievements: `collect_sapling`, `collect_wood` (reward: 2)
4. **Seed 6** - 2 achievements: `collect_sapling`, `collect_wood` (reward: 2)
5. **Seed 9** - 2 achievements: `collect_sapling`, `collect_wood` (reward: 2)
6. **Seed 4** - 1 achievement: `collect_wood` (reward: 1)
7. **Seed 7** - 1 achievement: `collect_wood` (reward: 1)

### Rollouts with No Achievements
- Seed 2, 5, 8 - No achievements earned

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
    reward_metadata TEXT,
    FOREIGN KEY(session_id) REFERENCES session_traces(session_id)
);
CREATE INDEX idx_outcome_rewards_session ON outcome_rewards (session_id);
CREATE INDEX idx_outcome_rewards_total ON outcome_rewards (total_reward);
```

## Query Examples

### Get rollouts with achievements > 0
```sql
SELECT 
    st.session_id, 
    st.num_timesteps, 
    orw.achievements_count, 
    orw.total_reward,
    json_extract(orw.reward_metadata, '$.final_achievements') as achievements
FROM session_traces st
INNER JOIN outcome_rewards orw ON st.session_id = orw.session_id
WHERE orw.achievements_count > 0
ORDER BY orw.achievements_count DESC, orw.total_reward DESC;
```

### Count rollouts by achievement count
```sql
SELECT achievements_count, COUNT(*) as count
FROM outcome_rewards
GROUP BY achievements_count
ORDER BY achievements_count DESC;
```

### Get top performers
```sql
SELECT session_id, total_reward, achievements_count, reward_metadata
FROM outcome_rewards
WHERE achievements_count > 0 OR total_reward > 0
ORDER BY achievements_count DESC, total_reward DESC
LIMIT 10;
```

## Key Changes Made

### 1. OpenAI Authorization Fix
Updated `openai_client.py` to properly set `Authorization: Bearer` header for OpenAI API calls:
```python
# If calling OpenAI directly (api.openai.com)
if "api.openai.com" in low_url:
    openai_key = os.getenv("OPENAI_API_KEY")
    if openai_key and isinstance(openai_key, str):
        headers["Authorization"] = f"Bearer {openai_key}"
```

### 2. Image-Only Mode Implementation
Added `image_only_mode` support to `CrafterPolicy` and `CrafterReActAgent`:
- When enabled, only image observations are sent to the LLM
- Text observations are set to empty string
- Vision mode is automatically enabled

### 3. Trace Format Support
Fixed CLI to properly handle both "compact" and "full" trace formats:
```python
# Handle both "compact" and "full" trace formats
session_trace_dict = trace_namespace.get("session_trace")
if not isinstance(session_trace_dict, dict):
    if "session_id" in trace_namespace:
        session_trace_dict = trace_namespace
```

### 4. Request Body Structure
Fixed rollout request to properly nest tracing parameters:
```python
"record": {
    "return_trace": True,
    "trace_format": "full",
}
```

## Files Modified
1. `/Users/joshpurtell/Documents/GitHub/synth-ai/examples/task_apps/crafter/task_app/synth_envs_hosted/inference/openai_client.py`
2. `/Users/joshpurtell/Documents/GitHub/synth-ai/examples/task_apps/crafter/task_app/synth_envs_hosted/envs/crafter/policy.py`
3. `/Users/joshpurtell/Documents/GitHub/synth-ai/examples/task_apps/crafter/task_app/synth_envs_hosted/envs/crafter/react_agent.py`
4. `/Users/joshpurtell/Documents/GitHub/synth-ai/synth_ai/cli/task_apps.py`
5. `/Users/joshpurtell/Documents/GitHub/synth-ai/examples/task_apps/crafter/eval_image_only_gpt4o.toml`

## Verification
- ✅ All 10 rollouts completed successfully
- ✅ Image-only input confirmed (base64 PNG images in prompts)
- ✅ Achievements computed and saved
- ✅ Foreign keys working (can join session_traces and outcome_rewards)
- ✅ Can query rollouts by achievement count and rewards
- ✅ Database size: 1.7MB with full trace data

## Next Steps
- Increase `max_steps_per_episode` for longer episodes
- Try different models (e.g., gpt-4o, claude-3.5-sonnet)
- Analyze which actions lead to the most achievements
- Use concurrent writes with higher concurrency (Turso MVCC supports this)


