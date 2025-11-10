# Monorepo Release Strategy

This repository uses a monorepo approach with **two independent versions**:
- **API Version** (`v1.0.0`) - For FastAPI server & Docker images
- **Client Version** (`client-v0.1.0`) - For PyPI package

## How It Works

### 🔧 API Changes (Server, Dockerfile, Scripts)

**When you change:**
- `src/api/**`
- `Dockerfile*`
- `docker-compose*.yml`
- `scripts/**`

**What happens:**
1. Push to `main` triggers `release.yml`
2. **CI checks run first** (Black, isort, Flake8)
3. Path filter detects API changes
4. Semantic Release analyzes commits
5. Creates new version tag (e.g., `v1.2.0`)
6. Updates `CHANGELOG.md` and `pyproject.toml`
7. Creates GitHub Release
8. Docker Build workflow triggers on tag
9. Builds & pushes Docker image to GHCR

### 📦 Client Changes (PyPI Package)

**When you change:**
- `src/elli_api_client/**`
- `setup.py`

**What happens:**
1. Push to `main` triggers `release.yml`
2. **CI checks run first** (Black, isort, Flake8)
3. Path filter detects client changes
4. Semantic Release analyzes commits
5. Creates new version tag (e.g., `client-v0.2.0`)
6. Updates `src/elli_api_client/CHANGELOG.md`, `setup.py`, `__init__.py`
7. Creates GitHub Release
8. Builds Python package
9. Publishes to PyPI automatically

## Commit Message Format

Use [Conventional Commits](https://www.conventionalcommits.org/):

```bash
# Client changes → triggers client release
git commit -m "feat(client): add refresh token support"
git commit -m "fix(client): handle timeout errors"

# API changes → triggers API release
git commit -m "feat(api): add new charging endpoint"
git commit -m "fix(api): correct authentication middleware"

# Mixed changes → triggers BOTH releases
git commit -m "feat: add new feature for both API and client"

# No release
git commit -m "docs: update README"
git commit -m "chore: update dependencies"
```

### Scope Guide

| Scope | Triggers | Example |
|-------|----------|---------|
| `(client)` | Client release only | `feat(client): add retry logic` |
| `(api)` | API release only | `fix(api): correct CORS headers` |
| No scope | Both releases | `feat: add charging history` |
| `(docs)`, `(chore)` | No release | `docs: update guide` |

## Version Management

### Release Rules

**MAJOR** (Breaking changes):
```bash
git commit -m "feat!: change authentication method"
git commit -m "feat(client)!: remove deprecated methods"
```

**MINOR** (New features):
```bash
git commit -m "feat: add battery status endpoint"
git commit -m "feat(client): add async support"
```

**PATCH** (Bug fixes):
```bash
git commit -m "fix: handle null values correctly"
git commit -m "fix(client): fix timeout handling"
```

### Example Version History

```
API Releases:
v1.0.0 - Initial release
v1.1.0 - Added charging history endpoint
v1.1.1 - Fixed CORS issue
v2.0.0 - Breaking: Changed auth method

Client Releases:
client-v0.1.0 - Initial PyPI package
client-v0.2.0 - Added retry logic
client-v0.2.1 - Fixed timeout bug
client-v1.0.0 - Breaking: Async API
```

## Configuration Files

### Semantic Release Configs

- `.releaserc.api.json` - API version config (creates `v*` tags)
- `.releaserc.client.json` - Client version config (creates `client-v*` tags)

### Workflows

- `.github/workflows/release.yml` - Main release workflow with CI checks, path filtering, and releases
- `.github/workflows/docker-build.yml` - Triggers on `v*` tags (not `client-v*`)
- `.github/workflows/ci.yml` - Runs on PRs and feature branches

## Setup Requirements

### GitHub Secrets

Add in repo settings → Secrets and variables → Actions:
- `PYPI_API_TOKEN` - For publishing to PyPI (required for client releases)

### PyPI Account Setup

1. Create account at https://pypi.org
2. Enable 2FA
3. Create API token: Account Settings → API tokens
4. Add token as GitHub Secret: `PYPI_API_TOKEN`

## Local Testing

### Test Client Package Locally

```bash
# Build the package
pip install build twine
python -m build

# Check the package
twine check dist/*

# Install locally
pip install dist/elli_api_client-*.whl

# Test import
python -c "from elli_api_client import ElliAPIClient; print('OK')"
```

### Manual PyPI Upload (Emergency Only)

```bash
# Upload to TestPyPI first
twine upload --repository testpypi dist/*

# Test install from TestPyPI
pip install --index-url https://test.pypi.org/simple/ elli-api-client

# Upload to production PyPI
twine upload dist/*
```

## Usage in Home Assistant (HACS)

### In your HACS integration

**manifest.json:**
```json
{
  "domain": "elli",
  "name": "Elli Wallbox",
  "requirements": ["elli-api-client==0.2.0"],
  ...
}
```

**Install in Python:**
```python
# HACS automatically installs from PyPI
from elli_api_client import ElliAPIClient

client = ElliAPIClient()
token = await client.login("email@example.com", "password")
stations = await client.get_stations()
```

## CI Integration

### ✅ CI Checks Run First

Every push to `main` now:
1. **Runs CI checks first** (Black, isort, Flake8)
2. **If CI fails** → No releases are created
3. **If CI passes** → Continues with releases

This ensures broken code never gets released!

### CI on Feature Branches

The separate `ci.yml` workflow runs on:
- All pull requests to `main` or `dev`
- Direct pushes to `dev` or `feature/**` branches

## Troubleshooting

### "CI failed, no release created"

**Expected behavior!** If formatting or linting fails:
- Fix the issues locally
- Run `black .` and `isort .`
- Commit and push again

### "Both API and client released on same commit"

**Intended behavior!** If you change both API and client files in one commit:
- `release.yml` creates both `v1.2.0` and `client-v0.3.0`
- Both are valid and independent

### "Docker build triggered on client release"

Check `docker-build.yml` - it should exclude `client-v*` tags:
```yaml
tags:
  - "v*.*.*"
  - "!client-v*.*.*"
```

### "PyPI upload failed: Package already exists"

Semantic Release increments versions automatically. If it fails:
1. Check the last successful client release tag
2. Verify commit message follows conventional commits
3. Make sure changes are in `src/elli_api_client/**`

### "No release created"

Check if commit message triggers a release:
- `feat:` → MINOR release
- `fix:` → PATCH release
- `docs:`, `chore:`, `style:` → No release
- Must be on `main` branch
- Must not contain `[skip ci]`

## Benefits of This Setup

✅ **Independent versions** - API and Client evolve separately
✅ **Automatic** - Push to main triggers appropriate releases
✅ **Clean history** - Two separate changelogs
✅ **Flexible** - Change API without client release
✅ **Professional** - Proper semantic versioning
✅ **HACS-ready** - PyPI package for easy integration
✅ **Monorepo** - Single source of truth, no code duplication

## Migration Notes

### From Old Setup

If you're migrating from the previous single-version setup:

1. ✅ Old `release.yml` → Renamed to `release.yml.old`
2. ✅ Old `.releaserc.json` → Renamed to `.releaserc.json.old`
3. ✅ New `release-api.yml` and `release-client.yml` created
4. ✅ Docker workflow updated to ignore client tags

### Current State

- API Version: Check `pyproject.toml` → `version = "1.0.1"`
- Client Version: Check `setup.py` → `version="1.0.1"`
- Both will be bumped independently going forward

## Example Workflow

### Scenario 1: Client Bug Fix

```bash
# Fix bug in client
vim src/elli_api_client/client.py

# Commit with conventional commit
git add src/elli_api_client/client.py
git commit -m "fix(client): handle connection timeout properly"
git push origin main

# Result:
# ✅ New tag: client-v0.2.1
# ✅ PyPI: elli-api-client 0.2.1
# ❌ No API release
# ❌ No Docker build
```

### Scenario 2: API Feature

```bash
# Add new endpoint
vim src/api/routers/charging.py

# Commit
git add src/api/routers/charging.py
git commit -m "feat(api): add charging history endpoint"
git push origin main

# Result:
# ✅ New tag: v1.2.0
# ✅ Docker image: ghcr.io/.../elli-charge-api:v1.2.0
# ✅ GitHub Release
# ❌ No PyPI upload
```

### Scenario 3: Both Change

```bash
# Update client and API
vim src/elli_api_client/client.py
vim src/api/routers/charging.py

# Commit
git add .
git commit -m "feat: add real-time charging status"
git push origin main

# Result:
# ✅ API tag: v1.2.0 + Docker build
# ✅ Client tag: client-v0.2.0 + PyPI upload
# ✅ Two GitHub Releases
```

## Package URLs

After publishing:
- **PyPI**: https://pypi.org/project/elli-api-client/
- **Docker**: https://github.com/marcszy91/elli-charge-api/pkgs/container/elli-charge-api
- **GitHub**: https://github.com/marcszy91/elli-charge-api

---

**Need help?** Check the [Conventional Commits guide](https://www.conventionalcommits.org/) or [Semantic Release docs](https://semantic-release.gitbook.io/).
