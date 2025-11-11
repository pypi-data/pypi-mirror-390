# Quick Start Guide - Publishing to PyPI with UV

This is your streamlined guide to publish `marqeta-diva-mcp` to PyPI using `uv`.

## ✅ Already Completed

- [x] Updated author info (Zvika Badalov)
- [x] Updated LICENSE (MIT)
- [x] Updated GitHub URLs
- [x] Initialized git repository
- [x] Polished README.md
- [x] Installed build tools (`build` and `twine`)

## 🚀 Next Steps

### Step 1: Create GitHub Repository (5 minutes)

**Option A: Web Interface (Easiest)**

1. Open: https://github.com/new
2. Fill in:
   - Owner: `zvika-finally`
   - Repository name: `marqeta-diva-mcp`
   - Description: "MCP server for Marqeta DiVA API - Data insights, Visualization, and Analytics"
   - Visibility: **Public**
   - Do NOT initialize with README/license
3. Click "Create repository"

**Then push your code:**

```bash
# Add remote
git remote add origin https://github.com/zvika-finally/marqeta-diva-mcp.git

# Commit and push
git commit -m "Initial commit: Marqeta DiVA MCP Server v0.2.0"
git push -u origin main
```

**Verify:** Visit https://github.com/zvika-finally/marqeta-diva-mcp

---

### Step 2: Create PyPI Accounts (10 minutes)

**2a. TestPyPI (for testing):**
- Register: https://test.pypi.org/account/register/
- Email: zvika.badalov@finally.com
- ✅ Verify your email

**2b. PyPI (production):**
- Register: https://pypi.org/account/register/
- Email: zvika.badalov@finally.com
- ✅ Verify your email

**Tip:** Use the same username for both!

---

### Step 3: Generate API Tokens (5 minutes)

**3a. TestPyPI Token:**
1. Login to TestPyPI
2. Visit: https://test.pypi.org/manage/account/token/
3. Click "Add API token"
4. Name: `marqeta-diva-mcp-upload`
5. Scope: "Entire account"
6. **Copy the token** (starts with `pypi-`)
7. Save it securely!

**3b. PyPI Token:**
1. Login to PyPI
2. Visit: https://pypi.org/manage/account/token/
3. Click "Add API token"
4. Name: `marqeta-diva-mcp-upload`
5. Scope: "Entire account"
6. **Copy the token** (starts with `pypi-`)
7. Save it securely (different from TestPyPI)!

**3c. Configure tokens (recommended):**

```bash
# Create ~/.pypirc
cat > ~/.pypirc << 'EOF'
[distutils]
index-servers =
    pypi
    testpypi

[testpypi]
repository = https://test.pypi.org/legacy/
username = __token__
password = pypi-YOUR-TESTPYPI-TOKEN-HERE

[pypi]
repository = https://upload.pypi.org/legacy/
username = __token__
password = pypi-YOUR-PYPI-TOKEN-HERE
EOF

# Secure the file
chmod 600 ~/.pypirc
```

Replace `pypi-YOUR-TESTPYPI-TOKEN-HERE` and `pypi-YOUR-PYPI-TOKEN-HERE` with your actual tokens!

---

### Step 4: Build the Package (1 minute)

```bash
# Clean previous builds
rm -rf dist/ build/ *.egg-info

# Build with uv
uv run pyproject-build

# Verify
ls -lh dist/
```

**Expected output:**
```
dist/marqeta-diva-mcp-0.2.0.tar.gz
dist/marqeta_diva_mcp-0.2.0-py3-none-any.whl
```

---

### Step 5: Test on TestPyPI (3 minutes)

```bash
# Upload to TestPyPI
twine upload --repository testpypi dist/*
```

**If you configured ~/.pypirc:** It uploads automatically
**If not:** Enter `__token__` as username and paste your TestPyPI token

**Test installation:**
```bash
pip install --index-url https://test.pypi.org/simple/ --no-deps marqeta-diva-mcp
python -c "from marqeta_diva_mcp import __version__; print(__version__)"
```

**Expected:** `0.2.0`

---

### Step 6: Publish to PyPI (2 minutes)

If TestPyPI worked, publish to production:

```bash
# Upload to PyPI
twine upload dist/*
```

**Success!** 🎉

Your package is now live at: https://pypi.org/project/marqeta-diva-mcp/

---

### Step 7: Verify Installation (1 minute)

```bash
# Test basic installation
pip install marqeta-diva-mcp
marqeta-diva-mcp --help

# Test with RAG features
pip install marqeta-diva-mcp[rag]
```

---

### Step 8: Create GitHub Release (3 minutes)

1. Visit: https://github.com/zvika-finally/marqeta-diva-mcp/releases
2. Click "Create a new release"
3. Tag: `v0.2.0`
4. Title: `v0.2.0 - Initial Release`
5. Description:

```markdown
## 🎉 Initial Release

First public release of Marqeta DiVA MCP Server!

### Features

**Core Features:**
- Transaction data access (authorizations, settlements, clearings, declines, loads)
- Financial data (program balances, settlement balances, activity balances)
- Card & user data with flexible filtering
- Chargeback data access
- Metadata tools (view discovery, schema inspection)
- Export to JSON/CSV
- Built-in rate limiting
- Comprehensive error handling

**Optional RAG Features:**
- Local SQLite storage (bypasses MCP token limits)
- Semantic search with AI embeddings
- ChromaDB vector store integration
- Offline analysis without API calls

### Installation

```bash
# Basic features
pip install marqeta-diva-mcp

# With RAG features
pip install marqeta-diva-mcp[rag]
```

### Links

- [PyPI Package](https://pypi.org/project/marqeta-diva-mcp/)
- [Documentation](https://github.com/zvika-finally/marqeta-diva-mcp#readme)
```

6. Click "Publish release"

---

## 🎉 Done!

Your package is now published! Users can install it with:

```bash
pip install marqeta-diva-mcp
```

---

## Quick Command Reference (UV Style)

```bash
# Build
rm -rf dist/ build/ *.egg-info
uv run pyproject-build

# Upload to TestPyPI
twine upload --repository testpypi dist/*

# Upload to PyPI
twine upload dist/*

# Test install
pip install --index-url https://test.pypi.org/simple/ --no-deps marqeta-diva-mcp
pip install marqeta-diva-mcp
```

---

## Troubleshooting

**"Invalid username or password"**
- Username must be `__token__` (not your PyPI username)
- Password is your full API token (starts with `pypi-`)

**"File already exists"**
- You can't re-upload the same version
- Bump version in `pyproject.toml` (0.2.0 → 0.2.1)
- Rebuild and upload again

**"Package name taken"**
- Try a different name like `marqeta-diva-client`
- Update in `pyproject.toml` and rebuild

---

## Future Updates

For version 0.3.0 and beyond:

```bash
# 1. Update version in pyproject.toml
# 2. Update SERVER_VERSION in src/marqeta_diva_mcp/server.py
# 3. Commit and tag
git commit -m "Release v0.3.0"
git tag v0.3.0
git push && git push --tags

# 4. Build and upload
rm -rf dist/ && uv run pyproject-build && twine upload dist/*
```

---

## Need More Help?

- **Detailed Guide:** [SETUP_CHECKLIST.md](SETUP_CHECKLIST.md)
- **GitHub Setup:** [GITHUB_SETUP.md](GITHUB_SETUP.md)
- **Publishing Details:** [PUBLISHING.md](PUBLISHING.md)

Good luck! 🚀
