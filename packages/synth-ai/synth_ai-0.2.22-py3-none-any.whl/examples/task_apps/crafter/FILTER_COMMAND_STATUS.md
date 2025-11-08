# Filter Command Status for Crafter

## Summary

The `synth-ai filter` command has been updated to work with Crafter's SessionTracer v3 traces, but there's currently an issue with message persistence that needs to be resolved.

## What Was Changed

### 1. Updated Filter Command (`synth_ai/cli/task_apps.py`)

The filter command now:
- ✅ Queries `outcome_rewards` table to filter by `total_reward`
- ✅ Queries `messages` table to extract user/assistant pairs
- ✅ Falls back to metadata-based filtering for backwards compatibility
- ✅ Supports filtering by achievements/rewards from Crafter rollouts
- ✅ Extracts text from structured message content (JSON payloads)

### 2. Created Filter Config

**File**: `examples/task_apps/crafter/filter_sft_dataset.toml`

```toml
[filter]
db = "traces/v3/crafter_eval.db"
output = "ft_data/crafter_image_only_sft.jsonl"
min_official_score = 0.01  # Only traces with rewards > 0
```

## Current Issue: Messages Not Being Saved

### Problem

When running evaluations, the database ends up with:
- ✅ 2 `session_traces` (metadata saved)
- ✅ 2 `outcome_rewards` (rewards saved)
- ❌ 0 `messages` (messages NOT saved)
- ✅ 40 `events` (environment events saved)
- ✅ 20 `session_timesteps` (timesteps saved)

### Expected Behavior

The rollout code calls:
1. `tracer.initialize()` - Opens database connection
2. `tracer.start_session()` - Creates session
3. `tracer.record_message()` - Records system/user prompts (via `record_policy_prompts`)
4. `tracer.end_session()` - Saves session with `auto_save=True`

The `insert_session_trace` method (in `NativeLibsqlTraceManager`) SHOULD iterate through `trace.markov_blanket_message_history` and save each message to the `messages` table.

### Actual Behavior

Messages are NOT being persisted to the database, even though:
- The code path looks correct
- `end_session()` is being called
- `auto_save=True` is the default
- The trace JSON payload includes `markov_blanket_message_history`

### Debugging Observations

1. **Trace payload includes messages**: The eval output shows a large JSON structure with `markov_blanket_messages` containing all the prompts
2. **No errors logged**: The `try/except` around `end_session()` doesn't log any failures
3. **Works with both TURSO_NATIVE=0 and TURSO_NATIVE=1**: Neither backend saves messages
4. **Database is writable**: `outcome_rewards` and `events` are being saved successfully

## Possible Causes

1. **Silent exception during message insertion**: The `insert_message_row` might be failing without raising
2. **Transaction not committed**: Messages might be inserted but not committed
3. **Messages not in trace object**: `markov_blanket_message_history` might be empty when `end_session` is called
4. **Record message not adding to history**: `tracer.record_message()` might not be appending to the list properly

## Next Steps to Fix

### Option 1: Debug Message Persistence

Add logging to trace the message save path:

```python
# In rollout.py, finalize method
logger.info(f"[finalize] trace has {len(self.tracer._current_trace.markov_blanket_message_history)} messages before end_session")

# In native_manager.py, insert_session_trace
logger.info(f"[insert_session_trace] saving {len(trace.markov_blanket_message_history)} messages")
for msg in trace.markov_blanket_message_history:
    logger.info(f"  - message type={msg.message_type}")
    await self.insert_message_row(...)
    logger.info(f"  - message saved")
```

### Option 2: Verify Messages Are Being Recorded

Check if `record_policy_prompts` is actually being called and adding messages:

```python
# In rollout.py, after record_policy_prompts
if self.tracer and self.tracer._current_trace:
    msg_count = len(self.tracer._current_trace.markov_blanket_message_history)
    logger.info(f"[record_policy_prompts] trace now has {msg_count} messages")
```

### Option 3: Manual Message Recording

As a workaround, explicitly save messages outside of SessionTracer:

```python
# In finalize(), before end_session()
if self.enabled and self.tracer is not None:
    conn = await self.tracer.db.get_connection()
    for msg in self.tracer._current_trace.markov_blanket_message_history:
        await conn.execute(
            "INSERT INTO messages (session_id, message_type, content, timestamp) VALUES (?, ?, ?, ?)",
            (self.run_id, msg.message_type, str(msg.content), msg.time_record.event_time)
        )
    await conn.commit()
```

### Option 4: Use SFT Records Instead

Crafter already has working SFT record generation that writes directly to JSONL files. Use that instead of the filter command:

```bash
export SFT_OUTPUT_DIR="ft_data/crafter_sft"
uv run synth-ai eval grpo-crafter-task-app --config eval_image_only_gpt4o.toml

# Then filter successful runs manually
cat ft_data/crafter_sft/sft_*.jsonl > ft_data/crafter_combined.jsonl
```

## Current Workaround

Until message persistence is fixed, use the direct SFT recording approach (Option 4) documented in `CREATE_SFT_DATASET.md`.

## Testing the Filter Command

Once messages are being saved:

```bash
# 1. Run eval to populate database
export TASKAPP_TRACING_ENABLED=1
export TURSO_NATIVE=0
export SQLD_DB_PATH="traces/v3/crafter_eval.db"
uv run synth-ai eval grpo-crafter-task-app --config eval_image_only_gpt4o.toml

# 2. Verify messages were saved
sqlite3 traces/v3/crafter_eval.db "SELECT COUNT(*) FROM messages;"
# Should be > 0

# 3. Run filter
uv run synth-ai filter --config filter_sft_dataset.toml

# 4. Check output
cat ft_data/crafter_image_only_sft.jsonl | jq .
```

## Related Files

- `synth_ai/cli/task_apps.py` - Filter command implementation (updated)
- `synth_ai/tracing_v3/session_tracer.py` - SessionTracer class
- `synth_ai/tracing_v3/turso/native_manager.py` - `insert_session_trace` method (should save messages)
- `examples/task_apps/crafter/task_app/synth_envs_hosted/rollout.py` - Rollout tracing context
- `filter_sft_dataset.toml` - Filter configuration
- `CREATE_SFT_DATASET.md` - Alternative approach using direct SFT recording

## Status

- ✅ Filter command updated to query messages table
- ✅ Filter command can join with outcome_rewards
- ✅ Filter config created
- ❌ Messages not being persisted to database
- ❌ Filter command cannot extract SFT data without messages

**Action Required**: Debug why messages aren't being saved to the database despite correct code path.








