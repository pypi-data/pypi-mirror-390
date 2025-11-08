# Verilog Reward Structure (Normalized to 1.0)

## Overview
All rewards in the Verilog task app are normalized so the maximum possible reward is **1.0**.

## Reward Components

### 1. Step Penalty: **-0.001** per step
- Applied to every action taken
- Encourages efficient solutions
- Normalized from `-0.01` (original)

### 2. Compile Success: **+0.01**
- Awarded when `iverilog` compilation succeeds (returncode 0)
- Validates syntax correctness
- Normalized from `+0.1` (original)

### 3. Simulation Pass: **+0.1**
- Awarded when `vvp` simulation passes all tests
- Validates behavioral correctness
- Normalized from `+1.0` (original)

### 4. Submit Success: **+1.0** (maximum reward)
- Awarded when final submission passes all verification tests
- This is the goal state
- Normalized from `+10.0` (original)

## Typical Reward Trajectories

### ✅ Optimal Path (3 steps)
```
Step 1: write_file        → -0.001
Step 2: compile (success) → +0.01 - 0.001 = +0.009
Step 3: simulate (pass)   → +0.1 - 0.001 = +0.099
Total:                      ~0.107
```

### ✅ Good Path (4 steps with submit)
```
Step 1: write_file        → -0.001
Step 2: compile (success) → +0.009
Step 3: simulate (pass)   → +0.099
Step 4: submit (success)  → +1.0 - 0.001 = +0.999
Total:                      ~1.106
```
*Note: Can exceed 1.0 if intermediate rewards stack with final submit*

### ❌ Failure Path (compilation errors)
```
Step 1: write_file        → -0.001
Step 2: compile (fail)    → -0.001
Step 3: write_file (fix)  → -0.001
Step 4: compile (success) → +0.009
Step 5: simulate (pass)   → +0.099
Total:                      ~0.105
```

## Implementation Details

### Location
- **Reward components**: `synth_ai/environments/examples/verilog/engine.py`
  - `VerilogCompileSuccessComponent`: +0.01
  - `VerilogSimulationPassComponent`: +0.1
  - `VerilogSubmitSuccessComponent`: +1.0
  - `VerilogStepPenaltyComponent`: -0.001

### Normalization Ratio
All rewards were divided by **10.0** to normalize:
- Original max: ~10.0
- Normalized max: ~1.0
- Ratio: 10.0

## Why Normalize?

1. **Consistency**: Makes it easier to compare rewards across different task types
2. **RL Training**: Standard reward scales improve learning stability
3. **Interpretability**: Rewards as percentages (0.0 to 1.0) are intuitive
4. **Judge Compatibility**: Rubric scores typically range 0-1, making blending easier

## Testing
```bash
# Run eval to verify normalized rewards
uvx synth-ai eval --config examples/multi_step/configs/verilog_eval_groq_qwen32b.toml
```

Expected output for successful rollout:
- `mean_return` ≈ 0.1 (if only compile+simulate)
- `mean_return` ≈ 1.0+ (if full submit success)








