# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

**Marqeta DiVA MCP Server** - A Model Context Protocol (MCP) server providing programmatic access to Marqeta's DiVA (Data insights, Visualization, and Analytics) API. The server enables AI assistants to retrieve aggregated production data for reporting, analytics, and data-driven business decisions.

**Key Technologies:**
- Python 3.10+ with `uv` package manager
- MCP (Model Context Protocol) for AI assistant integration
- httpx for HTTP client
- SQLite for local transaction storage (optional, requires `[rag]` extras)
- ChromaDB for vector embeddings (optional, requires `[rag]` extras)
- sentence-transformers for semantic search (optional, requires `[rag]` extras)

## Common Commands

### Development Setup
```bash
# Install basic dependencies
pip install -e .

# Install with RAG features (optional)
pip install -e ".[rag]"

# Run the server locally
uvx marqeta-diva-mcp
# OR
python -m marqeta_diva_mcp.server
```

### Enabling Optional Features

**RAG Features (local storage + semantic search):**
```bash
# 1. Install dependencies
pip install marqeta-diva-mcp[rag]

# 2. Enable in environment
export ENABLE_LOCAL_STORAGE=true

# 3. Verify in logs
# You should see: "[MCP Server] Local storage and RAG features ENABLED"
```

### Testing
```bash
# Run specific test files
python test_rag.py              # Test RAG/semantic search features
python test_pagination.py       # Test pagination and large datasets
python test_date_filtering.py   # Test date filtering
python test_fixes.py           # Integration tests for key fixes
python test_fixes_unit.py      # Unit tests
```

### Code Quality
```bash
# Format code
black src/

# Lint code
ruff check src/
```

### Environment Configuration
Required environment variables in `.env`:
```
MARQETA_APP_TOKEN=your_application_token
MARQETA_ACCESS_TOKEN=your_access_token
MARQETA_PROGRAM=your_program_name

# Optional: Enable RAG features
ENABLE_LOCAL_STORAGE=true  # Default: false
```

## Architecture Overview

### Optional Features System

**IMPORTANT:** RAG features are **optional** and must be explicitly enabled.

**When disabled (default):**
- Only core tools are available (transaction queries, export, metadata)
- No ChromaDB or sentence-transformers dependencies required
- Smaller installation footprint (~50MB vs ~500MB)
- Faster startup time

**When enabled (ENABLE_LOCAL_STORAGE=true):**
- All core tools PLUS RAG tools
- Requires `pip install marqeta-diva-mcp[rag]`
- Enables local storage, semantic search, and offline analysis
- Creates `transactions.db` (SQLite) and `chroma_db/` (ChromaDB) in working directory

**Feature Detection:**
- Server checks `ENABLE_LOCAL_STORAGE` environment variable at startup
- Conditionally imports RAG modules only if enabled
- If dependencies missing but flag is true, logs warning and disables features
- Tool list is built dynamically: `BASE_TOOLS` + `RAG_TOOLS` (if enabled)

### Core Components

1. **server.py** - MCP server implementation
   - Defines all MCP tools (transaction queries, export, metadata - always available)
   - Conditionally registers RAG tools based on ENABLE_LOCAL_STORAGE flag
   - Handles tool calls and routes them to appropriate components
   - Returns helpful error if RAG tool called without feature enabled

2. **client.py** - DiVA API Client
   - HTTP client for Marqeta DiVA API
   - Built-in rate limiting (300 requests per 5 minutes)
   - Schema caching and validation
   - Export functionality to JSON/CSV

3. **Hybrid Local Storage System** (Optional - requires `[rag]` extras)
   - **local_storage.py** - SQLite storage for complete transaction data
   - **vector_store.py** - ChromaDB for semantic search embeddings
   - **embeddings.py** - Text embedding generation using sentence-transformers
   - **rag_tools.py** - Orchestration layer that coordinates all components

### Key Architectural Pattern: Hybrid Storage

**Problem:** MCP has a 25,000 token response limit, but users need to analyze complete datasets (1,000+ transactions).

**Solution:** Dual storage approach:
```
DiVA API → sync_transactions → {
    SQLite (full transaction data)
    ChromaDB (384-dim embeddings)
}
```

**Query Flow:**
```
User Query → ChromaDB (semantic search) → Get IDs → SQLite (full data) → Return complete transactions
```

This eliminates:
- Token limits (data comes from local storage, not API responses)
- Repeated API calls
- Pagination complexity for end users

### Important Implementation Details

1. **API Response Format**
   - DiVA API returns `records` array (NOT `data`)
   - Maximum 10,000 records per query (hard API limit)
   - No offset pagination support - use date ranges for larger datasets

2. **Date Filtering**
   - Use actual field names in filters: `{"transaction_timestamp": ">=2023-10-20"}`
   - Do NOT use separate `start_date`/`end_date` parameters (they don't exist)
   - Supports operators: `>=`, `>`, `<`, `<=`, `..` (range)

3. **Field Validation**
   - Client-side field validation is DISABLED
   - API handles validation and returns meaningful errors
   - Uses fuzzy matching to suggest similar field names on errors

4. **Rate Limiting**
   - Built-in rate limiter: 300 requests per 5 minutes
   - Automatic throttling prevents 429 errors
   - Essential for bulk operations

5. **ChromaDB ID Requirements**
   - All IDs must be strings (ChromaDB requirement)
   - Transaction tokens are converted to strings before storage

## MCP Tools Reference

### Transaction Tools
- `get_authorizations`, `get_settlements`, `get_clearings`, `get_declines`, `get_loads`
- All support `aggregation`: detail, day, week, month
- All accept `filters`, `fields`, `sort_by`, `count` (max 10,000)

### Financial Tools
- `get_program_balances`, `get_program_balances_settlement`, `get_activity_balances`
- Day-level aggregation only

### Card & User Tools
- `get_cards`, `get_users`
- Detail-level only

### Metadata Tools
- `list_available_views` - Discover available endpoints
- `get_view_schema` - Get field definitions for any view

### Export Tool
- `export_view_to_file` - Export to JSON/CSV
- Supports all views and aggregation levels

### Local Storage & RAG Tools (Critical)
- `index_transactions` - Sync from DiVA to local storage (SQLite + ChromaDB)
- `query_local_transactions` - SQL-based queries on local data (NO TOKEN LIMITS)
- `semantic_search_transactions` - Natural language search using embeddings
- `find_similar_transactions` - Find transactions similar to a reference transaction
- `get_index_stats` - Check local storage statistics
- `clear_index` - Reset local storage

## Important Files to Understand

### Documentation Files
- **LOCAL_STORAGE_ARCHITECTURE.md** - Deep dive into hybrid storage solution
- **RAG_GUIDE.md** - Complete guide to semantic search features
- **LARGE_DATASET_GUIDE.md** - Strategies for handling large datasets
- **FIXES_SUMMARY.md** - Critical bug fixes and their solutions

### Test Files
- Test files are at the root level (not in a tests/ directory)
- Each test file targets specific functionality
- Tests use real API credentials from environment variables

## Common Gotchas

1. **Response Parsing**
   - Always use `result.get("records", [])` NOT `result.get("data", [])`
   - The API returns `records`, not `data`

2. **Date Filtering Syntax**
   - ✅ Correct: `filters={"transaction_timestamp": ">=2023-10-20"}`
   - ❌ Wrong: `start_date="2023-10-20"` (parameter doesn't exist)

3. **Record Limits**
   - DiVA API hard limit: 10,000 records per query
   - No offset pagination available
   - For larger datasets: use narrower date ranges or more specific filters

4. **Local Storage Workflow**
   - MUST call `index_transactions` before using RAG features
   - Local queries (`query_local_transactions`) bypass MCP token limits
   - Semantic search queries local SQLite, NOT the API

5. **Type Conversions**
   - ChromaDB requires string IDs
   - Transaction tokens must be converted to strings if they're integers

## Workflow Examples

### Getting Large Datasets for LLM Analysis
```python
# 1. Sync to local storage (one time)
index_transactions(
    filters={"business_user_token": "xyz"},
    max_records=2000
)

# 2. Query locally with NO token limits
query_local_transactions(
    filters={"transaction_amount": {">": 100}},
    limit=1000  # Can return 1000+ transactions!
)
```

### Semantic Search
```python
# Natural language queries
semantic_search_transactions(
    query="coffee shop purchases",
    n_results=50
)
```

### Export for External Analysis
```python
export_view_to_file(
    view_name="authorizations",
    output_path="./exports/data.json",
    format="json",
    filters={"transaction_timestamp": "2023-10-01..2023-10-31"}
)
```

## Project Structure

```
marqeta-diva-mcp/
├── src/marqeta_diva_mcp/
│   ├── server.py           # MCP server & tool definitions
│   ├── client.py           # DiVA API HTTP client
│   ├── local_storage.py    # SQLite storage
│   ├── vector_store.py     # ChromaDB vector store
│   ├── embeddings.py       # Embedding generation
│   ├── rag_tools.py        # RAG orchestration
│   └── __main__.py         # Entry point
├── test_*.py               # Test files (root level)
├── *.md                    # Documentation
├── pyproject.toml          # Project config
├── .env                    # Credentials (not in git)
├── transactions.db         # SQLite database (generated)
└── chroma_db/              # Vector store (generated)
```

## Version & Server Management

- Server version is tracked in `server.py` as `SERVER_VERSION`
- Use `get_server_version` tool to verify server has restarted after code changes
- Version is logged to stderr on startup

## Critical Constraints

1. **MCP Token Limit**: 25,000 tokens per response (why local storage exists)
2. **DiVA API Limit**: 10,000 records per query
3. **Rate Limit**: 300 requests per 5 minutes
4. **No Offset Pagination**: API doesn't support offset-based pagination
5. **ChromaDB String IDs**: All document IDs must be strings

## When Making Changes

1. **Adding New Tools**: Update both `TOOLS` list and `call_tool()` handler in server.py
2. **Modifying API Calls**: Remember to update rate limiter logic if needed
3. **Schema Changes**: Update both SQLite schema in local_storage.py and ChromaDB metadata in vector_store.py
4. **New Filters**: Document them in tool descriptions for LLM discoverability
5. **Version Bumps**: Update `SERVER_VERSION` in server.py and test with `get_server_version`

## Integration with Claude Desktop

**Basic configuration (core features only):**
```json
{
  "mcpServers": {
    "marqeta-diva": {
      "command": "uvx",
      "args": ["marqeta-diva-mcp"],
      "env": {
        "MARQETA_APP_TOKEN": "...",
        "MARQETA_ACCESS_TOKEN": "...",
        "MARQETA_PROGRAM": "..."
      }
    }
  }
}
```

**With RAG features enabled:**
```json
{
  "mcpServers": {
    "marqeta-diva": {
      "command": "uvx",
      "args": ["--with", "marqeta-diva-mcp[rag]", "marqeta-diva-mcp"],
      "env": {
        "MARQETA_APP_TOKEN": "...",
        "MARQETA_ACCESS_TOKEN": "...",
        "MARQETA_PROGRAM": "...",
        "ENABLE_LOCAL_STORAGE": "true"
      }
    }
  }
}
```
