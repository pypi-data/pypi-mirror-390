# Gemini Model Selection Feature

## Overview
Added ability for users to select their preferred Gemini model during configuration setup based on their API access level.

## Changes Made

### 1. Updated `cli/main_cli.py`
- Added **Step 2** in config wizard for Gemini model selection
- Available models (updated with latest):
  - `gemini-2.5-flash` ⭐ **NEW - Latest model** (recommended)
  - `gemini-2.0-flash-exp` (experimental)
  - `gemini-1.5-flash` (fast, efficient)
  - `gemini-1.5-flash-8b` (lightweight)
  - `gemini-1.5-pro` (more capable)
  - `gemini-pro` (legacy)
- Supports both numeric selection (1-6) and model name input
- Allows custom model names if user wants to use a different version
- Shows current model and allows updates
- **Added to CONFIG_KEYS** dictionary for config-show display
- **Updated _resolve_credential()** to read model from config
- **Updated credential display** to show GEMINI_MODEL_NAME (unmasked)

### 2. Updated `config.py`
- Added `GEMINI_MODEL_NAME` as a dynamic property
- Loads from `config.json` > environment variable > default
- Default: `gemini-2.0-flash-exp`
- Automatically reloads when accessed if not set

### 3. Configuration Flow
**Old Flow:**
1. Gemini API Key
2. Preferred Language
3. Telegram (Optional)

**New Flow:**
1. Gemini API Key
2. **Gemini Model Selection** ← NEW
3. Preferred Language
4. Telegram (Optional)

## Usage

### For Users
```bash
# Run config wizard
python -m leetagent config

# Or during first-time setup
python -m leetagent setup
```

### Config File Location
Settings are saved to: `~/.leetagent/config.json`

Example config:
```json
{
  "GEMINI_API_KEY": "your-api-key-here",
  "GEMINI_MODEL_NAME": "gemini-1.5-flash",
  "PREFERRED_LANGUAGE": "Python",
  "TELEGRAM_TOKEN": "optional",
  "CHAT_ID": "optional"
}
```

### Programmatic Access
```python
from config import settings

# Get current model (auto-loads from config)
model = settings.GEMINI_MODEL_NAME

# Model will be used in AI agents
print(f"Using model: {model}")
```

## Benefits

1. **Flexibility**: Users can choose model based on their API tier
2. **Cost Control**: Select lighter models (flash-8b) for cost savings
3. **Performance**: Choose pro models when needed for complex problems
4. **Future-Proof**: Easy to add new models to the list
5. **Backward Compatible**: Defaults to `gemini-2.0-flash-exp` if not set

## Testing

Verify the feature works:
```bash
# Check current config
python -m leetagent config-show

# Update model only
python -m leetagent config-set GEMINI_MODEL_NAME gemini-1.5-flash

# Run full wizard
python -m leetagent config
```

## Next Steps for v1.0.6 Release

1. Test with different models
2. Update documentation
3. Bump version to 1.0.6
4. Build and publish to PyPI

---
**Date Added**: November 8, 2025  
**Version**: 1.0.6 (planned)
