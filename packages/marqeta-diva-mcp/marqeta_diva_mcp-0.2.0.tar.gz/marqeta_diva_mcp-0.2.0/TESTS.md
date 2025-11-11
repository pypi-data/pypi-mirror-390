# Test Files Overview

This document explains the test files in this repository and how to use them.

## Test Files

### Core Tests (Keep for Production)

**`test_fixes_unit.py`** - Unit tests for key functionality
- Tests RAG feature availability checks
- Tests local storage and vector store initialization
- Mock-based tests (no API calls required)
- **Run with:** `python test_fixes_unit.py`

**`test_fixes.py`** - Integration tests
- Tests critical bug fixes
- Requires actual API credentials
- Tests date filtering, field validation, pagination
- **Run with:** `python test_fixes.py` (requires `.env` file)

**`test_rag.py`** - RAG feature tests
- Tests semantic search functionality
- Tests local storage sync
- Requires RAG dependencies (`pip install -e ".[rag]"`)
- Requires API credentials
- **Run with:** `ENABLE_LOCAL_STORAGE=true python test_rag.py`

### Debug/Development Tests (Optional)

These were used during development and debugging. They can be removed before publishing or kept in a separate `tests/debug/` directory:

- `test_api_url_format.py` - URL formatting tests
- `test_date_filtering.py` - Date filter validation
- `test_export_debug.py` - Export functionality debugging
- `test_field_validation.py` - Field validation tests
- `test_get_view_debug.py` - View endpoint debugging
- `test_index_debug.py` - Index operation debugging
- `test_pagination.py` - Pagination tests

## Running Tests

### Quick Test (No API Required)

```bash
python test_fixes_unit.py
```

### Full Test Suite (Requires API Credentials)

```bash
# Set up environment
cp .env.example .env
# Edit .env and add your credentials

# Run integration tests
python test_fixes.py

# Run RAG tests (if RAG features installed)
pip install -e ".[rag]"
ENABLE_LOCAL_STORAGE=true python test_rag.py
```

### With pytest (Future)

```bash
# Install pytest
pip install pytest

# Run all tests
pytest

# Run specific test file
pytest test_fixes_unit.py

# Run with coverage
pip install pytest-cov
pytest --cov=marqeta_diva_mcp --cov-report=html
```

## Test Organization Recommendations

For a cleaner structure, consider reorganizing:

```
tests/
├── __init__.py
├── unit/
│   ├── __init__.py
│   └── test_core.py           # From test_fixes_unit.py
├── integration/
│   ├── __init__.py
│   ├── test_api.py             # From test_fixes.py
│   └── test_rag.py             # From test_rag.py
└── debug/ (optional)
    ├── test_api_url_format.py
    ├── test_date_filtering.py
    └── ...other debug tests
```

## Creating New Tests

When adding new tests:

1. **Unit tests:** Test individual functions with mocks
2. **Integration tests:** Test API interactions (mark with `@pytest.mark.integration`)
3. **RAG tests:** Test local storage features (mark with `@pytest.mark.rag`)

Example structure:

```python
import pytest
from marqeta_diva_mcp.client import DiVAClient

class TestDiVAClient:
    @pytest.fixture
    def client(self):
        return DiVAClient("test_app", "test_access", "test_program")

    def test_client_initialization(self, client):
        assert client.app_token == "test_app"
        assert client.program == "test_program"

    @pytest.mark.integration
    def test_get_authorizations(self, client):
        result = client.get_view("authorizations", "detail", count=1)
        assert "records" in result
```

## Test Requirements

- **Python 3.10+**
- **For unit tests:** No additional requirements
- **For integration tests:** Valid Marqeta DiVA API credentials
- **For RAG tests:** RAG dependencies (`pip install -e ".[rag]"`)

## Continuous Integration (Future)

Consider setting up GitHub Actions:

`.github/workflows/tests.yml`:
```yaml
name: Tests

on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    strategy:
      matrix:
        python-version: ["3.10", "3.11", "3.12"]

    steps:
      - uses: actions/checkout@v3
      - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: ${{ matrix.python-version }}

      - name: Install dependencies
        run: |
          pip install -e ".[dev]"

      - name: Run unit tests
        run: |
          python test_fixes_unit.py

      # Integration tests would require secrets for API credentials
```

## Before Publishing

**Recommended cleanup:**
1. Keep: `test_fixes_unit.py`, `test_fixes.py`, `test_rag.py`
2. Move to `tests/` directory with proper pytest structure
3. Archive or remove debug test files
4. Add pytest configuration in `pyproject.toml`
5. Update `.gitignore` to exclude test artifacts

## Notes

- Integration tests require valid API credentials and will make real API calls
- RAG tests create local files (`transactions.db`, `chroma_db/`) - clean up after testing
- Debug tests were useful during development but aren't needed for production
- Consider adding test fixtures for common test data
