# ✅ Inference Success Report

**Date**: Oct 31, 2025  
**Models Tested**: Latest SFT and RL models from training  

## Working Solution

### Correct Endpoint
```
https://synth-laboratories-dev--learning-v2-service-fastapi-app.modal.run/chat/completions
```

### SFT/PEFT Models: ✅ WORKING

**Model ID**: `peft:Qwen/Qwen3-0.6B:job_24faa0fdfdf648b9`

**Test Code**:
```python
import httpx
import os

SYNTH_API_KEY = os.getenv("SYNTH_API_KEY")
url = "https://synth-laboratories-dev--learning-v2-service-fastapi-app.modal.run/chat/completions"

headers = {
    "Authorization": f"Bearer {SYNTH_API_KEY}",
    "Content-Type": "application/json",
}

payload = {
    "model": "peft:Qwen/Qwen3-0.6B:job_24faa0fdfdf648b9",
    "messages": [
        {"role": "system", "content": "You are a helpful assistant."},
        {"role": "user", "content": "Say 'Hello, I am working!' and nothing else."}
    ],
    "temperature": 0.2,
    "max_tokens": 100,
}

with httpx.Client(timeout=300.0) as client:
    response = client.post(url, json=payload, headers=headers)
    print(response.json())
```

**Result**:
- ✅ Status: 200 OK
- ✅ Response generated successfully
- ✅ Token usage tracked: 31 prompt + 72 completion = 103 total
- ✅ Output: "Hello, I am working!" (with thinking tokens as expected)

### RL Models: ⚠️ NEEDS PROMOTION

**Model ID**: `rl:Qwen/Qwen3-4B:job_19a38041c38f96e638c:checkpoint-epoch-1`

**Status**: 303 Redirect (empty response)

**Root Cause**: 
From monorepo backend code inspection, RL checkpoints require a "promotion" step to be loaded onto Modal before they can be used for inference. The direct Modal endpoint returns a redirect for unpromoted RL models.

**Solution Options**:

#### Option 1: Use Backend Proxy (Recommended)
The backend automatically handles RL promotion:
```python
# Use backend proxy instead of direct Modal
url = "https://your-backend.example.com/api/chat/completions"
# Backend will auto-promote and route to vLLM
```

#### Option 2: Manual Promotion (Advanced)
1. Call promotion endpoint first
2. Wait for model to load onto Modal
3. Then call inference endpoint

## Key Learnings

### What We Got Wrong Initially:
1. ❌ Wrong endpoint path: Used `/v1/chat/completions` → should be `/chat/completions`
2. ❌ Wrong base URL: Used render.com URL → should be Modal URL
3. ❌ Assumed RL = PEFT workflow → RL needs promotion step

### What We Got Right:
1. ✅ Model ID format from `synth-ai status models list`
2. ✅ Using SYNTH_API_KEY for auth
3. ✅ Bearer token authorization header

## Recommendations for Library Improvement

### 1. Add Simple CLI Command
```bash
synth-ai inference \
  --model "peft:Qwen/Qwen3-0.6B:job_xxx" \
  --message "Hello" \
  --max-tokens 100
```

### 2. Document Endpoint in Model Status
```bash
$ synth-ai status models get "peft:..."
Model: peft:Qwen/Qwen3-0.6B:job_xxx
Status: succeeded
Inference Endpoint: https://synth-laboratories-dev--learning-v2-service-fastapi-app.modal.run/chat/completions
Ready: ✅ Yes (use directly)
```

### 3. Add Python SDK Example
```python
from synth_ai import InferenceClient

client = InferenceClient(api_key=os.getenv("SYNTH_API_KEY"))
response = client.chat.completions.create(
    model="peft:Qwen/Qwen3-0.6B:job_xxx",
    messages=[{"role": "user", "content": "Hello"}]
)
print(response.choices[0].message.content)
```

### 4. Clear Error Messages
- 303 → "RL model needs promotion. Use backend proxy or call /promote endpoint first."
- 404 → "Model not found. Check model ID with: synth-ai status models list"

## Success Criteria Met

- ✅ Can get model ID from CLI
- ✅ Know correct endpoint
- ✅ Know correct auth (SYNTH_API_KEY)
- ✅ Can send test message
- ✅ Get response back
- ⚠️ RL models need extra step (documented)

**Status**: PEFT/SFT inference is fully working! RL needs backend proxy.

