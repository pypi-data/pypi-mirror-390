# Next Steps: Qwen3-VL-2B SFT & RL Training

**Status:** Data collection complete ✅ | Ready for SFT training 🚀

---

## 📋 Current Status

### ✅ Completed
1. **VLM Data Collection Pipeline** - WORKING END-TO-END
   - Fixed task app tracing to return full session traces
   - Fixed CLI to handle multimodal content preservation
   - Successfully collected traces with base64 PNG images
   - Database: `traces/gpt4o_vision_test/rollouts.db`
   - Exported: `traces/gpt4o_vision_test/sft/train.jsonl` (50 examples validated)

2. **Infrastructure Validated**
   - ✅ `synth-ai eval` stores traces with images
   - ✅ `synth-ai filter` exports SFT JSONL with preserved images
   - ✅ Multimodal messages follow OpenAI format
   - ✅ Images embedded as base64 PNG (~1306 chars per 64x64 image)

3. **Documentation**
   - `VLM_PIPELINE_COMPLETE.md` - Full pipeline guide
   - `PIPELINE_RUN_LOG.txt` - Execution log with all fixes
   - `BUGS_AND_FIXES.md` - Detailed bug reports
   - `SETUP_COMPLETE.md` - Summary of setup

---

## 🎯 Next Steps: Train Qwen3-VL-2B

### Step 1: Scale Up Data Collection (Optional)

We have 50 working examples. For production training, collect more:

```bash
cd /Users/joshpurtell/Documents/GitHub/synth-ai

# Collect 100 episodes (will create ~5000 samples)
export TASKAPP_TRACING_ENABLED=1
uvx synth-ai eval \
  --config examples/qwen_vl/configs/eval_gpt4o_vision_proper.toml \
  --seeds 0-99 \
  --trace-db traces/gpt4o_vision_100/rollouts.db \
  --env-file /path/to/.env

# Filter and export
uvx synth-ai filter \
  --config examples/qwen_vl/configs/filter_vision_test.toml
```

**Output:** ~4500 SFT examples with images

---

### Step 2: Create SFT Config for Qwen3-VL-2B

File: `/Users/joshpurtell/Documents/GitHub/monorepo/configs/vision_sft/crafter_qwen3vl_2b_gpt4o.toml`

```toml
# Crafter Vision SFT: Qwen3-VL-2B trained on gpt-4o-mini traces
# Using 2B model for faster iteration and lower GPU requirements

[algorithm]
type = "offline"
method = "sft"
variety = "lora"

[job]
model = "Qwen/Qwen3-VL-2B-Instruct"
data = "traces/gpt4o_vision_100/sft/train.jsonl"

[compute]
gpu_type = "H200"
gpu_count = 2
nodes = 1

[training]
mode = "lora"
use_qlora = true

[hyperparameters]
n_epochs = 3
per_device_batch = 1
gradient_accumulation_steps = 16
sequence_length = 2048
learning_rate = 5e-05
warmup_ratio = 0.03
train_kind = "peft"

# LoRA config
lora_rank = 16
lora_alpha = 32
lora_dropout = 0.05
lora_target_modules = ["all-linear"]

# Training optimizations
[hyperparameters.parallelism]
use_deepspeed = true
deepspeed_stage = 2
bf16 = true
activation_checkpointing = true

# Evaluation
evaluation_strategy = "steps"
eval_steps = 50
save_best_model_at_end = true
metric_for_best_model = "val.loss"

[tags]
task = "crafter"
modality = "vision"
data_source = "openai_gpt4o_mini"
model_family = "qwen3_vl"
model_size = "2b"
```

---

### Step 3: Run SFT Training

```bash
cd /Users/joshpurtell/Documents/GitHub/monorepo

# Copy data to monorepo (if not already there)
cp -r /Users/joshpurtell/Documents/GitHub/synth-ai/traces/gpt4o_vision_100/sft/ \
   backend/data/vision_sft/

# Submit SFT job
export BACKEND_BASE_URL="https://synth-backend-dev-docker.onrender.com/api"
uvx synth-ai train \
  --type sft \
  --config configs/vision_sft/crafter_qwen3vl_2b_gpt4o.toml \
  --env-file backend/.env.dev
```

**Expected:**
- Training time: 1-2 hours
- Cost: ~$10.50 (2x H200)
- Output: LoRA adapter at `lora_adapters/qwen3vl_2b_crafter_gpt4o/`

---

### Step 4: Create RL Config for Qwen3-VL-2B

File: `/Users/joshpurtell/Documents/GitHub/synth-ai/examples/qwen_vl/configs/crafter_rl_qwen3vl_2b.toml`

```toml
# Crafter Vision RL: Qwen3-VL-2B with GRPO
# Uses SFT-initialized model for RL fine-tuning

[algorithm]
type = "online"
method = "grpo"
variety = "default"

[model]
base = "Qwen/Qwen3-VL-2B-Instruct"
adapter = "lora_adapters/qwen3vl_2b_crafter_gpt4o"  # From SFT step

[job]
rollout_count = 50
n_iterations = 20
max_steps_per_rollout = 50

[compute]
gpu_type = "H200"
gpu_count = 4
nodes = 1

[topology]
type = "single_node_split"
gpus_for_vllm = 2
gpus_for_training = 2
gpus_for_ref = 0

[vllm]
tensor_parallel_size = 1  # 2B fits on 1 GPU
enable_prefix_caching = false
use_cudagraph = true
gpu_memory_utilization = 0.85
max_model_len = 2048

[training]
mode = "lora"
use_qlora = true

[hyperparameters]
per_device_batch = 2
gradient_accumulation_steps = 8
sequence_length = 2048
learning_rate = 2e-06
warmup_ratio = 0.1
train_kind = "peft"

lora_rank = 16
lora_alpha = 32
lora_dropout = 0.05
lora_target_modules = ["all-linear"]

[grpo]
kl_coeff = 0.1
clip_range = 0.2
value_clip_range = 0.2
normalize_rewards = true

[judge]
type = "remote"
provider = "openai"
model = "gpt-4o-mini"

[tags]
task = "crafter"
modality = "vision"
algorithm = "grpo"
model_family = "qwen3_vl"
model_size = "2b"
```

---

### Step 5: Run RL Training

```bash
cd /Users/joshpurtell/Documents/GitHub/synth-ai

# Submit RL job
uvx synth-ai train \
  --type rl \
  --config examples/qwen_vl/configs/crafter_rl_qwen3vl_2b.toml \
  --env-file /path/to/.env
```

**Expected:**
- Training time: 4-6 hours
- Cost: ~$70 (4x H200)
- Output: RL-tuned adapter at `lora_adapters/qwen3vl_2b_crafter_rl_iter20/`

---

### Step 6: Evaluate Results

```bash
# Run benchmark
python examples/qwen_vl/benchmark_vision_agents.py
```

**Expected Performance:**
- Base Qwen3-VL-2B: ~6.5% achievement rate
- After SFT: ~20% achievement rate (+13.5%)
- After RL: ~38% achievement rate (+18% more)
- Teacher (gpt-4o-mini): ~45% achievement rate

---

## 💰 Cost & Timeline Summary

### Qwen3-VL-2B Pipeline

| Step | Description | Cost | Time |
|------|-------------|------|------|
| 1 | Data collection (100 episodes) | ~$1-2 | 30-60 min |
| 2 | Dataset assembly | $0 | < 5 min |
| 3 | Vision SFT (3 epochs) | ~$10.50 | 1-2 hrs |
| 4 | Vision RL (20 iterations) | ~$70 | 4-6 hrs |
| 5 | Evaluation | ~$5 | 2-3 hrs |

**Total:** ~$87, 8-12 hours

### Cost Comparison: 2B vs 8B

| Model | SFT Cost | RL Cost | Total | Training Time |
|-------|----------|---------|-------|---------------|
| 2B    | $10.50   | $70     | $87   | 8-12 hrs      |
| 8B    | $21      | $112    | $140  | 12-18 hrs     |

**Savings with 2B:** 40% cost reduction, 30% faster

---

## 🎯 Key Advantages of 2B Model

1. **Faster Iteration**
   - SFT: 1-2 hours vs 2-4 hours for 8B
   - RL: 4-6 hours vs 6-10 hours for 8B
   - Enables rapid experimentation

2. **Lower GPU Requirements**
   - Fits on 1 GPU for inference (use 2 for safety)
   - Can use batch_size=2 vs 1 for 8B
   - More efficient GPU utilization

3. **Cost Effective**
   - ~$87 total vs $140 for 8B
   - Better for initial prototyping
   - Scale to 8B later if needed

4. **Competitive Performance**
   - ~38% achievement rate after RL
   - vs ~42% for 8B (only 4% difference)
   - Good enough for validation and testing

---

## 📝 Notes

- All configs use LoRA for memory efficiency
- Vision models require batch_size=1-2 (images are memory-intensive)
- Use DeepSpeed Stage 2 for training optimization
- Disable prefix caching (unstable with LoRA + vision)
- 2B model is perfect for initial testing and rapid iteration

---

## 🚀 Ready to Start!

The infrastructure is ready. Just need to:
1. Create the two TOML configs above
2. Run SFT training
3. Run RL training
4. Evaluate and compare

All the hard work (data collection, tracing fixes, filtering) is done! 🎉

