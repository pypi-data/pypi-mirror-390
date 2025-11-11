#!/usr/bin/env python3
"""Tests for RAG (Retrieval Augmented Generation) functionality."""

import tempfile
from pathlib import Path
from src.marqeta_diva_mcp.embeddings import TransactionEmbedder
from src.marqeta_diva_mcp.vector_store import TransactionVectorStore


def test_transaction_text_formatting():
    """Test that transactions are formatted correctly for embedding."""
    print("\n=== Test: Transaction Text Formatting ===")

    embedder = TransactionEmbedder()

    # Test transaction with full details
    transaction = {
        "merchant_name": "Starbucks Coffee",
        "transaction_amount": 4.50,
        "currency_code": "USD",
        "transaction_type": "AUTHORIZATION",
        "state": "COMPLETION",
        "merchant_category_code": "5814",
        "network": "VISA"
    }

    text = embedder.format_transaction_text(transaction)
    print(f"  Full transaction: {text}")

    expected_parts = ["Starbucks Coffee", "4.5", "AUTHORIZATION", "COMPLETION", "5814", "VISA"]
    if all(part in text for part in expected_parts):
        print("  ✓ All expected parts present")
    else:
        print(f"  ✗ Missing parts in: {text}")

    # Test minimal transaction
    minimal_transaction = {
        "transaction_token": "abc123",
        "transaction_amount": 10.00
    }

    text = embedder.format_transaction_text(minimal_transaction)
    print(f"  Minimal transaction: {text}")

    if "10.0" in text:
        print("  ✓ Minimal transaction formatted")
    else:
        print("  ✗ Minimal transaction formatting failed")


def test_embedding_generation():
    """Test that embeddings are generated correctly."""
    print("\n=== Test: Embedding Generation ===")

    embedder = TransactionEmbedder()

    # Test single embedding
    transaction = {
        "merchant_name": "Amazon",
        "transaction_amount": 99.99,
        "transaction_type": "AUTHORIZATION"
    }

    embedding = embedder.embed_transaction(transaction)

    print(f"  Embedding dimension: {len(embedding)}")
    print(f"  First 5 values: {embedding[:5]}")

    if len(embedding) == 384:  # MiniLM dimension
        print("  ✓ Correct embedding dimension")
    else:
        print(f"  ✗ Wrong dimension: {len(embedding)}")

    # Test batch embedding
    transactions = [
        {"merchant_name": "Starbucks", "transaction_amount": 5.00},
        {"merchant_name": "Shell Gas", "transaction_amount": 40.00},
        {"merchant_name": "Walmart", "transaction_amount": 150.00}
    ]

    embeddings = embedder.embed_transactions_batch(transactions)

    if len(embeddings) == 3:
        print(f"  ✓ Batch embedding generated {len(embeddings)} embeddings")
    else:
        print(f"  ✗ Wrong number of embeddings: {len(embeddings)}")

    # Test query embedding
    query_embedding = embedder.embed_query("coffee shop purchases")

    if len(query_embedding) == 384:
        print("  ✓ Query embedding generated")
    else:
        print("  ✗ Query embedding failed")


def test_vector_store_operations():
    """Test vector store add, search, and retrieve operations."""
    print("\n=== Test: Vector Store Operations ===")

    # Create temporary directory for test
    temp_dir = tempfile.mkdtemp()
    vector_store = TransactionVectorStore(persist_directory=temp_dir)
    vector_store.create_collection()

    embedder = TransactionEmbedder()

    # Create sample transactions
    transactions = [
        {
            "transaction_token": "txn_001",
            "merchant_name": "Starbucks",
            "transaction_amount": 5.50,
            "transaction_type": "AUTHORIZATION",
            "user_token": "user_123"
        },
        {
            "transaction_token": "txn_002",
            "merchant_name": "Peet's Coffee",
            "transaction_amount": 6.00,
            "transaction_type": "AUTHORIZATION",
            "user_token": "user_123"
        },
        {
            "transaction_token": "txn_003",
            "merchant_name": "Shell Gas Station",
            "transaction_amount": 45.00,
            "transaction_type": "AUTHORIZATION",
            "user_token": "user_456"
        }
    ]

    # Generate embeddings
    embeddings = embedder.embed_transactions_batch(transactions)

    # Add to vector store
    count = vector_store.add_transactions(transactions, embeddings)

    if count == 3:
        print(f"  ✓ Added {count} transactions to vector store")
    else:
        print(f"  ✗ Expected 3, got {count}")

    # Test search with query
    query_embedding = embedder.embed_query("coffee")
    results = vector_store.search(query_embedding, n_results=2)

    print(f"  Search results: {results['count']} found")
    if results['count'] > 0:
        top_result = results['transactions'][0]
        print(f"  Top result: {top_result.get('metadata', {}).get('merchant_name', 'N/A')}")
        print(f"  Similarity: {top_result.get('similarity_score', 0):.3f}")

        # Coffee shops should rank higher than gas station
        if "coffee" in top_result.get('metadata', {}).get('merchant_name', '').lower() or \
           "starbucks" in top_result.get('metadata', {}).get('merchant_name', '').lower():
            print("  ✓ Semantic search working correctly")
        else:
            print("  ✗ Top result not coffee-related")
    else:
        print("  ✗ No search results")

    # Test get by ID
    retrieved = vector_store.get_by_id("txn_001")
    if retrieved and retrieved["transaction_token"] == "txn_001":
        print("  ✓ Retrieved transaction by ID")
    else:
        print("  ✗ Failed to retrieve by ID")

    # Test stats
    stats = vector_store.get_stats()
    print(f"  Stats: {stats['count']} transactions, status: {stats['status']}")

    if stats['count'] == 3:
        print("  ✓ Stats correct")
    else:
        print(f"  ✗ Wrong count in stats: {stats['count']}")

    # Cleanup
    vector_store.clear()
    import shutil
    shutil.rmtree(temp_dir)


def test_similarity_search():
    """Test that similar transactions are found correctly."""
    print("\n=== Test: Similarity Search ===")

    temp_dir = tempfile.mkdtemp()
    vector_store = TransactionVectorStore(persist_directory=temp_dir)
    vector_store.create_collection()

    embedder = TransactionEmbedder()

    # Create transactions with varying similarity
    transactions = [
        {"transaction_token": "coffee_1", "merchant_name": "Starbucks", "transaction_amount": 5.00},
        {"transaction_token": "coffee_2", "merchant_name": "Dunkin Donuts", "transaction_amount": 4.50},
        {"transaction_token": "coffee_3", "merchant_name": "Peet's Coffee", "transaction_amount": 6.00},
        {"transaction_token": "gas_1", "merchant_name": "Shell Gas", "transaction_amount": 40.00},
        {"transaction_token": "grocery_1", "merchant_name": "Whole Foods", "transaction_amount": 85.00},
    ]

    embeddings = embedder.embed_transactions_batch(transactions)
    vector_store.add_transactions(transactions, embeddings)

    # Search for coffee-related transactions
    query_embedding = embedder.embed_query("coffee shop")
    results = vector_store.search(query_embedding, n_results=3)

    print(f"  Found {results['count']} results for 'coffee shop':")
    coffee_count = 0
    for i, txn in enumerate(results['transactions'][:3]):
        merchant = txn.get('metadata', {}).get('merchant_name', '')
        score = txn.get('similarity_score', 0)
        print(f"    {i+1}. {merchant} (score: {score:.3f})")

        if "coffee" in merchant.lower() or "starbucks" in merchant.lower() or "dunkin" in merchant.lower():
            coffee_count += 1

    if coffee_count >= 2:
        print(f"  ✓ Found {coffee_count}/3 coffee-related merchants in top 3")
    else:
        print(f"  ✗ Only found {coffee_count} coffee-related merchants")

    # Cleanup
    vector_store.clear()
    import shutil
    shutil.rmtree(temp_dir)


def test_metadata_filtering():
    """Test that metadata filters work correctly."""
    print("\n=== Test: Metadata Filtering ===")

    temp_dir = tempfile.mkdtemp()
    vector_store = TransactionVectorStore(persist_directory=temp_dir)
    vector_store.create_collection()

    embedder = TransactionEmbedder()

    # Create transactions with different amounts
    transactions = [
        {
            "transaction_token": "small_1",
            "merchant_name": "Coffee Shop A",
            "transaction_amount": 5.00,
            "user_token": "user_123"
        },
        {
            "transaction_token": "small_2",
            "merchant_name": "Coffee Shop B",
            "transaction_amount": 6.00,
            "user_token": "user_123"
        },
        {
            "transaction_token": "large_1",
            "merchant_name": "Coffee Shop C",
            "transaction_amount": 50.00,
            "user_token": "user_456"
        },
    ]

    embeddings = embedder.embed_transactions_batch(transactions)
    vector_store.add_transactions(transactions, embeddings)

    # Search with amount filter
    query_embedding = embedder.embed_query("coffee")
    results = vector_store.search(
        query_embedding,
        n_results=10,
        where={"transaction_amount": {"$lt": 10.0}}  # Less than $10
    )

    print(f"  Found {results['count']} transactions under $10")
    for txn in results['transactions']:
        amount = txn.get('metadata', {}).get('transaction_amount', 0)
        print(f"    - ${amount}")

    if results['count'] == 2:
        print("  ✓ Metadata filtering working")
    else:
        print(f"  ✗ Expected 2 results, got {results['count']}")

    # Cleanup
    vector_store.clear()
    import shutil
    shutil.rmtree(temp_dir)


if __name__ == "__main__":
    print("=" * 60)
    print("RAG Functionality Tests")
    print("=" * 60)

    test_transaction_text_formatting()
    test_embedding_generation()
    test_vector_store_operations()
    test_similarity_search()
    test_metadata_filtering()

    print("\n" * 2 + "=" * 60)
    print("All RAG tests completed!")
    print("=" * 60)
    print("\nNote: These tests use the actual embedding model and vector store.")
    print("First run will download the model (~90MB).")
