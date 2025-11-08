# Crafter RL LoRA (10-step runs)

This walkthrough shows how to fine-tune the Crafter task app with our 10-step RL LoRA config.

1. **Deploy the Crafter task app on Modal**

   ```bash
   # assumes .env contains SYNTH_API_KEY, ENVIRONMENT_API_KEY, GROQ_API_KEY, etc.
   uvx synth-ai modal-serve grpo-crafter \
     --env-file examples/warming_up_to_rl/.env \
     --name grpo-crafter-task-app
   ```

   * The command prints the public `https://…modal.run` URL; copy it for the RL configs below.*

2. **Wire up the three RL experiment configs**

   Update the `task_url` placeholder in each config with the Modal URL from step&nbsp;1:

   - `examples/multi_step/configs/crafter_rl_outcome.toml`
   - `examples/multi_step/configs/crafter_rl_stepwise_simple.toml`
   - `examples/multi_step/configs/crafter_rl_stepwise_shaped.toml`

   The difference between them (all run with LoRA on 2×H100 split 1/1 for vLLM vs. trainer):

   | Config | Reward signal |
   | ------ | ------------- |
   | `crafter_rl_outcome.toml` | Outcome-only — step rewards disabled. |
   | `crafter_rl_stepwise_simple.toml` | Stepwise (“consistent”) — +1 for every newly unlocked achievement. |
   | `crafter_rl_stepwise_shaped.toml` | Stepwise (“per_achievement”) — combines achievement credit with inventory/achievement-count shaping from the rollout hook. |

3. **Launch the three RL runs in parallel**

   ```bash
   export SYNTH_API_KEY=...       # already sourced if examples/.env was loaded
   export TASK_APP_URL=https://your-modal-task-app.modal.run

   uvx synth-ai train --type rl \
     --config examples/multi_step/configs/crafter_rl_outcome.toml \
     --run-name crafter-rl-outcome \
     --no-poll &

   uvx synth-ai train --type rl \
     --config examples/multi_step/configs/crafter_rl_stepwise_simple.toml \
     --run-name crafter-rl-stepwise-simple \
     --no-poll &

   uvx synth-ai train --type rl \
     --config examples/multi_step/configs/crafter_rl_stepwise_shaped.toml \
     --run-name crafter-rl-stepwise-shaped \
     --no-poll &

   wait
   ```

   *`--no-poll` returns immediately so each run can stream logs in its own terminal; `wait` blocks until all jobs finish.*

4. **Track results**

   Tail each job’s logs with `uvx synth-ai train logs --run-name <name>` or open the Modal dashboard. Compare:

   - Avg outcome reward (modal dashboard)
   - Stepwise reward components (`resource_reward`, `unique_achievements_total`) in the task app logs
   - Trace JSONL dumps under `traces/v3` if tracing is enabled


  * This config forces 10 agent turns per rollout, reduces batch size to avoid OOMs, and enforces Crafter-specific defaults.*

  INFO - 🎉 Training completed successfully!
  INFO - All batch rewards: [0.0625, 0.0625, 0.125, 0.0625, 0.0625, 0.3125, 0.375, 0.4375, 0.5, 0.9375]
