# Qwen Coder – Remaining TODOs

- [ ] Add small-base LoRA config for quick iteration
  - Create `configs/coder_lora_4b.toml` (base=`Qwen/Qwen3-4B`, 1x H100, LoRA all-linear, same hyperparameters structure as 30B).

- [ ] Improve SFT submission script (sft_lora_30b.py)
  - Include `metadata.effective_config.compute` in job payload (gpu_type, gpu_count, nodes) so API doesn’t 400 without TOML.
  - Write resulting `ft:<id>` to `examples/qwen_coder/ft_data/ft_model_id.txt` and print it clearly.
  - Add optional validation file support when present.

- [ ] Add post‑SFT inference script
  - Read `ft_data/ft_model_id.txt` and call the prod proxy (or SDK InferenceClient) to verify the finetuned adapter returns.
  - Save a short transcript to `ft_data/ft_infer_smoke.txt`.

- [ ] Add inference smoke tests (local opt‑in)
  - `tests/qwen_coder/test_infer_prod_proxy.py` (skips unless `SYNTH_API_KEY` set). Hits `/api/inference/v1/chat/completions` with `Qwen/Qwen3-Coder-30B-A3B-Instruct` and asserts 200/choices.
  - Optional: same test for an `ft:<id>` if `FT_MODEL_ID` env is provided.

- [ ] Document end‑to‑end flow in README
  - Expand README with explicit env section (`SYNTH_API_KEY`, `BACKEND_BASE_URL`).
  - Show: generate dataset → run LoRA (4B or 30B) → poll → infer with `ft:<id>`.
  - Mention cost/time caveats for 30B.

- [ ] Dataset utilities
  - Add `validate_jsonl.py` to check first N lines parse and contain `messages`/`assistant` fields required by SFT.
  - Add `subset_jsonl.py` to create capped training sets for quick runs.

- [ ] Optional: CLI convenience wrappers
  - `scripts/train_coder_30b.sh` to invoke `uvx synth-ai train --type sft --config configs/coder_lora_30b.toml --dataset ft_data/coder_sft.small.jsonl` with `.env` preload.
  - `scripts/infer_coder.sh` to run `infer_prod_proxy.py` against base or `ft:<id>`.

- [ ] Optional CI (requires secrets)
  - GitHub workflow job (smoke) that runs `infer_prod_proxy.py` with `SYNTH_API_KEY` secret and prints the first 200 chars of assistant output.

- [ ] (If needed) Add coder variants
  - If backend supports additional coder SKUs, append to `synth_ai/api/models/supported.py:QWEN3_CODER_MODELS` so SDK validation passes (SFT/inference).


