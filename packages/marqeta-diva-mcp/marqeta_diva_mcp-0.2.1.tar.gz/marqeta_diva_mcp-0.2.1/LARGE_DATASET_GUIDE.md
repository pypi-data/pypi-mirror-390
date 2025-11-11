# Handling Large Datasets in Marqeta DiVA MCP

## The Problem

MCP protocol has a **25,000 token response limit**. When querying large datasets:

```
Error: MCP tool "get_authorizations" response (178128 tokens) exceeds maximum allowed tokens (25000)
```

## Solutions

### Solution 1: Export to File (Recommended for >1000 records)

Use the `export_view_to_file` tool to automatically fetch all records and write to a file.

**Example: Export all authorizations for a business**

```python
export_view_to_file(
    view_name="authorizations",
    aggregation="detail",
    output_path="./exports/business_authorizations.json",
    format="json",  # or "csv"
    filters={
        "business_user_token": "c97bc74d-2489-4857-b8d1-8b2cb0c304c7",
        "transaction_timestamp": ">=2025-10-20"
    },
    fields=["transaction_status", "transaction_type", "transaction_amount", "transaction_timestamp"]
)
```

**Response:**
```json
{
  "success": true,
  "file_path": "/full/path/to/exports/business_authorizations.json",
  "format": "json",
  "records_exported": 1528,
  "file_size_bytes": 456789
}
```

**Features:**
- ✅ Automatically handles pagination
- ✅ No token limits
- ✅ Progress updates in stderr
- ✅ Supports JSON and CSV formats
- ✅ Works with all views (authorizations, settlements, cards, users, etc.)

---

### Solution 2: Manual Pagination (For controlled batching)

Use `offset` and `count` parameters to fetch data in batches.

**Example: Fetch authorizations in batches of 100**

```python
# First batch (records 0-99)
batch1 = get_authorizations(
    filters={"business_user_token": "c97bc74d-..."},
    count=100,
    offset=0
)

# Second batch (records 100-199)
batch2 = get_authorizations(
    filters={"business_user_token": "c97bc74d-..."},
    count=100,
    offset=100
)

# Third batch (records 200-299)
batch3 = get_authorizations(
    filters={"business_user_token": "c97bc74d-..."},
    count=100,
    offset=200
)
```

**Check if more records exist:**
```json
{
  "total": 1528,
  "is_more": true,  // <-- More records available
  "data": [...]
}
```

---

### Solution 3: Use Aggregation

For analytics, use aggregated views instead of detail records.

**Example: Get monthly transaction summaries instead of all transactions**

```python
# Instead of 1528 detail records...
get_authorizations(
    filters={"business_user_token": "c97bc74d-..."},
    aggregation="detail"  # ❌ 178k tokens!
)

# Use monthly aggregation
get_authorizations(
    filters={"business_user_token": "c97bc74d-..."},
    aggregation="month"  # ✅ Much smaller!
)
```

---

## Usage Patterns

### Pattern 1: Quick Summary + Detailed Export

```python
# Step 1: Get summary statistics (fast)
summary = get_authorizations(
    filters={"business_user_token": "c97bc74d-..."},
    aggregation="month"
)
# Shows: 1528 total transactions across 3 months

# Step 2: Export details to file if needed
export_view_to_file(
    view_name="authorizations",
    output_path="./exports/full_details.json",
    filters={"business_user_token": "c97bc74d-..."}
)
```

---

### Pattern 2: Sampling + Full Export

```python
# Step 1: Sample first 10 records to see structure
sample = get_authorizations(
    filters={"business_user_token": "c97bc74d-..."},
    count=10
)
# Examine fields and data

# Step 2: Export all with specific fields
export_view_to_file(
    view_name="authorizations",
    output_path="./exports/transactions.csv",
    format="csv",
    filters={"business_user_token": "c97bc74d-..."},
    fields=["transaction_amount", "merchant_name", "transaction_timestamp"]
)
```

---

### Pattern 3: Iterative Pagination

```python
# Process in batches without exceeding token limits
offset = 0
batch_size = 100
all_transactions = []

while True:
    batch = get_authorizations(
        filters={"business_user_token": "c97bc74d-..."},
        count=batch_size,
        offset=offset
    )

    if not batch["data"]:
        break

    all_transactions.extend(batch["data"])
    offset += len(batch["data"])

    if not batch["is_more"]:
        break
```

---

## Export Formats

### JSON Format
```json
[
  {
    "transaction_token": "abc123",
    "transaction_amount": 50.00,
    "merchant_name": "Coffee Shop",
    "transaction_timestamp": "2025-10-20T10:30:00Z"
  },
  ...
]
```

### CSV Format
```csv
transaction_token,transaction_amount,merchant_name,transaction_timestamp
abc123,50.00,Coffee Shop,2025-10-20T10:30:00Z
def456,25.50,Gas Station,2025-10-21T14:15:00Z
```

---

## Performance Tips

### 1. Use Field Filtering
Reduces tokens by ~60%:

```python
# ❌ All fields = 100 tokens/record
get_authorizations(count=500)

# ✅ Specific fields = 40 tokens/record
get_authorizations(
    count=500,
    fields=["transaction_amount", "transaction_timestamp", "merchant_name"]
)
```

### 2. Use Date Ranges
Limit scope:

```python
export_view_to_file(
    view_name="authorizations",
    output_path="./exports/october_transactions.json",
    start_date="2025-10-01",
    end_date="2025-10-31",
    filters={"business_user_token": "c97bc74d-..."}
)
```

### 3. Limit Max Records
Set reasonable limits:

```python
export_view_to_file(
    view_name="authorizations",
    output_path="./exports/recent_1000.json",
    max_records=1000,  # Stop after 1000 records
    filters={"business_user_token": "c97bc74d-..."},
    sort_by="-transaction_timestamp"  # Most recent first
)
```

---

## Troubleshooting

### Error: Token limit exceeded with offset
**Problem:** Even with pagination, single batch is too large

**Solution:** Reduce `count` or add field filtering
```python
# Instead of count=1000
get_authorizations(count=100, offset=0)

# Or use specific fields
get_authorizations(
    count=500,
    offset=0,
    fields=["transaction_token", "transaction_amount"]
)
```

### Error: Export taking too long
**Problem:** Exporting millions of records

**Solution:** Add filters or max_records limit
```python
export_view_to_file(
    view_name="authorizations",
    output_path="./exports/recent.json",
    max_records=10000,  # Limit to 10k
    sort_by="-transaction_timestamp"
)
```

### Error: CSV export fails with missing fields
**Problem:** Records have inconsistent fields

**Solution:** Use JSON format or specify fields
```python
export_view_to_file(
    view_name="authorizations",
    output_path="./exports/data.json",  # JSON handles missing fields better
    format="json"
)
```

---

## Complete Examples

### Example 1: Export All Transactions for a Business

```python
# Export all transactions to CSV for Excel analysis
export_view_to_file(
    view_name="authorizations",
    output_path="./exports/business_transactions.csv",
    format="csv",
    filters={
        "business_user_token": "c97bc74d-2489-4857-b8d1-8b2cb0c304c7"
    },
    fields=[
        "transaction_timestamp",
        "transaction_type",
        "transaction_amount",
        "merchant_name",
        "card_token",
        "user_token"
    ],
    sort_by="transaction_timestamp"
)
```

### Example 2: Export Declined Transactions

```python
# Get all declines for investigation
export_view_to_file(
    view_name="declines",
    output_path="./exports/declines_analysis.json",
    format="json",
    filters={
        "business_user_token": "c97bc74d-2489-4857-b8d1-8b2cb0c304c7",
        "transaction_timestamp": ">=2025-10-01"
    },
    fields=[
        "declining_entity",
        "decline_type",
        "transaction_amount",
        "transaction_timestamp",
        "displaymessage"
    ]
)
```

### Example 3: Export All Cards for a Business

```python
# Get complete card inventory
export_view_to_file(
    view_name="cards",
    output_path="./exports/card_inventory.csv",
    format="csv",
    aggregation="detail",
    filters={
        "business_user_token": "c97bc74d-2489-4857-b8d1-8b2cb0c304c7",
        "state": "ACTIVE"
    },
    fields=[
        "card_token",
        "user_token",
        "state",
        "created_time",
        "last_transaction_activity_date"
    ]
)
```

---

## Summary

| Records Needed | Best Solution | Method |
|----------------|---------------|--------|
| < 100 | Direct query | `get_authorizations(count=100)` |
| 100-1000 | Direct query or pagination | `get_authorizations(count=1000)` |
| > 1000 | **Export to file** | `export_view_to_file(...)` |
| Analytics | Aggregation | `get_authorizations(aggregation="month")` |

**Default Limits:**
- Default count: 100 records
- Maximum count: 1000 records per request
- MCP response limit: 25,000 tokens
- No limit on export file size
