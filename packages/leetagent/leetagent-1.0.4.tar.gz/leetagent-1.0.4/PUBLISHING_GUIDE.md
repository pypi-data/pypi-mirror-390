# 📦 PyPI Publishing Guide for LeetAgent

## ✅ Pre-Publishing Checklist (DONE!)

- [x] LICENSE file created (MIT)
- [x] .gitignore configured
- [x] pyproject.toml updated with correct email
- [x] GitHub URLs updated
- [x] README.md ready
- [x] All required files present

## 🚀 Steps to Publish on PyPI

### Step 1: Install Build Tools

```powershell
pip install --upgrade build twine
```

### Step 2: Clean Previous Builds

```powershell
# Remove old build artifacts
if (Test-Path "dist") { Remove-Item "dist" -Recurse -Force }
if (Test-Path "build") { Remove-Item "build" -Recurse -Force }
if (Test-Path "*.egg-info") { Remove-Item "*.egg-info" -Recurse -Force }
```

### Step 3: Build the Package

```powershell
# Build distribution packages
python -m build
```

This will create:
- `dist/leetagent-1.0.0-py3-none-any.whl`
- `dist/leetagent-1.0.0.tar.gz`

### Step 4: Create PyPI Account (If Not Done)

1. Go to https://pypi.org/account/register/
2. Create account and verify email
3. Go to https://pypi.org/manage/account/token/
4. Create API token with name "leetagent-upload"
5. Save the token (starts with `pypi-`)

### Step 5: Test on TestPyPI First (Recommended)

```powershell
# Upload to TestPyPI first
python -m twine upload --repository testpypi dist/*
```

When prompted:
- Username: `__token__`
- Password: `your-test-pypi-token`

Test installation:
```powershell
pip install --index-url https://test.pypi.org/simple/ --extra-index-url https://pypi.org/simple/ leetagent
```

### Step 6: Upload to Real PyPI

```powershell
# Upload to PyPI
python -m twine upload dist/*
```

When prompted:
- Username: `__token__`
- Password: `your-pypi-token`

### Step 7: Verify Installation

```powershell
# Install from PyPI
pip install leetagent

# Test it works
leetagent --help
leetagent config-show
```

## 🔄 For Future Updates

When releasing new versions:

1. Update version in `pyproject.toml`:
   ```toml
   version = "1.0.1"  # or 1.1.0, 2.0.0, etc.
   ```

2. Clean, build, and upload again:
   ```powershell
   # Clean
   Remove-Item dist -Recurse -Force -ErrorAction SilentlyContinue
   
   # Build
   python -m build
   
   # Upload
   python -m twine upload dist/*
   ```

## 📝 Quick Command Reference

```powershell
# One-liner to publish (after first time setup)
Remove-Item dist -Recurse -Force -ErrorAction SilentlyContinue; python -m build; python -m twine upload dist/*
```

## ⚠️ Important Notes

1. **Never commit .env files** - Already in .gitignore
2. **API tokens are secret** - Don't share them
3. **Can't delete from PyPI** - Only deprecate versions
4. **Test first on TestPyPI** - To catch issues
5. **Semantic versioning** - Use MAJOR.MINOR.PATCH format

## 🎯 Package URLs After Publishing

- PyPI Page: https://pypi.org/project/leetagent/
- Installation: `pip install leetagent`
- Upgrade: `pip install --upgrade leetagent`

## 📞 Support

If publishing fails:
- Check package name isn't taken: https://pypi.org/project/leetagent/
- Verify all files are included in `MANIFEST.in`
- Check `pyproject.toml` for syntax errors
- Ensure version number is unique

---

**Ready to publish! 🚀**

Run the commands in order, and your package will be live on PyPI!
