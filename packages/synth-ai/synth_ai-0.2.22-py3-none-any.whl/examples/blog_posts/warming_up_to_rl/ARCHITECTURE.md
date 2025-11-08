# Smoke Test Architecture

This document explains how the smoke test works internally, for future maintenance and debugging.

## Component Overview

```
┌─────────────────────────────────────────────────────────────────┐
│                     synth-ai smoke command                       │
│  (synth_ai/cli/commands/smoke/core.py)                         │
└────────────┬────────────────────────────────────────────────────┘
             │
             ├─► Auto-start sqld (optional)
             │   ├─ Kill existing process on ports 8080/8081
             │   ├─ Start: sqld --db-path ... --hrana-listen-addr ... --http-listen-addr ...
             │   └─ Health check: GET http://127.0.0.1:8081/health
             │
             ├─► Auto-start task app (optional)
             │   ├─ Kill existing process on port 8765
             │   ├─ Start: nohup uvx synth-ai task-app serve ... (from synth-ai root)
             │   ├─ Health check: GET http://localhost:8765/health (accepts 200 or 400)
             │   └─ Output: nohup_task_app.out
             │
             ├─► Start mock RL trainer (if use_mock=true)
             │   ├─ MockRLTrainer(port=0, backend="openai")
             │   ├─ Forwards requests to OpenAI API
             │   └─ Logs: [mock-rl] ← request / → response
             │
             └─► Execute rollout
                 ├─ POST /rollout to task app
                 ├─ Capture response with v3 trace
                 └─ Extract and display tool calls

```

## Key Implementation Details

### 1. Tool Call Extraction

**Location:** `synth_ai/cli/commands/smoke/core.py` lines ~946-1005

**How it works:**
1. Request rollout with `return_trace=True` and `trace_format="structured"`
2. Response includes `trace.event_history[]` - list of policy and environment events
3. Policy events have `call_records[]` containing LLM call metadata
4. Each `call_record` has `output_tool_calls[]` with tool call details
5. Extract `name` and `arguments_json` from each tool call
6. Display formatted tool calls to user

**Data structure:**
```python
response.trace = {
    "event_history": [
        {
            "call_records": [  # Present in policy events
                {
                    "output_tool_calls": [
                        {
                            "name": "interact_many",
                            "arguments_json": '{"actions":["move_up","move_up"]}',
                            "call_id": "call_xyz",
                            "index": 0
                        }
                    ],
                    "model_name": "gpt-4o-mini",
                    "provider": "openai",
                    ...
                }
            ],
            "metadata": {...},
            ...
        },
        {
            # Environment step event (no call_records)
            "reward": 1.0,
            "terminated": false,
            ...
        },
        ...
    ],
    "session_id": "...",
    "markov_blanket_message_history": [...],
    ...
}
```

### 2. Background Service Management

**Task App Startup:**
- Must run from synth-ai root for task app discovery
- Uses `nohup` to detach process
- Redirects output to `nohup_task_app.out`
- Polls `/health` endpoint (accepts 200 or 400 status)
- Timeout: 120 seconds with progress updates every 5 seconds
- Propagates `SYNTH_QUIET=1` to suppress diagnostic messages

**sqld Startup:**
- Starts with Hrana WebSocket (8080) and HTTP (8081) ports
- Polls `/health` endpoint for readiness
- Timeout: 30 seconds

**Port Cleanup:**
- Uses `lsof -ti :PORT` to find PIDs
- Kills processes with `kill -9 PID`
- Waits 2 seconds for port release

### 3. Mock RL Trainer

The mock trainer (`MockRLTrainer`) acts as a proxy:
- `backend="synthetic"`: Generates fake tool calls deterministically
- `backend="openai"`: Forwards to real OpenAI API
- Logs all requests/responses with `[mock-rl]` prefix
- Auto-assigns port if `port=0`

### 4. Diagnostic Message Suppression

**Permanently disabled (commented out):**
- `synth_ai/tracing_v3/config.py`: `[TRACING_V3_CONFIG_LOADED]` message
- `synth_ai/environments/examples/crafter_classic/engine_deterministic_patch.py`: All `[PATCH]` messages
- `synth_ai/environments/examples/crafter_classic/engine_serialization_patch_v3.py`: All `[PATCH]` messages
- `synth_ai/environments/examples/crafter_classic/world_config_patch_simple.py`: All `[PATCH]` messages

**Reason:** These messages add noise to smoke test output. They're still in the code as comments for documentation.

## Troubleshooting Guide

### No tool calls displayed

**Symptom:** Output shows `⚠ No tool calls found in trace`

**Causes:**
1. `return_trace=false` in config - **FIX:** Set `return_trace = true`
2. Trace format mismatch - Check `response.trace.event_history` structure
3. No LLM calls made - Check for policy errors in task app logs

**Debug:**
```bash
# Check task app logs
cat /path/to/synth-ai/nohup_task_app.out

# Verify trace structure
# Add debug output in core.py around line 978:
click.echo(f"DEBUG: trace keys: {list(tr.keys())}")
click.echo(f"DEBUG: event_history length: {len(event_history)}")
```

### Task app exits immediately

**Symptom:** `0 steps` in rollout, task app process not running

**Causes:**
1. Wrong task app name - **FIX:** Use `synth-ai task-app list` to find correct name
2. Missing .env file - **FIX:** Ensure `task_app_env_file` points to valid .env
3. Wrong working directory - **FIX:** Task app must be started from synth-ai root

**Debug:**
```bash
# Manual test
cd /path/to/synth-ai
uvx synth-ai task-app serve grpo-crafter --port 8765 --env-file /path/to/.env --force
```

### Port conflicts

**Symptom:** `Address already in use` errors

**Fix:** The smoke command auto-kills processes on ports 8080, 8081, 8765. If manual cleanup needed:
```bash
lsof -ti :8080 | xargs kill -9
lsof -ti :8081 | xargs kill -9
lsof -ti :8765 | xargs kill -9
```

## Future Improvements

Potential enhancements for future agents:

1. **Streaming tool call display**: Show tool calls as they happen, not just at the end
2. **Tool call validation**: Verify tool calls match expected format for the environment
3. **Performance metrics**: Track inference latency per tool call
4. **Cost tracking**: Display OpenAI API costs for the smoke test
5. **Parallel rollouts**: Support `--parallel N` to test concurrent execution
6. **Video/image capture**: For vision-based tasks, save observations
7. **Interactive mode**: Allow stepping through rollout one action at a time

## Related Files

- `synth_ai/cli/commands/smoke/core.py` - Main smoke command implementation
- `synth_ai/api/train/configs/rl.py` - `SmokeConfig` Pydantic model
- `synth_ai/api/train/builders.py` - Removes `[smoke]` section before sending to trainer
- `synth_ai/task/contracts.py` - `RolloutResponse` with trace field
- `examples/blog_posts/warming_up_to_rl/SMOKE_TESTING.md` - User-facing documentation
- `monorepo/docs/cli/smoke.mdx` - Mintlify documentation


