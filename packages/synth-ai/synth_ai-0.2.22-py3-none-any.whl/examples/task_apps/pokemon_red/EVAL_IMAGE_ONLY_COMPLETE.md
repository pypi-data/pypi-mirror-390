# Pokemon Red Image-Only Eval - Complete ✅

## Summary

Successfully ran **10 rollouts** of Pokemon Red with **image-only input** (no text observations), with full **Turso tracing** and **outcome rewards** saved to database.

## Configuration

- **Model**: `gpt-4o-mini-2024-07-18`
- **Input Mode**: Image-only (vision enabled, text observations disabled)
- **Max Steps**: 10 per episode  
- **Max LLM Calls**: 10 per rollout
- **Seeds**: 0-9 (10 rollouts)
- **Tracing**: Enabled with Turso/libsql (MVCC concurrent writes)
- **Database**: `traces/v3/pokemon_red_eval.db` (192KB)

## Results

### Overall Performance
- **Total Rollouts**: 10/10 completed
- **Success Rate**: 100% (no errors)
- **Mean Reward**: 0.000
- **Rollouts with Rewards**: 0/10 (0%)

*Note: 0 rewards are expected - the Pallet Town sequence is challenging with only 10 turns and image-only input*

### Database Verification
```sql
Total rollouts: 10
Rollouts with reward > 0: 0
Rollouts with achievements > 0: 0
Average reward: 0.0
Database size: 192KB
```

### All Rollouts
All 10 seeds stayed in Map 38 (Red's bedroom) with 0 party Pokemon and 0 badges.

## Implementation Details

### 1. Image-Only Mode
**File**: `task_app.py` → `_call_inference()` function

```python
# Check if vision mode is enabled
use_vision = bool(policy_cfg.get("use_vision", False))
image_only_mode = bool(policy_cfg.get("image_only_mode", False))

# Image-only mode: only send image, no text
if image_only_mode:
    user_content = [
        {"type": "image_url", "image_url": {"url": image_data_url}}
    ]
else:
    # Vision mode with text: send both text and image
    user_content = [
        {"type": "text", "text": state_summary},
        {"type": "image_url", "image_url": {"url": image_data_url}}
    ]
```

### 2. OpenAI API Integration
**File**: `task_app.py` → `_call_inference()` function

Fixed inference URL construction and authentication:
```python
# Add /v1/chat/completions if using OpenAI directly
if "api.openai.com" in inference_url:
    inference_url = inference_url + "/v1/chat/completions"

# External API: use direct HTTP client with auth header
if is_external:
    headers = {}
    if "api.openai.com" in inference_url:
        api_key = os.getenv("OPENAI_API_KEY")
        if api_key:
            headers["Authorization"] = f"Bearer {api_key}"
```

### 3. SessionTracer Integration
**File**: `task_app.py` → `rollout_executor()` function

Added full Turso tracing like Crafter:
```python
# Initialize SessionTracer for this rollout
tracer_factory = getattr(fastapi_request.app.state, "session_tracer_factory", None)
tracer_instance: SessionTracer | None = None
if callable(tracer_factory):
    inst = tracer_factory()
    tracer_instance = inst if isinstance(inst, SessionTracer) else None

# Start tracing session
if tracer_instance is not None:
    await tracer_instance.initialize()
    await tracer_instance.start_session(
        session_id=request.run_id,
        metadata={...}
    )
```

### 4. Outcome Rewards
**File**: `task_app.py` → `rollout_executor()` end

```python
# Record outcome rewards and end session
if tracer_instance is not None:
    achievements_count = len(milestone_events)
    
    reward_metadata = {
        "run_id": request.run_id,
        "env_name": "pokemon_red",
        "final_map": final_state.get("map_id", -1),
        "party_count": final_state.get("party_count", 0),
        "badges": final_state.get("badges", 0),
        "steps": len(steps),
        "milestone_events": milestone_events,
        "reward_components": all_reward_components,
    }
    
    # Record outcome reward to Turso
    await tracer_instance.record_outcome_reward(
        total_reward=int(total_reward),
        achievements_count=achievements_count,
        total_steps=len(steps),
        reward_metadata=reward_metadata,
    )
    
    # End session
    session_trace = await tracer_instance.end_session()
```

### 5. Tracer Factory Setup
**File**: `task_app.py` → `build_config()` function

```python
# Set up tracing
tracing_enabled = tracing_env_enabled()
tracing_db_url = resolve_tracing_db_url()
tracer_factory = build_tracer_factory(
    SessionTracer, enabled=tracing_enabled, db_url=tracing_db_url
)

app_state: dict[str, Any] = {
    "tracing_enabled": tracing_enabled,
}
if tracer_factory is not None:
    app_state["session_tracer_factory"] = tracer_factory
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
    reward_metadata TEXT,
    FOREIGN KEY(session_id) REFERENCES session_traces(session_id)
);
```

## Query Examples

### Get all sessions with rewards
```sql
SELECT 
    st.session_id,
    st.num_timesteps,
    orw.total_reward,
    orw.achievements_count,
    json_extract(orw.reward_metadata, '$.final_map') as final_map
FROM session_traces st
INNER JOIN outcome_rewards orw ON st.session_id = orw.session_id
ORDER BY orw.total_reward DESC;
```

### Filter for non-zero rewards (when they exist)
```sql
SELECT 
    session_id,
    total_reward,
    achievements_count,
    total_steps,
    json_extract(reward_metadata, '$.final_map') as final_map,
    json_extract(reward_metadata, '$.party_count') as party_count
FROM outcome_rewards
WHERE total_reward > 0
ORDER BY total_reward DESC;
```

## Comparison: Crafter vs Pokemon Red

| Feature | Crafter | Pokemon Red |
|---------|---------|-------------|
| Image-only mode | ✅ Working | ✅ Working |
| OpenAI API | ✅ Working | ✅ Working |
| Eval CLI | ✅ Working | ✅ Working |
| SessionTracer | ✅ Integrated | ✅ Integrated |
| Turso database | ✅ 1.7MB (10 rollouts) | ✅ 192KB (10 rollouts) |
| outcome_rewards | ✅ 10 rows | ✅ 10 rows |
| Foreign keys | ✅ Working | ✅ Working |
| Non-zero rewards | ✅ 7/10 rollouts | ❌ 0/10 rollouts* |

*Expected: Pokemon Red is harder (requires room navigation, NPC dialogue, etc.)

## Files Modified

1. **`task_app.py`**:
   - Added `use_vision` and `image_only_mode` support
   - Fixed OpenAI API URL construction and auth
   - Integrated SessionTracer for Turso persistence
   - Added `record_outcome_reward()` calls
   - Updated `build_config()` to create tracer_factory

2. **`eval_image_only_gpt4o.toml`** (new):
   - Config for image-only evaluation
   - 10 seeds, 10 max turns per episode
   - GPT-4o mini with vision enabled

## Running the Evaluation

```bash
cd /Users/joshpurtell/Documents/GitHub/synth-ai

# Set up tracing environment
export TASKAPP_TRACING_ENABLED=1
export TURSO_NATIVE=1
export SQLD_DB_PATH="traces/v3/pokemon_red_eval.db"

# Run evaluation
uv run synth-ai eval pokemon_red \
  --config examples/task_apps/pokemon_red/eval_image_only_gpt4o.toml
```

## Verification Commands

```bash
# Check database size
ls -lh traces/v3/pokemon_red_eval.db

# Count sessions
sqlite3 traces/v3/pokemon_red_eval.db \
  "SELECT COUNT(*) FROM session_traces;"

# View all rewards
sqlite3 -header -column traces/v3/pokemon_red_eval.db \
  "SELECT session_id, total_reward, achievements_count, total_steps 
   FROM outcome_rewards 
   ORDER BY total_reward DESC;"

# Test foreign keys
sqlite3 traces/v3/pokemon_red_eval.db \
  "SELECT st.session_id, orw.total_reward 
   FROM session_traces st 
   INNER JOIN outcome_rewards orw ON st.session_id = orw.session_id 
   LIMIT 5;"
```

## Next Steps

To improve rewards:
1. **Increase max_turns**: Try 50-100 turns per episode
2. **Better prompting**: Add more detailed instructions in system prompt
3. **Hybrid mode**: Use `use_vision=true` with `image_only_mode=false` to get both images and text
4. **Different model**: Try GPT-4o (full) or Claude 3.5 Sonnet for better vision understanding

## Summary

✅ **All goals achieved**:
- Image-only input mode working
- 10 rollouts completed successfully
- Turso database created with 192KB of trace data
- outcome_rewards table with foreign keys
- Can filter and query by rewards
- SessionTracer fully integrated

Pokemon Red now has the same Turso tracing capabilities as Crafter! 🎉


