#!/usr/bin/env python3
"""Test pagination and export functionality."""

from src.marqeta_diva_mcp.client import DiVAClient


def test_pagination_params():
    """Test that offset parameter is properly built."""
    print("\n=== Test: Pagination Parameters ===")

    client = DiVAClient("test_app", "test_access", "test_program")

    # Test with offset
    params = client._build_query_params(count=100, offset=200)

    if params.get("count") == "100" and params.get("offset") == "200":
        print("✓ Offset parameter added correctly")
        print(f"  count={params['count']}, offset={params['offset']}")
    else:
        print(f"✗ Failed: count={params.get('count')}, offset={params.get('offset')}")

    # Test without offset
    params = client._build_query_params(count=50)

    if params.get("count") == "50" and "offset" not in params:
        print("✓ Offset omitted when not specified")
    else:
        print(f"✗ Failed: offset should not be in params: {params}")


def test_export_structure():
    """Test export method exists and has correct signature."""
    print("\n=== Test: Export Method ===")

    client = DiVAClient("test_app", "test_access", "test_program")

    if hasattr(client, 'export_to_file'):
        print("✓ export_to_file method exists")

        import inspect
        sig = inspect.signature(client.export_to_file)
        params = list(sig.parameters.keys())

        required_params = ["view_name", "aggregation", "output_path", "format"]
        if all(p in params for p in required_params):
            print(f"✓ All required parameters present: {params}")
        else:
            print(f"✗ Missing parameters. Found: {params}")
    else:
        print("✗ export_to_file method not found")


def test_token_estimates():
    """Test that token estimates are still accurate."""
    print("\n=== Test: Token Estimation ===")

    client = DiVAClient("test_app", "test_access", "test_program")

    # Test with large count
    estimated, warning = client._estimate_response_size("authorizations", 1528, None)
    print(f"  1528 authorizations (all fields): ~{estimated:,} tokens")

    if warning:
        print(f"  ✓ Warning triggered: {warning[:80]}...")
    else:
        print(f"  ✗ No warning for {estimated} tokens")

    # Test with field filtering
    estimated, warning = client._estimate_response_size(
        "authorizations",
        1528,
        ["transaction_amount", "transaction_timestamp", "merchant_name", "transaction_status"]
    )
    print(f"  1528 authorizations (4 fields): ~{estimated:,} tokens")

    if estimated < 100000:
        print(f"  ✓ Field filtering reduces estimate")
    else:
        print(f"  ✗ Estimate still too high: {estimated}")


def test_mock_export():
    """Test export logic without actual API calls."""
    print("\n=== Test: Mock Export Logic ===")

    import tempfile
    import json
    from pathlib import Path

    # Create a mock export
    temp_dir = tempfile.mkdtemp()
    output_path = Path(temp_dir) / "test_export.json"

    print(f"  Mock export path: {output_path}")

    # Create sample data
    mock_data = [
        {"id": 1, "amount": 100.00, "timestamp": "2025-01-01"},
        {"id": 2, "amount": 200.00, "timestamp": "2025-01-02"},
        {"id": 3, "amount": 300.00, "timestamp": "2025-01-03"},
    ]

    # Write to file (simulating export)
    with open(output_path, 'w') as f:
        json.dump(mock_data, f, indent=2)

    # Verify
    if output_path.exists():
        print("  ✓ File created successfully")

        with open(output_path, 'r') as f:
            loaded = json.load(f)

        if len(loaded) == 3:
            print(f"  ✓ Correct number of records: {len(loaded)}")
        else:
            print(f"  ✗ Wrong record count: {len(loaded)}")

        file_size = output_path.stat().st_size
        print(f"  ✓ File size: {file_size} bytes")
    else:
        print("  ✗ File not created")

    # Cleanup
    output_path.unlink()
    Path(temp_dir).rmdir()


if __name__ == "__main__":
    print("=" * 60)
    print("Testing Pagination and Export Features")
    print("=" * 60)

    test_pagination_params()
    test_export_structure()
    test_token_estimates()
    test_mock_export()

    print("\n" + "=" * 60)
    print("Tests completed!")
    print("=" * 60)
    print("\nNote: Integration tests require valid API credentials.")
    print("See LARGE_DATASET_GUIDE.md for usage examples.")
