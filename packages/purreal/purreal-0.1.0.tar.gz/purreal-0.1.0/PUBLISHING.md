# Publishing Purreal to PyPI

Complete guide for publishing updates to https://pypi.org/project/purreal/

## Prerequisites

```bash
# Install build tools
pip install --upgrade build twine

# Ensure you have PyPI credentials
# Create ~/.pypirc or use environment variables
```

## Step-by-Step Publishing Guide

### 1. Update Version Number

Edit `pyproject.toml`:
```toml
version = "0.1.0"  # Increment this
```

**Version scheme:**
- `0.1.0` → `0.1.1` (patch - bug fixes)
- `0.1.0` → `0.2.0` (minor - new features)
- `0.1.0` → `1.0.0` (major - breaking changes)

### 2. Run Tests

**Critical:** Ensure all tests pass before publishing!

```bash
# Run all tests
pytest tests/

# Run connectivity test
./test.bat connectivity

# Run throughput benchmark
./test.bat throughput
```

All tests must pass ✅

### 3. Clean Previous Builds

```bash
# Remove old build artifacts
Remove-Item -Path "dist","build","*.egg-info" -Recurse -Force -ErrorAction SilentlyContinue
```

Or manually delete:
- `dist/`
- `build/`
- `purreal.egg-info/`

### 4. Build the Package

```bash
python -m build
```

This creates:
- `dist/purreal-0.1.0-py3-none-any.whl` (wheel)
- `dist/purreal-0.1.0.tar.gz` (source distribution)

**Verify build contents:**
```bash
# List files in wheel
python -m zipfile -l dist/purreal-0.1.0-py3-none-any.whl

# Extract and inspect tarball
tar -tzf dist/purreal-0.1.0.tar.gz
```

### 5. Test the Package Locally

```bash
# Install from local build
pip install dist/purreal-0.1.0-py3-none-any.whl

# Test import
python -c "from purreal import SurrealDBConnectionPool; print('✓ Import works')"

# Uninstall
pip uninstall purreal -y
```

### 6. Upload to Test PyPI (Optional)

**Test first to avoid mistakes:**

```bash
# Upload to TestPyPI
python -m twine upload --repository testpypi dist/*

# Install from TestPyPI
pip install --index-url https://test.pypi.org/simple/ purreal

# Test it works
python tests/test_connectivity.py
```

### 7. Upload to Production PyPI

**⚠️ This is permanent - you cannot delete or re-upload the same version!**

```bash
python -m twine upload dist/*
```

**You'll be prompted for:**
- Username: `__token__`
- Password: `pypi-...` (your PyPI API token)

**Or use API token directly:**
```bash
python -m twine upload --username __token__ --password pypi-YOUR_TOKEN_HERE dist/*
```

### 8. Verify Published Package

1. Check PyPI page: https://pypi.org/project/purreal/
2. Install from PyPI:
   ```bash
   pip install --upgrade purreal
   ```
3. Test it works:
   ```bash
   python -c "from purreal import SurrealDBConnectionPool; print(SurrealDBConnectionPool.__version__)"
   ```

### 9. Tag the Release (Git)

```bash
git tag -a v0.1.0 -m "Release version 0.1.0"
git push origin v0.1.0
```

### 10. Create GitHub Release

1. Go to https://github.com/dyleeeeeeee/purreal/releases
2. Click "Create a new release"
3. Select tag: `v0.1.0`
4. Title: `v0.1.0 - Production-Ready Release`
5. Add release notes (see template below)

## Release Notes Template

```markdown
## What's New in v0.1.0

### 🎉 Major Changes
- Fixed connection pool deadlock issue (#123)
- Improved high-throughput performance
- Reorganized package structure

### ✨ Features
- Added high-throughput benchmark suite
- Comprehensive performance testing guide
- Better error handling and recovery

### 🐛 Bug Fixes
- Fixed `reset_on_return` blocking issue
- Corrected parameter names in tests
- Fixed SurrealQL syntax compatibility

### 📚 Documentation
- Added PERFORMANCE_TESTING.md
- Restructured examples and benchmarks
- Improved README with usage examples

### 🔧 Breaking Changes
- Moved from `purreal.src` to `purreal` (update imports)
- Changed default `reset_on_return=False`

### 📦 Package Changes
- Version: 0.1a7 → 0.1.0 (stable)
- Status: Alpha → Beta
- Added keywords for better discoverability

## Installation

```bash
pip install --upgrade purreal
```

## Upgrading from 0.1a7

Update imports:
```python
# Old
from purreal.src.pooler import SurrealDBConnectionPool

# New
from purreal import SurrealDBConnectionPool
```

## Full Changelog
See https://github.com/dyleeeeeeee/purreal/compare/v0.1a7...v0.1.0
```

## PyPI API Token Setup

### Create API Token

1. Go to https://pypi.org/manage/account/token/
2. Click "Add API token"
3. Name: `purreal-upload`
4. Scope: "Project: purreal"
5. Copy token (starts with `pypi-`)

### Save Token Securely

**Option 1: `~/.pypirc`**
```ini
[pypi]
username = __token__
password = pypi-YOUR_TOKEN_HERE
```

**Option 2: Environment variable**
```bash
# Windows
set TWINE_PASSWORD=pypi-YOUR_TOKEN_HERE

# Linux/Mac
export TWINE_PASSWORD=pypi-YOUR_TOKEN_HERE
```

## Troubleshooting

### "File already exists"
- You cannot re-upload the same version
- Increment version in `pyproject.toml`
- Rebuild and upload

### "Invalid credentials"
- Use `__token__` as username
- Ensure token starts with `pypi-`
- Check token has correct scope

### "Package not found after upload"
- Wait 1-2 minutes for PyPI indexing
- Clear pip cache: `pip cache purge`
- Try again

### "Import fails after install"
- Check package structure is correct
- Verify `purreal/__init__.py` exists
- Test local build first

## Quick Command Reference

```bash
# Complete publish workflow
Remove-Item -Path "dist","build","*.egg-info" -Recurse -Force -ErrorAction SilentlyContinue
python -m build
python -m twine upload dist/*
pip install --upgrade purreal
```

## Pre-Release Checklist

- [ ] All tests pass (`pytest tests/`)
- [ ] Connectivity test passes (`./test.bat connectivity`)
- [ ] Version bumped in `pyproject.toml`
- [ ] CHANGELOG updated (if exists)
- [ ] README accurate
- [ ] No sensitive data in code
- [ ] `dist/` cleaned
- [ ] Built successfully
- [ ] Tested local install
- [ ] (Optional) Tested on TestPyPI

## Post-Release Checklist

- [ ] Package appears on PyPI
- [ ] Can install with `pip install purreal`
- [ ] Import works correctly
- [ ] Git tag created
- [ ] GitHub release published
- [ ] Announced (if significant release)

---

**Current Version:** 0.1.0  
**PyPI:** https://pypi.org/project/purreal/  
**GitHub:** https://github.com/dyleeeeeeee/purreal
