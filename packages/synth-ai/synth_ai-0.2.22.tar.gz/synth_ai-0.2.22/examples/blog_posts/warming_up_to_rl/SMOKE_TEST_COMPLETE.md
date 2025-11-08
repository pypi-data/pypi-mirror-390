# Smoke Test Implementation - Complete

## Summary

The smoke test now provides **complete visibility into RL training rollouts**, including:

✅ **Auto-start background services** (sqld, task app)  
✅ **Real OpenAI inference** with gpt-4o-mini  
✅ **Tool call display** - see every action the policy takes  
✅ **Trace validation** - verify v3 trace format  
✅ **Clean output** - all diagnostic noise suppressed  

## Quick Start

```bash
cd examples/blog_posts/warming_up_to_rl
uv run synth-ai smoke --config configs/smoke_test.toml
```

**Output shows:**
- Service startup (sqld, task app)
- Real-time inference requests  
- **All 10 tool calls with arguments** (e.g., `interact_many({"actions":["move_up","move_up"]})`)
- Rollout metrics (steps, returns, rewards)
- Success validation

## Documentation

All documentation has been updated for future agents:

### 1. User Documentation
- **`SMOKE_TESTING.md`** - How to run smoke tests, what to expect
- **`configs/smoke_test.toml`** - Well-commented example configuration
- **`monorepo/docs/cli/smoke.mdx`** - Mintlify CLI documentation

### 2. Developer Documentation  
- **`ARCHITECTURE.md`** - Internal architecture, troubleshooting guide
- **`synth_ai/cli/commands/smoke/core.py`** - Extensive inline comments explaining tool call extraction

### 3. Code Comments

**Tool Call Extraction (core.py lines 946-997):**
```python
# Extract and display tool calls from v3 trace
# 
# IMPORTANT: Tool calls are extracted from the structured v3 trace format.
# The trace must be requested with return_trace=True for this to work.
# 
# Trace structure:
#   trace.event_history[] - list of events (policy calls, env steps)
#     ├─ event.call_records[] - LLM calls made during this event
#        ├─ call_record.output_tool_calls[] - tool calls from LLM response
#           ├─ tool_call.name - function name (e.g., "interact_many")
#           └─ tool_call.arguments_json - JSON string of arguments
```

## Key Implementation Details

### Tool Call Display

**Requirements:**
1. `return_trace = true` in config (CRITICAL - without this, no tool calls)
2. v3 trace format (`trace_format="structured"`)
3. Mock proxy or real inference (direct API calls don't populate traces correctly)

**Data Flow:**
```
1. Rollout request with return_trace=True
   ↓
2. Task app makes LLM calls, captures responses
   ↓
3. LLM responses include tool_calls
   ↓
4. Task app stores call_records in event_history
   ↓
5. Smoke command extracts from trace.event_history[].call_records[].output_tool_calls[]
   ↓
6. Display: TOOL_CALL[N]: function_name({...args})
```

### Diagnostic Suppression

**Permanently disabled (commented out, not deleted):**
- `synth_ai/tracing_v3/config.py:21` - `[TRACING_V3_CONFIG_LOADED]`
- `synth_ai/environments/examples/crafter_classic/engine_deterministic_patch.py` - All `[PATCH]` messages
- `synth_ai/environments/examples/crafter_classic/engine_serialization_patch_v3.py` - All `[PATCH]` messages
- `synth_ai/environments/examples/crafter_classic/world_config_patch_simple.py` - All `[PATCH]` messages

**Why commented, not deleted?**
- Preserves context for debugging
- Shows what messages existed
- Easy to re-enable if needed

### Background Service Management

**Task App:**
- Runs from synth-ai root (required for discovery)
- Uses `nohup` for detachment
- Output → `nohup_task_app.out`
- Health check accepts 200 or 400 (400 = server up, auth failing)
- 120s timeout with progress updates

**sqld:**
- Dual ports: 8080 (Hrana WebSocket), 8081 (HTTP)
- Health check: `GET http://127.0.0.1:8081/health`
- 30s timeout
- Auto-cleanup of existing processes

## Configuration Reference

### Critical Settings

```toml
[smoke]
# Auto-start services
task_app_name = "grpo-crafter"  # Task app to serve
task_app_port = 8765
task_app_env_file = ".env"      # Required for this app
sqld_auto_start = true

# Inference - REAL OpenAI
model = "gpt-4o-mini"           # Actual model used
mock_backend = "openai"         # Route through OpenAI API
use_mock = true                 # Enable mock proxy

# CRITICAL for tool call display
return_trace = true             # Must be true!
```

### Optional Settings

All `[smoke]` parameters are optional - CLI args override TOML values:

```bash
# Override max steps
uv run synth-ai smoke --config configs/smoke_test.toml --max-steps 5

# Use different model
uv run synth-ai smoke --config configs/smoke_test.toml --model gpt-4o

# Disable mock (use direct API - won't show tool calls properly)
uv run synth-ai smoke --config configs/smoke_test.toml --no-mock
```

## Troubleshooting

### No tool calls displayed

**Symptom:** `⚠ No tool calls found in trace`

**Solutions:**
1. Verify `return_trace = true` in config
2. Check `v3_traces=1/1` in output (should match successes)
3. Ensure `use_mock = true` or using mock proxy
4. Check task app logs: `cat /path/to/synth-ai/nohup_task_app.out`

### Task app exits immediately

**Symptom:** `0 steps`, process not running

**Solutions:**
1. Verify task app name: `synth-ai task-app list`
2. Check .env file exists at `task_app_env_file` path
3. Ensure running from correct directory
4. Manual test: `cd /synth-ai && uvx synth-ai task-app serve grpo-crafter --port 8765 --env-file /path/.env --force`

### Port conflicts

**Symptom:** `Address already in use`

**Solution:** Auto-cleanup should handle this, but manual cleanup:
```bash
lsof -ti :8080 | xargs kill -9
lsof -ti :8081 | xargs kill -9
lsof -ti :8765 | xargs kill -9
```

## Testing

### Unit Tests

- `tests/unit/test_train_validation.py::test_rl_config_with_smoke_section` - Validates `[smoke]` section parsing
- `tests/unit/test_smoke_config.py` - Comprehensive Pydantic validation tests

### Integration Test

```bash
cd examples/blog_posts/warming_up_to_rl
uv run synth-ai smoke --config configs/smoke_test.toml
```

**Expected result:**
- ✅ Services start successfully
- ✅ 10 tool calls displayed
- ✅ `v3_traces=1/1`
- ✅ `successes=1/1`
- ✅ `nonzero_returns=1/1`

## Files Modified

### Core Implementation
- `synth_ai/cli/commands/smoke/core.py` - Tool call extraction, auto-start logic
- `synth_ai/api/train/configs/rl.py` - `SmokeConfig` Pydantic model
- `synth_ai/api/train/builders.py` - Remove `[smoke]` before sending to trainer

### Diagnostic Suppression
- `synth_ai/tracing_v3/config.py` - Commented out `[TRACING_V3_CONFIG_LOADED]`
- `synth_ai/environments/examples/crafter_classic/engine_deterministic_patch.py` - Commented out `[PATCH]`
- `synth_ai/environments/examples/crafter_classic/engine_serialization_patch_v3.py` - Commented out `[PATCH]`
- `synth_ai/environments/examples/crafter_classic/world_config_patch_simple.py` - Commented out `[PATCH]`

### Documentation
- `examples/blog_posts/warming_up_to_rl/SMOKE_TESTING.md` - User guide
- `examples/blog_posts/warming_up_to_rl/ARCHITECTURE.md` - Developer guide
- `examples/blog_posts/warming_up_to_rl/configs/smoke_test.toml` - Example config
- `examples/blog_posts/warming_up_to_rl/configs/train_rl_from_sft.toml` - Inline docs
- `monorepo/docs/cli/smoke.mdx` - Mintlify CLI reference

### Tests
- `tests/unit/test_train_validation.py` - Added smoke section test
- `tests/unit/test_smoke_config.py` - Comprehensive smoke config tests

## Future Improvements

Ideas for future agents:

1. **Streaming display** - Show tool calls as they happen, not just at end
2. **Tool call validation** - Verify format matches environment expectations
3. **Performance metrics** - Track inference latency per call
4. **Cost tracking** - Display OpenAI API costs
5. **Parallel rollouts** - Support concurrent execution testing
6. **Vision support** - Save observations for vision-based tasks
7. **Interactive mode** - Step through rollout one action at a time
8. **Replay mode** - Re-run saved traces for debugging

## Success Criteria Met

✅ **Tool calls visible** - All 10 calls displayed with arguments  
✅ **Real inference** - OpenAI gpt-4o-mini executing actual tool calls  
✅ **Clean output** - No diagnostic noise  
✅ **Auto-start** - Background services managed automatically  
✅ **Well documented** - Comprehensive docs for users and developers  
✅ **Robust** - Error handling, health checks, timeouts  
✅ **Tested** - Unit tests and working integration test  

## Contact

For questions or issues, see:
- Architecture details: `ARCHITECTURE.md`
- User guide: `SMOKE_TESTING.md`
- CLI reference: `monorepo/docs/cli/smoke.mdx`


