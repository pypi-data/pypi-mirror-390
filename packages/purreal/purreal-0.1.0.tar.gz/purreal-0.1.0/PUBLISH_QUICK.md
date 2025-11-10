# Quick Publish to PyPI

## One-Command Publish (Windows)

```powershell
# 1. Clean, build, and upload
Remove-Item -Path "dist","build","*.egg-info" -Recurse -Force -ErrorAction SilentlyContinue; python -m build; python -m twine upload dist/*
```

## Step-by-Step

### 1. Update Version
```toml
# pyproject.toml
version = "0.1.0"  # Increment this!
```

### 2. Test Everything
```bash
pytest tests/
./test.bat connectivity
```

### 3. Clean & Build
```powershell
Remove-Item -Path "dist","build","*.egg-info" -Recurse -Force -ErrorAction SilentlyContinue
python -m build
```

### 4. Upload
```bash
python -m twine upload dist/*
```

**Credentials:**
- Username: `__token__`
- Password: `pypi-...` (your API token)

### 5. Verify
```bash
pip install --upgrade purreal
python -c "from purreal import SurrealDBConnectionPool; print('✓')"
```

### 6. Git Tag
```bash
git tag -a v0.1.0 -m "Release v0.1.0"
git push origin v0.1.0
```

## Setup PyPI Token (One-Time)

Create `~/.pypirc`:
```ini
[pypi]
username = __token__
password = pypi-YOUR_TOKEN_HERE
```

Get token: https://pypi.org/manage/account/token/

## Common Issues

**"File already exists"**
→ Increment version in `pyproject.toml`

**"Invalid credentials"**
→ Use `__token__` as username, ensure token starts with `pypi-`

**Import fails**
→ Check `purreal/__init__.py` exports correctly

---

See [PUBLISHING.md](PUBLISHING.md) for detailed guide.
