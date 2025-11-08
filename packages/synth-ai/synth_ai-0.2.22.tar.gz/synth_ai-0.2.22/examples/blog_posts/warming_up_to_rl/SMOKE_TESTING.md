# Smoke Testing Your Task App

This guide shows how to quickly test your task app using the `synth-ai smoke` command with auto-start features.

## Quick Start

The easiest way to smoke test is using the `[smoke]` section in your RL config:

```bash
cd examples/blog_posts/warming_up_to_rl
uv run synth-ai smoke --config configs/smoke_test.toml
```

**That's it!** The smoke command will:
1. ✅ Auto-start sqld server for tracing (if `sqld_auto_start = true`)
2. ✅ Auto-start your task app on port 8765 (if `task_app_name` is set)
3. ✅ Run 10 rollout steps with `gpt-5-nano` using synthetic mocking
4. ✅ Automatically stop all background services when done

**Expected output:**
```
[smoke] sqld ready
[smoke] Task app ready at http://localhost:8765 (status=400)
[mock-rl] server ready http://127.0.0.1:51798 backend=synthetic
>> POST /rollout run_id=smoke-... env=crafter policy=crafter-react
[mock-rl] ← request backend=synthetic model=gpt-5-nano messages=2
[mock-rl] → response tool_calls=1 backend=synthetic
  rollout[0:0] episodes=1 steps=10 mean_return=1.0000
✓ Smoke rollouts complete
  successes=1/1 total_steps=10 v3_traces=1/1 nonzero_returns=1/1
[smoke] Background services stopped
```

## Configuration

Add a `[smoke]` section to your RL config:

```toml
[smoke]
# Auto-start task app
task_app_name = "grpo-crafter"
task_app_port = 8765
task_app_env_file = ".env"
task_app_force = true

# Auto-start sqld
sqld_auto_start = true
sqld_db_path = "./traces/local.db"
sqld_hrana_port = 8080
sqld_http_port = 8081

# Test parameters
max_steps = 10
policy = "gpt-5-nano"
mock_backend = "synthetic"  # or "openai" (requires valid OpenAI API key)
return_trace = true
```

## Testing Methods

### 1. Full Auto (Recommended)
Everything auto-starts from config:
```bash
uv run synth-ai smoke --config configs/smoke_test.toml
```

### 2. Manual Task App + Auto sqld
Start task app manually, auto-start sqld:
```bash
# Config with sqld_auto_start=true but no task_app_name
uv run synth-ai smoke --config configs/my_config.toml --url http://localhost:8765
```

### 3. Override Config Settings
Override any config value via CLI:
```bash
uv run synth-ai smoke --config configs/smoke_test.toml --max-steps 5
```

### 4. No Config (Manual Everything)
```bash
# Start services manually in separate terminals:
# Terminal 1: sqld --db-path ./traces/local.db --hrana-listen-addr 127.0.0.1:8080 --http-listen-addr 127.0.0.1:8081
# Terminal 2: uv run synth-ai task-app serve grpo-crafter --port 8765 --env-file .env --force

# Terminal 3: Run smoke test
uv run synth-ai smoke --url http://localhost:8765 \
  --env-name crafter \
  --policy-name crafter-react \
  --max-steps 10 \
  --policy mock \
  --mock-backend openai
```

## Prerequisites

### Install sqld (for tracing)
```bash
brew install sqld
# or
curl -fsSL https://get.turso.com/sqld | bash
```

### Verify Installation
```bash
which sqld
# Should output: /opt/homebrew/bin/sqld or similar
```

## Common Issues

### sqld not found
If you see "sqld not found in PATH":
```bash
brew install sqld
```

### Port already in use
Use `task_app_force = true` in config, or:
```bash
# Kill processes on ports 8080, 8081, 8765
lsof -ti:8080,8081,8765 | xargs kill -9
```

### Task app not starting
Check the error output - you may need:
- Valid `.env` file with required keys
- Correct task app name registered in your codebase

## Example Output

```
[smoke] Loaded configuration from configs/smoke_test.toml
[smoke] Config keys: task_app_name, task_app_port, sqld_auto_start, max_steps, policy
[smoke] Starting sqld server...
[smoke] DB path: /Users/you/project/traces/local.db
[smoke] Hrana port: 8080, HTTP port: 8081
[smoke] sqld ready
[smoke] Starting task app 'grpo-crafter' on port 8765...
[smoke] Task app ready at http://localhost:8765
[smoke] Task app started, will use URL: http://localhost:8765
[mock-rl] server ready http://127.0.0.1:52134 backend=openai
>> POST /rollout run_id=smoke-abc123...
  rollout[0:0] episodes=1 steps=20 mean_return=1.2500
✓ Smoke rollouts complete
  successes=1/1 total_steps=20 v3_traces=1/1 nonzero_returns=1/1
[smoke] Stopping sqld...
[smoke] Stopping task_app...
[smoke] Background services stopped
```

## Next Steps

Once smoke tests pass:
1. Train your model: `uv run synth-ai train --type rl --config configs/your_config.toml`
2. Check traces: Look in `./traces/` directory
3. Monitor training: Use the Synth dashboard

## Full Config Reference

See [`configs/smoke_test.toml`](configs/smoke_test.toml) for a complete example.

See [CLI Smoke Documentation](https://docs.usesynth.ai/cli/smoke) for all options.

