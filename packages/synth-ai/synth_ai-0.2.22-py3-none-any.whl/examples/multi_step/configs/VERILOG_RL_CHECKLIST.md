# Verilog Task App - RL Training Readiness Checklist

## ✅ Core Requirements

### 1. Reward Normalization
- ✅ **Max reward = 1.0**: All rewards scaled to `[0, 1]` range
- ✅ **Step penalty**: `-0.001` (normalized from `-0.01`)
- ✅ **Compile success**: `+0.01` (normalized from `+0.1`)
- ✅ **Simulate pass**: `+0.1` (normalized from `+1.0`)
- ✅ **Submit success**: `+1.0` (normalized from `+10.0`)

### 2. Inference URL Handling (Critical for Trace Correlation)
- ✅ **Extracts from policy config**: Uses `policy_config.get("inference_url")` as primary source
- ✅ **Includes in trajectory**: Sets `trajectory.inference_url` with `?cid=...` parameter
- ✅ **Includes in final.info**: Adds to `final["info"]["inference_url"]`
- ✅ **Includes in pipeline_metadata**: Top-level `inference_url` field for trainer extraction
- ✅ **Logs cid presence**: Logs `has_cid` flag for debugging
- ✅ **Fallback to agent.inference_url**: Uses agent's URL if policy config missing (eval mode)

**Location**: `grpo_verilog.py` lines 829-867, 887-908

### 3. Pipeline Metadata
- ✅ **Required fields present**:
  - `reward_score`: Final episode reward
  - `policy_id`: Policy identifier
  - `inference_url`: **CRITICAL** - Contains `?cid=trace_xxxxx` for correlation
  - `env_name`: Environment identifier
  - `task_id`: Problem identifier
  - `task_split`: Dataset split (train/val/test)
- ✅ **Inference details**: Provider, model, URL in nested `inference` dict

**Location**: `grpo_verilog.py` lines 887-908

### 4. Trace Correlation (Required for RL Training)
- ✅ **Trainer injects cid**: Trainer adds `?cid=trace_xxxxx` to `policy_config["inference_url"]`
- ✅ **Task app preserves cid**: Uses `policy_config["inference_url"]` directly
- ✅ **Trainer extracts cid**: Extracts from `trajectory.inference_url` using `inference_url_to_trace_correlation_id()`
- ✅ **Trace hydration**: Trainer queries trace store with extracted `trace_correlation_id`

**Flow**:
```
Trainer → policy_config["inference_url"] = "http://...?cid=trace_xxxxx"
         ↓
Task App → trajectory.inference_url = policy_config["inference_url"]
         ↓
Trainer → extract_trace_correlation_id(trajectory.inference_url)
         ↓
Trainer → trace_store.resolve_correlation(trace_correlation_id)
         ↓
Trainer → Hydrate v3 trace with event_history
         ↓
Judge   → Score using full trace
```

### 5. Response Contract Compliance
- ✅ **RolloutResponse fields**:
  - `run_id`: Unique identifier
  - `trajectories`: List of trajectories (with `inference_url`)
  - `metrics`: Episode metrics
  - `pipeline_metadata`: **CRITICAL** - Contains `inference_url` and `reward_score`
  - `trace_correlation_id`: Optional (trainer infers from `inference_url`)
- ✅ **Optional trace_correlation_id**: Made optional in `contracts.py` (trainer infers from URL)

**Location**: `synth_ai/task/contracts.py` line 156

### 6. Environment Implementation
- ✅ **Stateful engine**: `VerilogEngine` extends `StatefulEngine`
- ✅ **Reward stack**: Properly configured with normalized components
- ✅ **State management**: `VerilogPublicState` and `VerilogPrivateState`
- ✅ **Tool implementation**: All 4 tools (write_file, compile, simulate, submit)

**Location**: `synth_ai/environments/examples/verilog/engine.py`

### 7. LLM Agent Integration
- ✅ **Multi-turn support**: Agent maintains conversation history
- ✅ **Tool parsing**: Extracts tool calls from LLM responses
- ✅ **Guidance system**: Provides context-aware hints
- ✅ **Error handling**: Graceful fallback for malformed responses

**Location**: `grpo_verilog.py` lines 200-530

## 🔍 Verification Tests

### Test 1: Eval Mode (No Trace Correlation)
```bash
uvx synth-ai eval --config examples/multi_step/configs/verilog_eval_groq_qwen32b.toml
```
**Expected**:
- ✅ `mean_return` ≈ 0.1 (normalized rewards)
- ✅ `inference_url` = Groq API URL (no `?cid=...`)
- ✅ `task_completed` = True for correct solutions

### Test 2: RL Training Mode (With Trace Correlation)
```bash
uvx synth-ai train \
  --type rl \
  --config examples/multi_step/configs/verilog_rl_lora.toml \
  --task-url https://synth-laboratories--grpo-verilog-task-app-fastapi-app-dev.modal.run \
  --backend https://synth-backend-dev-docker.onrender.com/api \
  --env-file /path/to/verilog/.env
```
**Expected**:
- ✅ Trainer logs show `inference_url` with `?cid=trace_xxxxx`
- ✅ Task app logs show `has_cid=True`
- ✅ Trace hydration succeeds (no `404 Not Found` errors)
- ✅ Judge receives full `event_history`
- ✅ Training updates show non-zero rewards

### Test 3: Trace Correlation ID Extraction
```python
from synth_envs_hosted.utils import inference_url_to_trace_correlation_id

# Should extract trace_xxxxx from URL
url = "http://localhost:8000/v1/chat/completions?cid=trace_abc123"
cid = inference_url_to_trace_correlation_id(url)
assert cid == "trace_abc123"
```

### Test 4: Pipeline Metadata Structure
```python
# Verify response has correct structure for RL
response = await task_app.rollout(request)
assert "pipeline_metadata" in response
assert "inference_url" in response.pipeline_metadata
assert "reward_score" in response.pipeline_metadata
assert len(response.trajectories) > 0
assert response.trajectories[0].inference_url is not None
```

## 📋 Deployment Checklist

### Modal Deployment
1. ✅ **Environment variables set**:
   - `GROQ_API_KEY`
   - `VERILOG_INFERENCE_URL` (optional, uses Groq default)
2. ✅ **Secrets configured**: Groq API key in Modal secrets
3. ✅ **Task app URL**: Update in `verilog_rl_lora.toml`

### Training Configuration
1. ✅ **2x GPUs minimum**: 1 for vLLM, 1 for training
2. ✅ **Model size**: `Qwen/Qwen3-0.6B` for testing
3. ✅ **Batch size**: 4 (matches Crafter)
4. ✅ **Max turns**: 15 (enough for compile chains)
5. ✅ **Rubric enabled**: `rubric.enabled = true`

## 🚨 Common Issues & Fixes

### Issue 1: `trace_correlation_id` Missing
**Symptom**: Trainer logs `FATAL: Rollout payload missing 'trace_correlation_id'`
**Fix**: Verify `trajectory.inference_url` contains `?cid=...` parameter

### Issue 2: Trace Hydration Fails (404)
**Symptom**: `404 Not Found` when querying `/trace/by-correlation/...`
**Fix**: 
- Check inference server is capturing traces
- Verify `cid` parameter is in inference URL
- Ensure `vllm_public_url` is set correctly

### Issue 3: Rewards Not Normalized
**Symptom**: `mean_return` > 1.0 in eval
**Fix**: Verify all reward components in `engine.py` are scaled by 10x

### Issue 4: Agent Gets Stuck
**Symptom**: Agent repeats same action (e.g., compile without fixing)
**Fix**: Check guidance system is providing proper hints

## 🎯 Final Verification

Before starting RL training, verify:
- [ ] Eval runs successfully with normalized rewards (≈ 0.1)
- [ ] Modal deployment returns proper `inference_url` structure
- [ ] Trace correlation ID extraction works
- [ ] Pipeline metadata includes all required fields
- [ ] Response contract matches expected schema

**If all checks pass**: ✅ **Ready for RL training!**

## 📚 Related Documentation
- [VERILOG_REWARDS.md](./VERILOG_REWARDS.md) - Reward structure details
- [verilog_rl_lora.md](../verilog_rl_lora.md) - RL/LoRA feasibility analysis
- [verilog_rl_lora.toml](./verilog_rl_lora.toml) - Training configuration








