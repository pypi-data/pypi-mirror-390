# Crafter Eval Database Query Examples

## Database Location
```bash
/Users/joshpurtell/Documents/GitHub/synth-ai/traces/v3/crafter_eval.db
```

## Quick Stats

Run this query to get an overview:
```sql
SELECT 
    'Total rollouts' as metric, 
    CAST(COUNT(*) as TEXT) as value 
FROM outcome_rewards
UNION ALL
SELECT 
    'Rollouts with reward > 0', 
    CAST(COUNT(*) as TEXT)
FROM outcome_rewards 
WHERE total_reward > 0
UNION ALL
SELECT 
    'Average reward', 
    CAST(ROUND(AVG(total_reward), 2) as TEXT)
FROM outcome_rewards
UNION ALL
SELECT 
    'Max reward', 
    CAST(MAX(total_reward) as TEXT)
FROM outcome_rewards;
```

**Current Results:**
- Total rollouts: 10
- Rollouts with reward > 0: 7
- Average reward: 1.3
- Max reward: 3

## Filter for Non-Zero Rewards

### Simple Query
```sql
SELECT 
    session_id,
    total_reward,
    achievements_count,
    json_extract(reward_metadata, '$.env_seed') as seed,
    json_extract(reward_metadata, '$.final_achievements') as achievements
FROM outcome_rewards
WHERE total_reward > 0
ORDER BY total_reward DESC, achievements_count DESC;
```

### With Full Session Context
```sql
SELECT 
    st.session_id,
    st.created_at,
    st.num_timesteps,
    st.num_events,
    orw.total_reward,
    orw.achievements_count,
    json_extract(orw.reward_metadata, '$.final_achievements') as achievements,
    json_extract(orw.reward_metadata, '$.env_seed') as seed
FROM session_traces st
INNER JOIN outcome_rewards orw ON st.session_id = orw.session_id
WHERE orw.total_reward > 0
ORDER BY orw.total_reward DESC;
```

## Filter by Achievement Count

### Get rollouts with 2+ achievements
```sql
SELECT 
    session_id,
    total_reward,
    achievements_count,
    json_extract(reward_metadata, '$.final_achievements') as achievements
FROM outcome_rewards
WHERE achievements_count >= 2
ORDER BY achievements_count DESC, total_reward DESC;
```

### Get rollouts with specific achievement
```sql
SELECT 
    session_id,
    total_reward,
    achievements_count,
    json_extract(reward_metadata, '$.final_achievements') as achievements
FROM outcome_rewards
WHERE reward_metadata LIKE '%collect_drink%'
ORDER BY total_reward DESC;
```

## Group by Achievement Count
```sql
SELECT 
    achievements_count,
    COUNT(*) as num_rollouts,
    ROUND(AVG(total_reward), 2) as avg_reward,
    SUM(total_reward) as total_reward_sum,
    GROUP_CONCAT(DISTINCT json_extract(reward_metadata, '$.env_seed')) as seeds
FROM outcome_rewards
GROUP BY achievements_count
ORDER BY achievements_count DESC;
```

## Top Performers
```sql
SELECT 
    json_extract(orw.reward_metadata, '$.env_seed') as seed,
    orw.total_reward,
    orw.achievements_count,
    orw.total_steps,
    st.num_events,
    json_extract(orw.reward_metadata, '$.final_achievements') as achievements
FROM session_traces st
INNER JOIN outcome_rewards orw ON st.session_id = orw.session_id
ORDER BY orw.total_reward DESC, orw.achievements_count DESC
LIMIT 5;
```

## Get Event Details for High-Reward Rollouts
```sql
SELECT 
    e.event_type,
    e.model_name,
    e.input_tokens,
    e.output_tokens,
    e.latency_ms,
    e.reward as step_reward
FROM events e
INNER JOIN outcome_rewards orw ON e.session_id = orw.session_id
WHERE orw.total_reward >= 2
ORDER BY e.session_id, e.id
LIMIT 20;
```

## Running Queries

### From Command Line
```bash
cd /Users/joshpurtell/Documents/GitHub/synth-ai
sqlite3 traces/v3/crafter_eval.db "YOUR_QUERY_HERE"
```

### With Formatted Output
```bash
sqlite3 -header -column traces/v3/crafter_eval.db "YOUR_QUERY_HERE"
```

### With JSON Output
```bash
sqlite3 -json traces/v3/crafter_eval.db "YOUR_QUERY_HERE" | jq .
```

## Example: Get CSV Export of Non-Zero Rewards
```bash
sqlite3 -header -csv traces/v3/crafter_eval.db \
  "SELECT 
    json_extract(reward_metadata, '$.env_seed') as seed,
    total_reward,
    achievements_count,
    total_steps,
    json_extract(reward_metadata, '$.final_achievements') as achievements
   FROM outcome_rewards 
   WHERE total_reward > 0 
   ORDER BY total_reward DESC" \
  > crafter_rewards_nonzero.csv
```

## Current Data Summary

| Reward | Count | Seeds | Achievements |
|--------|-------|-------|--------------|
| 3 | 1 | 0 | collect_drink, collect_sapling, collect_wood |
| 2 | 4 | 1,3,6,9 | collect_sapling, collect_wood |
| 1 | 2 | 4,7 | collect_wood |
| 0 | 3 | 2,5,8 | none |

## Verifying Foreign Keys Work

```sql
-- This should return 7 rows (all rollouts with rewards > 0)
SELECT COUNT(*) 
FROM session_traces st
INNER JOIN outcome_rewards orw ON st.session_id = orw.session_id
WHERE orw.total_reward > 0;

-- This should return the same 7 session_ids
SELECT st.session_id 
FROM session_traces st
WHERE st.session_id IN (
  SELECT session_id FROM outcome_rewards WHERE total_reward > 0
);
```

✅ **Confirmed: Foreign keys are working correctly and can be used to join tables!**


