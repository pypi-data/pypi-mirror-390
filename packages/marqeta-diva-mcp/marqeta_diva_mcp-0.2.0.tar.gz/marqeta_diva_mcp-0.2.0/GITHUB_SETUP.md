# GitHub Repository Setup Guide

Follow these steps to create and push your repository to GitHub.

## Step 1: Create GitHub Repository

### Option A: Using GitHub Web Interface (Recommended)

1. Go to https://github.com/new
2. Fill in the repository details:
   - **Owner:** zvika-finally
   - **Repository name:** marqeta-diva-mcp
   - **Description:** MCP server for Marqeta DiVA API - Data insights, Visualization, and Analytics
   - **Visibility:** Public (recommended for PyPI packages)
   - **DO NOT initialize** with README, .gitignore, or license (we already have these)
3. Click "Create repository"

### Option B: Using GitHub CLI (if installed)

```bash
gh repo create zvika-finally/marqeta-diva-mcp \
  --public \
  --description "MCP server for Marqeta DiVA API - Data insights, Visualization, and Analytics" \
  --source=. \
  --remote=origin
```

## Step 2: Push Code to GitHub

After creating the repository on GitHub, connect your local repository:

```bash
# Add GitHub as remote origin
git remote add origin https://github.com/zvika-finally/marqeta-diva-mcp.git

# Verify remote was added
git remote -v

# Make initial commit
git commit -m "Initial commit: Marqeta DiVA MCP Server v0.2.0

Features:
- Core DiVA API integration with all transaction, financial, and metadata tools
- Optional RAG features (local storage + semantic search)
- Built-in rate limiting and error handling
- Export to JSON/CSV
- Comprehensive documentation"

# Push to GitHub
git branch -M main
git push -u origin main
```

## Step 3: Verify on GitHub

1. Go to https://github.com/zvika-finally/marqeta-diva-mcp
2. Verify all files are present
3. Check that README displays correctly
4. Verify LICENSE shows MIT

## Step 4: Configure Repository Settings (Optional but Recommended)

### Add Topics

Go to repository homepage → Click gear icon next to "About" → Add topics:
- `marqeta`
- `diva-api`
- `mcp`
- `model-context-protocol`
- `python`
- `fintech`
- `api-client`
- `analytics`

### Set Description

In the same "About" section, add:
- **Description:** MCP server for Marqeta DiVA API - Data insights, Visualization, and Analytics
- **Website:** https://pypi.org/project/marqeta-diva-mcp/ (add this after publishing to PyPI)

## Step 5: Create Release (After Testing)

Once you've tested and are ready to publish:

```bash
# Create a tag for version 0.2.0
git tag -a v0.2.0 -m "Release v0.2.0 - Initial PyPI release"
git push origin v0.2.0
```

Then create a GitHub Release:
1. Go to https://github.com/zvika-finally/marqeta-diva-mcp/releases
2. Click "Create a new release"
3. Choose tag: v0.2.0
4. Release title: v0.2.0 - Initial Release
5. Add release notes:

```markdown
## 🎉 Initial Release

First public release of Marqeta DiVA MCP Server!

### Features

**Core Features:**
- 🔍 Transaction data access (authorizations, settlements, clearings, declines, loads)
- 💰 Financial data (program balances, settlement balances, activity balances)
- 💳 Card & user data with flexible filtering
- 🔄 Chargeback data access
- 📊 Metadata tools (view discovery, schema inspection)
- 📤 Export to JSON/CSV
- ⚡ Built-in rate limiting (300 requests/5 min)
- 🛡️ Comprehensive error handling

**Optional RAG Features:**
- 🗄️ Local SQLite storage (bypasses MCP token limits)
- 🔎 Semantic search with AI embeddings
- 📦 ChromaDB vector store integration
- 🚀 Offline analysis without API calls

### Installation

```bash
# Basic features
pip install marqeta-diva-mcp

# With RAG features
pip install marqeta-diva-mcp[rag]
```

### Documentation

- [README](https://github.com/zvika-finally/marqeta-diva-mcp#readme)
- [RAG Guide](https://github.com/zvika-finally/marqeta-diva-mcp/blob/main/RAG_GUIDE.md)
- [Publishing Guide](https://github.com/zvika-finally/marqeta-diva-mcp/blob/main/PUBLISHING.md)
- [PyPI Package](https://pypi.org/project/marqeta-diva-mcp/)

### Requirements

- Python 3.10+
- Marqeta DiVA API credentials
```

## Troubleshooting

### "Repository already exists"

If you get an error that the repository already exists:
1. Go to https://github.com/zvika-finally
2. Check if `marqeta-diva-mcp` already exists
3. Either delete it or use a different name

### Authentication Error

If you get authentication errors when pushing:

**Option 1: Use Personal Access Token**
1. Go to https://github.com/settings/tokens
2. Generate new token (classic)
3. Select scopes: `repo`, `workflow`
4. Use token as password when pushing

**Option 2: Use GitHub CLI**
```bash
gh auth login
# Follow prompts to authenticate
```

**Option 3: Use SSH**
```bash
# Add SSH remote instead
git remote remove origin
git remote add origin git@github.com:zvika-finally/marqeta-diva-mcp.git
```

### "Updates were rejected" Error

If remote has changes you don't have locally:
```bash
git pull origin main --rebase
git push -u origin main
```

## Quick Reference

```bash
# Check git status
git status

# View commit history
git log --oneline

# Check remote
git remote -v

# Push changes
git push

# Pull latest changes
git pull

# Create and push tag
git tag v0.2.0
git push origin v0.2.0
```

## Next Steps

After setting up GitHub:
1. ✅ Repository is created and pushed
2. ⏭️ Create PyPI and TestPyPI accounts
3. ⏭️ Generate API tokens
4. ⏭️ Install build tools
5. ⏭️ Build and publish package

See [PUBLISHING.md](PUBLISHING.md) for PyPI publishing instructions.
