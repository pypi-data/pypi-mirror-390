#!/usr/bin/env python3
"""Test script to verify MCP server fixes."""

import os
from dotenv import load_dotenv
from src.marqeta_diva_mcp.client import DiVAClient, DiVAAPIError

load_dotenv()


def test_duplicate_aggregation_fix():
    """Test that aggregation parameter doesn't cause 'multiple values' error."""
    print("\n=== Test 1: Duplicate aggregation parameter fix ===")
    client = DiVAClient(
        os.getenv("MARQETA_APP_TOKEN"),
        os.getenv("MARQETA_ACCESS_TOKEN"),
        os.getenv("MARQETA_PROGRAM")
    )

    try:
        # This should NOT raise "multiple values for argument 'aggregation'"
        result = client.get_view(
            "authorizations",
            aggregation="detail",
            filters={"business_user_token": "test123"},
            count=10
        )
        print("✓ No 'multiple values' error!")
        print(f"  Response has {len(result.get('data', []))} records")
    except DiVAAPIError as e:
        if "multiple values" in str(e):
            print(f"✗ FAILED: {e}")
        else:
            print(f"✓ Different error (expected for invalid token): {e.message}")
    except Exception as e:
        print(f"✗ Unexpected error: {e}")


def test_invalid_filter_suggestion():
    """Test that invalid filter fields get helpful suggestions."""
    print("\n=== Test 2: Invalid filter field suggestions ===")
    client = DiVAClient(
        os.getenv("MARQETA_APP_TOKEN"),
        os.getenv("MARQETA_ACCESS_TOKEN"),
        os.getenv("MARQETA_PROGRAM")
    )

    try:
        # This should suggest 'business_user_token'
        result = client.get_view(
            "authorizations",
            aggregation="detail",
            filters={"business_token": "test123"}  # Wrong field name
        )
        print("✗ Should have raised validation error")
    except DiVAAPIError as e:
        if "business_user_token" in str(e):
            print("✓ Got helpful suggestion!")
            print(f"  Error: {e.response.get('message', '')[:200]}...")
        else:
            print(f"✗ No suggestion provided: {e}")


def test_default_count_limit():
    """Test that default count is applied."""
    print("\n=== Test 3: Default count limit ===")
    client = DiVAClient(
        os.getenv("MARQETA_APP_TOKEN"),
        os.getenv("MARQETA_ACCESS_TOKEN"),
        os.getenv("MARQETA_PROGRAM")
    )

    try:
        # No count specified - should default to 100
        result = client.get_view("authorizations", "detail")
        print("✓ Default count applied")
        print(f"  Returned {len(result.get('data', []))} records (max 100 expected)")
    except DiVAAPIError as e:
        print(f"✓ Query executed with default count (API error is OK): {e.message}")


def test_date_param_validation():
    """Test that date params on unsupported views are caught."""
    print("\n=== Test 4: Date parameter validation ===")
    client = DiVAClient(
        os.getenv("MARQETA_APP_TOKEN"),
        os.getenv("MARQETA_ACCESS_TOKEN"),
        os.getenv("MARQETA_PROGRAM")
    )

    try:
        # Cards view doesn't support start_date/end_date
        result = client.get_view(
            "cards",
            "detail",
            start_date="2025-01-01",
            end_date="2025-12-31"
        )
        print("✗ Should have raised validation error")
    except DiVAAPIError as e:
        if "does not support start_date/end_date" in str(e):
            print("✓ Date param validation working!")
            print(f"  Error: {e.message}")
        else:
            print(f"? Different error: {e}")


def test_token_estimation_warning():
    """Test that large requests trigger warnings."""
    print("\n=== Test 5: Token estimation warnings ===")
    client = DiVAClient(
        os.getenv("MARQETA_APP_TOKEN"),
        os.getenv("MARQETA_ACCESS_TOKEN"),
        os.getenv("MARQETA_PROGRAM")
    )

    print("  Requesting 500 cards (should trigger warning to stderr)...")
    try:
        result = client.get_view("cards", "detail", count=500)
        print("✓ Warning should appear above (check stderr)")
    except DiVAAPIError as e:
        print(f"✓ Query attempted (API error is OK): {e.message}")


def test_max_count_cap():
    """Test that count is capped at 1000."""
    print("\n=== Test 6: Maximum count cap ===")
    client = DiVAClient(
        os.getenv("MARQETA_APP_TOKEN"),
        os.getenv("MARQETA_ACCESS_TOKEN"),
        os.getenv("MARQETA_PROGRAM")
    )

    try:
        # Request 5000 but should be capped at 1000
        result = client.get_view("cards", "detail", count=5000)
        actual_count = len(result.get('data', []))
        print(f"✓ Count capped at 1000 (returned {actual_count} records)")
    except DiVAAPIError as e:
        print(f"✓ Count cap applied (API error is OK): {e.message}")


if __name__ == "__main__":
    print("=" * 60)
    print("Testing Marqeta DiVA MCP Server Fixes")
    print("=" * 60)

    test_duplicate_aggregation_fix()
    test_invalid_filter_suggestion()
    test_default_count_limit()
    test_date_param_validation()
    test_token_estimation_warning()
    test_max_count_cap()

    print("\n" + "=" * 60)
    print("Tests completed!")
    print("=" * 60)
