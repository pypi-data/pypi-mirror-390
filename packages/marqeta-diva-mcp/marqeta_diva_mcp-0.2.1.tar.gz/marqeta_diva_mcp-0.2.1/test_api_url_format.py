#!/usr/bin/env python3
"""Verify that the URL format matches DiVA API documentation examples."""

from urllib.parse import urlencode
from src.marqeta_diva_mcp.client import DiVAClient


def test_url_format_matches_docs():
    """Verify URL format matches documentation examples."""
    print("\n=== Testing URL Format Against DiVA API Docs ===\n")

    client = DiVAClient("test_app", "test_access", "test_program")

    # Example from docs:
    # /views/authorizations/detail?program=myprogram&transaction_timestamp=2023-10-21&sort_by=-request_amount&count=100
    print("Example 1 from docs:")
    print("  /views/authorizations/detail?program=myprogram&transaction_timestamp=2023-10-21&sort_by=-request_amount&count=100\n")

    params = client._build_query_params(
        program="myprogram",
        filters={"transaction_timestamp": "2023-10-21"},
        sort_by="-request_amount",
        count=100
    )

    expected = {
        "program": "myprogram",
        "transaction_timestamp": "2023-10-21",
        "sort_by": "-request_amount",
        "count": "100"
    }

    print("Generated params:")
    for key, value in params.items():
        print(f"  {key}: {value}")

    print("\nURL would be:")
    print(f"  /views/authorizations/detail?{urlencode(params)}\n")

    # Check all expected params are present
    for key, expected_value in expected.items():
        if key not in params:
            print(f"❌ FAIL: Missing key '{key}'")
            return False
        if params[key] != expected_value:
            print(f"❌ FAIL: Wrong value for '{key}': expected '{expected_value}', got '{params[key]}'")
            return False

    print("✅ PASS: URL format matches documentation\n")

    # Example 2: Date range with greater-than operator
    print("=" * 70)
    print("Example 2: Date range with >= operator")
    print("  transaction_timestamp=>=2025-10-20\n")

    params = client._build_query_params(
        filters={"transaction_timestamp": ">=2025-10-20"}
    )

    if params.get("transaction_timestamp") != ">=2025-10-20":
        print(f"❌ FAIL: Operator not preserved: {params.get('transaction_timestamp')}")
        return False

    print("Generated params:")
    print(f"  transaction_timestamp: {params['transaction_timestamp']}")
    print(f"\nURL would be:")
    print(f"  /views/authorizations/detail?{urlencode(params)}\n")
    print("✅ PASS: >= operator preserved correctly\n")

    # Example 3: Date range with .. operator
    print("=" * 70)
    print("Example 3: Date range with .. operator (from docs)")
    print("  post_date=2023-02-01..2023-02-28\n")

    params = client._build_query_params(
        filters={"post_date": "2023-02-01..2023-02-28"}
    )

    if params.get("post_date") != "2023-02-01..2023-02-28":
        print(f"❌ FAIL: Range not preserved: {params.get('post_date')}")
        return False

    print("Generated params:")
    print(f"  post_date: {params['post_date']}")
    print(f"\nURL would be:")
    print(f"  /views/loads/day?{urlencode(params)}\n")
    print("✅ PASS: .. range operator preserved correctly\n")

    # Example 4: User's actual use case
    print("=" * 70)
    print("Example 4: User's actual use case")
    print("  Filter by business_user_token and date range\n")

    params = client._build_query_params(
        filters={
            "transaction_timestamp": ">=2025-10-20",
            "business_user_token": "c97bc74d-2489-4857-b8d1-8b2cb0c304c7"
        },
        count=1000
    )

    required_keys = ["program", "transaction_timestamp", "business_user_token", "count"]
    for key in required_keys:
        if key not in params:
            print(f"❌ FAIL: Missing required key '{key}'")
            return False

    # Verify no invalid keys
    invalid_keys = ["start_date", "end_date", "offset"]
    for key in invalid_keys:
        if key in params:
            print(f"❌ FAIL: Invalid key '{key}' found in params")
            return False

    print("Generated params:")
    for key, value in params.items():
        print(f"  {key}: {value}")

    print(f"\nURL would be:")
    print(f"  /views/authorizations/detail?{urlencode(params)}\n")
    print("✅ PASS: User's use case generates correct URL\n")

    return True


def main():
    print("=" * 70)
    print("DiVA API URL Format Validation")
    print("=" * 70)

    try:
        result = test_url_format_matches_docs()
        if result:
            print("=" * 70)
            print("✅ ALL URL FORMAT TESTS PASSED")
            print("=" * 70)
            print("\nThe generated URLs match the DiVA API documentation examples.")
            print("Your index_transactions call should work correctly now!")
            return 0
        else:
            print("=" * 70)
            print("❌ URL FORMAT TESTS FAILED")
            print("=" * 70)
            return 1
    except Exception as e:
        print(f"\n❌ EXCEPTION: {e}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    import sys
    sys.exit(main())
