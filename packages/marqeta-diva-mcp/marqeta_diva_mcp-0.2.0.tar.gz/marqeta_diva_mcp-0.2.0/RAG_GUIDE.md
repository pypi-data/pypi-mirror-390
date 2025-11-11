# RAG (Semantic Search) Guide for Marqeta DiVA MCP

## Overview

The RAG (Retrieval Augmented Generation) features enable **semantic search** and **intelligent analytics** on your transaction data using natural language queries.

### What can you do?

- 🔍 **Semantic Search**: "Find all coffee shop transactions"
- 🔗 **Find Similar**: "Show me transactions like this one"
- 📊 **Analytics**: Group and analyze transactions by semantic meaning
- 🎯 **Pattern Detection**: Find transaction patterns and anomalies

---

## Quick Start

### Step 1: Install Dependencies

```bash
uv sync
```

This installs:
- **ChromaDB**: Local vector database
- **sentence-transformers**: Embedding model

### Step 2: Index Your Transactions

Before you can search, you need to index transactions into the vector store:

```python
# Index the last 30 days of transactions
index_transactions(
    view_name="authorizations",
    filters={"business_user_token": "your-business-token"},
    start_date="2025-10-01",
    max_records=1000  # Optional limit
)
```

**Response:**
```json
{
  "success": true,
  "message": "Successfully indexed 528 transactions",
  "indexed_count": 528,
  "total_in_store": 528,
  "view_name": "authorizations",
  "aggregation": "detail"
}
```

### Step 3: Search with Natural Language

```python
# Find coffee shop transactions
semantic_search_transactions(
    query="coffee shop purchases",
    n_results=10
)
```

**Response:**
```json
{
  "success": true,
  "query": "coffee shop purchases",
  "count": 10,
  "transactions": [
    {
      "transaction_token": "abc123",
      "similarity_score": 0.89,
      "metadata": {
        "merchant_name": "Starbucks Coffee",
        "transaction_amount": 5.50,
        "transaction_type": "AUTHORIZATION"
      },
      "full_transaction": { /* complete DiVA transaction data */ }
    },
    ...
  ]
}
```

---

## Core Concepts

### How It Works

1. **Text Generation**: Each transaction is converted to text
   - Example: "Merchant: Starbucks Coffee | Amount: 5.50 USD | Type: AUTHORIZATION"

2. **Embedding Generation**: Text is converted to a 384-dimensional vector using sentence-transformers

3. **Vector Storage**: Embeddings stored in ChromaDB (local, persistent)

4. **Semantic Search**: Natural language queries are embedded and compared using cosine similarity

### Why This Is Powerful

Traditional filters require exact matches:
```python
# Traditional: Must know exact merchant name
filters={"merchant_name": "STARBUCKS STORE #12345"}
```

Semantic search understands meaning:
```python
# Semantic: Natural language works
query="coffee shops"
# Matches: Starbucks, Dunkin, Peet's, local cafes, etc.
```

---

## MCP Tools Reference

### 1. `index_transactions`

Index transactions from DiVA into the vector store for semantic search.

**Parameters:**
- `view_name` (string): DiVA view (default: "authorizations")
- `aggregation` (string): Level (default: "detail")
- `filters` (object): DiVA filters to limit indexing
- `start_date` (string): ISO format date
- `end_date` (string): ISO format date
- `max_records` (integer): Limit number of records to index
- `program` (string): Override program

**Example:**
```python
index_transactions(
    filters={"business_user_token": "c97bc74d-..."},
    start_date="2025-10-01",
    end_date="2025-10-31",
    max_records=1000
)
```

**Best Practices:**
- Index recent transactions first (last 30-90 days)
- Use filters to index specific businesses/users
- Set `max_records` to avoid long indexing times
- Re-index periodically to add new transactions

---

### 2. `semantic_search_transactions`

Search transactions using natural language.

**Parameters:**
- `query` (string, **required**): Natural language search query
- `n_results` (integer): Number of results (default: 10)
- `filters` (object): Metadata filters (amount, date, etc.)
- `enrich` (boolean): Fetch full transaction data from DiVA (default: true)

**Example:**
```python
semantic_search_transactions(
    query="gas station purchases over $40",
    n_results=20,
    filters={"transaction_amount": {"$gt": 40}}
)
```

**Query Examples:**
- `"coffee shop purchases"`
- `"restaurant expenses"`
- `"online shopping transactions"`
- `"gas stations and fuel"`
- `"large purchases"`
- `"subscription payments"`

**Metadata Filters:**
```python
# Amount range
filters={"transaction_amount": {"$gt": 100, "$lt": 500}}

# Specific user
filters={"user_token": "user_123"}

# Combined
filters={
    "transaction_amount": {"$gt": 50},
    "user_token": "user_123"
}
```

---

### 3. `find_similar_transactions`

Find transactions similar to a specific transaction.

**Parameters:**
- `transaction_token` (string, **required**): Reference transaction
- `n_results` (integer): Number of similar transactions (default: 10)
- `filters` (object): Additional filters

**Example:**
```python
find_similar_transactions(
    transaction_token="txn_abc123",
    n_results=10
)
```

**Use Cases:**
- Find duplicate transactions
- Group related purchases
- Identify spending patterns
- Detect similar fraud cases

---

### 4. `get_index_stats`

Get statistics about the vector index.

**Example:**
```python
get_index_stats()
```

**Response:**
```json
{
  "success": true,
  "vector_store": {
    "collection_name": "transactions",
    "count": 1528,
    "persist_directory": "./chroma_db",
    "status": "initialized"
  },
  "embedding_model": "all-MiniLM-L6-v2",
  "embedding_dimension": 384
}
```

---

### 5. `clear_index`

Clear all transactions from the vector index.

**Example:**
```python
clear_index()
```

**Warning:** This cannot be undone. You'll need to re-index transactions.

---

## Usage Patterns

### Pattern 1: Initial Setup

```python
# 1. Index recent transactions
index_transactions(
    filters={"business_user_token": "your-business"},
    start_date="2025-10-01",
    max_records=1000
)

# 2. Check stats
get_index_stats()

# 3. Test search
semantic_search_transactions(
    query="coffee",
    n_results=5
)
```

---

### Pattern 2: Business Analytics

```python
# Find all entertainment expenses
semantic_search_transactions(
    query="entertainment movies dining restaurants",
    n_results=50,
    filters={"transaction_amount": {"$gt": 10}}
)

# Find subscription payments
semantic_search_transactions(
    query="monthly subscription recurring payment",
    n_results=20
)

# Find travel-related expenses
semantic_search_transactions(
    query="hotel airline uber taxi travel",
    n_results=30
)
```

---

### Pattern 3: Fraud Detection

```python
# 1. Index known fraud transaction
index_transactions(
    filters={"transaction_token": "known_fraud_txn"},
    max_records=1
)

# 2. Find similar patterns
find_similar_transactions(
    transaction_token="known_fraud_txn",
    n_results=20
)

# This finds transactions with similar characteristics:
# - Similar merchant types
# - Similar amounts
# - Similar patterns
```

---

### Pattern 4: Merchant Grouping

```python
# Problem: Merchant names vary
# - "STARBUCKS #1234"
# - "STARBUCKS STORE 5678"
# - "Starbucks Coffee"

# Solution: Semantic search groups them
semantic_search_transactions(
    query="Starbucks",
    n_results=100
)

# Returns all Starbucks variations
```

---

### Pattern 5: Periodic Re-indexing

```python
import datetime

# Get date 30 days ago
thirty_days_ago = (datetime.datetime.now() - datetime.timedelta(days=30)).isoformat()[:10]

# Index new transactions
index_transactions(
    start_date=thirty_days_ago,
    max_records=5000
)

# Note: Duplicate transactions are automatically updated
```

---

## Advanced Features

### Combining Semantic Search with DiVA Filters

```python
# Index only specific business
index_transactions(
    filters={
        "business_user_token": "business_abc",
        "transaction_amount": {"$gt": 10}
    },
    start_date="2025-01-01"
)

# Search within that subset
semantic_search_transactions(
    query="restaurant dining food",
    filters={"transaction_amount": {"$gt": 20}}
)
```

### Understanding Similarity Scores

```json
{
  "similarity_score": 0.95  // Extremely similar (almost identical)
  "similarity_score": 0.80  // Very similar
  "similarity_score": 0.65  // Somewhat similar
  "similarity_score": 0.40  // Loosely related
}
```

Scores above 0.70 typically indicate strong semantic similarity.

### Enrichment with Full Transaction Data

By default, `semantic_search_transactions` fetches full transaction details from DiVA:

```python
# With enrichment (default)
semantic_search_transactions(query="coffee", enrich=True)
# Returns: similarity score + metadata + full DiVA transaction

# Without enrichment (faster)
semantic_search_transactions(query="coffee", enrich=False)
# Returns: similarity score + metadata only
```

---

## Performance & Optimization

### Indexing Performance

**Timing:**
- Embedding generation: ~5ms per transaction
- Batch of 1000 transactions: ~30-60 seconds
- Vector store insertion: ~1-2 seconds per batch

**Recommendations:**
- Index in batches of 1000
- Use `max_records` for testing
- Index incrementally (new transactions only)

### Search Performance

**Timing:**
- Query embedding: ~5-10ms
- Vector search: <50ms for <100K transactions
- Full enrichment from DiVA: ~100-500ms

**Optimization:**
- Set `enrich=False` for faster searches (no DiVA API call)
- Use metadata filters to reduce search space
- Keep index size reasonable (<100K transactions)

### Storage

**Disk Usage:**
- ~1.5 KB per transaction (embedding + metadata)
- 10K transactions ≈ 15 MB
- 100K transactions ≈ 150 MB

**Location:**
- Default: `./chroma_db` directory
- Persistent across server restarts
- Can be backed up by copying directory

---

## Troubleshooting

### Error: "No matching transactions found"

**Cause:** Index is empty or doesn't contain matching transactions

**Solution:**
1. Check index stats: `get_index_stats()`
2. Verify transactions were indexed
3. Try re-indexing: `index_transactions(...)`

### Error: "Transaction not found in vector store"

**Cause:** The transaction hasn't been indexed yet

**Solution:**
```python
# Index the specific transaction
index_transactions(
    filters={"transaction_token": "your-transaction-token"}
)
```

### Low Similarity Scores

**Cause:** Query might be too generic or transactions don't match well

**Solution:**
- Make query more specific: "coffee shop" vs just "coffee"
- Try different query terms
- Verify transactions are relevant
- Check transaction text formatting

### Slow Indexing

**Cause:** Indexing large numbers of transactions

**Solution:**
- Use `max_records` to limit batches
- Index incrementally (date ranges)
- Be patient: 1000 transactions ≈ 1 minute

### Model Download on First Run

**Expected:** First run downloads ~90MB embedding model

**Solution:**
- Wait for download to complete (one-time only)
- Model is cached locally
- Subsequent runs are fast

---

## Technical Details

### Embedding Model

**Model:** `all-MiniLM-L6-v2` (sentence-transformers)
- **Size:** ~90 MB
- **Dimensions:** 384
- **Speed:** ~5ms per embedding
- **Quality:** Good for semantic similarity

**Alternatives (Future):**
- Fine-tuned models for financial data
- Larger models for better accuracy
- Domain-specific models

### Vector Database

**ChromaDB:**
- Local, persistent storage
- Cosine similarity search
- Metadata filtering support
- No external dependencies

**Future Options:**
- Qdrant for production
- FAISS for speed
- Pinecone for cloud

### Transaction Text Format

Transactions are formatted as:
```
Merchant: {merchant_name} | Amount: {amount} {currency} | Type: {type} | Status: {status} | MCC: {mcc} | Network: {network}
```

**Example:**
```
Merchant: Starbucks Coffee | Amount: 5.50 USD | Type: AUTHORIZATION | Status: COMPLETION | MCC: 5814 | Network: VISA
```

---

## Examples by Use Case

### E-commerce Analysis

```python
# Find all online purchases
semantic_search_transactions(
    query="amazon online shopping ecommerce digital purchase",
    n_results=50
)
```

### Expense Categorization

```python
# Find office supplies
semantic_search_transactions(query="office supplies stationery", n_results=20)

# Find utilities
semantic_search_transactions(query="electricity water gas utility bills", n_results=20)

# Find healthcare
semantic_search_transactions(query="pharmacy medical doctor hospital healthcare", n_results=20)
```

### Spending Pattern Analysis

```python
# Find weekend entertainment
semantic_search_transactions(
    query="restaurant bar entertainment movie theater",
    n_results=100
)

# Find commuting expenses
semantic_search_transactions(
    query="subway metro train bus public transportation",
    n_results=50
)
```

### Merchant Intelligence

```python
# Group all variations of a merchant
semantic_search_transactions(
    query="Walmart",
    n_results=100
)
# Returns: "WALMART #1234", "WAL-MART STORE", "Walmart Supercenter", etc.
```

---

## FAQ

**Q: Do I need to re-index after new transactions?**
A: Yes, run `index_transactions` periodically to add new transactions.

**Q: Can I search across multiple businesses?**
A: Yes, either index them all together or use metadata filters.

**Q: How accurate is semantic search?**
A: Very good for general merchant/category matching. Exact amounts need filters.

**Q: Can I use this offline?**
A: Yes! Everything runs locally after initial model download.

**Q: What happens if I restart the MCP server?**
A: Index is persisted in `./chroma_db` and loaded automatically.

**Q: Can I delete specific transactions?**
A: Not directly. Use `clear_index()` and re-index to remove transactions.

**Q: Does this work with other DiVA views?**
A: Yes! Works with settlements, clearings, declines, loads, etc.

---

## Next Steps

### Phase 1 (Current): MVP
✅ Local ChromaDB vector store
✅ Sentence-transformers embeddings
✅ Semantic search
✅ Transaction similarity

### Phase 2 (Future): Production
- Migrate to Qdrant for better performance
- Fine-tune embeddings on financial data
- Automatic background indexing
- Advanced analytics (clustering, anomaly detection)
- Multi-modal embeddings (time-series patterns)

---

## Support

For issues or questions:
1. Check the [FIXES_SUMMARY.md](./FIXES_SUMMARY.md) for common problems
2. Run tests: `uv run test_rag.py`
3. Check index stats: `get_index_stats()`
4. Review logs in stderr output

---

**Happy searching! 🔍**
