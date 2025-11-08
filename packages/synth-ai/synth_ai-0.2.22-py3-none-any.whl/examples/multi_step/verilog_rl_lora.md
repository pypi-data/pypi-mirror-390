# Verilog RL with LoRA Analysis

## Executive Summary

**✅ YES, Verilog can absolutely do RL with LoRA just like Crafter!** The architecture is nearly identical, but there are important considerations around model size and task complexity.

## Architecture Compatibility ✅

### **Same Foundation** (No changes needed)
- ✅ **Contracts**: Uses identical `RolloutRequest`/`RolloutResponse` as Crafter
- ✅ **Task App Framework**: Same `synth_ai.task.apps` framework
- ✅ **Environment Pattern**: Same `StatefulEnvironment` + tool-based architecture
- ✅ **Rubrics System**: Same evaluation and reward system
- ✅ **Trace Correlation**: Already implemented in `rollout_executor` (line 817 in `grpo_verilog.py`)
- ✅ **Modal Deployment**: Same deployment pattern as Crafter

### **Key Differences** (Considerations for LoRA)

#### 1. **Model Size: 8x Larger** ⚠️
```toml
# Verilog (current)
model = "qwen/qwen3-32b"  # 32B parameters

# Crafter (working)
model = "Qwen/Qwen3-4B"   # 4B parameters
```
**Impact**: Memory requirements 8x higher for LoRA training
**Solution**: Use gradient checkpointing, smaller batch sizes, or distributed training

#### 2. **Tool Set: Simpler but More Structured**
```python
# Verilog Tools (4 tools)
TOOLS = ["write_file", "compile", "simulate", "submit"]

# Crafter Tools (20+ tools)
# craft, move, attack, gather, etc.
```

**Verilog Advantages**:
- ✅ **Deterministic**: Write → Compile → Simulate → Submit workflow
- ✅ **Clear Success Criteria**: Tests pass = high reward
- ✅ **Sparse but Meaningful Rewards**: +10 for submit success, +1 for simulation pass

**Verilog Challenges**:
- ❌ **Sparser Rewards**: Fewer intermediate signals for learning
- ❌ **Longer Sequences**: Multi-step compilation chains
- ❌ **Error Recovery**: Must debug compilation failures

#### 3. **State Representation**
```python
# Verilog State (file-based)
{
    "files": {"TopModule.v": "module TopModule(..."},
    "compile_status": "Last compile: Success",
    "simulate_status": "Last simulation: Passed",
    "task_completed": false
}

# Crafter State (world-based)
{
    "inventory": {"wood": 5, "stone": 3},
    "position": [x, y],
    "nearby_entities": [...],
    "achievement_unlocked": true
}
```

## Configuration for LoRA RL

### **Option 1: Qwen3-0.6B (Recommended for testing)** ⭐
```toml
[algorithm]
type = "online"
method = "policy_gradient"
variety = "gspo"

[model]
base = "Qwen/Qwen3-0.6B"  # ✅ Same as existing SFT configs
trainer_mode = "lora"

[lora]
r = 16
alpha = 32
dropout = 0.05
target_modules = ["all-linear"]

[rollout]
env_name = "verilog"
max_turns = 15
policy_name = "verilog-designer"

[training]
batch_size = 4  # ✅ Same as Crafter
gradient_accumulation_steps = 1
```

### **Option 2: Qwen3-32B (Production)** ⚠️
```toml
[algorithm]
type = "online"
method = "policy_gradient"
variety = "gspo"

[model]
base = "qwen/qwen3-32b"  # ⚠️ 8x memory vs Crafter's 4B
trainer_mode = "lora"

[lora]
r = 16
alpha = 32
dropout = 0.05
target_modules = ["all-linear"]

[rollout]
env_name = "verilog"
max_turns = 15
policy_name = "verilog-designer"
```

### **Memory Optimization** (for 32B model)
```toml
[vllm]
max_model_len = 4096  # Shorter than Crafter's 8192
tensor_parallel_size = 2  # Distribute across GPUs

[training]
batch_size = 2  # Smaller than Crafter's 4
gradient_accumulation_steps = 4
```

## Task App Changes Needed

### **1. Mode Parameter Support** ✅ (Already implemented)
The Verilog task app already handles `mode="rl"` correctly:
```python
# In grpo_verilog.py rollout_executor
policy_config = dict(policy_config_raw)
# ... mode parameter flows through naturally
```

### **2. Trace Correlation** ✅ (Already implemented)
```python
# Line 817 in grpo_verilog.py
trajectory = RolloutTrajectory(
    # ...
    inference_url=agent.inference_url,  # ✅ Required for trace correlation
    decision_samples=None,
)
```

### **3. Rubric Integration** ✅ (Already configured)
```python
# In grpo_verilog.py
rubrics=RubricBundle(
    outcome=OUTCOME_RUBRIC,  # Tests pass reward
    events=EVENTS_RUBRIC,    # Process efficiency reward
)
```

## RL Training Feasibility

### **✅ Works Great**
1. **Clear Success Signal**: Submit passing tests = +10 reward
2. **Guided Process**: Natural write→compile→simulate→submit progression
3. **Error Learning**: Agent must learn to debug compilation failures
4. **Hardware Design**: Real-world applicable skills

### **⚠️ Challenges**
1. **Model Size**: 32B vs 4B = 8x memory, slower training
2. **Sparse Rewards**: Fewer learning signals than Crafter's dense rewards
3. **Longer Episodes**: 15+ steps vs Crafter's 10 steps
4. **Compilation Errors**: Must learn to interpret and fix syntax errors

## Recommended Approach

### **Phase 1: Start with Qwen3-0.6B** ⭐ (as you requested)
```toml
# Perfect for testing - same model used in existing SFT configs
model = "Qwen/Qwen3-0.6B"
batch_size = 4  # Same as Crafter
```
- ✅ **Zero setup**: Already configured in `synth-ai/examples/sft/configs/crafter_lora_qwen0p6b.toml`
- ✅ **Fast iteration**: 0.6B parameters = quick training cycles
- ✅ **Memory efficient**: Fits on single GPU easily
- ✅ **Proven baseline**: Same model used in RL demos and SFT examples

### **Phase 2: Scale to Qwen3-8B** (if 0.6B works well)
```toml
model = "qwen/qwen3-8b"
batch_size = 2
gradient_accumulation_steps = 2
```

### **Phase 3: Production with Qwen3-32B**
```toml
model = "qwen/qwen3-32b"
tensor_parallel_size = 2
batch_size = 1
gradient_accumulation_steps = 4
```

### **Phase 3: Optimize for Verilog Domain**
Consider fine-tuning the base model on:
- Verilog syntax and semantics
- Hardware design patterns
- Compilation error messages
- Testbench writing

## Conclusion

**✅ Verilog RL with LoRA is absolutely feasible** and should work with the same pipeline as Crafter. The main differences are:

1. **Larger model** (32B vs 4B) requires memory optimization
2. **Sparser rewards** may need different reward shaping
3. **More structured tasks** could actually make learning easier
4. **Real hardware skills** make it more valuable than game tasks

**Recommended next step**: Create a `verilog_rl_lora.toml` config starting with Qwen3-8B and adapt the reward rubrics for the compilation workflow.
