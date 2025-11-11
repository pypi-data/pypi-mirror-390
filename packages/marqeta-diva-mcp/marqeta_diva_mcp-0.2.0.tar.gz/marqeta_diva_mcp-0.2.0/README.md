# Marqeta DiVA API MCP Server

[![PyPI version](https://badge.fury.io/py/marqeta-diva-mcp.svg)](https://badge.fury.io/py/marqeta-diva-mcp)
[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

A Model Context Protocol (MCP) server that provides programmatic access to the Marqeta DiVA (Data insights, Visualization, and Analytics) API. This server enables AI assistants and applications to retrieve aggregated production data from the Marqeta platform for reporting, analytics, and data-driven business decisions.

> **Note:** This is an unofficial community project and is not officially supported by Marqeta.

## Features

### Core Features (Always Available)
- **Transaction Data**: Access authorizations, settlements, clearings, declines, and loads
- **Financial Data**: Retrieve program balances, settlement balances, and activity balances
- **Card & User Data**: Get card and user details with flexible filtering
- **Chargeback Data**: Access chargeback status and detailed information
- **Metadata Tools**: Discover available views and retrieve schema definitions
- **Export Tools**: Export data to JSON or CSV files
- **Rate Limiting**: Built-in rate limiting to comply with API limits (300 requests per 5 minutes)
- **Error Handling**: Comprehensive error handling with meaningful messages
- **Flexible Querying**: Support for filtering, sorting, field selection, date ranges, and more

### Optional RAG Features (Requires `[rag]` extras)
- **Local Storage**: Store complete transaction data in SQLite (bypasses MCP token limits)
- **Semantic Search**: Natural language queries on transaction data using AI embeddings
- **Vector Store**: ChromaDB integration for similarity-based transaction search
- **Offline Analysis**: Query local data without API calls or token limits

## Prerequisites

- Python 3.10 or higher
- [uv](https://docs.astral.sh/uv/) package manager (for running with `uvx`)
- Marqeta DiVA API credentials (Application Token, Access Token, and Program Name)

## Installation

### Option 1: Run with uvx (Recommended)

No installation needed! `uvx` will automatically handle dependencies when you run the server.

**For basic features only:**
```bash
uvx marqeta-diva-mcp
```

**For RAG features (local storage + semantic search):**
```bash
uvx --with marqeta-diva-mcp[rag] marqeta-diva-mcp
```

### Option 2: Traditional Installation

**Basic installation (core features only):**
```bash
pip install marqeta-diva-mcp
```

**With RAG features (recommended for advanced analytics):**
```bash
pip install marqeta-diva-mcp[rag]
```

**From source:**
```bash
cd marqeta-diva-mcp
pip install -e .              # Basic features
pip install -e ".[rag]"       # With RAG features
```

## Configuration

1. Copy the example environment file:

```bash
cp .env.example .env
```

2. Edit `.env` and add your Marqeta DiVA API credentials:

```env
# Required: Marqeta DiVA API credentials
MARQETA_APP_TOKEN=your_application_token_here
MARQETA_ACCESS_TOKEN=your_access_token_here
MARQETA_PROGRAM=your_program_name_here

# Optional: Enable local storage and RAG features
# Requires: pip install marqeta-diva-mcp[rag]
# ENABLE_LOCAL_STORAGE=true
```

**How to obtain credentials:**
- Contact your Marqeta representative, OR
- Generate via Marqeta Dashboard (Reports section)

**Enabling RAG Features:**

To use local storage, semantic search, and other RAG features:

1. Install RAG dependencies: `pip install marqeta-diva-mcp[rag]`
2. Set environment variable: `ENABLE_LOCAL_STORAGE=true`
3. Restart the MCP server

When enabled, you'll see this message in the logs:
```
[MCP Server] Local storage and RAG features ENABLED
```

When disabled (default):
```
[MCP Server] Local storage and RAG features DISABLED (set ENABLE_LOCAL_STORAGE=true to enable)
```

## Usage

### Running the Server Locally

#### With uvx (Recommended)

```bash
cd marqeta-diva-mcp
uvx marqeta-diva-mcp
```

#### With Python

```bash
cd marqeta-diva-mcp
python -m marqeta_diva_mcp.server
```

### Adding to Claude Desktop

Add this configuration to your Claude Desktop config file:

**macOS**: `~/Library/Application Support/Claude/claude_desktop_config.json`
**Windows**: `%APPDATA%/Claude/claude_desktop_config.json`

#### Using uvx (Recommended)

**Basic configuration (core features only):**
```json
{
  "mcpServers": {
    "marqeta-diva": {
      "command": "uvx",
      "args": ["marqeta-diva-mcp"],
      "env": {
        "MARQETA_APP_TOKEN": "your_application_token",
        "MARQETA_ACCESS_TOKEN": "your_access_token",
        "MARQETA_PROGRAM": "your_program_name"
      }
    }
  }
}
```

**With RAG features (local storage + semantic search):**
```json
{
  "mcpServers": {
    "marqeta-diva": {
      "command": "uvx",
      "args": ["--with", "marqeta-diva-mcp[rag]", "marqeta-diva-mcp"],
      "env": {
        "MARQETA_APP_TOKEN": "your_application_token",
        "MARQETA_ACCESS_TOKEN": "your_access_token",
        "MARQETA_PROGRAM": "your_program_name",
        "ENABLE_LOCAL_STORAGE": "true"
      }
    }
  }
}
```

#### Using Python

**Basic configuration (core features only):**
```json
{
  "mcpServers": {
    "marqeta-diva": {
      "command": "python",
      "args": ["-m", "marqeta_diva_mcp.server"],
      "cwd": "/path/to/marqeta-diva-mcp",
      "env": {
        "MARQETA_APP_TOKEN": "your_application_token",
        "MARQETA_ACCESS_TOKEN": "your_access_token",
        "MARQETA_PROGRAM": "your_program_name"
      }
    }
  }
}
```

**With RAG features (requires `pip install -e ".[rag]"` first):**
```json
{
  "mcpServers": {
    "marqeta-diva": {
      "command": "python",
      "args": ["-m", "marqeta_diva_mcp.server"],
      "cwd": "/path/to/marqeta-diva-mcp",
      "env": {
        "MARQETA_APP_TOKEN": "your_application_token",
        "MARQETA_ACCESS_TOKEN": "your_access_token",
        "MARQETA_PROGRAM": "your_program_name",
        "ENABLE_LOCAL_STORAGE": "true"
      }
    }
  }
}
```

## Available Tools

### Transaction Tools

#### `get_authorizations`
Get authorization transaction data with amounts, counts, acting users/cards, and merchant information.

**Parameters:**
- `aggregation` (string): `detail`, `day`, `week`, or `month` (default: `detail`)
- `start_date` (string): Start date in ISO format (YYYY-MM-DD or YYYY-MM-DDTHH:MM:SS)
- `end_date` (string): End date in ISO format
- `fields` (array): Specific fields to return
- `filters` (object): Additional filters (e.g., `{"transaction_amount": ">100"}`)
- `sort_by` (string): Field to sort by (prefix with `-` for descending)
- `count` (integer): Maximum records to return (up to 10,000)
- `program` (string): Override default program name

**Example:**
```json
{
  "aggregation": "day",
  "start_date": "2024-01-01",
  "end_date": "2024-01-31",
  "filters": {"transaction_amount": ">1000"},
  "sort_by": "-request_amount",
  "count": 100
}
```

#### `get_settlements`
Get settlement transaction data including status, post dates, purchase amounts, and network information.

**Parameters:** Same as `get_authorizations`

#### `get_clearings`
Get accounting-level line items for transaction lifecycle. Ideal for reconciliation.

**Parameters:** Same as `get_authorizations`

#### `get_declines`
Get declined transaction data with tokens, decline reasons, merchant info, and amounts.

**Parameters:** Same as `get_authorizations`

#### `get_loads`
Get load transaction data including amounts and transaction details.

**Parameters:** Same as `get_authorizations`

### Financial Tools

#### `get_program_balances`
Get program-level balance data including beginning/ending bank balances and amounts to send/receive.

**Parameters:**
- `start_date`, `end_date`, `fields`, `filters`, `sort_by`, `count`, `program`

#### `get_program_balances_settlement`
Get settlement-based program balance data and fund transfers.

**Parameters:** Same as `get_program_balances`

#### `get_activity_balances`
Get cardholder-level balance data, expandable by network.

**Parameters:**
- All standard parameters plus:
- `expand` (string): Field to expand for more detail (e.g., network data)

### Card & User Tools

#### `get_cards`
Get card detail data including user tokens, card state, active status, and UAI.

**Parameters:**
- `fields`, `filters`, `sort_by`, `count`, `program`

**Example filters:**
```json
{
  "filters": {
    "state": "ACTIVE",
    "user_token": "abc123"
  }
}
```

#### `get_users`
Get user detail data including tokens, UAI, and number of physical/virtual cards.

**Parameters:** Same as `get_cards`

### Chargeback Tools

#### `get_chargebacks_status`
Get chargeback status data including state, tokens, and provisional credit status.

**Parameters:**
- `start_date`, `end_date`, `fields`, `filters`, `sort_by`, `count`, `program`

#### `get_chargebacks_detail`
Get detailed chargeback information with transaction dates and types.

**Parameters:** Same as `get_chargebacks_status`

### Metadata Tools

#### `list_available_views`
Get a list of all available DiVA API view endpoints with metadata.

**Parameters:** None

#### `get_view_schema`
Get the schema definition for any view endpoint with field names, types, and descriptions.

**Parameters:**
- `view_name` (string, required): Name of the view (e.g., `authorizations`, `settlements`, `cards`)
- `aggregation` (string): Aggregation level if applicable (default: `detail`)

## Query Filtering

The DiVA API supports powerful filtering operators:

| Operator | Description | Example |
|----------|-------------|---------|
| `~` | Like (wildcard) | `{"company": "Mar~eta"}` |
| `..` | Range | `{"date": "2023-10-01..2023-10-03"}` |
| `<`, `<=` | Less than | `{"amount": "<=100"}` |
| `>`, `>=` | Greater than | `{"date": ">=2023-04-01"}` |
| `=` | Equal/In list | `{"amount": "0"}` or `{"country": "United States,Mexico"}` |
| `=!` | Not equal/Not in | `{"amount": "=!0"}` |

**Example:**
```json
{
  "filters": {
    "transaction_amount": ">1000",
    "post_date": "2023-02-01..2023-02-28",
    "state": "COMPLETION"
  }
}
```

## Rate Limits

- **Maximum:** 300 requests per 5-minute interval (≈1 per second)
- **Enforcement:** Built-in rate limiter automatically throttles requests
- **Error Code:** HTTP 429 if limit exceeded

## Data Synchronization

Report data is synchronized **3 times daily**. See Marqeta documentation for specific refresh timelines.

## Error Handling

The server handles all common DiVA API errors:

| Code | Description |
|------|-------------|
| 400 | Bad Request - Malformed query or filter |
| 403 | Forbidden - Unauthorized access to field, filter, or program |
| 404 | Not Found - Malformed URL or endpoint doesn't exist |
| 429 | Rate limit exceeded |

## Example Usage with Claude

Once configured in Claude Desktop, you can use natural language queries:

**Example queries:**
- "Get all authorization transactions from last week with amounts over $1000"
- "Show me the settlement data for January 2024"
- "List all active cards for user token abc123"
- "What are the available views in the DiVA API?"
- "Get the schema for the settlements view"
- "Show me chargeback status for the last 30 days"
- "Get program balances for February 2024"

## API Documentation

For complete DiVA API documentation, visit:
https://www.marqeta.com/docs/diva-api/introduction/

## Troubleshooting

### Missing Credentials Error
```
Error: Missing required environment variables: MARQETA_APP_TOKEN, MARQETA_ACCESS_TOKEN, MARQETA_PROGRAM
```
**Solution:** Ensure your `.env` file exists and contains all three required variables.

### Authentication Error (403)
```
Error 403: Forbidden - Unauthorized access
```
**Solution:** Verify your Application Token and Access Token are correct. Check that you have access to the specified program.

### Rate Limit Error (429)
```
Error 429: Rate limit exceeded - Maximum 300 requests per 5 minutes
```
**Solution:** The built-in rate limiter should prevent this, but if you see it, wait a few minutes before making more requests.

## Development

### Running Tests

```bash
pytest
```

### Code Formatting

```bash
black src/
ruff check src/
```

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request. For major changes, please open an issue first to discuss what you would like to change.

### Development Setup

```bash
# Clone the repository
git clone https://github.com/zvika-finally/marqeta-diva-mcp.git
cd marqeta-diva-mcp

# Install with development dependencies
pip install -e ".[dev,rag]"

# Run tests
python test_fixes_unit.py

# Format code
black src/
ruff check src/
```

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Author

**Zvika Badalov** - [zvika.badalov@finally.com](mailto:zvika.badalov@finally.com)

## Acknowledgments

- Built with [Model Context Protocol (MCP)](https://modelcontextprotocol.io/)
- Powered by [Marqeta's DiVA API](https://www.marqeta.com/docs/diva-api/)

## Support

- **Issues:** [GitHub Issues](https://github.com/zvika-finally/marqeta-diva-mcp/issues)
- **Marqeta API Questions:** Contact your Marqeta representative or refer to the [official Marqeta documentation](https://www.marqeta.com/docs/diva-api/introduction/)

## Disclaimer

This is an unofficial community project and is not officially endorsed or supported by Marqeta, Inc. Use at your own risk.
