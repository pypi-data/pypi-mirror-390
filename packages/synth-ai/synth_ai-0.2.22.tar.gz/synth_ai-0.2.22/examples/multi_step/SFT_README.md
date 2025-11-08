# SFT Training for Qwen3-Coder-30B with LoRA

Supervised Fine-Tuning configuration for the same 30B MoE model used in RL training.

## Configuration Overview

**Model:** `Qwen/Qwen3-Coder-30B-A3B-Instruct` (Mixture of Experts)

**Hardware:** 4x H200 GPUs (561GB total VRAM)

**Parallelism Strategy:**
- **Tensor Parallel (TP)**: 2 GPUs - Splits the model across 2 GPUs for inference/forward pass
- **Data Parallel (DP)**: 2 GPUs - Splits batches across 2 GPUs for training throughput

**LoRA Configuration:**
- Rank (r): 16
- Alpha: 32
- Dropout: 0.05
- Target modules: `["all-linear"]` - Applies LoRA to all linear layers

## Memory Breakdown per GPU

With 4x H200 (141GB each):

**Model Split (TP=2):**
- 2 GPUs hold the base model (70GB each)
- ~70GB free per GPU for activations and gradients

**Training (DP=2):**
- 2 GPUs process different batches
- LoRA adapters: ~5-10GB per GPU
- Gradients/optimizer states: ~20-30GB per GPU
- **Total per training GPU: ~50-60GB** ✅

## Quick Start

### 1. Prepare Your Dataset

Your dataset should be in JSONL format with conversation turns:

```jsonl
{"messages": [{"role": "system", "content": "..."}, {"role": "user", "content": "..."}, {"role": "assistant", "content": "..."}]}
{"messages": [{"role": "user", "content": "..."}, {"role": "assistant", "content": "..."}]}
```

### 2. Run Training

```bash
# Using the helper script
./examples/multi_step/run_sft_qwen30b.sh path/to/your/dataset.jsonl

# Or directly with synth-ai CLI
uvx synth-ai train \
  --type sft \
  --config examples/multi_step/configs/crafter_sft_qwen30b_lora.toml \
  --dataset path/to/your/dataset.jsonl \
  --env-file backend/.env.dev
```

### 3. Monitor Training

Check the Synth dashboard for:
- Training loss curve
- Validation metrics (if validation set provided)
- GPU utilization
- Training throughput (tokens/sec)

## Hyperparameters

**Batch Configuration:**
- Per-device batch size: 1
- Gradient accumulation: 64 steps
- **Effective global batch size: 128** (1 × 64 × 2 GPUs)

**Learning Rate:**
- Initial LR: 5e-6
- Warmup ratio: 3%
- Schedule: Linear decay

**Sequence Length:** 4096 tokens

**Training:**
- Epochs: 1
- Mixed precision: BF16
- DeepSpeed: Stage 2 (optimizer state sharding)
- Activation checkpointing: Enabled

## Configuration File Structure

```toml
[algorithm]
type = "offline"        # Supervised (not RL)
method = "sft"          # Supervised fine-tuning
variety = "lora"        # Using LoRA adapters

[compute]
gpu_type = "H200"
gpu_count = 4

[data.topology]
tensor_parallel = 2     # Split model across 2 GPUs
data_parallel = 2       # Split batches across 2 GPUs

[training]
mode = "lora"
use_qlora = true        # Quantized LoRA (4-bit base model)

[lora]
r = 16                  # LoRA rank
alpha = 32              # LoRA scaling
dropout = 0.05
target_modules = ["all-linear"]  # Apply to all linear layers
```

## Comparison with RL Config

| Aspect | SFT | RL |
|--------|-----|-----|
| Purpose | Supervised learning | Reinforcement learning |
| Data | Labeled examples | Environment interactions |
| Topology | TP=2, DP=2 | Split: 2 inference + 2 training |
| Batch size | 128 (effective) | Variable (episode-based) |
| Training | Standard backprop | Policy gradient (GSPO) |

## Tips

1. **Start Small:** Test with a small dataset first to verify the pipeline
2. **Validation:** Add a validation set to monitor overfitting
3. **Checkpointing:** Training saves checkpoints every 100 steps
4. **Resume:** Can resume from checkpoint if training is interrupted
5. **Inference:** After training, use the LoRA adapter with the base model

## Output

After training completes, you'll get:
- LoRA adapter weights (saved to volume)
- Training metrics and logs
- Best checkpoint (based on validation loss)
- Model ready for inference or RL initialization

## Next Steps

1. **Evaluate:** Test your fine-tuned model on held-out data
2. **RL Training:** Use this as initialization for RL (`init_from_sft = true`)
3. **Deploy:** Load LoRA adapter for inference
4. **Iterate:** Adjust hyperparameters based on performance

