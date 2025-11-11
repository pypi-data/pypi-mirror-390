"""Marqeta DiVA API MCP Server."""

import asyncio
import os
import sys
from typing import Any, Dict, List, Optional

from dotenv import load_dotenv
from mcp.server import Server
from mcp.types import Tool, TextContent
import mcp.server.stdio

from .client import DiVAClient, DiVAAPIError

# Load environment variables
load_dotenv()

# Version identifier to verify server restarts
SERVER_VERSION = "0.2.1"

# Check if local storage features are enabled
def is_local_storage_enabled() -> bool:
    """Check if local storage and RAG features are enabled."""
    enabled = os.getenv("ENABLE_LOCAL_STORAGE", "false").lower() in ("true", "1", "yes")
    return enabled

# Conditionally import RAG tools
RAG_AVAILABLE = False
rag_tools = None

if is_local_storage_enabled():
    try:
        from . import rag_tools
        RAG_AVAILABLE = True
        print("[MCP Server] Local storage and RAG features ENABLED", file=sys.stderr)
    except ImportError as e:
        print(f"[MCP Server] WARNING: ENABLE_LOCAL_STORAGE=true but RAG dependencies not installed.", file=sys.stderr)
        print(f"[MCP Server] Install with: pip install marqeta-diva-mcp[rag]", file=sys.stderr)
        print(f"[MCP Server] Error: {e}", file=sys.stderr)
        RAG_AVAILABLE = False
else:
    print("[MCP Server] Local storage and RAG features DISABLED (set ENABLE_LOCAL_STORAGE=true to enable)", file=sys.stderr)

# Initialize MCP server
app = Server("marqeta-diva-mcp")

# Log version on startup
print(f"[MCP Server] Starting version {SERVER_VERSION}", file=sys.stderr)

# Global client instance
_client: Optional[DiVAClient] = None


def get_client() -> DiVAClient:
    """Get or create the DiVA API client."""
    global _client
    if _client is None:
        app_token = os.getenv("MARQETA_APP_TOKEN")
        access_token = os.getenv("MARQETA_ACCESS_TOKEN")
        program = os.getenv("MARQETA_PROGRAM")

        if not app_token or not access_token or not program:
            raise ValueError(
                "Missing required environment variables: "
                "MARQETA_APP_TOKEN, MARQETA_ACCESS_TOKEN, MARQETA_PROGRAM"
            )

        _client = DiVAClient(app_token, access_token, program)
    return _client


def format_error(error: Exception) -> str:
    """Format an error message for display."""
    if isinstance(error, DiVAAPIError):
        msg = f"Error {error.status_code}: {error.message}"
        if error.response:
            msg += f"\nDetails: {error.response}"
        return msg
    return str(error)


def format_response(data: Dict[str, Any]) -> str:
    """Format API response for display."""
    import json
    return json.dumps(data, indent=2)


# Tool definitions
# Base tools available to all users
BASE_TOOLS = [
    # Transaction Tools
    Tool(
        name="get_authorizations",
        description=(
            "Get authorization transaction data. Includes authorization amounts, counts, "
            "acting users/cards, and merchant information. Supports detail, day, week, and month aggregation. "
            "Note: DiVA API limits results to 10,000 records per query. Use narrower date ranges or more specific filters for larger datasets."
        ),
        inputSchema={
            "type": "object",
            "properties": {
                "aggregation": {
                    "type": "string",
                    "enum": ["detail", "day", "week", "month"],
                    "default": "detail",
                    "description": "Aggregation level for the data",
                },
                "fields": {
                    "type": "array",
                    "items": {"type": "string"},
                    "description": "Specific fields to return (comma-separated)",
                },
                "filters": {
                    "type": "object",
                    "description": (
                        "Filters on data fields. For date filtering, use the actual date field name with operators. "
                        "Example: {'transaction_timestamp': '>=2023-10-20'} or {'transaction_timestamp': '2023-10-01..2023-10-31'}. "
                        "Do NOT include query parameters like 'count' or 'sort_by' in filters."
                    ),
                },
                "sort_by": {
                    "type": "string",
                    "description": "Field to sort by (prefix with - for descending)",
                },
                "count": {
                    "type": "integer",
                    "description": "Maximum number of records to return (up to 10,000, default 10,000)",
                },
                "program": {
                    "type": "string",
                    "description": "Override default program name",
                },
            },
        },
    ),
    Tool(
        name="get_settlements",
        description=(
            "Get settlement transaction data. Includes transaction status, post dates, "
            "purchase amounts, and network information. Supports detail, day, week, and month aggregation. "
            "Note: DiVA API limits results to 10,000 records per query. Use narrower date ranges or more specific filters for larger datasets."
        ),
        inputSchema={
            "type": "object",
            "properties": {
                "aggregation": {
                    "type": "string",
                    "enum": ["detail", "day", "week", "month"],
                    "default": "detail",
                    "description": "Aggregation level for the data",
                },
                "fields": {
                    "type": "array",
                    "items": {"type": "string"},
                    "description": "Specific fields to return",
                },
                "filters": {
                    "type": "object",
                    "description": (
                        "Filters on data fields. For date filtering, use actual date field names with operators. "
                        "Example: {'transaction_timestamp': '>=2023-10-20'}. Do NOT include query parameters like 'count' here."
                    ),
                },
                "sort_by": {"type": "string", "description": "Field to sort by"},
                "count": {"type": "integer", "description": "Maximum records to return (up to 10,000, default 10,000)"},
                "program": {"type": "string", "description": "Override default program"},
            },
        },
    ),
    Tool(
        name="get_clearings",
        description=(
            "Get clearing/reconciliation data. Provides accounting-level line items for "
            "the transaction lifecycle. Ideal for reconciliation. Supports detail, day, week, and month aggregation. "
            "Note: DiVA API limits results to 10,000 records per query. Use narrower date ranges or more specific filters for larger datasets."
        ),
        inputSchema={
            "type": "object",
            "properties": {
                "aggregation": {
                    "type": "string",
                    "enum": ["detail", "day", "week", "month"],
                    "default": "detail",
                    "description": "Aggregation level for the data",
                },
                "fields": {
                    "type": "array",
                    "items": {"type": "string"},
                    "description": "Specific fields to return",
                },
                "filters": {
                    "type": "object",
                    "description": "Filters on data fields. For date filtering, use actual date field names with operators (e.g., {'post_date': '>=2023-10-20'})"
                },
                "sort_by": {"type": "string", "description": "Field to sort by"},
                "count": {"type": "integer", "description": "Maximum records to return (up to 10,000, default 10,000)"},
                "program": {"type": "string", "description": "Override default program"},
            },
        },
    ),
    Tool(
        name="get_declines",
        description=(
            "Get declined transaction data. Includes transaction tokens, decline reasons, "
            "merchant information, and amounts. Supports detail, day, week, and month aggregation. "
            "Note: DiVA API limits results to 10,000 records per query. Use narrower date ranges or more specific filters for larger datasets."
        ),
        inputSchema={
            "type": "object",
            "properties": {
                "aggregation": {
                    "type": "string",
                    "enum": ["detail", "day", "week", "month"],
                    "default": "detail",
                    "description": "Aggregation level for the data",
                },
                "fields": {
                    "type": "array",
                    "items": {"type": "string"},
                    "description": "Specific fields to return",
                },
                "filters": {
                    "type": "object",
                    "description": "Filters on data fields. For date filtering, use actual date field names with operators (e.g., {'post_date': '>=2023-10-20'})"
                },
                "sort_by": {"type": "string", "description": "Field to sort by"},
                "count": {"type": "integer", "description": "Maximum records to return (up to 10,000, default 10,000)"},
                "program": {"type": "string", "description": "Override default program"},
            },
        },
    ),
    Tool(
        name="get_loads",
        description=(
            "Get load transaction data. Includes load amounts and transaction details. "
            "Note: DiVA API limits results to 10,000 records per query. Use narrower date ranges or more specific filters for larger datasets."
        ),
        inputSchema={
            "type": "object",
            "properties": {
                "aggregation": {
                    "type": "string",
                    "enum": ["detail", "day", "week", "month"],
                    "default": "detail",
                    "description": "Aggregation level for the data",
                },
                "fields": {
                    "type": "array",
                    "items": {"type": "string"},
                    "description": "Specific fields to return",
                },
                "filters": {
                    "type": "object",
                    "description": "Filters on data fields. For date filtering, use actual date field names with operators (e.g., {'post_date': '>=2023-10-20'})"
                },
                "sort_by": {"type": "string", "description": "Field to sort by"},
                "count": {"type": "integer", "description": "Maximum records to return (up to 10,000, default 10,000)"},
                "program": {"type": "string", "description": "Override default program"},
            },
        },
    ),
    # Financial Tools
    Tool(
        name="get_program_balances",
        description=(
            "Get program-level balance data. Includes beginning/ending bank balances, "
            "amounts to send/receive. Day-level aggregation only."
        ),
        inputSchema={
            "type": "object",
            "properties": {
                "fields": {
                    "type": "array",
                    "items": {"type": "string"},
                    "description": "Specific fields to return",
                },
                "filters": {
                    "type": "object",
                    "description": "Filters on data fields. For date filtering, use actual date field names with operators (e.g., {'post_date': '>=2023-10-20'})"
                },
                "sort_by": {"type": "string", "description": "Field to sort by"},
                "count": {"type": "integer", "description": "Maximum records to return (up to 10,000, default 10,000)"},
                "program": {"type": "string", "description": "Override default program"},
            },
        },
    ),
    Tool(
        name="get_program_balances_settlement",
        description=(
            "Get settlement-based program balance data. Includes settlement balance information "
            "and fund transfers. Day-level aggregation only."
        ),
        inputSchema={
            "type": "object",
            "properties": {
                "fields": {
                    "type": "array",
                    "items": {"type": "string"},
                    "description": "Specific fields to return",
                },
                "filters": {
                    "type": "object",
                    "description": "Filters on data fields. For date filtering, use actual date field names with operators (e.g., {'post_date': '>=2023-10-20'})"
                },
                "sort_by": {"type": "string", "description": "Field to sort by"},
                "count": {"type": "integer", "description": "Maximum records to return (up to 10,000, default 10,000)"},
                "program": {"type": "string", "description": "Override default program"},
            },
        },
    ),
    Tool(
        name="get_activity_balances",
        description=(
            "Get cardholder-level balance data. Includes individual cardholder balances, "
            "expandable by network. Day-level aggregation only."
        ),
        inputSchema={
            "type": "object",
            "properties": {
                "fields": {
                    "type": "array",
                    "items": {"type": "string"},
                    "description": "Specific fields to return",
                },
                "filters": {
                    "type": "object",
                    "description": "Filters on data fields. For date filtering, use actual date field names with operators (e.g., {'post_date': '>=2023-10-20'})"
                },
                "sort_by": {"type": "string", "description": "Field to sort by"},
                "count": {"type": "integer", "description": "Maximum records to return (up to 10,000, default 10,000)"},
                "expand": {
                    "type": "string",
                    "description": "Field to expand for more detail (e.g., network data)",
                },
                "program": {"type": "string", "description": "Override default program"},
            },
        },
    ),
    # Card & User Tools
    Tool(
        name="get_cards",
        description=(
            "Get card detail data. Includes user tokens, card state, active status, and UAI. "
            "Detail-level only. Supports filtering by user, state, etc. "
            "Note: DiVA API limits results to 10,000 records per query. Use narrower date ranges or more specific filters for larger datasets."
        ),
        inputSchema={
            "type": "object",
            "properties": {
                "fields": {
                    "type": "array",
                    "items": {"type": "string"},
                    "description": "Specific fields to return",
                },
                "filters": {
                    "type": "object",
                    "description": "Filters (e.g., {'state': 'ACTIVE', 'user_token': 'abc123'})",
                },
                "sort_by": {"type": "string", "description": "Field to sort by"},
                "count": {"type": "integer", "description": "Maximum records to return (up to 10,000, default 10,000)"},
                "program": {"type": "string", "description": "Override default program"},
            },
        },
    ),
    Tool(
        name="get_users",
        description=(
            "Get user detail data. Includes user tokens, UAI, and number of physical/virtual cards. "
            "Detail-level only. Note: DiVA API limits results to 10,000 records per query. Use more specific filters for larger datasets."
        ),
        inputSchema={
            "type": "object",
            "properties": {
                "fields": {
                    "type": "array",
                    "items": {"type": "string"},
                    "description": "Specific fields to return",
                },
                "filters": {
                    "type": "object",
                    "description": "Filters (e.g., {'user_token': 'abc123'})",
                },
                "sort_by": {"type": "string", "description": "Field to sort by"},
                "count": {"type": "integer", "description": "Maximum records to return (up to 10,000, default 10,000)"},
                "program": {"type": "string", "description": "Override default program"},
            },
        },
    ),
    # Chargeback Tools
    Tool(
        name="get_chargebacks_status",
        description=(
            "Get chargeback status data. Includes chargeback state, tokens, and "
            "provisional credit status."
        ),
        inputSchema={
            "type": "object",
            "properties": {
                "fields": {
                    "type": "array",
                    "items": {"type": "string"},
                    "description": "Specific fields to return",
                },
                "filters": {
                    "type": "object",
                    "description": "Filters on data fields. For date filtering, use actual date field names with operators (e.g., {'post_date': '>=2023-10-20'})"
                },
                "sort_by": {"type": "string", "description": "Field to sort by"},
                "count": {"type": "integer", "description": "Maximum records to return (up to 10,000, default 10,000)"},
                "program": {"type": "string", "description": "Override default program"},
            },
        },
    ),
    Tool(
        name="get_chargebacks_detail",
        description=(
            "Get detailed chargeback information. Includes transaction dates/types and "
            "comprehensive chargeback details."
        ),
        inputSchema={
            "type": "object",
            "properties": {
                "fields": {
                    "type": "array",
                    "items": {"type": "string"},
                    "description": "Specific fields to return",
                },
                "filters": {
                    "type": "object",
                    "description": "Filters on data fields. For date filtering, use actual date field names with operators (e.g., {'post_date': '>=2023-10-20'})"
                },
                "sort_by": {"type": "string", "description": "Field to sort by"},
                "count": {"type": "integer", "description": "Maximum records to return (up to 10,000, default 10,000)"},
                "program": {"type": "string", "description": "Override default program"},
            },
        },
    ),
    # Metadata Tools
    Tool(
        name="list_available_views",
        description=(
            "Get a list of all available DiVA API view endpoints with metadata. "
            "Useful for discovering available data sources."
        ),
        inputSchema={"type": "object", "properties": {}},
    ),
    Tool(
        name="get_view_schema",
        description=(
            "Get the schema definition for any view endpoint. Returns field names, "
            "data types, and descriptions."
        ),
        inputSchema={
            "type": "object",
            "required": ["view_name"],
            "properties": {
                "view_name": {
                    "type": "string",
                    "description": "Name of the view (e.g., 'authorizations', 'settlements', 'cards')",
                },
                "aggregation": {
                    "type": "string",
                    "enum": ["detail", "day", "week", "month"],
                    "default": "detail",
                    "description": "Aggregation level (if applicable)",
                },
            },
        },
    ),
    # Export Tools
    Tool(
        name="export_view_to_file",
        description=(
            "Export datasets to a file (JSON or CSV). Note: DiVA API limits results to 10,000 records per query. "
            "To get more data, use narrower date ranges or more specific filters and call multiple times. "
            "Supports all view types: authorizations, settlements, clearings, declines, loads, cards, users, etc."
        ),
        inputSchema={
            "type": "object",
            "required": ["view_name", "output_path"],
            "properties": {
                "view_name": {
                    "type": "string",
                    "description": "Name of the view (e.g., 'authorizations', 'settlements', 'cards')",
                },
                "aggregation": {
                    "type": "string",
                    "enum": ["detail", "day", "week", "month"],
                    "default": "detail",
                    "description": "Aggregation level",
                },
                "output_path": {
                    "type": "string",
                    "description": "File path where data will be written (e.g., './exports/authorizations.json')",
                },
                "format": {
                    "type": "string",
                    "enum": ["json", "csv"],
                    "default": "json",
                    "description": "Output file format",
                },
                "max_records": {
                    "type": "integer",
                    "description": "Maximum total records to export (omit to export all matching records)",
                },
                "fields": {
                    "type": "array",
                    "items": {"type": "string"},
                    "description": "Specific fields to include in export",
                },
                "filters": {
                    "type": "object",
                    "description": "Filters on data fields. For date filtering, use actual date field names with operators (e.g., {'transaction_timestamp': '>=2023-10-20'})",
                },
                "sort_by": {"type": "string", "description": "Field to sort by"},
                "program": {"type": "string", "description": "Override default program"},
            },
        },
    ),
    Tool(
        name="get_server_version",
        description=(
            "Get the MCP server version to verify it has been restarted with latest code changes."
        ),
        inputSchema={"type": "object", "properties": {}},
    ),
]

# RAG tools - only available when ENABLE_LOCAL_STORAGE=true
RAG_TOOLS = [
    Tool(
        name="index_transactions",
        description=(
            "Sync transactions from DiVA to local storage (SQLite + ChromaDB). "
            "Stores FULL transaction data locally and generates embeddings for semantic search. "
            "This eliminates token limits - query locally without MCP constraints! "
            "Must be called before using semantic search or local queries."
        ),
        inputSchema={
            "type": "object",
            "properties": {
                "view_name": {
                    "type": "string",
                    "default": "authorizations",
                    "description": "DiVA view to index (default: authorizations)",
                },
                "aggregation": {
                    "type": "string",
                    "enum": ["detail", "day", "week", "month"],
                    "default": "detail",
                    "description": "Aggregation level (default: detail)",
                },
                "filters": {
                    "type": "object",
                    "description": "Filters on data fields to limit which transactions to index. For date filtering, use actual date field names with operators (e.g., {'transaction_timestamp': '>=2023-10-20'})",
                },
                "max_records": {
                    "type": "integer",
                    "description": "Maximum records to index (up to 10,000 per query)",
                },
                "program": {"type": "string", "description": "Override default program"},
            },
        },
    ),
    Tool(
        name="semantic_search_transactions",
        description=(
            "Search transactions using natural language queries. "
            "Examples: 'coffee shop purchases', 'large transactions over $100', 'gas station visits'. "
            "Returns full transaction data from LOCAL storage (no API calls, no token limits!). "
            "Requires transactions to be synced first (use index_transactions)."
        ),
        inputSchema={
            "type": "object",
            "required": ["query"],
            "properties": {
                "query": {
                    "type": "string",
                    "description": "Natural language search query (e.g., 'coffee shop purchases')",
                },
                "n_results": {
                    "type": "integer",
                    "default": 10,
                    "description": "Number of results to return (default: 10)",
                },
                "filters": {
                    "type": "object",
                    "description": "Metadata filters to narrow search (e.g., amount range, date range)",
                },
                "enrich": {
                    "type": "boolean",
                    "default": True,
                    "description": "Include full transaction details from local storage (default: true)",
                },
            },
        },
    ),
    Tool(
        name="query_local_transactions",
        description=(
            "Query transactions directly from local SQLite storage using filters. "
            "No semantic search - just standard filtering (merchant, amount, date, etc.). "
            "Returns FULL transaction data with NO token limits or API calls. "
            "Perfect for LLM analysis of complete datasets. "
            "Supports pagination for large result sets."
        ),
        inputSchema={
            "type": "object",
            "properties": {
                "filters": {
                    "type": "object",
                    "description": (
                        "Filters using field names (e.g., {\"merchant_name\": \"Starbucks\", "
                        "\"transaction_amount\": {\">\": 10}}). "
                        "Operators: >, <, >=, <=, =, !=, like"
                    ),
                },
                "limit": {
                    "type": "integer",
                    "default": 100,
                    "description": "Maximum number of results (default: 100)",
                },
                "offset": {
                    "type": "integer",
                    "default": 0,
                    "description": "Offset for pagination in local SQLite storage (default: 0)",
                },
                "order_by": {
                    "type": "string",
                    "default": "created_time DESC",
                    "description": "SQL ORDER BY clause (default: 'created_time DESC')",
                },
            },
        },
    ),
    Tool(
        name="find_similar_transactions",
        description=(
            "Find transactions similar to a specific transaction. "
            "Useful for finding related purchases, duplicate transactions, or patterns. "
            "Requires the reference transaction to be indexed first."
        ),
        inputSchema={
            "type": "object",
            "required": ["transaction_token"],
            "properties": {
                "transaction_token": {
                    "type": "string",
                    "description": "Token of the reference transaction",
                },
                "n_results": {
                    "type": "integer",
                    "default": 10,
                    "description": "Number of similar transactions to return (default: 10)",
                },
                "filters": {
                    "type": "object",
                    "description": "Additional metadata filters",
                },
            },
        },
    ),
    Tool(
        name="get_index_stats",
        description=(
            "Get comprehensive statistics about local storage (SQLite + ChromaDB). "
            "Shows transaction counts, database size, embedding model info, and storage status. "
            "Useful for monitoring local data availability."
        ),
        inputSchema={"type": "object", "properties": {}},
    ),
    Tool(
        name="clear_index",
        description=(
            "Clear all transactions from the vector index. "
            "Use this to reset and start fresh. Cannot be undone."
        ),
        inputSchema={"type": "object", "properties": {}},
    ),
]

# Build the final TOOLS list dynamically based on feature flags
TOOLS = BASE_TOOLS.copy()
if RAG_AVAILABLE:
    TOOLS.extend(RAG_TOOLS)
    print(f"[MCP Server] Registered {len(BASE_TOOLS)} base tools + {len(RAG_TOOLS)} RAG tools = {len(TOOLS)} total tools", file=sys.stderr)
else:
    print(f"[MCP Server] Registered {len(BASE_TOOLS)} base tools (RAG tools disabled)", file=sys.stderr)


@app.list_tools()
async def list_tools() -> List[Tool]:
    """List all available tools."""
    return TOOLS


@app.call_tool()
async def call_tool(name: str, arguments: Any) -> List[TextContent]:
    """Handle tool calls."""
    try:
        client = get_client()

        # Transaction tools
        if name == "get_authorizations":
            aggregation = arguments.pop("aggregation", "detail")
            result = client.get_view("authorizations", aggregation, **arguments)
            return [TextContent(type="text", text=format_response(result))]

        elif name == "get_settlements":
            aggregation = arguments.pop("aggregation", "detail")
            result = client.get_view("settlements", aggregation, **arguments)
            return [TextContent(type="text", text=format_response(result))]

        elif name == "get_clearings":
            aggregation = arguments.pop("aggregation", "detail")
            result = client.get_view("clearing", aggregation, **arguments)
            return [TextContent(type="text", text=format_response(result))]

        elif name == "get_declines":
            aggregation = arguments.pop("aggregation", "detail")
            result = client.get_view("declines", aggregation, **arguments)
            return [TextContent(type="text", text=format_response(result))]

        elif name == "get_loads":
            aggregation = arguments.pop("aggregation", "detail")
            result = client.get_view("loads", aggregation, **arguments)
            return [TextContent(type="text", text=format_response(result))]

        # Financial tools
        elif name == "get_program_balances":
            result = client.get_view("programbalances", "day", **arguments)
            return [TextContent(type="text", text=format_response(result))]

        elif name == "get_program_balances_settlement":
            result = client.get_view("programbalancessettlement", "day", **arguments)
            return [TextContent(type="text", text=format_response(result))]

        elif name == "get_activity_balances":
            result = client.get_view("activitybalances", "day", **arguments)
            return [TextContent(type="text", text=format_response(result))]

        # Card & User tools
        elif name == "get_cards":
            result = client.get_view("cards", "detail", **arguments)
            return [TextContent(type="text", text=format_response(result))]

        elif name == "get_users":
            result = client.get_view("users", "detail", **arguments)
            return [TextContent(type="text", text=format_response(result))]

        # Chargeback tools
        elif name == "get_chargebacks_status":
            result = client.get_view("chargebacks", "status", **arguments)
            return [TextContent(type="text", text=format_response(result))]

        elif name == "get_chargebacks_detail":
            result = client.get_view("chargebacks", "detail", **arguments)
            return [TextContent(type="text", text=format_response(result))]

        # Metadata tools
        elif name == "list_available_views":
            result = client.get_views_list()
            return [TextContent(type="text", text=format_response(result))]

        elif name == "get_view_schema":
            view_name = arguments["view_name"]
            aggregation = arguments.pop("aggregation", "detail")
            result = client.get_view_schema(view_name, aggregation)
            return [TextContent(type="text", text=format_response(result))]

        # Export tool
        elif name == "export_view_to_file":
            view_name = arguments.pop("view_name")
            aggregation = arguments.pop("aggregation", "detail")
            output_path = arguments.pop("output_path")
            format_type = arguments.pop("format", "json")
            max_records = arguments.pop("max_records", None)

            result = client.export_to_file(
                view_name=view_name,
                aggregation=aggregation,
                output_path=output_path,
                format=format_type,
                max_records=max_records,
                **arguments
            )
            return [TextContent(type="text", text=format_response(result))]

        # RAG tools
        elif name == "index_transactions":
            if not RAG_AVAILABLE:
                return [TextContent(type="text", text=format_response({
                    "error": "Local storage features are not enabled",
                    "message": "To use this feature, set ENABLE_LOCAL_STORAGE=true in your environment and install RAG dependencies",
                    "install_command": "pip install marqeta-diva-mcp[rag]"
                }))]

            view_name = arguments.pop("view_name", "authorizations")
            aggregation = arguments.pop("aggregation", "detail")

            result = rag_tools.index_transactions(
                diva_client=client,
                view_name=view_name,
                aggregation=aggregation,
                **arguments
            )
            return [TextContent(type="text", text=format_response(result))]

        elif name == "semantic_search_transactions":
            if not RAG_AVAILABLE:
                return [TextContent(type="text", text=format_response({
                    "error": "Local storage features are not enabled",
                    "message": "To use this feature, set ENABLE_LOCAL_STORAGE=true in your environment and install RAG dependencies",
                    "install_command": "pip install marqeta-diva-mcp[rag]"
                }))]

            query = arguments.pop("query")
            n_results = arguments.pop("n_results", 10)
            filters = arguments.pop("filters", None)
            enrich = arguments.pop("enrich", True)

            result = rag_tools.semantic_search_transactions(
                diva_client=client,
                query=query,
                n_results=n_results,
                filters=filters,
                enrich=enrich
            )
            return [TextContent(type="text", text=format_response(result))]

        elif name == "query_local_transactions":
            if not RAG_AVAILABLE:
                return [TextContent(type="text", text=format_response({
                    "error": "Local storage features are not enabled",
                    "message": "To use this feature, set ENABLE_LOCAL_STORAGE=true in your environment and install RAG dependencies",
                    "install_command": "pip install marqeta-diva-mcp[rag]"
                }))]

            filters = arguments.pop("filters", None)
            limit = arguments.pop("limit", 100)
            offset = arguments.pop("offset", 0)
            order_by = arguments.pop("order_by", "created_time DESC")

            result = rag_tools.query_local_transactions(
                filters=filters,
                limit=limit,
                offset=offset,
                order_by=order_by
            )
            return [TextContent(type="text", text=format_response(result))]

        elif name == "find_similar_transactions":
            if not RAG_AVAILABLE:
                return [TextContent(type="text", text=format_response({
                    "error": "Local storage features are not enabled",
                    "message": "To use this feature, set ENABLE_LOCAL_STORAGE=true in your environment and install RAG dependencies",
                    "install_command": "pip install marqeta-diva-mcp[rag]"
                }))]

            transaction_token = arguments.pop("transaction_token")
            n_results = arguments.pop("n_results", 10)
            filters = arguments.pop("filters", None)

            result = rag_tools.find_similar_transactions(
                diva_client=client,
                transaction_token=transaction_token,
                n_results=n_results,
                filters=filters
            )
            return [TextContent(type="text", text=format_response(result))]

        elif name == "get_index_stats":
            if not RAG_AVAILABLE:
                return [TextContent(type="text", text=format_response({
                    "error": "Local storage features are not enabled",
                    "message": "To use this feature, set ENABLE_LOCAL_STORAGE=true in your environment and install RAG dependencies",
                    "install_command": "pip install marqeta-diva-mcp[rag]"
                }))]

            result = rag_tools.get_index_stats()
            return [TextContent(type="text", text=format_response(result))]

        elif name == "clear_index":
            if not RAG_AVAILABLE:
                return [TextContent(type="text", text=format_response({
                    "error": "Local storage features are not enabled",
                    "message": "To use this feature, set ENABLE_LOCAL_STORAGE=true in your environment and install RAG dependencies",
                    "install_command": "pip install marqeta-diva-mcp[rag]"
                }))]

            result = rag_tools.clear_index()
            return [TextContent(type="text", text=format_response(result))]

        elif name == "get_server_version":
            result = {
                "version": SERVER_VERSION,
                "message": "If you don't see version 0.2.0, the server needs to be restarted",
                "rag_features_enabled": RAG_AVAILABLE,
                "features": {
                    "base_tools": f"{len(BASE_TOOLS)} tools available",
                    "rag_tools": f"{len(RAG_TOOLS)} tools available" if RAG_AVAILABLE else "disabled (set ENABLE_LOCAL_STORAGE=true to enable)",
                },
                "fixes_included": [
                    "Removed non-existent start_date/end_date parameters",
                    "Added sys import to fix export errors",
                    "Updated to correct 10,000 record limit",
                    "Disabled client-side field validation",
                    "Fixed filter syntax for date fields",
                    "CRITICAL FIX: Changed 'data' to 'records' to match actual API response format",
                    "Fixed ChromaDB ID type error - convert integer IDs to strings",
                    "Made RAG features optional with ENABLE_LOCAL_STORAGE environment variable"
                ]
            }
            return [TextContent(type="text", text=format_response(result))]

        else:
            return [TextContent(type="text", text=f"Unknown tool: {name}")]

    except Exception as e:
        error_msg = format_error(e)
        return [TextContent(type="text", text=f"Error: {error_msg}")]


async def async_main():
    """Run the MCP server."""
    async with mcp.server.stdio.stdio_server() as (read_stream, write_stream):
        await app.run(
            read_stream,
            write_stream,
            app.create_initialization_options(),
        )


def main():
    """Entry point for the MCP server."""
    asyncio.run(async_main())


if __name__ == "__main__":
    main()
