# Marqeta DiVA MCP Server - Fixes Summary

## Overview
This document summarizes the fixes implemented to address issues discovered during usage testing.

## Major Updates

### v2.0 - Large Dataset Support (Latest)
- ✅ Added pagination with `offset` parameter
- ✅ Added `export_view_to_file` tool for automatic export with pagination
- ✅ Supports JSON and CSV export formats
- ✅ All tools now support pagination
- 📖 See **LARGE_DATASET_GUIDE.md** for detailed usage

### v1.0 - Initial Fixes
- ✅ Fixed duplicate `aggregation` parameter bug
- ✅ Added default count limits (100 default, 1000 max)
- ✅ Added filter field validation with fuzzy matching
- ✅ Added date parameter validation
- ✅ Added token estimation warnings
- ✅ Improved error messages

---

## Issues Fixed

### 1. ✅ Duplicate `aggregation` Parameter Error

**Problem:**
```
Error: DiVAClient.get_view() got multiple values for argument 'aggregation'
```

**Root Cause:** The `aggregation` parameter was being passed both as a positional argument and within `**arguments`, causing a parameter collision.

**Fix:** Changed from `.get()` to `.pop()` to remove the parameter from the arguments dict before spreading.

**Location:** `server.py:443-505`

**Before:**
```python
aggregation = arguments.get("aggregation", "detail")
result = client.get_view("authorizations", aggregation, **arguments)
```

**After:**
```python
aggregation = arguments.pop("aggregation", "detail")
result = client.get_view("authorizations", aggregation, **arguments)
```

---

### 2. ✅ Token Overflow - No Default Count Limit

**Problem:**
```
Error: MCP tool "get_users" response (528046 tokens) exceeds maximum allowed tokens (25000)
Error: MCP tool "get_cards" response (743279 tokens) exceeds maximum allowed tokens (25000)
```

**Root Cause:** When `count` was not specified, the API would return ALL records (potentially thousands), causing massive token usage.

**Fix:** Added smart defaults:
- Default count: 100 records
- Maximum count: 1000 records (capped even if user requests more)

**Location:** `client.py:164-169`

**Before:**
```python
if count is not None:
    params["count"] = str(count)
```

**After:**
```python
if count is not None:
    params["count"] = str(min(count, 1000))  # Cap at 1000
else:
    params["count"] = "100"  # Default to 100
```

---

### 3. ✅ Invalid Filter Fields - No Validation

**Problem:**
```
Error: /authorizations/detail does not have a column with the name: 'business_token'
```

---

### 7. ✅ MCP Token Limit Exceeded - Large Datasets

**Problem:**
```
Error: MCP tool "get_authorizations" response (178128 tokens) exceeds maximum allowed tokens (25000)
```

Even with field filtering, large datasets (>1000 records) couldn't be retrieved due to MCP protocol's 25k token limit.

**Fix:** Added two solutions:

1. **Pagination Support** - `offset` parameter for manual batching
2. **Automatic Export** - `export_view_to_file` tool that handles pagination automatically

**Location:** `client.py:359-440`, `server.py:105-108, 448-499, 583-599`

**Solution 1: Pagination**
```python
# Fetch in batches
batch1 = get_authorizations(filters={...}, count=100, offset=0)
batch2 = get_authorizations(filters={...}, count=100, offset=100)
batch3 = get_authorizations(filters={...}, count=100, offset=200)
```

**Solution 2: Export to File (Recommended)**
```python
export_view_to_file(
    view_name="authorizations",
    output_path="./exports/transactions.json",
    format="json",  # or "csv"
    filters={"business_user_token": "c97bc74d-..."},
    fields=["transaction_amount", "merchant_name", "transaction_timestamp"]
)

# Response:
{
  "success": true,
  "file_path": "/full/path/to/exports/transactions.json",
  "records_exported": 1528,
  "file_size_bytes": 456789
}
```

**Features:**
- Automatically paginates through all records
- Supports JSON and CSV formats
- Progress updates via stderr
- Works with all views
- No token limits

**See LARGE_DATASET_GUIDE.md for complete documentation**


**Root Cause:** Invalid filter field names weren't caught until the API call, requiring manual schema lookups to find correct field names.

**Fix:** Added client-side validation with fuzzy matching for helpful suggestions.

**Location:** `client.py:88-147, 365-368`

**Features:**
- Schema caching to avoid repeated API calls
- Fuzzy field name matching using `difflib`
- Helpful error messages with suggestions

**Example Error:**
```
/authorizations/detail does not have the following column(s): 'business_token'
Suggestions: 'business_token' -> did you mean 'business_user_token'?
Use get_view_schema('authorizations', 'detail') to see all valid fields.
```

---

### 4. ✅ Date Parameters on Unsupported Views

**Problem:**
```
Error: /loads/detail does not have a column with the name: 'end_date'
```

**Root Cause:** Date range parameters (`start_date`, `end_date`) aren't supported on all views (e.g., `cards`, `users`), but this wasn't validated client-side.

**Fix:** Added pre-validation for date parameters.

**Location:** `client.py:149-178, 360-363`

**Example Error:**
```
The 'cards' view does not support start_date/end_date parameters.
Use filters on date fields instead (check schema for available date columns).
```

---

### 5. ✅ Token Estimation Warnings

**Problem:** Even with field filtering, large requests like `count=1832` with 2 fields still returned 193k tokens, exceeding the 25k limit.

**Fix:** Added response size estimation with warnings.

**Location:** `client.py:180-223, 370-378`

**Features:**
- Estimates tokens per view type
- Adjusts estimate based on field filtering (~60% reduction)
- Warns when estimated response exceeds 20k tokens

**Example Warning:**
```
[DiVA Client Warning] Requesting 1832 records may return ~58,624 tokens (limit is 25,000).
Consider reducing 'count' or using more specific 'fields'.
```

---

### 6. ✅ Improved Error Messages

**Problem:** Generic error messages didn't help users understand what went wrong.

**Fix:** Enhanced error messages with helpful context.

**Location:** `client.py:308-321, server.py:89-96`

**Before:**
```
Error 400: Bad Request - Malformed query or filter parameters
```

**After:**
```
Error 400: Bad Request - Malformed query or filter parameters

Note: This error usually means you're using an invalid field name in 'filters'.
Query parameters like 'start_date', 'end_date', 'count', 'sort_by' should NOT be in 'filters'.
Only actual data field names belong in 'filters'.
```

**Also updated tool descriptions:**
```python
"filters": {
    "description": (
        "Filters on data fields. Use actual field names from schema only. "
        "Do NOT include query parameters like 'start_date', 'end_date', 'count' here."
    )
}
```

---

## Test Results

All unit tests pass successfully:

```
✓ Filter field validation with fuzzy matching
✓ Date parameter validation
✓ Token estimation and warnings
✓ Default count = 100
✓ Count capped at 1000
✓ Schema caching
```

Run tests: `uv run test_fixes_unit.py`

---

## Summary of Changes

| File | Lines | Changes |
|------|-------|---------|
| **Pagination & Export** | | |
| `client.py` | 3-8 | Added imports for csv, json, Path |
| `client.py` | 234 | Added `offset` parameter to `_build_query_params()` |
| `client.py` | 266-268 | Added offset to query params |
| `client.py` | 359-440 | Added `export_to_file()` method with auto-pagination |
| `server.py` | 105-108 | Added `offset` parameter to all tools |
| `server.py` | 448-499 | Added `export_view_to_file` tool |
| `server.py` | 583-599 | Added export tool handler |
| `server.py` | 66, 113, etc. | Updated tool descriptions with pagination guidance |
| **Initial Fixes** | | |
| `server.py` | 443-505 | Changed `.get()` to `.pop()` for aggregation parameter |
| `server.py` | 89-96, 130-137, etc. | Updated filter descriptions in all tool schemas |
| `client.py` | 4 | Added `import difflib` for fuzzy matching |
| `client.py` | 71-77 | Added schema cache and date range view tracking |
| `client.py` | 79-86 | Added `_find_similar_fields()` method |
| `client.py` | 88-147 | Added `_validate_filters()` method |
| `client.py` | 149-178 | Added `_validate_date_params()` method |
| `client.py` | 180-223 | Added `_estimate_response_size()` method |
| `client.py` | 258-264 | Added default count=100, max=1000 |
| `client.py` | 308-321 | Enhanced 400 error messages |
| `client.py` | 461-482 | Added validation calls in `get_view()` |

---

## Behavior Changes

### Default Count
- **Before:** No default (could return unlimited records)
- **After:** Defaults to 100, max 1000

### Filter Validation
- **Before:** Invalid fields discovered at API call time
- **After:** Validated client-side with helpful suggestions

### Date Parameters
- **Before:** Invalid usage discovered at API call time
- **After:** Validated client-side with clear error messages

### Large Requests
- **Before:** Silent failure with token overflow
- **After:** Warning message (logged to stderr) before request

---

## Usage Examples

### Correct Usage After Fixes

```python
# Query with business user token (correct field name)
get_authorizations(
    filters={"business_user_token": "c97bc74d-..."},
    aggregation="detail"
)

# Query with date range (transaction views only)
get_authorizations(
    start_date="2025-10-20",
    end_date="2025-11-10",
    count=100
)

# Large query with field filtering
get_cards(
    filters={"business_user_token": "c97bc74d-..."},
    fields=["card_token", "user_token"],
    count=500  # Will warn but proceed
)

# Default count (100 records)
get_users(
    filters={"business_user_token": "c97bc74d-..."}
)
```

### Common Errors Caught Early

```python
# ❌ Wrong field name - gets helpful suggestion
get_authorizations(filters={"business_token": "..."})
# Error: Did you mean 'business_user_token'?

# ❌ Date params on wrong view - clear error
get_cards(start_date="2025-01-01", end_date="2025-12-31")
# Error: 'cards' view doesn't support start_date/end_date

# ❌ Too many records - warning before overflow
get_users(count=5000)
# Warning: May return ~350,000 tokens (limit: 25,000)
```
