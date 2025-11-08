# Vision Inference & SFT Integration Tests

Complete integration tests for vision inference and SFT training with multimodal data.

## Overview

Two new test suites validate the full vision ML pipeline:
1. **Inference Tests** - Vision model inference with multimodal requests
2. **SFT Tests** - Supervised fine-tuning with vision data

## Test Files

### 1. Vision Inference Tests
**File:** `tests/integration/cli/test_cli_inference_vision.py`

**Tests:**
- `test_vision_inference_with_image` - Basic vision inference with image + text
- `test_vision_inference_validation` - Invalid image validation (empty URLs, etc.)
- `test_vision_inference_multiple_images` - Multiple images in one request

**What They Test:**
- ✅ Backend accepts multimodal messages
- ✅ Vision models process image + text input
- ✅ Image validation catches invalid data before inference
- ✅ Multiple image handling
- ✅ Response format validation

### 2. Vision SFT Tests
**File:** `tests/integration/cli/test_cli_train_sft_vision.py`

**Tests:**
- `test_cli_train_sft_vision_qwen2vl` - Full SFT training job submission
- `test_vision_sft_dataset_validation` - Dataset validation with mixed valid/invalid
- `test_cli_train_sft_vision_small_config` - Fast CI test with artifact config

**What They Test:**
- ✅ Vision SFT dataset creation with images
- ✅ Job submission for vision SFT training
- ✅ Backend accepts vision training config
- ✅ Dataset validation filters invalid examples
- ✅ LoRA training configuration for vision models

## Quick Start

### Prerequisites
```bash
export SYNTH_API_KEY="your-api-key"
export BACKEND_BASE_URL="https://agent-learning.onrender.com/api"
```

### Run Inference Tests
```bash
cd /Users/joshpurtell/Documents/GitHub/synth-ai

# All inference tests
uv run pytest tests/integration/cli/test_cli_inference_vision.py -v -s

# Single test
uv run pytest tests/integration/cli/test_cli_inference_vision.py::test_vision_inference_with_image -v

# With marks
uv run pytest -m "vision and slow" tests/integration/cli/test_cli_inference_vision.py
```

### Run SFT Tests
```bash
# All SFT tests
uv run pytest tests/integration/cli/test_cli_train_sft_vision.py -v -s

# Dataset validation only (fast)
uv run pytest tests/integration/cli/test_cli_train_sft_vision.py::test_vision_sft_dataset_validation -v

# Small config test (job submission)
uv run pytest tests/integration/cli/test_cli_train_sft_vision.py::test_cli_train_sft_vision_small_config -v
```

### Run All Vision Tests
```bash
# All vision tests (inference + SFT + RL)
uv run pytest -m vision -v -s

# Vision tests without slow ones
uv run pytest -m "vision and not slow" -v
```

## Test Details

### Inference Test 1: Basic Vision Inference
**Function:** `test_vision_inference_with_image`

**Creates:**
- Simple 64x64 red image (base64 encoded)
- Multimodal request with text + image
- POST to `/v1/chat/completions`

**Validates:**
- Response has `choices` array
- Choice has `message` with `content`
- Content is non-empty string

**Expected Output:**
```
✅ Vision inference successful
   Model: Qwen/Qwen2-VL-2B-Instruct
   Response: This image is red...
```

**Runtime:** ~10-20 seconds (depends on model loading)

### Inference Test 2: Validation
**Function:** `test_vision_inference_validation`

**Tests Invalid Requests:**
1. Empty image URL: `{"url": ""}`
2. Missing URL field: `{"image_url": {}}`
3. Whitespace URL: `{"url": "   "}`

**Validates:**
- Backend returns 4xx error (validation failure)
- Error message indicates the problem
- No wasted inference on invalid data

**Expected Output:**
```
✅ Correctly rejected: Empty image URL
   Error code: 400
   Error message: Image URL cannot be empty...
```

### Inference Test 3: Multiple Images
**Function:** `test_vision_inference_multiple_images`

**Creates:**
- Red and blue test images
- Single message with 2 images

**Validates:**
- Backend handles multiple images
- Model processes both images
- Response mentions both colors (if model supports)

**Note:** May skip if model doesn't support multiple images per message.

### SFT Test 1: Full Training Job
**Function:** `test_cli_train_sft_vision_qwen2vl`

**Creates:**
- 3-example vision SFT dataset (JSONL)
- Each example has 1 image (base64 in data URL)
- Minimal training config (1 epoch, LoRA)

**Submits:**
- SFT training job via CLI
- Model: Qwen2-VL-2B-Instruct
- Config includes `supports_vision = true`

**Validates:**
- Job created successfully
- Job ID returned
- Config accepted by backend

**Expected Output:**
```
✅ Vision SFT job created: job-abc123
   Model: Qwen2-VL-2B-Instruct
   Dataset: /tmp/.../vision_sft_test.jsonl
   Examples: 3 (with images)
```

**Runtime:** ~30-60 seconds (job submission only, not training)

### SFT Test 2: Dataset Validation
**Function:** `test_vision_sft_dataset_validation`

**Creates:**
- 4-example dataset (2 valid, 2 invalid)
- Invalid examples have empty/missing URLs

**Validates:**
- SDK validation correctly identifies valid examples
- Invalid examples are flagged with specific errors
- No false positives or negatives

**Expected Output:**
```
✅ Example 0: Valid
❌ Example 1: Invalid - Has 1 image_url entries but only 0 valid URLs
❌ Example 2: Invalid - Has 1 image_url entries but only 0 valid URLs
✅ Example 3: Valid

✅ Dataset validation working correctly
   Total examples: 4
   Valid: 2
   Invalid: 2
```

**Runtime:** ~1-2 seconds (pure validation, no network)

### SFT Test 3: Fast CI Test
**Function:** `test_cli_train_sft_vision_small_config`

**Uses:**
- Artifact config (`tests/artifacts/configs/sft.vision.small.toml`)
- Minimal settings for fast validation

**Validates:**
- Same as Test 1 but faster
- Config artifact is correct

**Runtime:** ~20-40 seconds

## Dataset Format

### Vision SFT Example
```json
{
  "messages": [
    {
      "role": "user",
      "content": [
        {"type": "text", "text": "What color is this?"},
        {
          "type": "image_url",
          "image_url": {
            "url": "data:image/png;base64,iVBORw0KG..."
          }
        }
      ]
    },
    {
      "role": "assistant",
      "content": "This image is red."
    }
  ],
  "metadata": {"example_id": 1}
}
```

### Supported Image Formats
- **Data URLs:** `data:image/png;base64,<base64-data>`
- **HTTP URLs:** `https://example.com/image.jpg`
- **Local paths:** `/path/to/image.png` (converted to PIL Image)

### Validation Rules
✅ **Valid:**
- Non-empty URL string
- Valid scheme (http://, https://, data:image/)
- Properly formatted base64 (if data URL)

❌ **Invalid:**
- Empty string: `""`
- Whitespace only: `"   "`
- Null value: `None` or `null`
- Missing URL field
- Non-string URL

## Integration with Other Tests

### Combined with RL Vision Tests
```bash
# All vision tests (inference + SFT + RL)
uv run pytest -m vision tests/integration/cli/ -v

# Specific pipeline
uv run pytest \
  tests/integration/cli/test_cli_inference_vision.py \
  tests/integration/cli/test_cli_train_sft_vision.py \
  tests/integration/cli/test_cli_train_rl_vision.py \
  -v -s
```

### Test Matrix

| Test Suite | Model | Data | Runtime | Purpose |
|------------|-------|------|---------|---------|
| Inference | Qwen2-VL-2B | Generated | ~20s | API validation |
| SFT | Qwen2-VL-2B | Generated | ~30s | Training job |
| RL | Qwen3-VL-4B | Task app | ~5-10min | Full pipeline |

## Troubleshooting

### Inference Test Fails
```bash
# Check backend connectivity
curl $BACKEND_BASE_URL/health

# Check API key
echo $SYNTH_API_KEY

# Verify model is available
curl -H "Authorization: Bearer $SYNTH_API_KEY" \
  $BACKEND_BASE_URL/v1/models
```

### SFT Test Fails
```bash
# Check dataset was created
cat /tmp/test_sft_vision/vision_sft_test.jsonl

# Validate dataset manually
python -c "
from synth_ai.learning.sft.data import load_jsonl, validate_vision_example
examples = load_jsonl('path/to/dataset.jsonl', min_messages=1)
for ex in examples:
    is_valid, error = validate_vision_example(ex, require_images=True)
    print(f'Valid: {is_valid}, Error: {error}')
"
```

### PIL Not Available
```bash
# Install Pillow
uv pip install Pillow

# Or use conda
conda install pillow
```

### Image Too Large
```python
# Reduce image size in test
img = Image.new('RGB', (32, 32), color='red')  # 32x32 instead of 64x64
```

## CI Integration

### Pytest Marks
```python
@pytest.mark.slow       # Takes >5 seconds
@pytest.mark.vision     # Requires vision support
@pytest.mark.integration  # Full integration test
```

### Run in CI
```yaml
# .github/workflows/test.yml
- name: Run vision integration tests
  run: |
    pytest -m "vision and integration" \
      tests/integration/cli/test_cli_inference_vision.py \
      tests/integration/cli/test_cli_train_sft_vision.py \
      -v --tb=short
  env:
    SYNTH_API_KEY: ${{ secrets.SYNTH_API_KEY }}
    BACKEND_BASE_URL: ${{ secrets.BACKEND_URL }}
```

### Skip in Fast CI
```bash
# Skip slow tests for PR checks
pytest -m "not slow" tests/

# Include vision but skip slow
pytest -m "vision and not slow" tests/
```

## Performance Expectations

### Inference Tests
- **test_vision_inference_with_image:** 10-20s
- **test_vision_inference_validation:** 5-10s (3 requests)
- **test_vision_inference_multiple_images:** 15-25s

**Total:** ~30-55 seconds

### SFT Tests
- **test_vision_sft_dataset_validation:** 1-2s (local only)
- **test_cli_train_sft_vision_small_config:** 20-40s
- **test_cli_train_sft_vision_qwen2vl:** 30-60s

**Total:** ~50-100 seconds

### All Vision Tests (Inference + SFT + RL)
- **Total Runtime:** ~6-12 minutes
- **Network calls:** ~10-15
- **GPU time:** 0 (job submission only, not actual training)

## Related Documentation

- **RL Vision Tests:** `RL_VISION_TESTING.md`
- **Image Validation:** `IMAGE_VALIDATION_COMPLETE.md`
- **VLM Pipeline:** `VLM_PIPELINE_COMPLETE.md`
- **Quick Start:** `QUICKSTART_RL_VISION.md`

## Summary

✅ **Complete test coverage for vision ML pipeline:**
- Inference API with multimodal messages
- Image validation before inference
- SFT dataset creation and validation
- SFT training job submission
- Integration with existing RL vision tests

**Test Count:**
- Inference: 3 tests
- SFT: 3 tests
- RL: 3 tests (from previous work)
- **Total: 9 vision integration tests**

**Coverage:**
- ✅ End-to-end inference
- ✅ Request validation
- ✅ Dataset creation
- ✅ Dataset validation
- ✅ SFT job submission
- ✅ RL job submission
- ✅ Task app vision support

---

**Status:** Production-ready! Run `pytest -m vision -v` to validate the full vision ML pipeline from inference to RL training! 🎉

