# SDK Vision Support Integration

**Status**: ✅ Complete

## Overview

Added comprehensive vision/multimodal support to the synth-ai SDK's SFT data module, and integrated it with the monorepo backend for consistent multimodal data handling across both codebases.

## Changes Made

### 1. **SDK Enhancement** (`synth-ai/synth_ai/learning/sft/data.py`)

Added vision-specific utilities to the SDK:

#### New Functions

1. **`has_image_content(content: SFTMessageContent) -> bool`**
   - Detects if message content contains images
   - Supports OpenAI multimodal format
   - Handles both `{"type": "image_url"}` and `{"type": "image"}` formats

2. **`message_has_image(message: SFTMessage) -> bool`**
   - Checks if an SFTMessage contains image content
   - Convenience wrapper around `has_image_content`

3. **`example_has_image(example: SFTExample) -> bool`**
   - Checks if any message in an SFTExample contains images
   - Used for filtering vision datasets

4. **`count_images_in_content(content: SFTMessageContent) -> int`**
   - Counts number of image segments in message content
   - Useful for statistics and validation

5. **`extract_image_urls(content: SFTMessageContent) -> list[str]`**
   - Extracts all image URLs from message content
   - Supports http(s):// URLs and data:image/... base64
   - Returns list of URL strings

6. **`validate_vision_example(example: SFTExample, *, require_images: bool = True) -> tuple[bool, str | None]`**
   - Comprehensive validation of vision SFT examples
   - Checks for image presence, URL validity
   - Returns `(is_valid, error_message)` tuple
   - Logs warnings for suspicious URLs

7. **`iter_vision_examples(...) -> Iterator[SFTExample]`**
   - Specialized iterator for vision examples
   - Includes vision-specific validation
   - Option to require images or skip invalid examples
   - Useful for processing large JSONL files

#### Example Usage

```python
from synth_ai.learning.sft.data import (
    load_jsonl,
    example_has_image,
    validate_vision_example,
    extract_image_urls
)

# Load and filter vision examples
examples = load_jsonl("vision_data.jsonl")
vision_examples = [ex for ex in examples if example_has_image(ex)]

# Validate each example
for ex in vision_examples:
    is_valid, error = validate_vision_example(ex)
    if not is_valid:
        print(f"Invalid: {error}")
    
    # Extract image URLs for inspection
    for msg in ex.messages:
        urls = extract_image_urls(msg.content)
        print(f"Images: {urls}")
```

### 2. **Backend Integration** (`monorepo/backend/.../training/sft/data.py`)

Updated the monorepo backend to use SDK utilities:

#### Changes

1. **Added SDK imports with fallback**:
   ```python
   try:
       from synth_ai.learning.sft.data import (
           has_image_content as sdk_has_image_content,
           example_has_image as sdk_example_has_image,
           validate_vision_example as sdk_validate_vision_example,
           # ... more imports
       )
       SDK_VISION_AVAILABLE = True
   except ImportError:
       SDK_VISION_AVAILABLE = False
       logger.warning("synth_ai SDK not available - vision support will be limited")
   ```

2. **Updated `SFTDataProcessor` docstring**:
   - Documents integration with SDK
   - Shows OpenAI multimodal format example
   - Explains fallback behavior

3. **Enhanced `_vision_message_has_image()` method**:
   - Uses SDK's `has_image_content()` when available
   - Falls back to local implementation if SDK unavailable
   - Ensures consistency between SDK and backend

4. **Enhanced `_validate_vision_examples()` method**:
   - Uses SDK's `coerce_example()` and `validate_vision_example()` for messages format
   - Provides comprehensive validation with detailed error messages
   - Falls back gracefully if SDK validation fails
   - Maintains backward compatibility with non-messages formats

## Supported Data Formats

### OpenAI Multimodal Format (Recommended)

```json
{
  "messages": [
    {
      "role": "system",
      "content": "You are a helpful assistant."
    },
    {
      "role": "user",
      "content": [
        {"type": "text", "text": "What's in this image?"},
        {"type": "image_url", "image_url": {"url": "data:image/png;base64,iVBORw0KGgo..."}}
      ]
    },
    {
      "role": "assistant",
      "content": "I see a cat sitting on a couch."
    }
  ],
  "metadata": {
    "session_id": "ep001",
    "has_image": true
  }
}
```

### Alternative Formats (Also Supported)

**Legacy image field**:
```json
{
  "messages": [...],
  "images": ["/path/to/image.jpg"],
  "metadata": {}
}
```

**Single image field**:
```json
{
  "messages": [...],
  "image": "https://example.com/image.jpg",
  "metadata": {}
}
```

## Image URL Formats

Supported image URL formats:

1. **HTTP(S) URLs**: `https://example.com/image.jpg`
2. **Data URLs (base64)**: `data:image/png;base64,iVBORw0KGgo...`
3. **Local file paths**: `/path/to/image.jpg` (for local training only)

## Validation Rules

The SDK validates:

1. **Image presence**: At least one message must contain an image (when `require_images=True`)
2. **URL format**: All image URLs must be non-empty strings
3. **URL scheme**: URLs should start with `http://`, `https://`, or `data:image/`
   - Warnings logged for non-standard formats
4. **Message structure**: Messages must follow OpenAI format

## Benefits

### 1. **Consistency**
- Single source of truth for vision data validation
- Both SDK and backend use the same logic
- Reduces bugs and maintenance burden

### 2. **Type Safety**
- Strong typing with dataclasses
- Clear SFTMessage and SFTExample structures
- IDE autocomplete and type checking

### 3. **Error Handling**
- Comprehensive validation with detailed error messages
- Graceful fallbacks if SDK unavailable
- Helpful warnings for edge cases

### 4. **OpenAI Compatibility**
- Matches OpenAI's fine-tuning format exactly
- Data can be used with OpenAI or local models
- Easy migration between platforms

### 5. **Tool Call Support**
- SDK already handles tool calls, tool definitions
- Ready for complex agentic workflows
- Supports reasoning blocks (`<think>` tags) if needed

## Testing

### Quick SDK Test

```python
# Test in synth-ai repo
from synth_ai.learning.sft.data import has_image_content, validate_vision_example, coerce_example
import json

# Test multimodal message detection
content = [
    {"type": "text", "text": "What's this?"},
    {"type": "image_url", "image_url": {"url": "data:image/png;base64,abc123"}}
]
assert has_image_content(content) == True

# Test validation
example_data = {
    "messages": [
        {"role": "user", "content": content},
        {"role": "assistant", "content": "A test image"}
    ]
}
example = coerce_example(example_data)
is_valid, error = validate_vision_example(example)
assert is_valid == True
print("✓ SDK vision utilities working correctly!")
```

### Integration Test

```python
# Test in monorepo backend
from backend.app.routes.simple_training.training.sft.data import SFTDataProcessor

processor = SFTDataProcessor()
test_data = [{
    "messages": [
        {"role": "user", "content": [
            {"type": "text", "text": "Describe this."},
            {"type": "image_url", "image_url": {"url": "data:image/png;base64,..."}}
        ]},
        {"role": "assistant", "content": "Description"}
    ]
}]

validated = processor._validate_vision_examples(test_data)
assert len(validated) == 1
print("✓ Backend SDK integration working!")
```

## Future Enhancements

### Potential Additions

1. **Image preprocessing utilities**
   - Resize images to model requirements
   - Validate image dimensions
   - Convert between formats (JPEG ↔ PNG)

2. **Base64 encoding helpers**
   - Convert file paths to data URLs
   - Batch encode images for JSONL
   - Memory-efficient streaming

3. **Statistics and analytics**
   - Count images per example
   - Measure average image sizes
   - Detect corrupted or invalid images

4. **Dataset transformation**
   - Convert between formats
   - Augment with additional images
   - Filter by image properties

## Migration Guide

### For Existing Backend Code

If you have existing vision validation code:

```python
# Before (manual validation)
def has_images(messages):
    for msg in messages:
        content = msg.get("content")
        if isinstance(content, list):
            for part in content:
                if part.get("type") == "image_url":
                    return True
    return False

# After (use SDK)
from synth_ai.learning.sft.data import has_image_content

def has_images(messages):
    return any(has_image_content(msg.get("content")) for msg in messages)
```

### For Existing SDK Code

No changes needed! The SDK already handles OpenAI message formats correctly. Vision utilities are additive and don't break existing functionality.

## Documentation

- **SDK docs**: See `synth_ai/learning/sft/data.py` docstrings
- **Backend docs**: See `backend/app/routes/simple_training/training/sft/data.py` class docstring
- **Examples**: See `synth-ai/examples/qwen_vl/` for vision-specific examples

## Related Files

- SDK: `synth-ai/synth_ai/learning/sft/data.py`
- Backend: `monorepo/backend/app/routes/simple_training/training/sft/data.py`
- Examples: `synth-ai/examples/qwen_vl/`
- Pipeline guide: `synth-ai/examples/qwen_vl/NEXT_STEPS_2B.md`

---

✅ **SDK vision support is now production-ready for both synth-ai and monorepo!**

