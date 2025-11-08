# SSE metrics/event streaming design (RL + FT)

## Goals
- Near real-time push of job status, metrics, and logs during RL training, evaluation, and fine-tuning (FT)
- Single streaming endpoint per job, resumable (Last-Event-ID), low overhead, widely compatible (HTTP/1.1)
- Minimal client friction (CLI + Python helper), production-ready (auth, backpressure, rate limit)

## Non-goals
- Binary/frame multiplexing (use WebSocket if needed later)
- Arbitrary high-frequency payloads (we will coalesce/limit ~2–4 Hz for metrics)

---

## Endpoint
- Method: GET `/rl/jobs/{job_id}/stream`
- Headers:
  - Auth: `X-API-Key: <env key>` or `Authorization: Bearer <token>`
  - Cache: `Cache-Control: no-cache`
- Response:
  - Content-Type: `text/event-stream; charset=utf-8`
  - Transfer-Encoding: `chunked`
  - Connection: `keep-alive`
- Query params (optional):
  - `since_id`: int; resume from a specific event id (inclusive)
  - `types`: comma list `metric,status,log,artifact` (default: all)
  - `heartbeat`: seconds between heartbeats (default 20)
  - `split`: `train|eval` (filters metrics only)

## Event framing (SSE)
- Fields per message:
  - `id: <int>` monotonically increasing per job
  - `event: <status|metric|log|artifact|heartbeat>`
  - `data: <JSON>` single-line JSON (compact)
- Heartbeats: comment lines `: keep-alive` at configured interval
- Flush: after each event write + heartbeat
- Backpressure: if producer > consumer, coalesce metrics, keep status/logs, never buffer unbounded

## Payload schemas
- `status`
  - `{ "state": "queued|running|succeeded|failed|canceled", "step": 123, "epoch": 3, "phase": "train|eval|ft", "message": "...", "ts": 173.12 }`
- `metric`
  - `{ "name": "avg_reward|loss|accuracy|success_rate|return", "value": 0.123, "step": 123, "epoch": 3, "split": "train|eval", "window": 100, "mean": 0.42, "std": 0.08, "ts": 173.12 }`
  - Optional extras: `{ "tags": {"env": "crafter", "policy": "react"} }`
- `log`
  - `{ "level": "INFO|WARN|ERROR", "message": "...", "ts": 173.12 }`
- `artifact`
  - `{ "kind": "checkpoint|trace|plot|jsonl", "url": "/rl/jobs/{id}/artifacts/ckpt_0003.pt", "step": 123, "ts": 173.12 }`
- `heartbeat`
  - `{ "alive": true, "ts": 173.12 }`

### Example stream (illustrative)
```
id: 101
event: status
data: {"state":"running","phase":"train","step":820,"epoch":4,"ts":173.12}

id: 102
event: metric
data: {"name":"avg_reward","value":0.62,"step":820,"epoch":4,"split":"train","ts":173.13}

id: 103
event: metric
data: {"name":"loss","value":1.84,"step":820,"epoch":4,"split":"train","window":100,"mean":1.90,"std":0.15,"ts":173.13}

id: 104
event: log
data: {"level":"INFO","message":"checkpoint saved","ts":173.16}

id: 105
event: artifact
data: {"kind":"checkpoint","url":"/rl/jobs/j_abc/artifacts/ckpt_0004.pt","step":820,"ts":173.16}

: keep-alive
```

---

## Server architecture

### Components
- Event bus per `job_id` (async queue) where producers (RL, FT, evaluator) `emit(Event)`
- Ring buffer per job for replay (configurable: last N events OR last T minutes)
- SSE handler:
  1) Authenticate, pick job, determine resume cursor (`since_id` or `Last-Event-ID`)
  2) Replay from ring buffer >= cursor
  3) Attach to live queue; stream new events
  4) Emit heartbeats; close after terminal `status` + grace

### Concurrency & ordering
- Single writer increments `event_id`
- Replay preserves original order; live continues from last id
- If consumer slow: drop/coalesce metrics (preserve last per metric name), always deliver status/log/artifact

### Rate limiting & coalescing
- Default target 2–4 Hz for metrics per split
- Coalesce by metric name within a small interval (e.g., 250–500 ms)
- Status events limited to phase changes or every 5–10s

### Auth & security
- Accept `X-API-Key` or `Authorization: Bearer`
- Validate job ownership/visibility
- CORS: allow EventSource; set `Access-Control-Allow-Origin` appropriately
- Timeouts: server idle timeout > heartbeat * 2; client reconnect on drop

### Config knobs (env)
- `SSE_HEARTBEAT_SECS` (default 20)
- `SSE_RING_BUFFER_EVENTS` (e.g., 2000) OR `SSE_RING_BUFFER_WINDOW_SECS` (e.g., 600)
- `SSE_MAX_METRIC_HZ` (e.g., 4)
- `SSE_MAX_CLIENTS_PER_JOB` (protect from fan-out)

---

## Emit points

### RL training/eval
- On train step end: `metric` avg_reward/return/success_rate; `status` every N steps
- On eval step end: `metric` eval_return/success_rate; `artifact` eval JSONL optional
- On checkpoint: `artifact` + `log`
- On phase transitions: `status` (train→eval, etc.)

### Fine-tuning (FT)
- On optimizer step: `metric` loss (and optional lr)
- On validation: `metric` val_loss/accuracy; optional `artifact` (curves)
- On checkpoint: `artifact` + `log`

---

## Client (synth-ai)

### CLI
- `synth-ai jobs stream <job_id> [--jsonl out.jsonl] [--types metric,status]`
- Prints compact lines: `t=18:22:40 step=820 avg_reward=0.62 loss=1.84`
- Writes raw events to JSONL if specified

### Python helper
```python
from synth_ai.client import TaskAppClient

with TaskAppClient(base_url, api_key) as c:
    for ev in c.stream_job(job_id, types=["metric","status"], since_id=None):
        handle(ev)
```
- Handles reconnect with `Last-Event-ID`
- Dedupes by event id; optional local aggregation windows

---

## Error handling & edge cases
- 404 (job not found): immediate error, no stream
- 401/403: immediate error, no stream
- Producer stalls: heartbeats continue; client shows "connected: no new data"
- Ring buffer miss (client too far behind): send a summary `status` snapshot, then live only
- Buffer overflow: set `dropped_events: true` field in a `status` update

---

## Testing plan
- Unit: SSE formatting, ring buffer indexing, resume semantics, coalescing
- Integration: run toy RL + FT loops; assert ordered sequence and types
- Load: simulate 100 Hz metric emissions; verify rate limiting and non-blocking behavior
- Auth: invalid key, missing key, cross-job access rejection

---

## Rollout plan
1) Implement event bus + ring buffer per job
2) Add SSE route with auth, resume, heartbeat
3) Emiters in RL/FT loops (train/eval steps, loss/reward, checkpoints)
4) synth-ai client: CLI + Python helper; optional JSONL sink
5) Docs and example snippets (curl, Python, browser EventSource)

---

## Open questions / decisions
- Do we persist events beyond ring buffer? (optional artifact JSONL)
- Multi-tenant limits per org/user? (SSE_MAX_CLIENTS_PER_ORG?)
- Artifact URLs: signed vs. authenticated direct
- Backward compatibility with current polling endpoints
I'll scan the backend to find where RL jobs are created, status is served, and whether there's any existing streaming/event infrastructure to extend. Then I'll identify exact files/functions to change for adding an SSE endpoint and metric emitters.

[2 tools called]

Here’s the exact backend surface you’ll need to touch to add a single SSE stream for status + metrics, with where to hook metric emitters.

### Where jobs and events live
- Job and event tables (legacy RL path):
```1:20:monorepo/backend/app/db/models/jobs.py
"""Job orchestration models (RL/SFT shared).
"""
```
```31:58:monorepo/backend/app/db/models/jobs.py
class Job(Base):
    __tablename__ = "jobs"
    job_id = Column(String, primary_key=True)
    ...
    status = Column(String, nullable=False, default="QUEUED")
    ...
    last_seq = Column(BigInteger, nullable=True, default=0)
    events = relationship("JobEvent", back_populates="job", cascade="all, delete-orphan", passive_deletes=True)
```
```66:88:monorepo/backend/app/db/models/jobs.py
class JobEvent(Base):
    """Append-only job event log."""
    __tablename__ = "job_events"
    job_id = Column(String, ForeignKey("jobs.job_id", ondelete="CASCADE"), primary_key=True)
    seq = Column(BigInteger, primary_key=True)
    ts = Column(DateTime(timezone=True), server_default=func.now())
    type = Column(String, nullable=False)
    level = Column(String, nullable=False, default="info")
    message = Column(Text, nullable=False)
    data = Column(JSONB, nullable=True)
```

- DB repo (atomic seq increment + append):
```108:146:monorepo/backend/app/orchestration/jobs/repository_db.py
async def append_event(...):
    res = await self.session.execute(
        update(LearningJob)
        .where(LearningJob.job_id == job_id)
        .values(last_seq=func.coalesce(LearningJob.last_seq, 0) + 1, updated_at=func.now())
        .returning(LearningJob.last_seq)
    )
    seq = res.scalar_one()
    ev = JobEvent(job_id=job_id, seq=seq, type=type_, level=level, message=message, data=(data or {}))
    ...
```

- RL jobs REST (create + emit first events via PostgREST emitter):
```214:233:monorepo/backend/app/routes/clustered_training/core/routes.py
@router.post("/jobs", ...)
async def create_job(...):
    ...
```
```784:799:monorepo/backend/app/routes/clustered_training/core/routes.py
await get_postgrest_emitter().append_event(job_id=job_id, type_="rl.job.created", message="RL job created", data={"work": payload.work})
```

- Shared storage path showing how “update” and “append event” are broadcast via the PostgREST emitter:
```242:271:monorepo/backend/app/routes/simple_training/services/job_service.py
async def update_job(...): ...
async def append_job_event(...): ...
```

What to add/change (SSE + emitters)

1) Add SSE endpoint under RL jobs
- File: `monorepo/backend/app/routes/clustered_training/core/routes.py`
- New route: `GET /api/rl/jobs/{job_id}/stream`
  - Auth: `ValidatedAPIKey`
  - Headers: honor `Last-Event-ID`; Query: `since_id`, `types`, `heartbeat`
  - Flow:
    - Validate job exists (use the DB-backed repo in production mode)
    - Determine start seq (from Last-Event-ID or since_id, else 0)
    - Replay: call repo `list_events(job_id, after=seq)` and stream as SSE (`id`, `event`, `data`)
    - Live tail: loop with short sleep (e.g., 0.5–1.0s) fetching new events by `after=last_seq`
    - Heartbeats as comments `: keep-alive` every N seconds
  - Event mapping:
    - `JobEvent.type` prefixes map to SSE `event`:
      - `rl.job.*`, `job.updated` → `status`
      - `rl.step.metric`, `ft.step.metric`, `eval.metric` → `metric`
      - `system.log.*` → `log`
      - `artifact.*` → `artifact`
    - `Job.status` can be snapshotted once at connect (send a `status`)

2) Ensure a consistent event source for reads
- Prefer the DB repo (`JobsRepositoryDB`) in prod mode. If the current code path uses the PostgREST emitter for appends, verify that the repo’s `list_events` reads from the same canonical table (it does for `JobEvent`). If your RL path uses the “learning_shared” models instead, use the associated repository there (same pattern: list by job_id + seq).
- If you must keep PostgREST for append-only, that’s fine; SSE can still read the DB rows inserted alongside (your outbox/emitter already supports both).

3) Emitters in training/FT loops
- File(s): `monorepo/backend/app/orchestration/hatchet/workflows.py` (RL workflow nodes), any FT job loops
- After each meaningful step:
  - Train: append `type="rl.step.metric"`, `data={"avg_reward":..., "return":..., "success_rate":..., "step":..., "epoch":..., "split":"train"}`.
  - Eval: `type="eval.metric"` with eval metrics and split.
  - FT: `type="ft.step.metric"`, `data={"loss":..., "lr":..., "step":..., "epoch":..., "split":"train"}`; validation as `split="eval"`.
  - On phase changes/checkpoints: `type="job.updated"` or `artifact.checkpoint` with URLs.
- Use the same helper used elsewhere:
```236:276:monorepo/backend/app/routes/simple_training/services/job_service.py
async def append_job_event(...): return await get_postgrest_emitter().append_event(...)
```

4) Optional shared service abstraction
- File: `monorepo/backend/app/routes/simple_training/services/storage_shared.py`
  - Add a small `stream_job_events(job_id, after)` helper that wraps `repo.list_events(...)` and normalizes schemas (legacy vs learning_shared). The SSE route can call this.

5) Wire the router
- File: `monorepo/backend/app/routes/main.py`
  - Include the new GET route (under the RL router you already mount).
- CORS: ensure EventSource allowed if frontend will use browser SSE.

Indexes/Perf you already have
- Jobs/events tables include per-job indexes and a `last_seq`; reads by `(job_id, seq)` are efficient:
```84:88:monorepo/backend/app/db/models/jobs.py
Index("idx_job_events_job_ts", "job_id", "ts"),
Index("idx_job_events_data_gin", "data", postgresql_using="gin"),
```
- For learning_shared events (if used), there are sequence indexes too:
```159:165:monorepo/backend/app/db/models/learning_shared.py
sa.Index("idx_learning_job_events_job_seq_idx", "job_id", "seq"),
```

Summary of minimal backend edits
- Add SSE route:
  - `monorepo/backend/app/routes/clustered_training/core/routes.py` (GET `/api/rl/jobs/{job_id}/stream`)
- Consume events via repo:
  - `monorepo/backend/app/orchestration/jobs/repository_db.py` (use `list_events`)
- Emit metrics from loops:
  - `monorepo/backend/app/orchestration/hatchet/workflows.py` (append_event at train/eval steps)
- Optional shared helper:
  - `monorepo/backend/app/routes/simple_training/services/storage_shared.py` (normalize event reads)
- Wireup:
  - `monorepo/backend/app/routes/main.py` (include SSE route)
- No schema changes required; you already have `JobEvent`/indexes and event append plumbing.

### SDK additions for great terminal polling (with SSE fallback)

- RlJobsApi extensions (synth_ai/jobs/client.py)
  - stream(job_id, since_id=None, types=None, heartbeat=None) -> async iterator of events (uses SSE; falls back to polling)
  - events(job_id, after=None, limit=500) -> list[JobEvent] (poll)
  - status(job_id) -> JobSummary (single snapshot)

- Event models (synth_ai/jobs/types.py)
  - JobEvent base: {id, type, level, message, data, ts}
  - StatusEvent, MetricEvent, LogEvent, ArtifactEvent (typed helpers)

- JobsWatcher helper (synth_ai/jobs/watcher.py)
  - constructor(client, job_id, interval=2.0, prefer_sse=True, jsonl_path=None, types=None)
  - run(on_event, stop_when=None) → handles SSE connect/reconnect, polling fallback, Last-Event-ID cursor, dedupe
  - metrics_tracker: rolling windows per metric name (mean/std/min/max, last_value, last_step)
  - backoff policy: jittered reconnect; rate limiter for render

- Terminal renderer (synth_ai/jobs/render.py)
  - RichRenderer (or minimal TTY): compact line updates: t=HH:MM:SS | step/E | key metrics (avg_reward, loss, val_loss, success_rate)
  - modes: one-line ticker vs. per-event lines; quiet mode; color by level/state
  - JSONL sink: raw event writes without printing prompts/payloads

- CLI command (synth_ai/api/train/cli.py)
  - synth-ai jobs watch <job_id> [--types metric,status] [--interval 2] [--jsonl out.jsonl] [--since-id N] [--no-sse]
  - exit codes: 0 on succeeded, 1 on failed/canceled, 2 on timeout

- Utilities (synth_ai/jobs/utils.py)
  - BackoffPolicy(retry, max) with jitter
  - EventCursor(last_id, update)
  - MetricsFormatter(map by job_type: RL vs FT metric labels)
  - Coalescer: compress frequent metrics to ≤4 Hz

- Defaults/behavior
  - Prefer SSE; if 404/405/close → fallback to polling events() every interval
  - Heartbeat support; show “connected/no data” when only heartbeats
  - Resume: honor --since-id or Last-Event-ID; persist cursor optionally

- Minimal backend assumptions
  - GET /api/rl/jobs/{job_id}/stream (SSE) or /api/rl/jobs/{job_id}/events?after=… (poll)
  - Events include metric/status/log/artifact with seq ids and ts

- Extensibility
  - Plugin renderers per job_type (rl, sft/ft)
  - Hooks: on_status_change, on_metric(name, value), on_artifact(url)