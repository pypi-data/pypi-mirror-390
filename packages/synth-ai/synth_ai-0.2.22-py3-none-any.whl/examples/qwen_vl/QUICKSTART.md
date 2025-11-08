# Qwen VL Quickstart Guide

Complete guide to running vision-language models on Crafter with image observations.

## 🚀 Quick Demo

### Option 1: Run gpt-5-nano (OpenAI)
```bash
export OPENAI_API_KEY="sk-..."
uv run python examples/qwen_vl/crafter_gpt5nano_agent.py --seeds 5 --steps 10
```

### Option 2: Run Qwen-VL (synth-ai)
```bash
export SYNTH_API_KEY="sk_live_..."
uv run python examples/qwen_vl/crafter_qwen_vl_agent.py \
  --model Qwen/Qwen2-VL-7B-Instruct --seeds 5 --steps 10
```

### Option 3: Compare Both
```bash
export OPENAI_API_KEY="sk-..."
export SYNTH_API_KEY="sk_live_..."
bash examples/qwen_vl/run_vision_comparison.sh
```

---

## 📊 Expected Output

```
Running 10 Crafter episodes with model=gpt-5-nano
Using OpenAI API

Seed 00: steps=10, achievements=2, tool_calls=10, reward≈1.250
Seed 01: steps=10, achievements=1, tool_calls=10, reward≈0.750
Seed 02: steps=10, achievements=3, tool_calls=10, reward≈1.500
...

Summary
-------
{
  "model": "gpt-5-nano",
  "provider": "openai",
  "episodes": 10,
  "mean_steps": 9.8,
  "mean_achievements": 2.1,
  "total_tool_calls": 98,
  "output_dir": "examples/qwen_vl/temp/gpt5nano_frames"
}

Frames saved in: examples/qwen_vl/temp/gpt5nano_frames/
```

Each episode saves PNG frames (64x64) showing what the VLM saw:
```
examples/qwen_vl/temp/gpt5nano_frames/
  seed_0000/
    step_000.png
    step_001.png
    step_002.png
    ...
  seed_0001/
    ...
```

---

## 🎯 Full Pipeline: Data Collection → SFT → RL

### Step 1: Collect Vision Traces

Collect 100 episodes with gpt-5-nano (for teacher distillation):

```bash
export OPENAI_API_KEY="sk-..."

uv run python examples/qwen_vl/collect_vision_traces.py \
  --model gpt-5-nano \
  --provider openai \
  --episodes 100 \
  --max-steps 50 \
  --output-dir traces/gpt5nano_vision
```

**Output:**
- SQLite DB: `traces/gpt5nano_vision/rollouts.db`
- Contains multimodal traces with images
- ~5000 samples (100 episodes × ~50 steps)

**Timeline:** 30-60 minutes  
**Cost:** ~$1-2 (OpenAI gpt-5-nano)

---

### Step 2: Export to SFT JSONL

Convert SQLite traces to SFT training format:

```bash
uv run python examples/qwen_vl/export_traces_to_sft.py \
  --db-path traces/gpt5nano_vision/rollouts.db \
  --output traces/gpt5nano_vision/sft_dataset.jsonl \
  --min-steps 5
```

**Output:**
- JSONL file with OpenAI-format messages
- Each line: `{"messages": [...], "metadata": {...}}`
- Messages include base64-encoded images

---

### Step 3: Split Train/Val

```bash
uv run python examples/qwen_vl/split_sft_data.py \
  --input traces/gpt5nano_vision/sft_dataset.jsonl \
  --train-output traces/gpt5nano_vision/train.jsonl \
  --val-output traces/gpt5nano_vision/val.jsonl \
  --val-fraction 0.1
```

**Output:**
- `train.jsonl`: ~4400 samples
- `val.jsonl`: ~500 samples

---

### Step 4: Train Vision SFT

Use the example config or create your own:

```bash
cd /path/to/monorepo

export BACKEND_BASE_URL="https://synth-backend-dev-docker.onrender.com/api"

uvx synth-ai train \
  --type sft \
  --config examples/qwen_vl/configs/crafter_vlm_sft_example.toml \
  --env-file backend/.env.dev
```

**Hardware:** 2x H200 (or 4x H100)  
**Time:** 2-4 hours (2 epochs)  
**Cost:** ~$21 (Modal GPU pricing)

**Output:**
- LoRA adapter saved to HF Hub or S3
- Wandb logs with training curves

---

### Step 5: Run Vision RL (Optional)

After SFT, fine-tune with GRPO for better performance:

```toml
# example RL config
[algorithm]
type = "online"
method = "grpo"

[model]
base = "Qwen/Qwen2-VL-7B-Instruct"
adapter = "s3://my-bucket/qwen2vl_crafter_sft"  # From SFT

[compute]
gpu_count = 4  # 2 inference + 2 training
```

**Time:** 6-10 hours (20 iterations)  
**Cost:** ~$112

---

## 📁 File Structure

```
synth-ai/examples/qwen_vl/
├── README.md                       # Overview
├── QUICKSTART.md                   # This file
├── __init__.py
│
├── crafter_gpt5nano_agent.py       # OpenAI gpt-5-nano demo
├── crafter_qwen_vl_agent.py        # Qwen-VL (synth-ai) demo
├── collect_vision_traces.py        # Trace collection for SFT
├── run_vision_comparison.sh        # Compare both models
│
├── configs/
│   └── crafter_vlm_sft_example.toml  # Example SFT config
│
└── temp/                           # Output frames and summaries
    ├── gpt5nano_frames/
    ├── qwen_vl_frames/
    └── comparison/
```

---

## 🔍 How Vision Detection Works

CrafterPolicy automatically detects vision capability:

```python
# From examples/task_apps/crafter/.../policy.py
@staticmethod
def _is_vision_model(model_name: str) -> bool:
    """Check if model supports vision from its name."""
    model_lower = model_name.lower()
    
    vision_patterns = [
        "gpt-5",           # ✅ gpt-5-nano, gpt-5-turbo, etc.
        "gpt-4o",          # ✅ gpt-4o-mini, gpt-4o
        "qwen-vl",         # ✅ Qwen-VL-Chat
        "qwen2-vl",        # ✅ Qwen2-VL-7B-Instruct
        "qwen3-vl",        # ✅ Qwen3-VL-8B
        # ... more patterns
    ]
    
    return any(pattern in model_lower for pattern in vision_patterns)
```

If detected:
- Policy includes base64 image in user message
- Images are 64x64 PNG frames from Crafter
- Format: `{"type": "image_url", "image_url": {"url": "data:image/png;base64,..."}}`

---

## 🎛️ Advanced Configuration

### Custom Image Resolution

Edit Crafter task instance config:

```python
instance.config = {
    "seed": seed,
    "length": 256,
    "area": [128, 128],  # Higher resolution (default: 64x64)
}
```

**Note:** Higher resolution = more tokens = higher cost

### Image-Only Mode

Disable text observations, use only images:

```python
await policy.initialize({
    "use_tools": True,
    "model": model,
    "image_only_mode": True,  # No text, only images
})
```

### Multiple Images per Step

For temporal context (not yet implemented):

```python
# Future: Include last N frames
image_parts = [
    {"type": "image_url", "image_url": {"url": frame_t}},
    {"type": "image_url", "image_url": {"url": frame_t_minus_1}},
    {"type": "image_url", "image_url": {"url": frame_t_minus_2}},
]
```

---

## 🐛 Troubleshooting

### Error: `OPENAI_API_KEY not set`
```bash
export OPENAI_API_KEY="sk-..."
```

### Error: `SYNTH_API_KEY not set`
```bash
export SYNTH_API_KEY="sk_live_..."
```

### Error: `TracingStore not available`
Traces require synth-ai tracing module:
```bash
uv sync  # Ensure all dependencies are installed
```

### Vision not detected
Manually enable:
```python
await policy.initialize({"use_vision": True})
```

---

## 📚 Related Documentation

- **SFT Pipeline:** See `/Users/joshpurtell/Documents/GitHub/monorepo/vision_sft_rl.txt` (Phase 9)
- **Crafter Environment:** `examples/task_apps/crafter/README.md`
- **OpenAI VLM Examples:** `examples/vlm/crafter_openai_vlm_agent.py`
- **Image-Only Eval:** `examples/task_apps/IMAGE_ONLY_EVAL_QUICKSTART.md`

---

## 🎉 Next Steps

1. ✅ Run demos to verify vision inference works
2. 🎯 Collect training traces (100-1000 episodes)
3. 📦 Export and split into train/val
4. 🚀 Train VLM with LoRA (see `crafter_vlm_sft_example.toml`)
5. 🏆 Fine-tune with RL/GRPO for better achievement rates
6. 📊 Benchmark: base model vs SFT vs SFT+RL

**Expected Performance:**
- Base Qwen-VL: ~5-10% achievement rate
- After SFT (gpt-5-nano distillation): ~20-30%
- After RL (20 iterations): ~40-50%

---

Happy vision-language model training! 🚀✨

