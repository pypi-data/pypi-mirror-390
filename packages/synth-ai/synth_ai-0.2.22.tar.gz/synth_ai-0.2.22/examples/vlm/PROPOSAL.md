# Crafter VLM Fine-Tuning Plan

## Why

Crafter observations already expose 64×64 RGB frames, but until now the stack only
surfaced text summaries. The new multimodal trace format allows us to:

- Retrieve and persist `observation_image_base64` on every step.
- Thread data URLs through policy prompts so LLMs see the raw frame.
- Emit multimodal content parts inside LLM call records (and therefore SFT datasets).
- Capture the same information inside the session trace (`policy_user_prompt` entries).

This unlocks a supervised dataset for vision‑language models that treat the frame as a
first-class token alongside the textual state summary.

## What Changed

1. **Environment wrappers** now attach `observation_image_base64`, `..._data_url`,
   and image metadata to every observation (initialise + step).
2. **Crafter policy** augments the user prompt with `{"type":"image_url"}` segments
   while still emitting the textual summary for language-only models.
3. **Tracing** stores structured prompt content and serialises it to JSON so prompts
   with images survive the round-trip to SQLite/Turso.
4. **Dataset exporter** preserves multimodal content, flags rows with images, and
   carries this metadata through SFT JSONL.
5. **Utility scripts** under `examples/vlm/` make it easy to sanity check frames,
   filter datasets, and spin up an image-aware training job.

## Proposed Workflow

1. **Collect rollouts** with tracing enabled (either via the task app or scripted
   runs) to populate `traces/v3/synth_ai.db`.
2. **Export** using `export_trace_sft.py` — images are embedded automatically.
3. **Filter** to rows with user images (see `filter_image_rows.py`) and optionally
   build validation splits.
4. **Upload** the JSONL via `run_fft_and_save.py` or the Synth CLI.
5. **Train** with a VLM-capable base model (e.g. `openai/gpt-4o-mini-2024-07-18`)
   using `configs/crafter_vlm_gpt4o.toml`.
6. **Evaluate** the resulting checkpoint on Crafter tasks (reuse the evaluation
   harness from `examples/warming_up_to_rl` but now with multimodal prompts).

## Open Questions / Future Work

- **Longer context**: investigate packing multiple sequential frames per turn
  (e.g. last N frames) as either separate image parts or a stitched sprite sheet.
- **Reward shaping**: extend metadata so SFT rows carry frame-level reward deltas,
  enabling hybrid BC + value regression objectives.
- **Assistant images**: currently most assistant messages are textual; we could
  experiment with returning thumbnails explaining the plan.
- **Automated filtering**: add CLI helpers to keep only turns whose tool calls led
  to high-reward outcomes (e.g. achievements).
- **Evaluation**: define a reference set of human-labelled “vision checkpoints”
  (e.g. recognise nearby resource, detect threats) to quantify multimodal progress.
