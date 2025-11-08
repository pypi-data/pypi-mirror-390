# ✅ VLM Setup Complete!

Complete vision-language model (VLM) infrastructure for Crafter with image observations.

## 📦 What Was Created

### **Core Examples** (Python Scripts)
1. **`crafter_gpt5nano_agent.py`** - Demo agent using OpenAI gpt-5-nano
2. **`crafter_qwen_vl_agent.py`** - Demo agent using Qwen-VL via synth-ai
3. **`collect_vision_traces.py`** - Manual trace collection script

### **CLI-Based Pipeline** (Recommended)
4. **`run_vision_sft_pipeline.sh`** - Complete automated pipeline
5. **`run_vision_comparison.sh`** - Compare gpt-5-nano vs Qwen-VL

### **Configuration Files**
6. **`configs/eval_gpt5nano_vision.toml`** - Eval config for gpt-5-nano
7. **`configs/eval_qwen3vl_vision.toml`** - Eval config for Qwen3-VL
8. **`configs/eval_gpt4o_mini_vision.toml`** - Eval config for gpt-4o-mini (stronger teacher)
9. **`configs/filter_vision_sft.toml`** - Filter config for gpt-5-nano traces
10. **`configs/filter_qwen3vl_sft.toml`** - Filter config for Qwen3-VL traces
11. **`configs/crafter_vlm_sft_example.toml`** - Example SFT training config

### **Documentation**
12. **`README.md`** - Overview and quick start
13. **`QUICKSTART.md`** - Complete manual pipeline guide
14. **`collect_data_via_cli.md`** - **Detailed CLI guide** ⭐
15. **`SETUP_COMPLETE.md`** - This file

---

## 🚀 Quick Start (3 Commands)

### Option 1: Automated Pipeline
```bash
cd /Users/joshpurtell/Documents/GitHub/synth-ai
export OPENAI_API_KEY="sk-..."
bash examples/qwen_vl/run_vision_sft_pipeline.sh
```

### Option 2: Step-by-Step CLI
```bash
# 1. Collect traces (30-60 min)
uvx synth-ai eval --config examples/qwen_vl/configs/eval_gpt5nano_vision.toml

# 2. Filter and export (< 1 min)
uvx synth-ai filter --config examples/qwen_vl/configs/filter_vision_sft.toml

# 3. Train SFT (2-4 hours)
cd /Users/joshpurtell/Documents/GitHub/monorepo
uvx synth-ai train --type sft --config configs/vision_sft/crafter_qwen3vl_8b_gpt5nano.toml
```

### Option 3: Quick Demo
```bash
# Test gpt-5-nano (5 episodes, 10 steps each)
export OPENAI_API_KEY="sk-..."
uv run python examples/qwen_vl/crafter_gpt5nano_agent.py --seeds 5 --steps 10
```

---

## 📖 Documentation Index

| File | Purpose |
|------|---------|
| **`collect_data_via_cli.md`** ⭐ | **Main guide**: Complete CLI-based pipeline |
| `README.md` | Overview and quick reference |
| `QUICKSTART.md` | Manual Python script approach |
| `SETUP_COMPLETE.md` | This summary (you are here) |

**Start here:** 👉 `collect_data_via_cli.md`

---

## 🎯 What Each Tool Does

### **synth-ai eval** (Data Collection)
- Runs rollouts with vision-enabled models
- Automatically detects vision capability from model name
- Stores traces to SQLite with base64-encoded images
- Supports parallel episodes for faster collection

**Config:** `eval_gpt5nano_vision.toml`, `eval_qwen3vl_vision.toml`, etc.

### **synth-ai filter** (Quality Filtering)
- Removes low-quality episodes (too short, errors, loops)
- Deduplicates state-action pairs
- Exports to SFT JSONL format (OpenAI-style messages)
- Splits into train/val sets

**Config:** `filter_vision_sft.toml`, `filter_qwen3vl_sft.toml`

### **synth-ai train** (Model Training)
- Trains VLM with LoRA on collected traces
- Supports Qwen-VL models (Qwen2-VL, Qwen3-VL)
- Uses 2x or 4x H200 GPUs
- Saves adapters to HF Hub or S3

**Config:** `crafter_vlm_sft_example.toml` (in synth-ai repo)
**Training config:** `monorepo/configs/vision_sft/crafter_qwen3vl_8b_gpt5nano.toml`

---

## 🔍 Key Features

### **Automatic Vision Detection**
CrafterPolicy auto-detects vision from model names:
```python
# These automatically enable vision:
"gpt-5-nano"           # ✅
"gpt-4o-mini"          # ✅
"Qwen2-VL-7B-Instruct" # ✅
"Qwen3-VL-8B"          # ✅
```

### **Multimodal Messages**
User messages include both text and images:
```json
{
  "role": "user",
  "content": [
    {"type": "text", "text": "Observation: Health: 9/9, Hunger: 9/9..."},
    {"type": "image_url", "image_url": {"url": "data:image/png;base64,iVBORw0KGgo..."}}
  ]
}
```

### **64x64 PNG Images**
Crafter renders 64x64 frames as base64-encoded PNGs:
- Efficient token usage (~85 tokens per image)
- High enough resolution for gameplay
- Standard OpenAI vision format

---

## 💰 Cost & Timeline

### Complete Pipeline (gpt-5-nano → SFT → RL)

| Step | Duration | Cost | Hardware |
|------|----------|------|----------|
| Data collection (100 episodes) | 30-60 min | ~$1-2 | OpenAI API |
| Filter & export | < 5 min | Free | Local |
| SFT training (2 epochs) | 2-4 hrs | ~$21 | 2x H200 |
| RL fine-tuning (20 iterations) | 6-10 hrs | ~$112 | 4x H200 |
| Evaluation (100 episodes × 4 models) | 2-3 hrs | ~$5 | 1x H200 |

**Total:** ~$140, 12-18 hours

---

## 🎉 Next Steps

1. **Run a quick demo** to verify vision inference works:
   ```bash
   uv run python examples/qwen_vl/crafter_gpt5nano_agent.py --seeds 3 --steps 5
   ```

2. **Collect training data** (100 episodes):
   ```bash
   uvx synth-ai eval --config examples/qwen_vl/configs/eval_gpt5nano_vision.toml
   ```

3. **Filter and export** to SFT format:
   ```bash
   uvx synth-ai filter --config examples/qwen_vl/configs/filter_vision_sft.toml
   ```

4. **Train VLM** with LoRA:
   ```bash
   cd /Users/joshpurtell/Documents/GitHub/monorepo
   uvx synth-ai train --type sft --config configs/vision_sft/crafter_qwen3vl_8b_gpt5nano.toml
   ```

5. **Fine-tune with RL** (optional):
   ```bash
   uvx synth-ai train --type rl --config configs/vision_rl/crafter_qwen3vl_8b_grpo.toml
   ```

6. **Benchmark** final model vs baselines

---

## 🔧 Customization

### Use a Different Teacher Model
Edit `configs/eval_gpt5nano_vision.toml`:
```toml
[eval]
model = "gpt-4o-mini-2024-07-18"  # Stronger teacher
```

### Collect More Episodes
```toml
[eval]
seeds = "0-499"  # Default: "0-99"
```

### Change Image Resolution
```toml
[eval.env_config]
env_params = {render_size = [128, 128]}  # Default: [64, 64]
```

### Adjust Quality Filters
Edit `configs/filter_vision_sft.toml`:
```toml
[filter]
min_steps_per_episode = 10  # Stricter (default: 5)
min_achievements_per_episode = 2  # Require achievements (default: 0)
```

---

## 📊 Expected Results

### Data Collection Quality
- **gpt-5-nano:** ~20-30% achievement rate
- **gpt-4o-mini:** ~35-45% achievement rate (better teacher)
- **Qwen2-VL-7B (base):** ~5-10% achievement rate

### SFT Performance (After Training)
- **Base Qwen-VL:** ~5-10% → **SFT:** ~20-30%
- **Improvement:** +15-20% absolute gain from distillation

### RL Performance (After 20 Iterations)
- **SFT:** ~20-30% → **SFT+RL:** ~40-50%
- **Improvement:** +20% absolute gain from RL fine-tuning

---

## 🐛 Troubleshooting

### Vision not detected
```bash
# Add explicitly in eval config:
use_vision = true
```

### API key errors
```bash
# OpenAI
export OPENAI_API_KEY="sk-..."

# synth-ai
export SYNTH_API_KEY="sk_live_..."
```

### Task app connection failed
```bash
# Check task app is running
curl https://synth-laboratories--grpo-crafter-task-app.modal.run/health
```

### Filter removes all samples
```bash
# Lower quality thresholds in filter config
min_steps_per_episode = 3
min_achievements_per_episode = 0
```

---

## 📚 Related Resources

- **Main plan:** `/Users/joshpurtell/Documents/GitHub/monorepo/vision_sft_rl.txt` (Phase 9)
- **Crafter environment:** `examples/task_apps/crafter/README.md`
- **OpenAI VLM examples:** `examples/vlm/`
- **synth-ai CLI docs:** Run `uvx synth-ai --help`

---

**Infrastructure ready!** 🎉 Start collecting vision traces and training your VLM! 🚀
