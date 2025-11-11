#!/usr/bin/env python3
"""Test correct date filtering behavior after removing start_date/end_date parameters."""

import sys
from src.marqeta_diva_mcp.client import DiVAClient


def test_build_query_params_no_start_end_date():
    """Verify start_date and end_date are NOT added to query params."""
    print("\n=== Test 1: Query params should NOT have start_date/end_date ===")

    client = DiVAClient("test_app", "test_access", "test_program")

    # Build params with filters
    params = client._build_query_params(
        filters={"transaction_timestamp": ">=2025-10-20", "business_user_token": "abc123"}
    )

    # Check that start_date and end_date are NOT in params
    if "start_date" in params:
        print(f"❌ FAIL: start_date should not be in params: {params}")
        return False
    if "end_date" in params:
        print(f"❌ FAIL: end_date should not be in params: {params}")
        return False

    print(f"✅ PASS: No start_date/end_date in params")
    print(f"   Generated params: {params}")
    return True


def test_filters_passed_correctly():
    """Verify filters are passed through correctly to URL params."""
    print("\n=== Test 2: Filters should be converted to URL params ===")

    client = DiVAClient("test_app", "test_access", "test_program")

    # Build params with date filter
    params = client._build_query_params(
        filters={
            "transaction_timestamp": ">=2025-10-20",
            "business_user_token": "c97bc74d-2489-4857-b8d1-8b2cb0c304c7"
        }
    )

    # Check that filters are converted to individual params
    if "transaction_timestamp" not in params:
        print(f"❌ FAIL: transaction_timestamp should be in params: {params}")
        return False

    if params["transaction_timestamp"] != ">=2025-10-20":
        print(f"❌ FAIL: transaction_timestamp value incorrect: {params['transaction_timestamp']}")
        return False

    if "business_user_token" not in params:
        print(f"❌ FAIL: business_user_token should be in params: {params}")
        return False

    print(f"✅ PASS: Filters converted correctly")
    print(f"   transaction_timestamp: {params['transaction_timestamp']}")
    print(f"   business_user_token: {params['business_user_token']}")
    return True


def test_date_range_syntax():
    """Test that date range syntax works correctly."""
    print("\n=== Test 3: Date range syntax (2025-10-01..2025-10-31) ===")

    client = DiVAClient("test_app", "test_access", "test_program")

    # Build params with date range
    params = client._build_query_params(
        filters={
            "transaction_timestamp": "2025-10-01..2025-10-31"
        }
    )

    if "transaction_timestamp" not in params:
        print(f"❌ FAIL: transaction_timestamp should be in params: {params}")
        return False

    if params["transaction_timestamp"] != "2025-10-01..2025-10-31":
        print(f"❌ FAIL: Date range not preserved: {params['transaction_timestamp']}")
        return False

    print(f"✅ PASS: Date range syntax preserved")
    print(f"   transaction_timestamp: {params['transaction_timestamp']}")
    return True


def test_count_defaults():
    """Verify count defaults to 10000."""
    print("\n=== Test 4: Count should default to 10000 ===")

    client = DiVAClient("test_app", "test_access", "test_program")

    # Build params without count
    params = client._build_query_params()

    if "count" not in params:
        print(f"❌ FAIL: count should be in params: {params}")
        return False

    if params["count"] != "10000":
        print(f"❌ FAIL: count should default to 10000, got: {params['count']}")
        return False

    print(f"✅ PASS: Count defaults to 10000")
    return True


def test_count_max_limit():
    """Verify count is capped at 10000."""
    print("\n=== Test 5: Count should be capped at 10000 ===")

    client = DiVAClient("test_app", "test_access", "test_program")

    # Try to set count higher than 10000
    params = client._build_query_params(count=50000)

    if params["count"] != "10000":
        print(f"❌ FAIL: count should be capped at 10000, got: {params['count']}")
        return False

    print(f"✅ PASS: Count capped at 10000")
    return True


def test_import_sys():
    """Verify sys is imported in client.py."""
    print("\n=== Test 6: sys module should be imported ===")

    try:
        from src.marqeta_diva_mcp import client
        if hasattr(client, 'sys'):
            print(f"✅ PASS: sys is imported in client module")
            return True
        else:
            # Check if sys is actually used in the module
            import inspect
            source = inspect.getsource(client)
            if 'import sys' in source:
                print(f"✅ PASS: sys is imported in client.py")
                return True
            else:
                print(f"❌ FAIL: sys not imported in client.py")
                return False
    except Exception as e:
        print(f"❌ FAIL: Error checking sys import: {e}")
        return False


def test_example_use_case():
    """Test the exact use case from the user's scenario."""
    print("\n=== Test 7: User's exact use case ===")

    client = DiVAClient("test_app", "test_access", "test_program")

    # Simulate the exact filters the user wants to use
    params = client._build_query_params(
        filters={
            "transaction_timestamp": ">=2025-10-20",
            "business_user_token": "c97bc74d-2489-4857-b8d1-8b2cb0c304c7"
        },
        count=100
    )

    expected_keys = ["program", "count", "transaction_timestamp", "business_user_token"]

    for key in expected_keys:
        if key not in params:
            print(f"❌ FAIL: Missing expected key '{key}' in params")
            return False

    # Verify invalid keys are NOT present
    invalid_keys = ["start_date", "end_date", "offset"]
    for key in invalid_keys:
        if key in params:
            print(f"❌ FAIL: Invalid key '{key}' should not be in params")
            return False

    print(f"✅ PASS: All expected params present, no invalid params")
    print(f"   Full params: {params}")
    return True


def main():
    print("=" * 70)
    print("Testing DiVA API Date Filtering Fixes")
    print("=" * 70)

    tests = [
        test_build_query_params_no_start_end_date,
        test_filters_passed_correctly,
        test_date_range_syntax,
        test_count_defaults,
        test_count_max_limit,
        test_import_sys,
        test_example_use_case,
    ]

    results = []
    for test in tests:
        try:
            result = test()
            results.append(result)
        except Exception as e:
            print(f"❌ EXCEPTION in {test.__name__}: {e}")
            import traceback
            traceback.print_exc()
            results.append(False)

    print("\n" + "=" * 70)
    print("SUMMARY")
    print("=" * 70)
    passed = sum(results)
    total = len(results)
    print(f"Tests passed: {passed}/{total}")

    if passed == total:
        print("\n✅ All tests passed! The fixes are working correctly.")
        print("\nYou can now use the API like this:")
        print("""
index_transactions(
    view_name="authorizations",
    filters={
        "transaction_timestamp": ">=2025-10-20",
        "business_user_token": "c97bc74d-2489-4857-b8d1-8b2cb0c304c7"
    }
)
""")
        return 0
    else:
        print(f"\n❌ {total - passed} test(s) failed. Review the output above.")
        return 1


if __name__ == "__main__":
    sys.exit(main())
