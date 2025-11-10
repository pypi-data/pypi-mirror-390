# Version 1.0.6 - Update Summary

## 🎯 New Features

### 1. Gemini Model Selection
- Users can now choose their preferred Gemini model during configuration
- **6 models available**:
  1. `gemini-2.5-flash` ⭐ (Latest, recommended, set as default)
  2. `gemini-2.0-flash-exp` (Experimental)
  3. `gemini-1.5-flash` (Fast and efficient)
  4. `gemini-1.5-flash-8b` (Lightweight)
  5. `gemini-1.5-pro` (More capable)
  6. `gemini-pro` (Legacy)

- **How to use:**
  ```bash
  # Interactive selection during config wizard
  leetagent config
  
  # Direct setting
  leetagent config-set GEMINI_MODEL_NAME gemini-2.5-flash
  
  # View current model
  leetagent config-show
  ```

### 2. Fixed Paste Issue in secret-set Command
- **Problem:** Users couldn't paste API keys when using `leetagent secret-set`
- **Solution:** Removed `hide_input=True` and `confirmation_prompt=True` parameters
- **Now:** Users can easily paste their credentials when prompted

## 📝 Changes Made

### Code Changes

1. **cli/main_cli.py**
   - Added `GEMINI_MODEL_NAME` to `CONFIG_KEYS` dictionary
   - Added Step 2 in config wizard for model selection
   - Updated `_resolve_credential()` to read model from config
   - Updated credential display to show model (unmasked)
   - Fixed `secret-set` command to allow pasting
   - Excluded `GEMINI_MODEL_NAME` from secret keys (it's not sensitive)

2. **config.py**
   - Added `_gemini_model` instance variable in `_load_credentials()`
   - Created `GEMINI_MODEL_NAME` property with dynamic loading
   - Priority: config.json > environment > default (`gemini-2.5-flash`)
   - Removed static `GEMINI_MODEL_NAME` class variable

### Documentation Updates

3. **USER_GUIDE.md**
   - Added `GEMINI_MODEL_NAME` to configuration options
   - Added "Available Gemini Models" section with descriptions
   - Updated `config-set` examples to include model selection
   - Added tip about paste now working in `secret-set`
   - Clarified that paste is enabled when prompted

4. **GEMINI_MODEL_FEATURE.md** (New)
   - Comprehensive documentation of the feature
   - Usage examples and benefits
   - Testing instructions

## 🎨 User Experience Improvements

### Before (v1.0.5)
```
1️⃣  Gemini API Key
2️⃣  Preferred Coding Language  
3️⃣  Telegram Notifications (Optional)
```

### After (v1.0.6)
```
1️⃣  Gemini API Key
2️⃣  Gemini Model                    ← NEW!
   Available models:
     1. gemini-2.5-flash
     2. gemini-2.0-flash-exp
     3. gemini-1.5-flash
     4. gemini-1.5-flash-8b
     5. gemini-1.5-pro
     6. gemini-pro
3️⃣  Preferred Coding Language
4️⃣  Telegram Notifications (Optional)
```

### Config Display Enhancement
```
╭─── Current Configuration ───╮
│ Gemini API Key    │ ✅ │ AIza***wsOY      │
│ Gemini Model      │ ✅ │ gemini-2.5-flash │  ← NEW!
│ Preferred Language│ ✅ │ Python           │
│ Telegram Token    │ ✅ │ 8189***YHj8      │
╰─────────────────────────────╯
```

## ✅ Testing Performed

1. ✅ Config wizard shows model selection
2. ✅ Model saves to `~/.leetagent/config.json`
3. ✅ `config-show` displays selected model
4. ✅ Custom model names accepted (e.g., `gemini-2.5-flash`)
5. ✅ Paste works in `secret-set` command
6. ✅ Non-sensitive values (model, language) shown unmasked
7. ✅ `GEMINI_MODEL_NAME` excluded from `secret-set` (not a secret)

## 🚀 Ready for Release

**Version:** 1.0.6  
**Status:** Ready for PyPI upload  
**Breaking Changes:** None (backward compatible)

### Files Modified
- ✅ cli/main_cli.py
- ✅ config.py
- ✅ USER_GUIDE.md
- ✅ GEMINI_MODEL_FEATURE.md (new)

### Next Steps
1. Update version in `pyproject.toml`, `setup.py`, `leetagent/__init__.py`
2. Build package: `python -m build`
3. Upload to PyPI: `python -m twine upload dist/*`
4. Test installation: `pip install --upgrade leetagent`

---
**Date:** November 9, 2025  
**Author:** Satyam Yadav
