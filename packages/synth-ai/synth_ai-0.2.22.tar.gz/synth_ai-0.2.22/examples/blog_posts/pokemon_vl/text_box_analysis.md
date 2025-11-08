# Pokemon Red Text Box Issue Analysis

## Problem Summary
The model is getting stuck in text boxes during evaluation, particularly at the starting position `Map26:(3,6)`.

## Key Findings

### Statistics
- **42 out of 76 states (55%)** have `text_box_active=True`
- **Position Map26:(3,6) is stuck 18 times** - this is the starting bedroom position
- The model does eventually escape text boxes, but it takes many steps (50+ steps)

### Visual Issue: Gray Block
- **Reported**: There's a weird gray block visible in the captured images
- **Possible causes**:
  1. PyBoy screen rendering artifact
  2. Text box background overlay (normal Game Boy behavior)
  3. Screen capture timing issue (captured during screen transition)
  4. RGBA→RGB conversion issue in `environment.py` line 295-296
  
**Investigation needed**: Check if gray block appears in:
- All images vs only text_box_active=True images
- Specific screen regions (bottom half = text box area?)
- Consistent across all steps or only certain states

### State Progression
```
Step   0: pos=Map26:(3,6)          text_box=True  reward=  0.00 map=38
Step  10: pos=Map26:(3,6)          text_box=True  reward=  0.02 map=38
Step  16: pos=Map26:(3,6)          text_box=True  reward=  0.02 map=38
...
Step  33: pos=Map26:(4,6)          text_box=True  reward=  0.04 map=38
Step  43: pos=Map26:(5,7)          text_box=True  reward=  0.10 map=38
Step  52: pos=Map26:(5,7)          text_box=False reward=  0.10 map=38  ← Finally escaped
```

### Observations

1. **Text box persists across multiple steps** - Even when the model presses B then A (as instructed), the text box doesn't advance immediately
2. **Position doesn't change when stuck** - The model is stuck at the same position (3,6) for many steps
3. **Reward stays low** - The model gets minimal reward (0.02-0.04) while stuck
4. **Eventually breaks free** - After ~50 steps, the model does escape and starts exploring

## Possible Causes

### 1. Game Environment Issue
- The text box might require a specific button sequence that the model isn't using
- There might be a timing issue - the model needs to wait longer between button presses
- The text box might be part of a multi-screen dialogue that requires multiple A presses

### 2. Model Behavior Issue
- The model might not be pressing buttons correctly (wrong duration/frames)
- The model might be pressing B too quickly after A, canceling the action
- The model might need to see the text box advance before understanding it worked

### 3. Reward Function Issue
- No reward for advancing text boxes means the model doesn't learn this is progress
- The model might not realize escaping the text box is beneficial

## Recommendations

### Immediate Fixes

1. **Add explicit reward for text box advancement**
   - Give small reward (+1-2 points) when `text_box_active` transitions from True to False
   - This signals to the model that escaping text boxes is progress

2. **Improve system prompt**
   - Be more explicit: "When text_box_active=True, you MUST press A multiple times (5-10 times) to advance through all dialogue screens"
   - Add: "Each dialogue screen requires pressing A. Continue pressing A until text_box_active becomes False"

3. **Increase button press duration**
   - Current: `{"button": "A", "frames": 10}` or `{"button": "A", "frames": 30}`
   - Try: `{"button": "A", "frames": 60}` to ensure the press registers

4. **Add loop detection**
   - If stuck at same position with text_box_active=True for 3+ turns, force a sequence of 10 A presses

### Longer-term Solutions

1. **Investigate game emulator behavior**
   - Check if the Pokemon Red emulator handles button presses correctly
   - Verify text box advancement logic

2. **Add visual feedback**
   - Show the model screenshots before/after text box advancement
   - Help it understand the visual change

3. **Pre-training on text box handling**
   - Create a simple reward for pressing A when text_box_active=True
   - Let the model learn this basic skill first

## Current Performance

- **Mean outcome score**: 0.010 (very low)
- **Official mean**: 0.500 (one seed succeeded, one failed)
- **Total reward**: 0.42-0.50 (milestones give 20-150 points each)
- **Steps taken**: 105-115 steps (but most spent stuck in text boxes)

## Next Steps

1. Add reward for text box advancement
2. Update system prompt to be more explicit about text box handling
3. Test with longer A button press durations
4. Consider adding loop detection to break out of stuck states

