# Image-Only Evaluation - Quick Reference

This document provides a quick reference for running image-only evaluations on **Crafter** and **Pokemon Red** with Turso tracing.

## 📚 Full Documentation

- **Crafter**: [`crafter/README_IMAGE_ONLY_EVAL.md`](crafter/README_IMAGE_ONLY_EVAL.md)
- **Pokemon Red**: [`pokemon_red/README_IMAGE_ONLY_EVAL.md`](pokemon_red/README_IMAGE_ONLY_EVAL.md)

## ⚡ Quick Start

### Prerequisites

```bash
# 1. Set OpenAI API key in .env
echo "OPENAI_API_KEY=sk-proj-..." >> .env

# 2. Navigate to synth-ai repo
cd /path/to/synth-ai
```

### Run Crafter (Easier - 70% Success Rate)

```bash
# Set up tracing
export TASKAPP_TRACING_ENABLED=1
export TURSO_NATIVE=1
export SQLD_DB_PATH="traces/v3/crafter_eval.db"

# Run evaluation
uv run synth-ai eval grpo-crafter \
  --config examples/task_apps/crafter/eval_image_only_gpt4o.toml

# Check results
sqlite3 -header -column traces/v3/crafter_eval.db \
  "SELECT total_reward, achievements_count, 
   json_extract(reward_metadata, '$.final_achievements') as achievements
   FROM outcome_rewards WHERE total_reward > 0;"
```

### Run Pokemon Red (Harder - 0% with Default Config)

```bash
# Set up tracing
export TASKAPP_TRACING_ENABLED=1
export TURSO_NATIVE=1
export SQLD_DB_PATH="traces/v3/pokemon_red_eval.db"

# Run evaluation
uv run synth-ai eval pokemon_red \
  --config examples/task_apps/pokemon_red/eval_image_only_gpt4o.toml

# Check results
sqlite3 -header -column traces/v3/pokemon_red_eval.db \
  "SELECT total_reward, achievements_count, 
   json_extract(reward_metadata, '$.final_map') as map,
   json_extract(reward_metadata, '$.party_count') as party
   FROM outcome_rewards;"
```

## 📊 Comparison

| Feature | Crafter | Pokemon Red |
|---------|---------|-------------|
| **Difficulty** | Easier | Harder |
| **Default success** | ~70% earn rewards | ~0% (needs tuning) |
| **Typical reward** | 1-3 achievements | 0 (10 steps too short) |
| **Best for** | Testing vision models | RL research |
| **Recommended steps** | 10 (default works) | 100-500 (need more) |

## 🔧 Configuration Files

### Crafter Config
**Location**: `examples/task_apps/crafter/eval_image_only_gpt4o.toml`

```toml
[eval]
app_id = "grpo-crafter"
model = "gpt-4o-mini-2024-07-18"
seeds = [0, 1, 2, 3, 4, 5, 6, 7, 8, 9]
max_turns = 10
env_name = "crafter"
policy_name = "crafter-react"

[eval.policy_config]
use_vision = true
image_only_mode = true  # Only images, no text
```

### Pokemon Red Config
**Location**: `examples/task_apps/pokemon_red/eval_image_only_gpt4o.toml`

```toml
[eval]
app_id = "pokemon_red"
model = "gpt-4o-mini-2024-07-18"
seeds = [0, 1, 2, 3, 4, 5, 6, 7, 8, 9]
max_turns = 10
env_name = "pokemon_red"

[eval.policy_config]
use_vision = true
image_only_mode = true  # Only images, no text
```

## 📈 Improving Pokemon Red Results

Pokemon Red is harder and needs more steps. To get non-zero rewards:

```toml
[eval]
model = "gpt-4o-2024-08-06"  # Use full GPT-4o
max_turns = 100

[eval.env_config]
env_params = {max_steps_per_episode = 500}

[eval.policy_config]
model = "gpt-4o-2024-08-06"
image_only_mode = false  # Enable text too (multimodal)
max_llm_calls = 100
```

## 🗄️ Database Queries

### Get All Rewards

```sql
-- Crafter
SELECT 
    json_extract(reward_metadata, '$.env_seed') as seed,
    total_reward,
    achievements_count,
    json_extract(reward_metadata, '$.final_achievements') as achievements
FROM outcome_rewards
ORDER BY total_reward DESC;

-- Pokemon Red
SELECT 
    session_id,
    total_reward,
    achievements_count,
    json_extract(reward_metadata, '$.final_map') as map,
    json_extract(reward_metadata, '$.party_count') as party
FROM outcome_rewards
ORDER BY total_reward DESC;
```

### Filter Non-Zero Rewards

```sql
SELECT * FROM outcome_rewards WHERE total_reward > 0;
```

### Get Statistics

```sql
SELECT 
    COUNT(*) as total,
    SUM(CASE WHEN total_reward > 0 THEN 1 ELSE 0 END) as with_rewards,
    AVG(total_reward) as avg_reward,
    MAX(total_reward) as max_reward
FROM outcome_rewards;
```

## 🎯 What is Image-Only Mode?

**Image-Only Mode** means:
- ✅ Agent receives **only** base64-encoded PNG images
- ❌ Agent receives **no** text observations (HP, position, inventory, etc.)
- 🎓 Tests pure vision understanding

**Multimodal Mode** (recommended for Pokemon Red):
- ✅ Agent receives **both** images and text
- 🏆 Better performance but "easier"

Toggle with:
```toml
[eval.policy_config]
use_vision = true         # Enable vision
image_only_mode = false   # false = send text too
```

## 📁 Files Created

### Crafter
- `crafter/eval_image_only_gpt4o.toml` - Config
- `crafter/README_IMAGE_ONLY_EVAL.md` - Full guide
- `crafter/EVAL_IMAGE_ONLY_RESULTS.md` - Example results
- `crafter/QUERY_EXAMPLES.md` - SQL queries

### Pokemon Red  
- `pokemon_red/eval_image_only_gpt4o.toml` - Config
- `pokemon_red/README_IMAGE_ONLY_EVAL.md` - Full guide
- `pokemon_red/EVAL_IMAGE_ONLY_COMPLETE.md` - Implementation
- `pokemon_red/EVAL_IMAGE_ONLY_STATUS.md` - Status

## 🐛 Common Issues

### Database Not Created
```bash
# Ensure variables are set
export TASKAPP_TRACING_ENABLED=1
export TURSO_NATIVE=1
export SQLD_DB_PATH="traces/v3/your_eval.db"
```

### 401 Unauthorized
```bash
# Check API key in .env
cat .env | grep OPENAI_API_KEY
```

### Pokemon Red: ROM Not Found
```bash
# Place ROM at expected location
cp pokemon_red.gb synth_ai/environments/examples/red/roms/
```

### All Rewards Zero
- **Crafter**: Should get ~70% non-zero by default
- **Pokemon Red**: Expected with 10 steps - increase to 100-500

## 🎓 Understanding Results

### Crafter Achievements
- `collect_wood` - Cut down trees
- `collect_sapling` - Collect tree saplings  
- `collect_drink` - Drink from water

### Pokemon Red Milestones
- Leave bedroom (+20)
- Exit house (+30)
- Find Oak's lab (+40)
- Get starter Pokemon (+100)
- Win first battle (+150)

**Total possible**: ~600 points

## 🚀 Next Steps

1. **Read full docs**: See task-specific READMEs for details
2. **Run evaluations**: Start with Crafter (easier)
3. **Query database**: Use SQL to analyze results
4. **Tune configs**: Adjust steps/model for better performance
5. **Compare modes**: Try image-only vs multimodal

## 📞 Support

For issues or questions:
1. Check full README for your task app
2. Review example results files
3. Query database to verify data
4. Adjust config parameters

Happy evaluating! 🎮


