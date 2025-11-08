# Creating SFT Datasets from Crafter Traces

There are two approaches to create SFT (Supervised Fine-Tuning) datasets from Crafter rollouts:

## Approach 1: Direct SFT Recording (Recommended)

Crafter's rollout system can write SFT-ready JSONL files directly during evaluation by setting the `sft_output_dir`.

### Setup

1. Set the SFT output directory environment variable:
```bash
export SFT_OUTPUT_DIR="ft_data/crafter_sft"
```

2. Run evaluation:
```bash
cd /Users/joshpurtell/Documents/GitHub/synth-ai

export TASKAPP_TRACING_ENABLED=1
export TURSO_NATIVE=1
export SQLD_DB_PATH="traces/v3/crafter_eval.db"
export SFT_OUTPUT_DIR="ft_data/crafter_sft"  # Enable SFT recording

uv run synth-ai eval grpo-crafter \
  --config examples/task_apps/crafter/eval_image_only_gpt4o.toml
```

3. SFT files will be written to:
```
ft_data/crafter_sft/
├── sft_<run_id_1>.jsonl
├── sft_<run_id_2>.jsonl
├── ...
└── sft_<run_id_10>.jsonl
```

### SFT Record Format

Each JSONL file contains records like:
```json
{
  "messages": [
    {"role": "system", "content": "...system prompt..."},
    {"role": "user", "content": "...observation..."},
    {"role": "assistant", "content": "...action..."}
  ],
  "metadata": {
    "run_id": "...",
    "turn": 5,
    "reward": 1.0,
    ...
  }
}
```

### Combine Multiple Files

```bash
# Combine all SFT files into one
cat ft_data/crafter_sft/sft_*.jsonl > ft_data/crafter_combined.jsonl

# Count examples
wc -l ft_data/crafter_combined.jsonl
```

## Approach 2: Extract from Turso Database (Not Currently Supported)

The `synth-ai filter` command is designed for traces with a different structure (where prompt/completion are stored in session metadata). 

**Current Limitation**: Crafter's SessionTracer-based traces don't store messages in the format expected by the filter command.

### Why Filter Doesn't Work

The filter command expects:
```python
metadata = {
    "prompt": "...",  # User message
    "completion": "..."  # Assistant response
}
```

But Crafter traces store:
- Messages in separate `messages` table (currently 0 messages - not recorded during eval)
- Rewards in `outcome_rewards` table
- Metadata without prompt/completion fields

### Future Enhancement

To make filter work with Crafter traces, we would need to:
1. Modify rollout to record messages to the `messages` table
2. Update filter command to query `messages` table directly
3. Join with `outcome_rewards` to filter by achievements

## Comparison

| Feature | Direct SFT | Filter Command |
|---------|-----------|----------------|
| **Setup** | Set `SFT_OUTPUT_DIR` | Create filter config |
| **When** | During rollout | After rollout |
| **Format** | JSONL per rollout | Combined JSONL |
| **Filtering** | Manual (combine files) | Automatic (SQL queries) |
| **Status** | ✅ Works now | ❌ Needs implementation |

## Recommended Workflow

### 1. Run evaluation with SFT recording:
```bash
export SFT_OUTPUT_DIR="ft_data/crafter_sft"
uv run synth-ai eval grpo-crafter --config examples/task_apps/crafter/eval_image_only_gpt4o.toml
```

### 2. Filter for successful rollouts:

Since we can't use the filter command yet, manually select files:

```bash
# Query database to find session_ids with rewards
sqlite3 traces/v3/crafter_eval.db \
  "SELECT session_id FROM outcome_rewards WHERE total_reward > 0" \
  > successful_sessions.txt

# Create directory for filtered SFT
mkdir -p ft_data/crafter_sft_filtered

# Copy only successful rollout SFT files
while read session_id; do
  if [ -f "ft_data/crafter_sft/sft_${session_id}.jsonl" ]; then
    cp "ft_data/crafter_sft/sft_${session_id}.jsonl" ft_data/crafter_sft_filtered/
  fi
done < successful_sessions.txt

# Combine filtered files
cat ft_data/crafter_sft_filtered/sft_*.jsonl > ft_data/crafter_high_reward.jsonl

echo "Created SFT dataset: ft_data/crafter_high_reward.jsonl"
wc -l ft_data/crafter_high_reward.jsonl
```

### 3. Verify dataset:

```bash
# Look at first example
head -1 ft_data/crafter_high_reward.jsonl | jq .

# Count examples
wc -l ft_data/crafter_high_reward.jsonl

# Check message types
jq -r '.messages[].role' ft_data/crafter_high_reward.jsonl | sort | uniq -c
```

## Example: Complete Pipeline

```bash
#!/bin/bash
# complete_sft_pipeline.sh

cd /Users/joshpurtell/Documents/GitHub/synth-ai

# 1. Run evaluation with SFT recording
export TASKAPP_TRACING_ENABLED=1
export TURSO_NATIVE=1
export SQLD_DB_PATH="traces/v3/crafter_eval.db"
export SFT_OUTPUT_DIR="ft_data/crafter_sft"

echo "Running evaluation..."
uv run synth-ai eval grpo-crafter \
  --config examples/task_apps/crafter/eval_image_only_gpt4o.toml

# 2. Filter for successful rollouts
echo "Filtering for successful rollouts..."
mkdir -p ft_data/crafter_sft_filtered

sqlite3 traces/v3/crafter_eval.db \
  "SELECT session_id FROM outcome_rewards WHERE total_reward > 0" | \
while read session_id; do
  if [ -f "ft_data/crafter_sft/sft_${session_id}.jsonl" ]; then
    cp "ft_data/crafter_sft/sft_${session_id}.jsonl" ft_data/crafter_sft_filtered/
  fi
done

# 3. Combine into single dataset
echo "Creating combined dataset..."
cat ft_data/crafter_sft_filtered/sft_*.jsonl > ft_data/crafter_high_reward.jsonl

# 4. Report statistics
echo ""
echo "=== SFT Dataset Created ==="
echo "Total examples: $(wc -l < ft_data/crafter_high_reward.jsonl)"
echo "Location: ft_data/crafter_high_reward.jsonl"
echo ""
echo "Rollouts included:"
sqlite3 traces/v3/crafter_eval.db \
  "SELECT 
    COUNT(*) as count,
    SUM(total_reward) as total_reward,
    AVG(achievements_count) as avg_achievements
   FROM outcome_rewards 
   WHERE total_reward > 0"
```

## Troubleshooting

### No SFT Files Created

**Issue**: `ft_data/crafter_sft/` is empty after evaluation

**Possible causes**:
1. `SFT_OUTPUT_DIR` environment variable not set
2. Rollout doesn't record SFT by default in eval mode
3. Directory permissions issue

**Debug**:
```bash
# Check if variable is set
echo $SFT_OUTPUT_DIR

# Check directory exists and is writable
ls -la ft_data/

# Try with explicit path
export SFT_OUTPUT_DIR="/Users/joshpurtell/Documents/GitHub/synth-ai/ft_data/crafter_sft"
```

### SFT Files Don't Match Successful Rollouts

**Issue**: Have SFT files for rollouts with 0 rewards

**Solution**: This is expected - SFT is recorded for all rollouts. Use the filtering step to keep only successful ones.

## Future Work

To enable the `synth-ai filter` command for Crafter traces:

1. **Modify Crafter rollout** to record messages to database:
```python
# In RolloutTracingContext
await self.tracer.record_message(
    content=user_prompt,
    message_type="user",
    metadata={"turn": turn}
)

await self.tracer.record_message(
    content=assistant_response,
    message_type="assistant", 
    metadata={"turn": turn, "reward": step_reward}
)
```

2. **Update filter command** to query messages table:
```python
# Instead of looking for metadata.prompt/completion
# Query messages table directly
messages = await tracer.db.get_messages(session_id)
```

3. **Create filter config** that works:
```toml
[filter]
db = "traces/v3/crafter_eval.db"
output = "ft_data/crafter_filtered.jsonl"
min_official_score = 0.01  # Filter by outcome_rewards
```

## See Also

- `README_IMAGE_ONLY_EVAL.md` - How to run evaluations
- `EVAL_IMAGE_ONLY_RESULTS.md` - Example results
- `QUERY_EXAMPLES.md` - SQL queries for trace analysis








