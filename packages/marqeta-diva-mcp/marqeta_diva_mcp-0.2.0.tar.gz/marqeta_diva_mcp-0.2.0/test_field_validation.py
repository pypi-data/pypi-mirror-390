#!/usr/bin/env python3
"""Test to diagnose the field validation issue."""

import os
from src.marqeta_diva_mcp.client import DiVAClient


def test_business_user_token_field():
    """Check if business_user_token is a valid field."""

    # You need actual credentials for this test
    app_token = os.getenv("MARQETA_APP_TOKEN")
    access_token = os.getenv("MARQETA_ACCESS_TOKEN")
    program = os.getenv("MARQETA_PROGRAM")

    if not all([app_token, access_token, program]):
        print("⚠️  Missing credentials. Set MARQETA_APP_TOKEN, MARQETA_ACCESS_TOKEN, MARQETA_PROGRAM")
        print("   Skipping API test.")
        return

    print("\n=== Testing Field Validation ===\n")

    client = DiVAClient(app_token, access_token, program)

    # First, get the schema to see available fields
    print("Fetching authorizations schema...")
    try:
        schema = client.get_view_schema("authorizations", "detail")

        print(f"\nFound {len(schema)} fields in schema")
        print("\nSearching for 'business' related fields:")

        business_fields = [f["field"] for f in schema if "business" in f["field"].lower()]
        if business_fields:
            print("  Found:", ", ".join(business_fields))
        else:
            print("  No fields with 'business' in the name")

        print("\nSearching for 'user' related fields:")
        user_fields = [f["field"] for f in schema if "user" in f["field"].lower()]
        if user_fields:
            print("  Found:", ", ".join(user_fields))
        else:
            print("  No fields with 'user' in the name")

        print("\nSearching for 'token' related fields:")
        token_fields = [f["field"] for f in schema if "token" in f["field"].lower()]
        if token_fields:
            print("  Found:", ", ".join(token_fields))
        else:
            print("  No fields with 'token' in the name")

        # Check if business_user_token exists
        field_names = [f["field"] for f in schema]
        if "business_user_token" in field_names:
            print("\n✅ business_user_token IS a valid field")
        else:
            print("\n❌ business_user_token is NOT in the schema")
            print("\n   Possible alternatives:")
            # Look for similar fields
            for field in field_names:
                if any(word in field.lower() for word in ["business", "user", "token"]):
                    print(f"   - {field}")

    except Exception as e:
        print(f"❌ Error fetching schema: {e}")
        import traceback
        traceback.print_exc()


def test_without_validation():
    """Test if we can bypass validation."""

    print("\n=== Testing Direct API Call (No Validation) ===\n")

    app_token = os.getenv("MARQETA_APP_TOKEN")
    access_token = os.getenv("MARQETA_ACCESS_TOKEN")
    program = os.getenv("MARQETA_PROGRAM")

    if not all([app_token, access_token, program]):
        print("⚠️  Skipping - no credentials")
        return

    client = DiVAClient(app_token, access_token, program)

    # Build params directly without going through get_view
    params = client._build_query_params(
        filters={
            "transaction_timestamp": ">=2025-10-20",
            "business_user_token": "c97bc74d-2489-4857-b8d1-8b2cb0c304c7"
        },
        count=10
    )

    print("Generated params:")
    for key, value in params.items():
        print(f"  {key}: {value}")

    # Try making the request directly
    print("\nAttempting direct API call...")
    try:
        endpoint = "/views/authorizations/detail"
        result = client._make_request(endpoint, params)
        print(f"✅ SUCCESS! Got {result.get('count', 0)} records")
    except Exception as e:
        print(f"❌ FAILED: {e}")


if __name__ == "__main__":
    print("=" * 70)
    print("Field Validation Diagnostic")
    print("=" * 70)

    test_business_user_token_field()
    test_without_validation()

    print("\n" + "=" * 70)
    print("Diagnostic Complete")
    print("=" * 70)
