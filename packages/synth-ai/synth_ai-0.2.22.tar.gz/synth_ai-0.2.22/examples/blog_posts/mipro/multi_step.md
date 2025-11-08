# Banking77 Multi-Step Pipeline (Classifier ➞ Calibrator)

This note explains how to spin up the new two-stage Banking77 task app and baseline. The pipeline mirrors the multi-module design from `monorepo/multi_step.md`: a classifier proposes an intent, then a calibrator confirms or adjusts it before reporting the final label.

## 1. Prerequisites

- Repo checked out and editable: `/Users/joshpurtell/Documents/GitHub/synth-ai`
- Python dependencies installed (`uv pip install -e .` or equivalent)
- Environment variables exported:
  - `SYNTH_API_KEY`
  - `ENVIRONMENT_API_KEY` (shared with task app)
  - `GROQ_API_KEY` (policy model; optional if using OpenAI)
  - `OPENAI_API_KEY` (meta-model for MIPRO proposals)

## 2. Task App: `banking77-pipeline`

The task app lives in `examples/task_apps/banking77_pipeline/`. It reuses the single-step dataset loader and router, but evaluates a two-step sequence inside `rollout_executor`.

### Local launch (uvicorn)

```bash
cd /Users/joshpurtell/Documents/GitHub/synth-ai
uvx synth-ai deploy banking77-pipeline --runtime uvicorn --port 8112 \
  --env-file .env --follow
```

- Health check: `curl -H "X-API-Key: $ENVIRONMENT_API_KEY" http://127.0.0.1:8112/health`
- All inference calls must flow through the prompt-learning interceptor; both classifier and calibrator enforce `tool_choice="required"` on `banking77_classify`.

### Modal deploy (optional)

```bash
uvx synth-ai deploy banking77-pipeline --runtime modal --name banking77-pipeline-dev \
  --env-file .env --follow
```

## 3. Baseline Runner

`examples/baseline/banking77_pipeline_baseline.py` mirrors the online pipeline so you can measure performance without hosting the task app.

Example invocation:

```bash
cd /Users/joshpurtell/Documents/GitHub/synth-ai
uvx synth-ai baseline run banking77_pipeline --split train --seeds 0,1,2 --verbose
```

Outputs include per-module tool calls, the final intent, and accuracy. Set `--output baseline_results.json` to store artifacts.

## 4. Prompt-Learning Configs (MIPROv2)

- Task app id: `prompt_learning.task_app_id = "banking77-pipeline"`
- Default URL points to Modal dev (`https://synth-laboratories-dev--synth-banking77-pipeline-web.modal.run`). Override by setting `TASK_APP_URL` if you run locally.
- New configs live in `examples/blog_posts/mipro/configs/`:
  - `banking77_pipeline_mipro_local.toml` – main config for local backend runs
  - `banking77_pipeline_mipro_test.toml` – reduced-iteration variant for CI smoke tests
- Each config includes:
  - `prompt_learning.initial_prompt.metadata.pipeline_modules` with classifier/calibrator instruction text and few-shot placeholders
  - Tuned iteration counts (5×2 for local, 2×2 for smoke) to keep latency manageable since every trial runs two modules
  - Updated seed pools (`bootstrap_train`, `online_pool`, `test_pool`) sized for pipeline evaluation

### Running the Multi-Step Optimiser

1. Start the task app (port 8112)  
   `./examples/blog_posts/mipro/deploy_banking77_pipeline_task_app.sh`
2. Kick off optimisation  
   `TASK_APP_URL=https://synth-laboratories-dev--synth-banking77-pipeline-web.modal.run \
   ./examples/blog_posts/mipro/run_mipro_banking77_pipeline.sh`

The run script performs environment checks, verifies the pipeline health endpoint, and forwards the new config to the backend.

## 5. Checklist

- [x] Task app registered via `ModalDeploymentConfig` under `app_id="banking77-pipeline"`
- [x] Baseline present (`banking77_pipeline_baseline.py`)
- [x] Prompt-learning configs + helper scripts landed (`banking77_pipeline_mipro_*.toml`, run/deploy scripts)
- [ ] Multi-step CLI reporting + tests (pending once backend wiring lands)

Use this guide to verify the service locally before integration with the prompt-learning job runner.
