# Vision RL - Quick Start 🚀

Complete RL training with vision models in 3 commands.

## Prerequisites

```bash
export SYNTH_API_KEY="your-key"
export BACKEND_BASE_URL="https://agent-learning.onrender.com/api"
export ENVIRONMENT_API_KEY="your-modal-key"
```

## Option 1: Run Tests (Validate Pipeline)

```bash
cd /Users/joshpurtell/Documents/GitHub/synth-ai

# Fast test (~3-5 min)
uv run pytest tests/integration/cli/test_cli_train_rl_vision.py::test_cli_train_rl_vision_small_config -v -s

# Full test (~5-10 min)
uv run pytest tests/integration/cli/test_cli_train_rl_vision.py::test_cli_train_rl_vision_qwen3vl4b -v -s

# All vision tests
uv run pytest tests/integration/cli/test_cli_train_rl_vision.py -v -s
```

## Option 2: Manual Training

```bash
# 1. Deploy task app
uvx synth-ai task-app deploy grpo-crafter --name grpo-crafter-task-app

# 2. Get URL (from deploy output)
export TASK_APP_URL="https://your-app.modal.run"

# 3. Run RL training
uvx synth-ai train \
  --type rl \
  --config examples/qwen_vl/configs/crafter_rl_vision_qwen3vl4b.toml \
  --backend $BACKEND_BASE_URL \
  --task-url $TASK_APP_URL
```

## What It Does

1. ✅ Deploys Crafter task app (generates image observations)
2. ✅ Runs Qwen3-VL-4B with image-only input
3. ✅ RL training with GRPO/GSPO
4. ✅ Uses same task app as SFT data collection

## Configs

### Fast CI Test
**Config:** `tests/artifacts/configs/rl.vision.small.toml`
- 1 iteration, 3 steps, 1 episode
- Runtime: ~5 minutes

### Full Training
**Config:** `examples/qwen_vl/configs/crafter_rl_vision_qwen3vl4b.toml`
- 3 iterations per epoch, 10 steps, 2 episodes
- Runtime: ~30-45 minutes per epoch

## Expected Output

```
✅ Vision RL job created: job-abc123
   Model: Qwen3-VL-4B
   Task App: https://your-app.modal.run
   Image Mode: image_only
```

## Troubleshooting

### Task app timeout?
```bash
export TASK_APP_WARMUP_TIMEOUT=600  # 10 minutes
```

### OOM?
```toml
# Edit config: reduce batch_size to 1
[training]
batch_size = 1
```

### Not seeing images?
```bash
# Verify config
grep "supports_vision = true" <config.toml>
grep "use_vision = true" <config.toml>
```

## Full Documentation

- 📘 **Complete Guide:** `RL_VISION_COMPLETE.md`
- 🧪 **Testing Details:** `RL_VISION_TESTING.md`
- 📊 **SFT Pipeline:** `VLM_PIPELINE_COMPLETE.md`

## One-Liner Test

```bash
cd /Users/joshpurtell/Documents/GitHub/synth-ai && \
  uv run pytest tests/integration/cli/test_cli_train_rl_vision.py::test_cli_train_rl_vision_small_config -v -s
```

---

**Ready?** Run the tests to validate your vision RL pipeline! 🎯

