# Vision RL Integration Testing

Complete integration tests for Reinforcement Learning with vision-language models using the Crafter task app.

## Overview

These tests verify the full vision RL pipeline:
1. **Task App**: Same Crafter task app used for SFT data collection (generates image observations)
2. **Model**: Qwen3-VL-4B (smaller, faster for testing)
3. **Policy**: Uses `image_only_mode=true` - agent sees only images, no text observations
4. **Training**: Full RL (GRPO/GSPO) with vision-capable model

## Files

### Configs
- `configs/crafter_rl_vision_qwen3vl4b.toml` - Full RL config for Qwen3-VL-4B with vision

### Tests
- `../../tests/integration/cli/test_cli_train_rl_vision.py` - Integration tests:
  - `test_cli_train_rl_vision_qwen3vl4b` - Full RL training test
  - `test_task_app_vision_support` - Task app vision capability test

## Quick Start

### 1. Prerequisites

```bash
# Required environment variables
export SYNTH_API_KEY="your-api-key"
export BACKEND_BASE_URL="https://agent-learning.onrender.com/api"  # or your backend
export ENVIRONMENT_API_KEY="your-modal-key"  # For Modal deployment

# Optional: for faster testing
export TASK_APP_WARMUP_TIMEOUT=300  # 5min for vision models
export SYNTH_TRAIN_TEST_POLL_TIMEOUT=180
```

### 2. Run Tests

```bash
cd /Users/joshpurtell/Documents/GitHub/synth-ai

# Run all vision RL tests
uv run pytest tests/integration/cli/test_cli_train_rl_vision.py -v -s

# Run specific test
uv run pytest tests/integration/cli/test_cli_train_rl_vision.py::test_cli_train_rl_vision_qwen3vl4b -v -s

# Run with marks
uv run pytest -m "vision and slow" -v -s
```

### 3. Manual RL Training (without pytest)

```bash
# 1. Deploy task app (if not already deployed)
uvx synth-ai task-app deploy grpo-crafter --name grpo-crafter-task-app

# 2. Get task app URL (from deploy output)
export TASK_APP_URL="https://your-app.modal.run"

# 3. Run RL training
uvx synth-ai train \
  --type rl \
  --config examples/qwen_vl/configs/crafter_rl_vision_qwen3vl4b.toml \
  --backend $BACKEND_BASE_URL \
  --task-url $TASK_APP_URL
```

## Configuration Details

### Model: Qwen3-VL-4B
```toml
[model]
base = "Qwen/Qwen3-VL-4B-Instruct"
trainer_mode = "lora"
supports_vision = true  # Enable vision support
```

### Vision-Specific Settings
```toml
[vllm]
limit_mm_per_prompt = { "image": 1 }  # Max 1 image per prompt

[rollout.policy_config]
use_vision = true  # Enable vision input
image_only_mode = true  # Use only images, no text observations
temperature = 0.6
max_tokens = 512

[training]
batch_size = 2  # Smaller for vision models (memory)
max_images_per_message = 1
supports_vision = true
```

### GPU Allocation (2x H200)
```toml
[topology]
gpus_for_vllm = 1  # Inference
gpus_for_training = 1  # Training
tensor_parallel = 1
```

## Test Details

### Test 1: Full RL Training
**Function:** `test_cli_train_rl_vision_qwen3vl4b`

**What it tests:**
1. Task app deployment
2. Task app warmup (health check)
3. RL job submission with vision config
4. Job creation confirmation

**Expected output:**
```
✅ Vision RL job created: job-abc123
   Model: Qwen3-VL-4B
   Task App: https://your-app.modal.run
   Image Mode: image_only
```

**Runtime:** ~5-10 minutes (deploy + warmup + job submit)

### Test 2: Task App Vision Support
**Function:** `test_task_app_vision_support`

**What it tests:**
1. Task app can be deployed
2. Task app health endpoint responds
3. Task app accepts vision policy config
4. Can make rollout request with `use_vision=true` and `image_only_mode=true`

**Expected output:**
```
✅ Task app supports vision config
   Response keys: ['trajectory', 'metadata', ...]
```

**Runtime:** ~2-3 minutes (deploy + warmup + single rollout)

## Task App Details

The Crafter task app (`grpo-crafter-task-app`) provides:

### Environment
- **Crafter game** with visual observations
- Generates RGB images (64x64 or configurable)
- Text observations also available (but ignored in `image_only_mode`)

### Policy (crafter-react)
- **Vision Detection:** Auto-detects vision models from name (e.g., "Qwen3-VL", "gpt-4o-mini")
- **Image Formatting:** Converts observations to OpenAI-style multimodal messages
- **Tool Calling:** Supports structured action space via tools

### Trace Format
- **Structured traces** with multimodal messages
- Images stored as base64 in trace DB
- Compatible with `synth-ai filter` for SFT export

## Integration with SFT Pipeline

This RL setup uses the **same task app** as the SFT data collection:

### SFT Data Collection
```bash
# Collect episodes with gpt-4o-mini teacher
uvx synth-ai eval --config configs/eval_gpt4o_vision_proper.toml

# Export to SFT dataset
uvx synth-ai filter --config configs/filter_vision_sft.toml
```

### RL Training
```bash
# Train student model (Qwen3-VL-4B) with RL
uvx synth-ai train \
  --type rl \
  --config configs/crafter_rl_vision_qwen3vl4b.toml
```

**Benefits:**
1. **Consistency:** Same environment, same observations
2. **Curriculum:** SFT → RL progression
3. **Debugging:** Compare SFT and RL traces in same format

## Troubleshooting

### Task App Deployment Fails
```bash
# Check Modal auth
modal token set --token-id <id> --token-secret <secret>

# Check environment variables
echo $SYNTH_API_KEY
echo $ENVIRONMENT_API_KEY

# Try manual deploy
uvx synth-ai task-app deploy grpo-crafter --name grpo-crafter-task-app
```

### Task App Won't Warm Up
```bash
# Increase timeout
export TASK_APP_WARMUP_TIMEOUT=600  # 10 minutes

# Check task app logs in Modal dashboard
# https://modal.com/apps

# Try health check manually
curl https://your-app.modal.run/health
```

### RL Job Submission Fails
```bash
# Check backend connectivity
curl $BACKEND_BASE_URL/health

# Verify API key
curl -H "Authorization: Bearer $SYNTH_API_KEY" $BACKEND_BASE_URL/api/health

# Check task app URL format
echo $TASK_APP_URL  # Should be https://...modal.run
```

### Vision Model OOM (Out of Memory)
```toml
# Reduce batch size in config
[training]
batch_size = 1  # Down from 2
gradient_accumulation_steps = 4  # Up from 2

# Reduce concurrent rollouts
[rollout]
max_concurrent_rollouts = 2  # Down from 4
```

### Images Not Appearing in Training
```bash
# Verify vision support is enabled
grep -A 5 "\[model\]" configs/crafter_rl_vision_qwen3vl4b.toml
# Should show: supports_vision = true

# Check policy config
grep -A 10 "\[rollout.policy_config\]" configs/crafter_rl_vision_qwen3vl4b.toml
# Should show: use_vision = true, image_only_mode = true

# Verify vLLM config
grep -A 3 "\[vllm\]" configs/crafter_rl_vision_qwen3vl4b.toml
# Should show: limit_mm_per_prompt = { "image": 1 }
```

## Performance Expectations

### Qwen3-VL-4B (2x H200)
- **Throughput:** ~2-4 episodes/min (with TP=1)
- **Memory:** ~40-60GB GPU (model + images + gradients)
- **Iteration Time:** ~10-15 min (with 4 episodes, 10 steps each)

### Training Time Estimates
- **3 iterations (test):** ~30-45 minutes
- **10 iterations (short run):** ~2-3 hours
- **50 iterations (full run):** ~12-20 hours

## Next Steps

### 1. Baseline Evaluation
```bash
# Evaluate untrained model
uvx synth-ai eval \
  --model Qwen/Qwen3-VL-4B-Instruct \
  --env crafter \
  --seeds 0,1,2,3,4 \
  --policy-config '{"use_vision": true, "image_only_mode": true}'
```

### 2. SFT Initialization (Optional)
```bash
# Train on teacher demonstrations first
uvx synth-ai train \
  --type sft \
  --model Qwen/Qwen3-VL-4B-Instruct \
  --data traces/gpt4o_vision/sft/train.jsonl
```

### 3. RL Fine-Tuning
```bash
# Run full RL training
uvx synth-ai train \
  --type rl \
  --config configs/crafter_rl_vision_qwen3vl4b.toml \
  --iterations 50
```

### 4. Eval Comparison
```bash
# Compare pre-trained vs post-RL
uvx synth-ai eval --model <rl-checkpoint> --seeds 0-9
```

## References

- **VLM SFT Pipeline:** `examples/qwen_vl/PIPELINE_RUN_LOG.txt`
- **Image Validation:** `examples/qwen_vl/IMAGE_VALIDATION_COMPLETE.md`
- **Task App Source:** `examples/task_apps/crafter/task_app/`
- **Policy Implementation:** `examples/task_apps/crafter/task_app/synth_envs_hosted/policy.py`

## CI Integration

### Pytest Marks
```python
@pytest.mark.slow      # Takes >5 minutes
@pytest.mark.vision    # Requires vision model support
@pytest.mark.integration  # Full pipeline test
```

### Run in CI
```bash
# Run all integration tests including vision
pytest tests/integration/cli/ -m integration -v

# Run only vision tests
pytest -m vision -v

# Skip slow tests for PR checks
pytest -m "not slow" -v
```

---

**Status:** ✅ Integration tests ready. Task app and RL config validated for Qwen3-VL-4B with image-only observations.

