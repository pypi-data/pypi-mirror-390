# Collect Vision Training Data via synth-ai CLI

Use synth-ai's built-in CLI tools to collect vision traces for SFT training.

## 📋 Overview

**Pipeline:**
1. `synth-ai deploy --runtime=uvicorn` → Start the Crafter task app locally
2. `synth-ai eval` → Run rollouts with GPT-4o Mini or Qwen3-VL and collect traces
3. `synth-ai filter` → Filter traces by quality, convert to SFT format

---

## 🚀 Step 1: Serve Crafter Task App

### Option A: Serve Locally

```bash
cd /Users/joshpurtell/Documents/GitHub/synth-ai

# Serve Crafter task app on localhost:8000
uvx synth-ai deploy grpo-crafter-task-app \
  --runtime uvicorn \
  --port 8000 \
  --trace traces/v3
```

**Output:**
```
🚀 Task app running at http://localhost:8000
📝 Health check: http://localhost:8000/health
```

### Option B: Use Hosted Task App (Modal)

If you already have a deployed Crafter task app on Modal:
```bash
export TASK_APP_URL="https://synth-laboratories--grpo-crafter-task-app.modal.run"
```

---

## 🎯 Step 2: Run Eval with Vision Models

### Collect GPT-4o-mini Vision Traces (OpenAI)

Create eval config: `examples/qwen_vl/configs/eval_gpt5nano_vision.toml`

```toml
# Evaluation config for gpt-4o-mini (vision)
# Legacy filename kept for convenience
[eval]
app_id = "grpo-crafter-task-app"
task_app_url = "http://localhost:8000"  # or your hosted URL
model = "gpt-4o-mini-2024-07-18"
seeds = "0-99"
max_turns = 50
concurrency = 5
env_name = "crafter"
policy_name = "crafter-react"
trace_format = "structured"
return_trace = true

[eval.env_config]
env_params = {max_steps_per_episode = 50}

[eval.policy_config]
provider = "openai"
model = "gpt-4o-mini-2024-07-18"
temperature = 0.7
max_tokens = 512
use_vision = true
image_only_mode = false
use_tools = true
```

**Run evaluation:**
```bash
export OPENAI_API_KEY="sk-..."

uvx synth-ai eval \
  --config examples/qwen_vl/configs/eval_gpt5nano_vision.toml \
  --trace-db traces/gpt4omini_vision/rollouts.db
```

**Expected output:**
```
🎮 Running evaluation: gpt-4o-mini on crafter
📊 Episodes: 100, Max steps: 50
🔍 Vision: enabled (auto-detected from model name)
📦 Collecting traces to: traces/gpt4omini_vision/rollouts.db

Episode 0/100 (seed=0): 50 steps, 3 achievements ✓
Episode 1/100 (seed=1): 48 steps, 2 achievements ✓
Episode 2/100 (seed=2): 50 steps, 4 achievements ✓
...
Episode 99/100 (seed=99): 50 steps, 3 achievements ✓

✅ Evaluation complete!
   Total episodes: 100
   Total steps: 4,923
   Avg achievements: 2.8
   Traces saved to: traces/gpt4omini_vision/rollouts.db
```

---

### Collect Qwen3-VL Traces (Synth hosted inference)

Create eval config: `examples/qwen_vl/configs/eval_qwen3vl_vision.toml`

```toml
# Evaluation config for Qwen3-VL vision rollouts
[eval]
app_id = "grpo-crafter-task-app"
task_app_url = "http://localhost:8000"
model = "Qwen/Qwen3-VL-8B-Instruct"
seeds = "100-199"
max_turns = 50
concurrency = 5
env_name = "crafter"
policy_name = "crafter-react"
trace_format = "structured"
return_trace = true

[eval.env_config]
env_params = {max_steps_per_episode = 50}

[eval.policy_config]
provider = "synth"
model = "Qwen/Qwen3-VL-8B-Instruct"
temperature = 0.7
max_tokens = 512
use_vision = true
image_only_mode = false
use_tools = true
```

**Run evaluation:**
```bash
export SYNTH_API_KEY="sk_live_..."

uvx synth-ai eval \
  --config examples/qwen_vl/configs/eval_qwen3vl_vision.toml \
  --trace-db traces/qwen3vl_vision/rollouts.db
```

---

## 🔍 Step 3: Filter Traces for SFT

Use `synth-ai filter` to:
1. Remove low-quality episodes (too short, no achievements)
2. Convert to SFT JSONL format
3. Split into train/val sets

### Filter Config

Create `examples/qwen_vl/configs/filter_vision_sft.toml`:

```toml
# Filter vision traces for SFT training
[filter]
input_db = "traces/gpt4omini_vision/rollouts.db"
output_dir = "traces/gpt4omini_vision/sft"

# Quality filters
min_steps_per_episode = 5
min_achievements_per_episode = 1
max_steps_per_episode = 50

# Remove episodes where model got stuck (repeated actions)
detect_loops = true
max_repeated_actions = 5

# Export format
export_format = "sft_jsonl"  # OpenAI-style messages format
include_images = true         # Keep base64 images in messages

# Train/val split
train_val_split = true
val_fraction = 0.1
random_seed = 42

[sft]
# SFT-specific options
max_sequence_length = 2048    # Truncate if longer
deduplicate = true            # Remove duplicate state-action pairs
shuffle = true                # Shuffle samples
```

**Run filter:**
```bash
uvx synth-ai filter \
  --config examples/qwen_vl/configs/filter_vision_sft.toml
```

**Expected output:**
```
📂 Loading traces from traces/gpt4omini_vision/rollouts.db
   Total episodes: 100
   Total steps: 4,923

🔍 Applying quality filters...
   ✓ Min steps (5): kept 98 episodes
   ✓ Min achievements (1): kept 87 episodes
   ✓ Loop detection: removed 3 episodes
   
   Final: 84 episodes, 4,235 steps

📦 Exporting to SFT JSONL format...
   ✓ Images included (base64 PNG, 64x64)
   ✓ Deduplication: removed 45 duplicate samples
   ✓ Final dataset: 4,190 samples

✂️ Splitting train/val (90%/10%)...
   ✓ Train: 3,771 samples → traces/gpt4omini_vision/sft/train.jsonl
   ✓ Val: 419 samples → traces/gpt4omini_vision/sft/val.jsonl

✅ Filter complete!
```

---

## 📊 Verify Dataset

Check the SFT JSONL format:

```bash
# Inspect first sample
head -1 traces/gpt4omini_vision/sft/train.jsonl | jq .
```

**Expected format:**
```json
{
  "messages": [
    {
      "role": "system",
      "content": "You are a Crafter agent. Your goal is to survive and unlock achievements..."
    },
    {
      "role": "user",
      "content": [
        {
          "type": "text",
          "text": "Observation:\n- Health: 9/9\n- Hunger: 9/9\n- Position: (32, 32)\n..."
        },
        {
          "type": "image_url",
          "image_url": {
            "url": "data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAA..."
          }
        }
      ]
    },
    {
      "role": "assistant",
      "content": null,
      "tool_calls": [
        {
          "id": "call_abc123",
          "type": "function",
          "function": {
            "name": "move",
            "arguments": "{\"direction\": \"forward\"}"
          }
        }
      ]
    }
  ],
  "metadata": {
    "episode_id": "ep0042",
    "step": 12,
    "seed": 42,
    "has_image": true,
    "model": "gpt-4o-mini-2024-07-18"
  }
}
```

---

## 🚀 Step 4: Train Vision SFT

Now use the filtered dataset for SFT training:

```bash
cd /Users/joshpurtell/Documents/GitHub/monorepo

export BACKEND_BASE_URL="https://synth-backend-dev-docker.onrender.com/api"

uvx synth-ai train \
  --type sft \
  --config configs/vision_sft/crafter_qwen3vl_8b_gpt5nano.toml \
  --dataset traces/gpt4omini_vision/sft/train.jsonl \
  --eval-dataset traces/gpt4omini_vision/sft/val.jsonl \
  --env-file backend/.env.dev
```

---

## 🔄 Complete Workflow (One-Liner per Step)

```bash
# Terminal 1: Serve task app
cd /Users/joshpurtell/Documents/GitHub/synth-ai
uvx synth-ai deploy grpo-crafter-task-app \
  --runtime uvicorn \
  --port 8000 \
  --trace traces/v3

# Terminal 2: Collect traces
export OPENAI_API_KEY="sk-..."
uvx synth-ai eval \
  --config examples/qwen_vl/configs/eval_gpt5nano_vision.toml \
  --trace-db traces/gpt4omini_vision/rollouts.db

# Terminal 2: Filter and export
uvx synth-ai filter \
  --config examples/qwen_vl/configs/filter_vision_sft.toml

# Terminal 2: Train SFT
cd /Users/joshpurtell/Documents/GitHub/monorepo
export BACKEND_BASE_URL="https://synth-backend-dev-docker.onrender.com/api"
uvx synth-ai train \
  --type sft \
  --config configs/vision_sft/crafter_qwen3vl_8b_gpt5nano.toml \
  --dataset /Users/joshpurtell/Documents/GitHub/synth-ai/traces/gpt4omini_vision/sft/train.jsonl \
  --eval-dataset /Users/joshpurtell/Documents/GitHub/synth-ai/traces/gpt4omini_vision/sft/val.jsonl \
  --env-file backend/.env.dev
```

---

## 💰 Cost & Timeline

| Step | Duration | Cost | Notes |
|------|----------|------|-------|
| 1. Serve | Continuous | Free | Local or Modal |
| 2. Eval (100 episodes) | 30-60 min | ~$1-2 | OpenAI gpt-4o-mini |
| 3. Filter | < 5 min | Free | Local processing |
| 4. SFT (2 epochs) | 2-4 hrs | ~$21 | 2x H200 on Modal |

**Total:** ~$22-23, ~3-5 hours

---

## 🎯 Advanced: Collect from Multiple Models

Compare teacher quality by collecting from multiple models:

```bash
# Collect from gpt-5-nano
uvx synth-ai eval --config configs/eval_gpt5nano_vision.toml

# Collect from gpt-4o-mini (stronger teacher)
uvx synth-ai eval --config configs/eval_gpt4o_mini_vision.toml

# Collect from Qwen3-VL (for comparison)
uvx synth-ai eval --config configs/eval_qwen3vl_vision.toml

# Merge and filter all traces
uvx synth-ai filter \
  --input-dbs traces/gpt4omini_vision/rollouts.db,traces/qwen3vl_vision/rollouts.db \
  --output-dir traces/merged_vision/sft \
  --config configs/filter_vision_sft.toml
```

---

## 📚 Next Steps

1. ✅ Collect traces with `synth-ai eval`
2. ✅ Filter and export with `synth-ai filter`
3. 🚀 Train VLM with `synth-ai train --type sft`
4. 🏆 Fine-tune with RL: `synth-ai train --type rl`
5. 📊 Evaluate final model: `synth-ai eval --config configs/eval_trained_vlm.toml`

---

## 🔧 Troubleshooting

### Vision not detected
Add explicitly in eval config:
```toml
[eval]
use_vision = true
```

### Task app connection failed
Check task app is running:
```bash
curl http://localhost:8000/health
```

### Traces not saving
Ensure you pass `--trace-db` (or accept the default) so traces land in a SQLite/Turso database.

### Filter removes all samples
Lower quality thresholds:
```toml
[filter]
min_steps_per_episode = 3      # Lower from 5
min_achievements_per_episode = 0  # Allow episodes with no achievements
```

---

## 📖 Related Docs

- **synth-ai CLI Reference:** Run `uvx synth-ai --help`
- **Eval Config Schema:** `synth-ai eval --help`
- **Filter Config Schema:** `synth-ai filter --help`
- **Full Pipeline:** See `/Users/joshpurtell/Documents/GitHub/monorepo/vision_sft_rl.txt`
