# Verilog RL with LoRA (Qwen3-0.6B)

## Quick Start

1. **Deploy Verilog Task App**:
```bash
cd synth-ai
uvx synth-ai modal-serve grpo-verilog
```
Note the Modal URL and update `task_url` in `verilog_rl_lora.toml`.

2. **Run Training**:
```bash
uvx synth-ai rl run --config examples/multi_step/configs/verilog_rl_lora.toml
```

## Configuration Overview

### **Key Adaptations from Crafter**:

- **Model**: `Qwen/Qwen3-0.6B` (✅ proven in SFT configs)
- **Environment**: `verilog` instead of `crafter`
- **Steps**: 15 turns (vs Crafter's 10) for compilation workflows
- **Rewards**: Adjusted for sparser Verilog rewards (0.5 vs 1.0 indicator_lambda)
- **Rubrics**: Verilog-specific judging criteria

### **Hardware Requirements** (Standard RL setup):
- ✅ **2x H100 GPUs** (vLLM inference + LoRA training split)
- ✅ **No tensor parallelism** needed for 0.6B model
- ✅ **4x faster inference** than 32B model
- ✅ **Same compute pattern** as Crafter (just smaller model)

### **Expected Workflow**:
1. Agent writes Verilog code (`write_file`)
2. Compiles to check syntax (`compile`)
3. Simulates to verify behavior (`simulate`)
4. Submits if tests pass (`submit`)
5. **Rewards**: +1.0 for compilation success, +10.0 for passing tests

## Rubric Design

### **Event Rewards** (per decision):
- **Compilation Success**: 70% weight (1.0 for success, 0.0 for errors)
- **Process Efficiency**: 30% weight (penalizes redundant operations)

### **Outcome Rewards** (final score):
- **Tests Passed**: 80% weight (full credit when all tests pass)
- **Design Quality**: 20% weight (code clarity, documentation)

## Troubleshooting

### **If training fails**:
1. Check Modal URL in `task_url` field
2. Verify `GROQ_API_KEY` for inference
3. Ensure `OPENAI_API_KEY` for judging

### **Memory issues** (unlikely with 0.6B):
- Reduce `batch_size` to 2
- Set `gradient_accumulation_steps = 2`
- Verify 2x GPU split is working (vLLM on GPU 0, training on GPU 1)

### **Slow training**:
- Increase `episodes_per_batch` to 6-8
- Check network latency to Modal task app

## Expected Results

- **Convergence**: Should learn basic compilation workflow in 1-2 hours
- **Success Rate**: 20-40% initial test pass rate (improves with training)
- **Learning**: Agent learns to debug compilation errors and write correct Verilog

## Next Steps

1. **Monitor reward progression** in training logs
2. **Adjust rubrics** if agent struggles with compilation errors
3. **Scale to 8B model** once 0.6B baseline works
4. **Add domain-specific fine-tuning** for Verilog syntax
