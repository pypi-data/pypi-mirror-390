"""RAG tool implementations for semantic search and transaction analysis."""

import sys
from typing import Any, Dict, List, Optional

from .client import DiVAClient
from .embeddings import get_embedder
from .vector_store import get_vector_store
from .local_storage import get_storage


def sync_transactions(
    diva_client: DiVAClient,
    view_name: str = "authorizations",
    aggregation: str = "detail",
    filters: Optional[Dict[str, Any]] = None,
    max_records: Optional[int] = None,
    **kwargs: Any
) -> Dict[str, Any]:
    """
    Fetch transactions from DiVA and store in BOTH SQLite (full data) and ChromaDB (embeddings).
    This is the main function to populate local storage.

    Args:
        diva_client: DiVA API client
        view_name: DiVA view to query (e.g., 'authorizations')
        aggregation: Aggregation level
        filters: Transaction filters. For date filtering, use the actual date field name
                 with operators. Example: {"transaction_timestamp": ">=2023-10-20"}
        max_records: Maximum number of records to sync (up to 10,000)
        **kwargs: Additional DiVA query parameters

    Returns:
        Sync statistics
    """
    print(f"[Sync] Starting transaction sync from {view_name}...", file=sys.stderr)

    # Get all components
    embedder = get_embedder()
    vector_store = get_vector_store()
    storage = get_storage()

    # Fetch transactions from DiVA
    query_params = {
        "filters": filters,
        **kwargs
    }

    # Remove None values
    query_params = {k: v for k, v in query_params.items() if v is not None}

    # Set count limit (DiVA API limit: 10,000 for JSON responses)
    if max_records:
        query_params["count"] = min(max_records, 10000)
    else:
        query_params["count"] = 10000  # Max per DiVA API

    all_transactions = []

    print(f"[Sync] Fetching transactions (count={query_params['count']})...", file=sys.stderr)
    result = diva_client.get_view(view_name, aggregation, **query_params)

    transactions = result.get("records", [])

    if transactions:
        all_transactions.extend(transactions)

        # Truncate if we got more than max_records
        if max_records and len(all_transactions) > max_records:
            all_transactions = all_transactions[:max_records]

        # Warn if there are more records available
        if result.get("is_more", False):
            print(f"[Sync] Warning: More records available but DiVA API does not support offset pagination.", file=sys.stderr)
            print(f"[Sync] Retrieved {len(all_transactions)} records. To get more data, use narrower date ranges or filters.", file=sys.stderr)

    if not all_transactions:
        return {
            "success": False,
            "message": "No transactions found matching the criteria",
            "synced_count": 0
        }

    print(f"[Sync] Fetched {len(all_transactions)} transactions.", file=sys.stderr)

    # 1. Store full data in SQLite
    print(f"[Sync] Storing full data in SQLite...", file=sys.stderr)
    storage_count = storage.add_transactions(all_transactions, view_name, aggregation)

    # 2. Generate embeddings and store in ChromaDB
    print(f"[Sync] Generating embeddings...", file=sys.stderr)
    embeddings = embedder.embed_transactions_batch(all_transactions)

    print(f"[Sync] Storing embeddings in ChromaDB...", file=sys.stderr)
    vector_count = vector_store.add_transactions(all_transactions, embeddings)

    # Get stats
    storage_stats = storage.get_stats()
    vector_stats = vector_store.get_stats()

    return {
        "success": True,
        "message": f"Successfully synced {storage_count} transactions",
        "synced_count": storage_count,
        "storage": {
            "total_transactions": storage_stats["total_transactions"],
            "database_size_mb": storage_stats["database_size_mb"]
        },
        "vector_store": {
            "total_indexed": vector_stats["count"]
        },
        "view_name": view_name,
        "aggregation": aggregation
    }


# Keep old name for backward compatibility, but point to new function
def index_transactions(*args, **kwargs):
    """Alias for sync_transactions for backward compatibility."""
    return sync_transactions(*args, **kwargs)


def semantic_search_transactions(
    diva_client: DiVAClient,
    query: str,
    n_results: int = 10,
    filters: Optional[Dict[str, Any]] = None,
    enrich: bool = True
) -> Dict[str, Any]:
    """
    Search for transactions using natural language semantic search.
    Returns FULL transaction data from local SQLite storage (no token limits!).

    Args:
        diva_client: DiVA API client (not used if enrich=True, kept for compatibility)
        query: Natural language search query (e.g., "coffee shop purchases")
        n_results: Number of results to return
        filters: Metadata filters (e.g., {"transaction_amount": {"$gt": 10}})
        enrich: If True, fetch full transaction details from local SQLite storage

    Returns:
        Search results with similarity scores and full transaction data
    """
    print(f"[Search] Semantic search: '{query}'", file=sys.stderr)

    # Get components
    embedder = get_embedder()
    vector_store = get_vector_store()
    storage = get_storage()

    # Generate query embedding
    query_embedding = embedder.embed_query(query)

    # Search vector store (gets transaction IDs + similarity scores)
    results = vector_store.search(
        query_embedding=query_embedding,
        n_results=n_results,
        where=filters
    )

    if results["count"] == 0:
        return {
            "success": True,
            "query": query,
            "count": 0,
            "transactions": [],
            "message": "No matching transactions found. Try syncing more transactions first."
        }

    # Enrich with full transaction data from LOCAL STORAGE (not DiVA API!)
    if enrich and results["transactions"]:
        transaction_tokens = [txn["transaction_token"] for txn in results["transactions"]]

        print(f"[Search] Fetching full data for {len(transaction_tokens)} transactions from local storage...", file=sys.stderr)

        # Fetch from SQLite (fast, no API calls, no token limits!)
        full_transactions = storage.get_transactions(transaction_tokens)

        # Create a map of token -> full transaction
        full_txns_map = {
            txn["transaction_token"]: txn
            for txn in full_transactions
        }

        # Enrich results with full transaction data
        for result_txn in results["transactions"]:
            token = result_txn["transaction_token"]
            if token in full_txns_map:
                result_txn["full_transaction"] = full_txns_map[token]
            else:
                print(f"[Search] Warning: Transaction {token} not found in local storage", file=sys.stderr)

    return {
        "success": True,
        "query": query,
        "count": results["count"],
        "transactions": results["transactions"],
        "note": "Full transaction data retrieved from local storage (no API calls)"
    }


def find_similar_transactions(
    diva_client: DiVAClient,
    transaction_token: str,
    n_results: int = 10,
    filters: Optional[Dict[str, Any]] = None
) -> Dict[str, Any]:
    """
    Find transactions similar to a given transaction.

    Args:
        diva_client: DiVA API client
        transaction_token: Token of the reference transaction
        n_results: Number of similar transactions to return
        filters: Additional metadata filters

    Returns:
        Similar transactions with similarity scores
    """
    print(f"[RAG] Finding similar transactions to {transaction_token}", file=sys.stderr)

    # Get vector store
    vector_store = get_vector_store()

    # Get the reference transaction's embedding
    ref_txn = vector_store.get_by_id(transaction_token)

    if not ref_txn or not ref_txn.get("embedding"):
        return {
            "success": False,
            "message": f"Transaction {transaction_token} not found in vector store. Index it first.",
            "transaction_token": transaction_token
        }

    # Search for similar transactions
    results = vector_store.search(
        query_embedding=ref_txn["embedding"],
        n_results=n_results + 1,  # +1 because the reference itself will be included
        where=filters
    )

    # Filter out the reference transaction itself
    similar_txns = [
        txn for txn in results["transactions"]
        if txn["transaction_token"] != transaction_token
    ][:n_results]

    return {
        "success": True,
        "reference_transaction": transaction_token,
        "reference_metadata": ref_txn.get("metadata", {}),
        "count": len(similar_txns),
        "similar_transactions": similar_txns
    }


def query_local_transactions(
    filters: Optional[Dict[str, Any]] = None,
    limit: int = 100,
    offset: int = 0,
    order_by: str = "created_time DESC"
) -> Dict[str, Any]:
    """
    Query transactions directly from local SQLite storage.
    No API calls, no token limits, full transaction data.

    Args:
        filters: Dictionary of filters (e.g., {"merchant_name": "Starbucks", "transaction_amount": {">": 10}})
        limit: Maximum number of results (default: 100)
        offset: Offset for pagination (default: 0)
        order_by: SQL ORDER BY clause (default: "created_time DESC")

    Returns:
        Query results with full transaction data
    """
    print(f"[Query] Querying local storage with filters: {filters}", file=sys.stderr)

    storage = get_storage()

    results = storage.query_transactions(
        filters=filters,
        limit=limit,
        offset=offset,
        order_by=order_by
    )

    return {
        "success": True,
        **results,
        "note": "Data retrieved from local SQLite storage (no API calls, no token limits)"
    }


def get_storage_stats() -> Dict[str, Any]:
    """
    Get comprehensive statistics about local storage (SQLite + ChromaDB).

    Returns:
        Storage statistics including counts, sizes, and status
    """
    storage = get_storage()
    vector_store = get_vector_store()
    embedder = get_embedder()

    storage_stats = storage.get_stats()
    vector_stats = vector_store.get_stats()

    return {
        "success": True,
        "sqlite_storage": storage_stats,
        "vector_store": vector_stats,
        "embedding_model": {
            "name": embedder.model_name,
            "dimension": embedder.embedding_dim
        },
        "note": "Local storage eliminates token limits and API dependency"
    }


# Keep old name for backward compatibility
def get_index_stats():
    """Alias for get_storage_stats for backward compatibility."""
    return get_storage_stats()


def clear_local_storage(clear_sqlite: bool = True, clear_vector_store: bool = True) -> Dict[str, Any]:
    """
    Clear data from local storage (SQLite and/or ChromaDB).

    Args:
        clear_sqlite: If True, clear SQLite database
        clear_vector_store: If True, clear ChromaDB vector store

    Returns:
        Confirmation of clearing
    """
    print("[Clear] Clearing local storage...", file=sys.stderr)

    results = {}

    if clear_sqlite:
        storage = get_storage()
        count = storage.clear()
        results["sqlite"] = {
            "cleared": True,
            "transactions_deleted": count
        }

    if clear_vector_store:
        vector_store = get_vector_store()
        vector_store.clear()
        results["vector_store"] = {
            "cleared": True
        }

    return {
        "success": True,
        "message": "Local storage cleared successfully",
        **results
    }


# Keep old name for backward compatibility
def clear_index():
    """Alias for clear_local_storage for backward compatibility."""
    return clear_local_storage(clear_sqlite=True, clear_vector_store=True)
