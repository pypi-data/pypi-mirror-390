# Complete Setup Checklist for PyPI Publishing

This is your step-by-step checklist to get your package published to PyPI.

## ✅ Completed Steps

- [x] Updated author information (Zvika Badalov, zvika.badalov@finally.com)
- [x] Updated LICENSE with MIT and correct name
- [x] Updated GitHub URLs in pyproject.toml
- [x] Initialized git repository
- [x] Completed and polished README.md
- [x] Organized test files and created TESTS.md

## 🚀 Remaining Steps

### Step 1: Create GitHub Repository

Follow the guide in **[GITHUB_SETUP.md](GITHUB_SETUP.md)**

**Quick steps:**
1. Go to https://github.com/new
2. Repository name: `marqeta-diva-mcp`
3. Owner: `zvika-finally`
4. Description: "MCP server for Marqeta DiVA API - Data insights, Visualization, and Analytics"
5. Public repository
6. **Do NOT** initialize with README/license (we have them)
7. Click "Create repository"

Then run:
```bash
git remote add origin https://github.com/zvika-finally/marqeta-diva-mcp.git
git commit -m "Initial commit: Marqeta DiVA MCP Server v0.2.0"
git push -u origin main
```

**Verify:** https://github.com/zvika-finally/marqeta-diva-mcp

---

### Step 2: Create PyPI Accounts

#### 2a. TestPyPI Account (for testing)

1. Go to: https://test.pypi.org/account/register/
2. Fill in:
   - Username: (choose a username)
   - Email: zvika.badalov@finally.com
   - Password: (choose a secure password)
3. Click "Create account"
4. **IMPORTANT:** Check your email and verify your account
5. Save your credentials securely

#### 2b. PyPI Account (production)

1. Go to: https://pypi.org/account/register/
2. Fill in:
   - Username: (use the same username as TestPyPI)
   - Email: zvika.badalov@finally.com
   - Password: (choose a secure password - can be different from TestPyPI)
3. Click "Create account"
4. **IMPORTANT:** Check your email and verify your account
5. Save your credentials securely

**Security Tip:** Use a password manager to store these credentials!

---

### Step 3: Generate API Tokens

API tokens are more secure than passwords for uploading packages.

#### 3a. TestPyPI Token

1. Log in to TestPyPI
2. Go to: https://test.pypi.org/manage/account/token/
3. Click "Add API token"
4. Fill in:
   - Token name: `marqeta-diva-mcp-upload`
   - Scope: "Entire account" (for first upload)
5. Click "Add token"
6. **CRITICAL:** Copy the token immediately (starts with `pypi-`)
7. You will NOT see it again!
8. Save it in a secure location

**Save your token:**
```bash
# Option 1: Save to a file (secure it!)
echo "pypi-YOUR-TOKEN-HERE" > ~/.testpypi-token
chmod 600 ~/.testpypi-token

# Option 2: Save to your password manager
```

#### 3b. PyPI Token

1. Log in to PyPI
2. Go to: https://pypi.org/manage/account/token/
3. Click "Add API token"
4. Fill in:
   - Token name: `marqeta-diva-mcp-upload`
   - Scope: "Entire account" (for first upload)
5. Click "Add token"
6. **CRITICAL:** Copy the token immediately (starts with `pypi-`)
7. You will NOT see it again!
8. Save it in a secure location (different from TestPyPI token)

**Save your token:**
```bash
# Option 1: Save to a file (secure it!)
echo "pypi-YOUR-TOKEN-HERE" > ~/.pypi-token
chmod 600 ~/.pypi-token

# Option 2: Save to your password manager
```

#### 3c. Configure ~/.pypirc (Recommended)

This lets you avoid entering tokens each time:

```bash
# Create the file
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

**Replace:**
- `pypi-YOUR-TESTPYPI-TOKEN-HERE` with your actual TestPyPI token
- `pypi-YOUR-PYPI-TOKEN-HERE` with your actual PyPI token

---

### Step 4: Install Build Tools

```bash
# Install build and twine packages
pip install --upgrade build twine

# Verify installation
python -m build --version
twine --version
```

**Expected output:**
```
build 1.0.x
twine version x.x.x
```

---

### Step 5: Build the Package

```bash
# Clean any previous builds
rm -rf dist/ build/ *.egg-info

# Build the package
python -m build

# Verify the build
ls -lh dist/
```

**Expected output:**
```
dist/
├── marqeta-diva-mcp-0.2.0.tar.gz      (source distribution)
└── marqeta_diva_mcp-0.2.0-py3-none-any.whl  (wheel)
```

---

### Step 6: Upload to TestPyPI (Test First!)

```bash
# Upload to TestPyPI
python -m twine upload --repository testpypi dist/*
```

**If you configured ~/.pypirc:**
- It should upload automatically

**If you didn't configure ~/.pypirc:**
- Username: `__token__`
- Password: (paste your TestPyPI token)

**Expected output:**
```
Uploading distributions to https://test.pypi.org/legacy/
Uploading marqeta_diva_mcp-0.2.0-py3-none-any.whl
100% ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Uploading marqeta-diva-mcp-0.2.0.tar.gz
100% ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

View at:
https://test.pypi.org/project/marqeta-diva-mcp/0.2.0/
```

---

### Step 7: Test Installation from TestPyPI

```bash
# Create a test environment (optional but recommended)
python -m venv test_env
source test_env/bin/activate  # On Windows: test_env\Scripts\activate

# Test basic installation
pip install --index-url https://test.pypi.org/simple/ --no-deps marqeta-diva-mcp

# Test it works
python -c "from marqeta_diva_mcp import __version__; print(__version__)"
marqeta-diva-mcp --help

# Clean up
deactivate
rm -rf test_env
```

**If everything works, proceed to production!**

---

### Step 8: Upload to Production PyPI

```bash
# Upload to PyPI
python -m twine upload dist/*
```

**If you configured ~/.pypirc:**
- It should upload automatically

**If you didn't configure ~/.pypirc:**
- Username: `__token__`
- Password: (paste your PyPI token)

**Expected output:**
```
Uploading distributions to https://upload.pypi.org/legacy/
Uploading marqeta_diva_mcp-0.2.0-py3-none-any.whl
100% ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Uploading marqeta-diva-mcp-0.2.0.tar.gz
100% ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

View at:
https://pypi.org/project/marqeta-diva-mcp/0.2.0/
```

---

### Step 9: Verify Production Installation

```bash
# In a fresh environment
pip install marqeta-diva-mcp

# Test it works
marqeta-diva-mcp --help
python -c "from marqeta_diva_mcp import __version__; print(__version__)"

# Test with RAG features
pip install marqeta-diva-mcp[rag]
```

---

### Step 10: Create GitHub Release

1. Go to: https://github.com/zvika-finally/marqeta-diva-mcp/releases
2. Click "Create a new release"
3. Tag version: `v0.2.0`
4. Release title: `v0.2.0 - Initial Release`
5. Copy release notes from **[GITHUB_SETUP.md](GITHUB_SETUP.md)**
6. Click "Publish release"

---

## 🎉 Success Checklist

After completing all steps, verify:

- [ ] GitHub repository is live and accessible
- [ ] Package is on TestPyPI: https://test.pypi.org/project/marqeta-diva-mcp/
- [ ] Package is on PyPI: https://pypi.org/project/marqeta-diva-mcp/
- [ ] Can install with: `pip install marqeta-diva-mcp`
- [ ] Can install with RAG: `pip install marqeta-diva-mcp[rag]`
- [ ] README displays correctly on PyPI
- [ ] GitHub release is created with tag v0.2.0
- [ ] All badges in README work

---

## Quick Command Reference

```bash
# Build
rm -rf dist/ build/ *.egg-info && python -m build

# Upload to TestPyPI
twine upload --repository testpypi dist/*

# Upload to PyPI
twine upload dist/*

# Test install from TestPyPI
pip install --index-url https://test.pypi.org/simple/ --no-deps marqeta-diva-mcp

# Test install from PyPI
pip install marqeta-diva-mcp
```

---

## Troubleshooting

### "Repository already exists" on GitHub
- Check if you already created it
- Use a different name or delete the existing one

### "Invalid username or password" on PyPI
- Username must be `__token__` (not your PyPI username)
- Password is your API token (starts with `pypi-`)
- Check you're using the right token (TestPyPI vs PyPI)

### "File already exists" on PyPI
- You cannot re-upload the same version
- Bump version in `pyproject.toml` (e.g., 0.2.0 → 0.2.1)
- Rebuild and upload again

### Package name taken
- Try: `marqeta-diva-mcp-client`, `mqt-diva-mcp`, etc.
- Update name in `pyproject.toml` and rebuild

---

## Need Help?

- **Full Publishing Guide:** [PUBLISHING.md](PUBLISHING.md)
- **GitHub Setup:** [GITHUB_SETUP.md](GITHUB_SETUP.md)
- **Test Information:** [TESTS.md](TESTS.md)
- **Python Packaging:** https://packaging.python.org/
- **PyPI Help:** https://pypi.org/help/

---

## Next Time (for version 0.3.0)

After your first release, updates are easier:

```bash
# 1. Make changes to your code
# 2. Update version in pyproject.toml
# 3. Update SERVER_VERSION in server.py
# 4. Commit and push to GitHub
git commit -m "Release v0.3.0"
git tag v0.3.0
git push && git push --tags

# 5. Build and upload
rm -rf dist/ && python -m build && twine upload dist/*
```

Good luck! 🚀
