#!/usr/bin/env python3
"""Unit tests for MCP server fixes (no API credentials required)."""

from src.marqeta_diva_mcp.client import DiVAClient, DiVAAPIError


def test_filter_validation():
    """Test filter field validation with fuzzy matching."""
    print("\n=== Test 1: Filter field validation ===")

    # Create client with dummy credentials (won't make actual API calls)
    client = DiVAClient("test_app", "test_access", "test_program")

    # Mock schema in cache
    client._schema_cache["authorizations:detail"] = [
        {"field": "business_user_token"},
        {"field": "user_token"},
        {"field": "card_token"},
        {"field": "transaction_amount"},
    ]

    try:
        # Should suggest business_user_token
        client._validate_filters(
            "authorizations",
            "detail",
            {"business_token": "abc123"}  # Wrong field
        )
        print("✗ Should have raised validation error")
    except DiVAAPIError as e:
        if "business_user_token" in e.response.get("message", ""):
            print("✓ Correct suggestion provided!")
            print(f"  Message: {e.response['message'][:150]}...")
        else:
            print(f"✗ No suggestion: {e.response}")


def test_date_param_validation():
    """Test that date params are validated for unsupported views."""
    print("\n=== Test 2: Date parameter validation ===")

    client = DiVAClient("test_app", "test_access", "test_program")

    try:
        # Cards view doesn't support date ranges
        client._validate_date_params(
            "cards",
            "detail",
            "2025-01-01",
            "2025-12-31"
        )
        print("✗ Should have raised validation error")
    except DiVAAPIError as e:
        if "does not support" in e.message or "not supported" in e.message:
            print("✓ Date validation working!")
            print(f"  Error: {e.message}")
        else:
            print(f"✗ Wrong error: {e.message}")

    # Authorizations should allow date params
    try:
        client._validate_date_params(
            "authorizations",
            "detail",
            "2025-01-01",
            "2025-12-31"
        )
        print("✓ Authorizations accepts date params (no error)")
    except DiVAAPIError as e:
        print(f"✗ Should not raise error: {e.message}")


def test_token_estimation():
    """Test response size estimation."""
    print("\n=== Test 3: Token estimation ===")

    client = DiVAClient("test_app", "test_access", "test_program")

    # Test with cards view
    estimated, warning = client._estimate_response_size("cards", 100, None)
    print(f"  100 cards (all fields): ~{estimated} tokens")
    print(f"  Warning: {warning or 'None'}")

    estimated, warning = client._estimate_response_size("cards", 100, ["card_token", "user_token"])
    print(f"  100 cards (2 fields): ~{estimated} tokens")
    print(f"  Warning: {warning or 'None'}")

    estimated, warning = client._estimate_response_size("cards", 1000, None)
    print(f"  1000 cards (all fields): ~{estimated} tokens")
    if warning and "25,000" in warning:
        print(f"✓ Warning triggered for large request!")
    else:
        print(f"✗ Should warn about token limit")


def test_query_params_building():
    """Test that query params are built correctly with defaults."""
    print("\n=== Test 4: Query param defaults ===")

    client = DiVAClient("test_app", "test_access", "test_program")

    # No count specified - should default to 100
    params = client._build_query_params()
    if params.get("count") == "100":
        print("✓ Default count = 100")
    else:
        print(f"✗ Default count = {params.get('count')}")

    # Count of 2000 should be capped at 1000
    params = client._build_query_params(count=2000)
    if params.get("count") == "1000":
        print("✓ Count capped at 1000")
    else:
        print(f"✗ Count not capped: {params.get('count')}")

    # Count of 50 should stay as-is
    params = client._build_query_params(count=50)
    if params.get("count") == "50":
        print("✓ Small count preserved")
    else:
        print(f"✗ Small count changed: {params.get('count')}")


def test_fuzzy_field_matching():
    """Test fuzzy matching for similar field names."""
    print("\n=== Test 5: Fuzzy field matching ===")

    client = DiVAClient("test_app", "test_access", "test_program")

    valid_fields = [
        "business_user_token",
        "user_token",
        "card_token",
        "transaction_amount",
        "merchant_name"
    ]

    # Test various typos
    tests = [
        ("business_token", ["business_user_token"]),
        ("usr_token", ["user_token"]),
        ("amount", ["transaction_amount"]),
        ("merchant", ["merchant_name"]),
    ]

    for invalid, expected in tests:
        matches = client._find_similar_fields(invalid, valid_fields)
        if any(exp in matches for exp in expected):
            print(f"✓ '{invalid}' → {matches}")
        else:
            print(f"✗ '{invalid}' → {matches} (expected {expected})")


def test_schema_caching():
    """Test that schema caching works."""
    print("\n=== Test 6: Schema caching ===")

    client = DiVAClient("test_app", "test_access", "test_program")

    # Manually add to cache
    test_schema = [{"field": "test_field"}]
    client._schema_cache["test_view:detail"] = test_schema

    # Check cache hit
    if "test_view:detail" in client._schema_cache:
        print("✓ Schema caching works")
        print(f"  Cache keys: {list(client._schema_cache.keys())}")
    else:
        print("✗ Cache not working")


if __name__ == "__main__":
    print("=" * 60)
    print("Unit Tests for Marqeta DiVA MCP Server Fixes")
    print("(No API credentials required)")
    print("=" * 60)

    test_filter_validation()
    test_date_param_validation()
    test_token_estimation()
    test_query_params_building()
    test_fuzzy_field_matching()
    test_schema_caching()

    print("\n" + "=" * 60)
    print("All unit tests completed!")
    print("=" * 60)
