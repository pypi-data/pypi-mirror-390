# Publishing to PyPI Guide

This guide walks you through publishing the `marqeta-diva-mcp` package to PyPI.

## Prerequisites

### 1. Create PyPI Accounts

You'll need accounts on both TestPyPI (for testing) and PyPI (production).

**TestPyPI (for testing):**
- Go to https://test.pypi.org/account/register/
- Verify your email

**PyPI (production):**
- Go to https://pypi.org/account/register/
- Verify your email

### 2. Set Up API Tokens

API tokens are more secure than passwords and recommended for uploading packages.

**For TestPyPI:**
1. Go to https://test.pypi.org/manage/account/token/
2. Click "Add API token"
3. Name it (e.g., "marqeta-diva-mcp-upload")
4. Scope: "Entire account" (for first upload) or "Project: marqeta-diva-mcp" (after first upload)
5. Copy the token (starts with `pypi-`)
6. Save it securely - you won't see it again!

**For PyPI:**
1. Go to https://pypi.org/manage/account/token/
2. Follow same steps as TestPyPI
3. Save the token separately

### 3. Install Build Tools

```bash
pip install --upgrade build twine
```

## Before Publishing

### 1. Update Package Metadata

Edit `pyproject.toml` and update:

```toml
[project]
name = "marqeta-diva-mcp"
version = "0.2.0"  # Update this for each release
authors = [
    {name = "Your Name", email = "your.email@example.com"}  # UPDATE THIS
]

[project.urls]
Homepage = "https://github.com/yourusername/marqeta-diva-mcp"  # UPDATE THIS
Repository = "https://github.com/yourusername/marqeta-diva-mcp"  # UPDATE THIS
Issues = "https://github.com/yourusername/marqeta-diva-mcp/issues"  # UPDATE THIS
```

### 2. Update LICENSE

Edit `LICENSE` and replace `[Your Name]` with your actual name.

### 3. Clean Previous Builds

```bash
rm -rf dist/ build/ *.egg-info
```

## Publishing Steps

### Step 1: Build the Package

```bash
python -m build
```

This creates two files in `dist/`:
- `marqeta-diva-mcp-0.2.0.tar.gz` (source distribution)
- `marqeta_diva_mcp-0.2.0-py3-none-any.whl` (wheel distribution)

**Verify the build:**
```bash
ls -lh dist/
```

### Step 2: Test Upload to TestPyPI

Always test on TestPyPI first!

```bash
python -m twine upload --repository testpypi dist/*
```

**You'll be prompted for:**
- Username: `__token__`
- Password: Your TestPyPI token (paste the `pypi-...` token)

**Or configure once in `~/.pypirc`:**
```ini
[testpypi]
username = __token__
password = pypi-AgEIcHlwaS5vcmc... # Your TestPyPI token

[pypi]
username = __token__
password = pypi-AgEIcHlwaS5vcmc... # Your PyPI token
```

Then you can just run:
```bash
twine upload --repository testpypi dist/*
```

### Step 3: Test Installation from TestPyPI

```bash
# Test basic installation
pip install --index-url https://test.pypi.org/simple/ --no-deps marqeta-diva-mcp

# Test with RAG features
pip install --index-url https://test.pypi.org/simple/ marqeta-diva-mcp[rag]

# Note: --no-deps because dependencies might not be on TestPyPI
# For full test with dependencies, install deps separately first
```

**Verify it works:**
```bash
marqeta-diva-mcp --help
# Or
python -c "from marqeta_diva_mcp import __version__; print(__version__)"
```

### Step 4: Upload to Production PyPI

Once you've verified everything works on TestPyPI:

```bash
python -m twine upload dist/*
```

**You'll be prompted for:**
- Username: `__token__`
- Password: Your PyPI token

**Success!** Your package is now on PyPI: https://pypi.org/project/marqeta-diva-mcp/

### Step 5: Verify Production Installation

```bash
# In a new environment
pip install marqeta-diva-mcp

# With RAG features
pip install marqeta-diva-mcp[rag]

# Test it
marqeta-diva-mcp --help
```

## Common Issues & Solutions

### Issue: "File already exists"

**Cause:** You're trying to upload the same version again.

**Solution:**
- You cannot replace files on PyPI
- Bump the version in `pyproject.toml` (e.g., `0.2.0` → `0.2.1`)
- Rebuild and upload again

### Issue: "Invalid username or password"

**Cause:** Wrong token or username.

**Solution:**
- Make sure username is `__token__` (not your PyPI username)
- Paste the full token including the `pypi-` prefix
- Check you're using the right token (TestPyPI vs PyPI)

### Issue: Package name already taken

**Cause:** Someone else registered that name.

**Solution:**
- Choose a different name in `pyproject.toml`
- Try variations like `marqeta-diva-mcp-client`, `mqt-diva-mcp`, etc.

### Issue: Missing README or LICENSE

**Cause:** Files not included in build.

**Solution:**
- Make sure `README.md` exists
- Make sure `LICENSE` exists
- Check `pyproject.toml` has `readme = "README.md"`

### Issue: Import errors after installation

**Cause:** Package structure issues.

**Solution:**
- Make sure `src/marqeta_diva_mcp/__init__.py` exists
- Check that all Python files have proper imports
- Verify build with: `tar -tzf dist/marqeta-diva-mcp-*.tar.gz`

## Version Management

Follow semantic versioning (SemVer):

- **0.2.0** → **0.2.1**: Bug fixes, patches
- **0.2.0** → **0.3.0**: New features, backward compatible
- **0.2.0** → **1.0.0**: Major changes, breaking changes

**Before each release:**
1. Update version in `pyproject.toml`
2. Update `SERVER_VERSION` in `src/marqeta_diva_mcp/server.py`
3. Test thoroughly
4. Create git tag: `git tag v0.2.0 && git push --tags`
5. Build and upload

## Automation (Optional)

Consider automating releases with GitHub Actions:

**.github/workflows/publish.yml:**
```yaml
name: Publish to PyPI

on:
  release:
    types: [published]

jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - uses: actions/setup-python@v4
        with:
          python-version: '3.10'
      - name: Install dependencies
        run: |
          pip install build twine
      - name: Build package
        run: python -m build
      - name: Publish to PyPI
        env:
          TWINE_USERNAME: __token__
          TWINE_PASSWORD: ${{ secrets.PYPI_API_TOKEN }}
        run: twine upload dist/*
```

Add your PyPI token to GitHub repository secrets as `PYPI_API_TOKEN`.

## Quick Reference

```bash
# Clean
rm -rf dist/ build/ *.egg-info

# Build
python -m build

# Upload to TestPyPI
twine upload --repository testpypi dist/*

# Upload to PyPI
twine upload dist/*

# Install from TestPyPI
pip install --index-url https://test.pypi.org/simple/ marqeta-diva-mcp

# Install from PyPI
pip install marqeta-diva-mcp
```

## Resources

- **PyPI:** https://pypi.org/
- **TestPyPI:** https://test.pypi.org/
- **Python Packaging Guide:** https://packaging.python.org/
- **Twine Docs:** https://twine.readthedocs.io/

## Support

If you encounter issues:
1. Check the error message carefully
2. Consult the [Python Packaging Guide](https://packaging.python.org/)
3. Search [PyPI issue tracker](https://github.com/pypa/packaging-problems/issues)
4. Ask on [Python Packaging Discourse](https://discuss.python.org/c/packaging/)
