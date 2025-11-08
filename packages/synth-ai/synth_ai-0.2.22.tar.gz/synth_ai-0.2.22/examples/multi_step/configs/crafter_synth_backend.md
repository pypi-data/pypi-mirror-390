# Crafter Eval Using Synth Backend with Qwen 4B

## What Changed

Created `crafter_eval_synth_qwen4b.toml` to evaluate Crafter using Qwen3-4B via the Synth backend inference proxy.

## Key Difference from Groq Config

**Before (Groq):**
```toml
[eval.policy_config]
provider = "groq"
model = "qwen/qwen3-32b"
inference_url = "https://api.groq.com/openai/v1/chat/completions"
```

**After (Synth Backend):**
```toml
[eval.policy_config]
provider = "openai"
model = "Qwen/Qwen3-4B"
inference_url = "https://synth-backend-dev-docker.onrender.com/api/v1/chat/completions"
```

## Usage

```bash
uvx synth-ai eval --config examples/multi_step/configs/crafter_eval_synth_qwen4b.toml
```

## Why This Works

The Synth backend's `/api/v1/chat/completions` endpoint:
1. Accepts OpenAI-compatible requests
2. Routes to Modal vLLM service
3. Loads the base model (Qwen/Qwen3-4B from HuggingFace)
4. Returns OpenAI-compatible responses

No code changes needed - the infrastructure already exists.

