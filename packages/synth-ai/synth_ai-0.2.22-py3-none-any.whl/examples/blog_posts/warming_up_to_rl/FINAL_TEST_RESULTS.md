# Final Inference Test Results

**Date**: Oct 31, 2025  
**Endpoint**: `https://synth-laboratories-dev--learning-v2-service-fastapi-app.modal.run/chat/completions`

## Summary

| Model Type | Status | Result |
|------------|--------|--------|
| Base Model (Qwen/Qwen3-4B) | ✅ WORKS | Inference successful |
| PEFT/SFT (Qwen3-0.6B) | ✅ WORKS | Inference successful |
| RL (Qwen3-4B) | ❌ **BROKEN** | Modal function crashes |

## Detailed Results

### ✅ Test 1: Base Model (No Fine-Tuning)

**Model**: `Qwen/Qwen3-4B`

**Result**: **SUCCESS** ✅
- **Status**: 200 OK
- **Tokens**: 31 prompt + 100 completion = 131 total
- **Response**: Generated successfully

**Notes**:
- First attempt returned 303 redirect (cold start)
- Retry succeeded immediately
- This confirms the endpoint and auth work correctly

---

### ✅ Test 2: PEFT/SFT Model

**Model**: `peft:Qwen/Qwen3-0.6B:job_24faa0fdfdf648b9`

**Result**: **SUCCESS** ✅
- **Status**: 200 OK (consistent across retries)
- **Tokens**: 31 prompt + 100 completion = 131 total  
- **Response**: "Hello, I am working!" (with thinking tokens)

**Notes**:
- Works reliably
- No cold start issues
- This is the expected behavior for all models

---

### ❌ Test 3: RL Model

**Model**: `rl:Qwen/Qwen3-4B:job_19a38041c38f96e638c:checkpoint-epoch-1`

**Result**: **FAILURE** ❌ - Multiple error modes

#### First Attempt:
```
Status: 400 Bad Request
Error: "Device string must not be empty"
```

#### Retry:
```
Status: 500 Internal Server Error
Error: "modal-http: internal error: function was terminated by signal"
```

**This is a Modal function crash** - the inference function terminated unexpectedly.

#### Cold Start (from Modal logs):
```
RuntimeError: Cannot find any model weights with 
'/models/rl/Qwen/Qwen3-4B/job_19a38041c38f96e638c/checkpoint-fixed'
```

**Root Cause**: RL checkpoint contains LoRA adapter files (`adapter_config.json`, `adapter_model.safetensors`), but vLLM expects full merged model weights.

---

## Conclusion

### What Works ✅
- **Base models**: Standard HuggingFace models load and inference correctly
- **PEFT/SFT models**: Fine-tuned models with merged weights work perfectly

### What's Broken ❌
- **RL models**: Crash during model loading because:
  1. RL checkpoints are stored as LoRA adapters
  2. vLLM weight loader expects full model weights
  3. Missing merge step causes vLLM to crash
  4. Modal function terminates with signal (crash)

### Impact
- **HIGH SEVERITY**: All RL-trained models cannot be used for inference
- Users can train RL models but cannot deploy them
- This blocks the core RL training → inference workflow

### Next Steps
See `monorepo/RL_INFERENCE_BUG.md` for:
- Detailed root cause analysis
- Reproduction script
- Suggested fix (merge LoRA adapters before vLLM loading)
- Code locations to modify

---

## Developer Experience Issues Identified

### Issue #1: Confusing Error Messages
- **400 "Device string must not be empty"** - Not helpful, doesn't indicate RL adapter issue
- **500 "function was terminated by signal"** - Generic crash, no context
- **Should be**: "RL checkpoint contains adapter files. Merge required for vLLM loading."

### Issue #2: Inconsistent Behavior
- Sometimes returns 303 redirect
- Sometimes returns 400
- Sometimes crashes with 500
- **Should be**: Consistent error message explaining the issue

### Issue #3: Not Obvious How to Test Models
- Had to try 3 different endpoint URLs before finding the right one
- No documentation on model ID formats
- **Should be**: `synth-ai inference --model "rl:..." --message "test"` CLI command

---

**Status**: Bug documented and reproduction available.  
**See**: `monorepo/RL_INFERENCE_BUG.md` for full details.

