#!/usr/bin/env python3
"""Test get_view directly with same filters."""

import sys
from marqeta_diva_mcp.client import DiVAClient

# Credentials from .mcp.json
app_token = "fd2c22d1-8daa-45ce-863d-a82daf6d7262"
access_token = "6e23f40f-bab6-4456-98ee-35b190223fb9"
program = "flyaddbn"

print("=" * 80)
print("Testing get_view directly with debug logging")
print("=" * 80)

# Create client
client = DiVAClient(app_token, access_token, program)

# Test filters that work with get_authorizations
filters = {
    "business_user_token": "c97bc74d-2489-4857-b8d1-8b2cb0c304c7",
    "transaction_timestamp": ">=2025-10-20"
}

print(f"\nCalling get_view with filters: {filters}")
print("-" * 80)

# Call get_view directly (this is what sync_transactions calls internally)
result = client.get_view(
    view_name="authorizations",
    aggregation="detail",
    filters=filters,
    count=100
)

print("-" * 80)
print(f"\nTotal records: {result.get('count', 0)}")
print(f"Is more: {result.get('is_more', False)}")
print(f"Records length: {len(result.get('records', []))}")
if result.get('records'):
    print(f"First record keys: {list(result['records'][0].keys())[:10]}")
print("=" * 80)
