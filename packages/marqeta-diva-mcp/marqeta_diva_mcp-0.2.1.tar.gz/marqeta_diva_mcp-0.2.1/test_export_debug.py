#!/usr/bin/env python3
"""Test export_view_to_file with debug logging."""

import sys
import json
from marqeta_diva_mcp.client import DiVAClient

# Credentials from .mcp.json
app_token = "fd2c22d1-8daa-45ce-863d-a82daf6d7262"
access_token = "6e23f40f-bab6-4456-98ee-35b190223fb9"
program = "flyaddbn"

print("=" * 80)
print("Testing export_view_to_file with debug logging")
print("=" * 80)

# Create client
client = DiVAClient(app_token, access_token, program)

# Test filters that work with get_authorizations
filters = {
    "business_user_token": "c97bc74d-2489-4857-b8d1-8b2cb0c304c7",
    "transaction_timestamp": ">=2025-10-20"
}

output_path = "/tmp/test_export.json"

print(f"\nCalling export_to_file with filters: {filters}")
print(f"Output path: {output_path}")
print("-" * 80)

# Call export_to_file
result = client.export_to_file(
    view_name="authorizations",
    aggregation="detail",
    output_path=output_path,
    format="json",
    filters=filters,
    max_records=50
)

print("-" * 80)
print(f"\nResult: {result}")

# Verify the file
with open(output_path, 'r') as f:
    data = json.load(f)
    print(f"File contains {len(data)} records")
    if data:
        print(f"First record keys: {list(data[0].keys())[:10]}")

print("=" * 80)
