#!/usr/bin/env python3
"""Test index_transactions with debug logging."""

import sys
from marqeta_diva_mcp.client import DiVAClient
from marqeta_diva_mcp import rag_tools

# Credentials from .mcp.json
app_token = "fd2c22d1-8daa-45ce-863d-a82daf6d7262"
access_token = "6e23f40f-bab6-4456-98ee-35b190223fb9"
program = "flyaddbn"

print("=" * 80)
print("Testing index_transactions with debug logging")
print("=" * 80)

# Create client
client = DiVAClient(app_token, access_token, program)

# Test filters that work with get_authorizations
filters = {
    "business_user_token": "c97bc74d-2489-4857-b8d1-8b2cb0c304c7",
    "transaction_timestamp": ">=2025-10-20"
}

print(f"\nCalling index_transactions with filters: {filters}")
print("-" * 80)

# Call index_transactions
result = rag_tools.index_transactions(
    diva_client=client,
    view_name="authorizations",
    aggregation="detail",
    filters=filters,
    max_records=100  # Limit to 100 for testing
)

print("-" * 80)
print(f"\nResult: {result}")
print("=" * 80)
