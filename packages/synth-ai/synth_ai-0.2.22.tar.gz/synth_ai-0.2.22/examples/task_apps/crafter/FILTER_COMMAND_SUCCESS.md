# Filter Command Success - SFT Dataset Creation Working!

## ✅ Complete Success!

The `uvx synth-ai eval` → `uvx synth-ai filter` loop is now working end-to-end for Crafter!

## What Was Fixed

### Issue 1: Early Return in `insert_session_trace`
**Problem**: Sessions created by `start_session` already existed in the database, so `insert_session_trace` returned early without saving messages.

**Fix**: Modified `/Users/joshpurtell/Documents/GitHub/synth-ai/synth_ai/tracing_v3/turso/native_manager.py` to continue processing messages even when the session already exists:

```python
if session_exists:
    # Update metadata but don't return early
    # Continue to save messages
```

### Issue 2: Invalid Message Types
**Problem**: Crafter was using custom message types (`policy_system_prompt`, `policy_user_prompt`, `policy_tool_call`) that violated the database CHECK constraint.

**Fix**: Modified `/Users/joshpurtell/Documents/GitHub/synth-ai/examples/task_apps/crafter/task_app/synth_envs_hosted/rollout.py` to use standard message types:
- `policy_system_prompt` → `system`
- `policy_user_prompt` → `user`  
- `policy_tool_call` → `assistant` (with `is_tool_call: true` metadata)

## Full Working Pipeline

### 1. Run Evaluation with Tracing

```bash
cd /Users/joshpurtell/Documents/GitHub/synth-ai

export TASKAPP_TRACING_ENABLED=1
export TURSO_NATIVE=0
export SQLD_DB_PATH="traces/v3/crafter_eval.db"

uv run synth-ai eval grpo-crafter-task-app \
  --config examples/task_apps/crafter/eval_image_only_gpt4o.toml
```

**Result**:
- ✅ 2 rollouts completed
- ✅ 120 messages saved to database (40 system + 40 user + 40 assistant)
- ✅ 2 outcome_rewards saved with achievements
- ✅ Traces returned successfully

### 2. Filter to Create SFT Dataset

```bash
uv run synth-ai filter \
  --config examples/task_apps/crafter/filter_sft_dataset.toml
```

**Result**:
```
Wrote 40 examples -> ft_data/crafter_image_only_sft.jsonl
```

### 3. Verify SFT Data

```bash
# Check first example
head -1 ft_data/crafter_image_only_sft.jsonl | jq .

# Count examples
wc -l ft_data/crafter_image_only_sft.jsonl
```

## SFT Dataset Format

Each line in the JSONL contains:

```json
{
  "messages": [
    {
      "role": "user",
      "content": "=== CRAFTER GAME STATE ===\nStep: 0/10000\n..."
    },
    {
      "role": "assistant",
      "content": "[{'tool_name': 'interact_many', 'arguments': {...}}]"
    }
  ],
  "metadata": {
    "session_id": "...",
    "env_name": "crafter",
    "policy_name": "crafter-react",
    "seed": 0,
    "total_reward": 1,
    "achievements_count": 1,
    "created_at": "2025-10-22T23:55:25.533188+00:00"
  }
}
```

## Database Schema

The filter command queries these tables:

### messages table
```sql
SELECT message_type, content, timestamp 
FROM messages 
WHERE session_id = :session_id
ORDER BY timestamp ASC
```

- ✅ 120 messages total
- System (40) + User (40) + Assistant (40) messages
- Pairs extracted: user → assistant

### outcome_rewards table
```sql
SELECT total_reward, achievements_count 
FROM outcome_rewards 
WHERE session_id = :session_id
```

- Used to filter for successful rollouts
- `min_official_score = 0.01` filters for rewards > 0
- Both rollouts had `total_reward = 1` (1 achievement each)

## Filter Configuration

**File**: `examples/task_apps/crafter/filter_sft_dataset.toml`

```toml
[filter]
db = "traces/v3/crafter_eval.db"
output = "ft_data/crafter_image_only_sft.jsonl"
min_official_score = 0.01  # Only traces with rewards > 0
```

### Available Filter Options

```toml
[filter]
db = "path/to/traces.db"              # Required
output = "path/to/output.jsonl"        # Required

# Optional filters
min_official_score = 0.01              # Filter by reward
splits = ["train", "test"]             # Filter by split
task_ids = ["task_1"]                  # Filter by task
models = ["gpt-4o"]                    # Filter by model
limit = 100                            # Limit number of examples
```

## Statistics

From 2 rollouts with 10 turns each:

| Metric | Count |
|--------|-------|
| Total rollouts | 2 |
| Rollouts with rewards | 2 (100%) |
| Total messages saved | 120 |
| System messages | 40 |
| User messages | 40 |
| Assistant messages | 40 |
| **SFT examples** | **40** |
| Average turns per rollout | 10 |
| Examples per rollout | 20 |

## Next Steps

### Scale Up

Run with more seeds for a larger dataset:

```toml
# In eval_image_only_gpt4o.toml
seeds = [0, 1, 2, 3, 4, 5, 6, 7, 8, 9]  # 10 rollouts
max_turns = 50                           # More examples per rollout
```

Expected output: ~1000 SFT examples from 10 rollouts @ 50 turns each

### Use the SFT Data

```bash
# For OpenAI fine-tuning
# The JSONL format is compatible with OpenAI's fine-tuning API

# For local fine-tuning
# Convert to your preferred format (HuggingFace, etc.)
```

### Filter Variations

```bash
# Only high-reward traces
min_official_score = 2.0

# Only specific achievements
# Query manually then filter by session_id

# Time-based filtering
min_created_at = "2025-10-22T00:00:00"
```

## Files Modified

1. **`synth_ai/tracing_v3/turso/native_manager.py`**
   - Fixed early return when session exists
   - Added logging for debugging

2. **`examples/task_apps/crafter/task_app/synth_envs_hosted/rollout.py`**
   - Changed message types to standard values
   - Added debug logging

3. **`synth_ai/cli/task_apps.py`**
   - Updated filter command to query messages table
   - Added support for outcome_rewards filtering
   - Fixed SQL parameter format

4. **`examples/task_apps/crafter/filter_sft_dataset.toml`**
   - Created filter configuration

## Troubleshooting

### No messages in database

**Check**:
```bash
sqlite3 traces/v3/crafter_eval.db "SELECT COUNT(*) FROM messages;"
```

**Fix**: Ensure `TASKAPP_TRACING_ENABLED=1` and `TURSO_NATIVE=0`

### Filter returns no examples

**Check**:
```bash
sqlite3 traces/v3/crafter_eval.db \
  "SELECT COUNT(*) FROM outcome_rewards WHERE total_reward > 0;"
```

**Fix**: Lower `min_official_score` or remove it to include all traces

### Invalid message types

**Error**: `CHECK constraint failed: message_type IN (...)`

**Fix**: Already fixed in rollout.py - update to latest code

## Related Documentation

- `README_IMAGE_ONLY_EVAL.md` - How to run evaluations
- `EVAL_IMAGE_ONLY_RESULTS.md` - Example evaluation results
- `QUERY_EXAMPLES.md` - SQL query examples
- `CREATE_SFT_DATASET.md` - Original approach (now superseded)

## Success Metrics

✅ Eval completes without errors  
✅ Messages saved to database (system, user, assistant)  
✅ Outcome rewards saved with foreign keys  
✅ Filter command extracts user/assistant pairs  
✅ SFT JSONL created with proper format  
✅ Metadata includes rewards and achievements  

**Status**: 🎉 **WORKING END-TO-END!**








