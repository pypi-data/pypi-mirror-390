# Integration Guide - Connecting to AI Platforms

This guide shows you how to connect `marqeta-diva-mcp` to various AI platforms and tools.

## Table of Contents

- [Claude Desktop (Recommended)](#claude-desktop-recommended)
- [Claude Code](#claude-code)
- [Cline (VS Code Extension)](#cline-vs-code-extension)
- [Other MCP-Compatible Clients](#other-mcp-compatible-clients)
- [Non-MCP Platforms (ChatGPT, etc.)](#non-mcp-platforms)
- [Custom Integrations](#custom-integrations)
- [Troubleshooting](#troubleshooting)

---

## Claude Desktop (Recommended)

Claude Desktop has native MCP support and is the easiest way to use this server.

### Installation

1. **Install Claude Desktop**
   - macOS: Download from https://claude.ai/download
   - Windows: Download from https://claude.ai/download

2. **Install the MCP Server**
   ```bash
   # Basic features
   pip install marqeta-diva-mcp

   # With RAG features (recommended)
   pip install marqeta-diva-mcp[rag]
   ```

3. **Configure Claude Desktop**

   **Location:**
   - macOS: `~/Library/Application Support/Claude/claude_desktop_config.json`
   - Windows: `%APPDATA%/Claude/claude_desktop_config.json`

   **Basic Configuration:**
   ```json
   {
     "mcpServers": {
       "marqeta-diva": {
         "command": "uvx",
         "args": ["marqeta-diva-mcp"],
         "env": {
           "MARQETA_APP_TOKEN": "your_app_token_here",
           "MARQETA_ACCESS_TOKEN": "your_access_token_here",
           "MARQETA_PROGRAM": "your_program_name"
         }
       }
     }
   }
   ```

   **With RAG Features:**
   ```json
   {
     "mcpServers": {
       "marqeta-diva": {
         "command": "uvx",
         "args": ["--with", "marqeta-diva-mcp[rag]", "marqeta-diva-mcp"],
         "env": {
           "MARQETA_APP_TOKEN": "your_app_token_here",
           "MARQETA_ACCESS_TOKEN": "your_access_token_here",
           "MARQETA_PROGRAM": "your_program_name",
           "ENABLE_LOCAL_STORAGE": "true"
         }
       }
     }
   }
   ```

   **Alternative: Using Python Directly**
   ```json
   {
     "mcpServers": {
       "marqeta-diva": {
         "command": "python",
         "args": ["-m", "marqeta_diva_mcp.server"],
         "cwd": "/path/to/your/project",
         "env": {
           "MARQETA_APP_TOKEN": "your_app_token_here",
           "MARQETA_ACCESS_TOKEN": "your_access_token_here",
           "MARQETA_PROGRAM": "your_program_name",
           "ENABLE_LOCAL_STORAGE": "true"
         }
       }
     }
   }
   ```

4. **Restart Claude Desktop**

5. **Verify Connection**

   Look for the 🔌 icon in Claude Desktop. Your server should appear in the list.

### Usage Examples in Claude Desktop

```
You: "Get all authorization transactions from last week with amounts over $1000"

You: "Show me settlement data for January 2024"

You: "List all active cards for user token abc123"

You: "Export authorization data to a JSON file"

You: "Search for all coffee shop transactions" (requires RAG features)
```

---

## Claude Code

Claude Code (CLI) also supports MCP servers.

### Installation

1. **Install Claude Code**
   ```bash
   npm install -g @anthropic-ai/claude-code
   ```

2. **Configure MCP Server**

   Create or edit `~/.config/claude-code/config.json`:

   ```json
   {
     "mcpServers": {
       "marqeta-diva": {
         "command": "uvx",
         "args": ["marqeta-diva-mcp"],
         "env": {
           "MARQETA_APP_TOKEN": "your_app_token_here",
           "MARQETA_ACCESS_TOKEN": "your_access_token_here",
           "MARQETA_PROGRAM": "your_program_name"
         }
       }
     }
   }
   ```

3. **Start Claude Code**
   ```bash
   claude-code
   ```

### Usage in Claude Code

Claude Code will automatically discover and use your MCP server tools.

---

## Cline (VS Code Extension)

Cline is a VS Code extension that supports MCP servers.

### Installation

1. **Install Cline Extension**
   - Open VS Code
   - Go to Extensions (Cmd+Shift+X or Ctrl+Shift+X)
   - Search for "Cline"
   - Click Install

2. **Configure MCP Server**

   Open VS Code settings and add to `cline.mcpServers`:

   ```json
   {
     "cline.mcpServers": {
       "marqeta-diva": {
         "command": "uvx",
         "args": ["marqeta-diva-mcp"],
         "env": {
           "MARQETA_APP_TOKEN": "your_app_token_here",
           "MARQETA_ACCESS_TOKEN": "your_access_token_here",
           "MARQETA_PROGRAM": "your_program_name"
         }
       }
     }
   }
   ```

3. **Restart VS Code**

---

## Other MCP-Compatible Clients

Any MCP-compatible client can use this server. The MCP protocol is open and growing.

### Generic MCP Configuration

```json
{
  "servers": {
    "marqeta-diva": {
      "command": "uvx",
      "args": ["marqeta-diva-mcp"],
      "env": {
        "MARQETA_APP_TOKEN": "your_token",
        "MARQETA_ACCESS_TOKEN": "your_token",
        "MARQETA_PROGRAM": "your_program"
      }
    }
  }
}
```

### Known MCP Clients

- **Claude Desktop** (Anthropic)
- **Claude Code** (Anthropic)
- **Cline** (VS Code Extension)
- **Continue** (VS Code Extension with MCP support)
- **Your custom MCP client** (see [MCP Specification](https://modelcontextprotocol.io/))

---

## Non-MCP Platforms

ChatGPT, OpenAI, and other platforms don't support MCP protocol. However, you can still access your Marqeta data.

### Option 1: Use the Python Client Directly

Since this is a Python package, you can use it programmatically:

```python
from marqeta_diva_mcp.client import DiVAClient

# Initialize client
client = DiVAClient(
    app_token="your_app_token",
    access_token="your_access_token",
    program="your_program"
)

# Get data
result = client.get_view(
    "authorizations",
    "detail",
    filters={"transaction_amount": ">1000"},
    count=100
)

print(result)
```

### Option 2: Create a REST API Wrapper

You could wrap this in a Flask/FastAPI server:

```python
from flask import Flask, jsonify, request
from marqeta_diva_mcp.client import DiVAClient
import os

app = Flask(__name__)

client = DiVAClient(
    app_token=os.getenv("MARQETA_APP_TOKEN"),
    access_token=os.getenv("MARQETA_ACCESS_TOKEN"),
    program=os.getenv("MARQETA_PROGRAM")
)

@app.route("/api/authorizations", methods=["GET"])
def get_authorizations():
    filters = request.args.to_dict()
    result = client.get_view("authorizations", "detail", filters=filters)
    return jsonify(result)

if __name__ == "__main__":
    app.run(port=5000)
```

Then use with ChatGPT via API calls or Custom GPTs with Actions.

### Option 3: Export Data and Upload

```python
from marqeta_diva_mcp.client import DiVAClient

client = DiVAClient(...)

# Export to file
result = client.export_to_file(
    view_name="authorizations",
    aggregation="detail",
    output_path="./data.json",
    format="json",
    filters={"transaction_timestamp": ">=2024-01-01"}
)

# Now upload data.json to ChatGPT for analysis
```

### Option 4: Use with OpenAI Function Calling

Create OpenAI function definitions:

```python
import openai
from marqeta_diva_mcp.client import DiVAClient

client = DiVAClient(...)

functions = [
    {
        "name": "get_authorizations",
        "description": "Get authorization transaction data from Marqeta DiVA",
        "parameters": {
            "type": "object",
            "properties": {
                "filters": {
                    "type": "object",
                    "description": "Filters for transactions"
                },
                "count": {
                    "type": "integer",
                    "description": "Number of records to return"
                }
            }
        }
    }
]

# Use with OpenAI chat completions
response = openai.ChatCompletion.create(
    model="gpt-4",
    messages=[{"role": "user", "content": "Get transactions over $1000"}],
    functions=functions,
    function_call="auto"
)

# Parse function call and execute
if response.choices[0].message.get("function_call"):
    function_name = response.choices[0].message.function_call.name
    function_args = json.loads(response.choices[0].message.function_call.arguments)

    if function_name == "get_authorizations":
        result = client.get_view("authorizations", "detail", **function_args)
```

---

## Custom Integrations

### Building Your Own MCP Client

The MCP protocol is open. You can build your own client:

1. **Read the MCP Specification**
   - https://modelcontextprotocol.io/

2. **Use an MCP SDK**
   - Python: `pip install mcp`
   - TypeScript: `npm install @modelcontextprotocol/sdk`

3. **Connect to the Server**
   ```python
   import asyncio
   from mcp import ClientSession, StdioServerParameters
   from mcp.client.stdio import stdio_client

   async def main():
       server_params = StdioServerParameters(
           command="uvx",
           args=["marqeta-diva-mcp"],
           env={
               "MARQETA_APP_TOKEN": "...",
               "MARQETA_ACCESS_TOKEN": "...",
               "MARQETA_PROGRAM": "..."
           }
       )

       async with stdio_client(server_params) as (read, write):
           async with ClientSession(read, write) as session:
               # Initialize
               await session.initialize()

               # List tools
               tools = await session.list_tools()
               print(f"Available tools: {tools}")

               # Call a tool
               result = await session.call_tool(
                   "get_authorizations",
                   arguments={"count": 10}
               )
               print(result)

   asyncio.run(main())
   ```

### Integrating with Other Platforms

**Slack Bot:**
- Create a bot that uses the DiVAClient
- Respond to slash commands with transaction data

**Discord Bot:**
- Similar to Slack, use DiVAClient in your bot

**Web Dashboard:**
- Build a React/Vue frontend
- Backend API uses DiVAClient
- Real-time updates with WebSockets

**Jupyter Notebooks:**
```python
from marqeta_diva_mcp.client import DiVAClient
import pandas as pd

client = DiVAClient(...)
result = client.get_view("authorizations", "detail", count=1000)
df = pd.DataFrame(result["records"])
df.head()
```

---

## Environment Variables Reference

All platforms need these credentials:

```bash
# Required
MARQETA_APP_TOKEN=your_application_token
MARQETA_ACCESS_TOKEN=your_access_token
MARQETA_PROGRAM=your_program_name

# Optional (for RAG features)
ENABLE_LOCAL_STORAGE=true  # Default: false
```

**How to get credentials:**
1. Contact your Marqeta representative, OR
2. Generate via Marqeta Dashboard (Reports section)

---

## Troubleshooting

### Claude Desktop Issues

**Server not appearing:**
1. Check config file location (macOS vs Windows)
2. Verify JSON syntax (use JSONLint.com)
3. Check Claude Desktop logs:
   - macOS: `~/Library/Logs/Claude/mcp*.log`
   - Windows: `%APPDATA%/Claude/logs/mcp*.log`
4. Restart Claude Desktop

**Connection errors:**
1. Verify credentials are correct
2. Test credentials with direct client:
   ```python
   from marqeta_diva_mcp.client import DiVAClient
   client = DiVAClient("app", "access", "program")
   result = client.get_views_list()
   print(result)
   ```
3. Check network connectivity to Marqeta API

**"Tool not found" errors:**
- Server may not be running
- Check if RAG tools require `ENABLE_LOCAL_STORAGE=true`
- Verify package is installed: `pip list | grep marqeta`

### General MCP Issues

**Server won't start:**
```bash
# Test manually
uvx marqeta-diva-mcp

# Check for errors
python -m marqeta_diva_mcp.server

# Verify installation
pip show marqeta-diva-mcp
```

**Import errors:**
```bash
# Reinstall
pip uninstall marqeta-diva-mcp
pip install marqeta-diva-mcp[rag]
```

**Rate limit errors:**
- DiVA API limit: 300 requests per 5 minutes
- Built-in rate limiter should prevent this
- If you see 429 errors, wait a few minutes

### Platform-Specific Issues

**VS Code / Cline:**
- Check VS Code Output panel → Cline
- Verify extension is updated
- Restart VS Code

**ChatGPT / OpenAI:**
- MCP not supported - use direct Python client
- Consider building Custom GPT with Actions
- Use REST API wrapper approach

---

## Best Practices

### Security

1. **Never commit credentials** to git
2. **Use environment variables** or secure vaults
3. **Rotate tokens** periodically
4. **Limit token scopes** when possible

### Performance

1. **Use filters** to reduce data transfer
2. **Enable RAG features** for large datasets
3. **Cache results** when appropriate
4. **Use local storage** to bypass MCP token limits

### Development

1. **Test on TestPyPI** first
2. **Use version tags** in production
3. **Monitor logs** for errors
4. **Keep package updated**: `pip install --upgrade marqeta-diva-mcp`

---

## Examples Gallery

### Claude Desktop: Complex Query
```
You: "Get all authorization transactions from last month where the amount
was over $500, export them to a CSV file, then analyze the spending patterns
by merchant category"
```

### Python Script: Automated Report
```python
from marqeta_diva_mcp.client import DiVAClient
import datetime

client = DiVAClient(...)

# Get last month's data
last_month = (datetime.datetime.now() - datetime.timedelta(days=30)).strftime("%Y-%m-%d")

client.export_to_file(
    view_name="authorizations",
    aggregation="detail",
    output_path="./monthly_report.json",
    format="json",
    filters={"transaction_timestamp": f">={last_month}"}
)

print("Report generated: monthly_report.json")
```

### Jupyter Notebook: Data Analysis
```python
from marqeta_diva_mcp.client import DiVAClient
import pandas as pd
import matplotlib.pyplot as plt

client = DiVAClient(...)

# Get data
result = client.get_view("authorizations", "detail", count=1000)
df = pd.DataFrame(result["records"])

# Analyze
df["transaction_amount"].hist(bins=50)
plt.title("Transaction Amount Distribution")
plt.show()

# Top merchants
df.groupby("merchant_name")["transaction_amount"].sum().sort_values(ascending=False).head(10)
```

---

## Additional Resources

- **MCP Specification:** https://modelcontextprotocol.io/
- **Claude Desktop:** https://claude.ai/download
- **Marqeta DiVA API Docs:** https://www.marqeta.com/docs/diva-api/
- **Package Repository:** https://github.com/zvika-finally/marqeta-diva-mcp
- **PyPI Package:** https://pypi.org/project/marqeta-diva-mcp/

---

## Support

- **GitHub Issues:** https://github.com/zvika-finally/marqeta-diva-mcp/issues
- **Email:** zvika.badalov@finally.com
- **Marqeta Support:** Contact your Marqeta representative

---

**Happy Integrating!** 🚀
