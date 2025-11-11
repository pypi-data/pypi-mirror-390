# Quick Integration Reference

Fast setup guide for popular platforms.

## Claude Desktop (2 minutes)

1. **Install:**
   ```bash
   pip install marqeta-diva-mcp[rag]
   ```

2. **Configure:**

   Edit `~/Library/Application Support/Claude/claude_desktop_config.json` (macOS) or `%APPDATA%/Claude/claude_desktop_config.json` (Windows):

   ```json
   {
     "mcpServers": {
       "marqeta-diva": {
         "command": "uvx",
         "args": ["--with", "marqeta-diva-mcp[rag]", "marqeta-diva-mcp"],
         "env": {
           "MARQETA_APP_TOKEN": "your_app_token",
           "MARQETA_ACCESS_TOKEN": "your_access_token",
           "MARQETA_PROGRAM": "your_program",
           "ENABLE_LOCAL_STORAGE": "true"
         }
       }
     }
   }
   ```

3. **Restart Claude Desktop**

4. **Test:** Look for 🔌 icon and try:
   ```
   "Get authorization transactions from last week"
   ```

---

## Claude Code (2 minutes)

1. **Install:**
   ```bash
   npm install -g @anthropic-ai/claude-code
   pip install marqeta-diva-mcp[rag]
   ```

2. **Configure `~/.config/claude-code/config.json`:**
   ```json
   {
     "mcpServers": {
       "marqeta-diva": {
         "command": "uvx",
         "args": ["marqeta-diva-mcp"],
         "env": {
           "MARQETA_APP_TOKEN": "your_app_token",
           "MARQETA_ACCESS_TOKEN": "your_access_token",
           "MARQETA_PROGRAM": "your_program"
         }
       }
     }
   }
   ```

3. **Run:** `claude-code`

---

## Python Script (1 minute)

```python
from marqeta_diva_mcp.client import DiVAClient

client = DiVAClient(
    app_token="your_app_token",
    access_token="your_access_token",
    program="your_program"
)

# Get data
result = client.get_view("authorizations", "detail", count=10)
print(result)
```

---

## Jupyter Notebook (1 minute)

```python
%pip install marqeta-diva-mcp

from marqeta_diva_mcp.client import DiVAClient
import pandas as pd

client = DiVAClient("app", "access", "program")
result = client.get_view("authorizations", "detail", count=100)
df = pd.DataFrame(result["records"])
df.head()
```

---

## ChatGPT / Non-MCP (Export Method)

```python
from marqeta_diva_mcp.client import DiVAClient

client = DiVAClient("app", "access", "program")

# Export to file
client.export_to_file(
    view_name="authorizations",
    aggregation="detail",
    output_path="./data.json",
    format="json",
    count=1000
)

# Upload data.json to ChatGPT for analysis
```

---

## VS Code with Cline

1. **Install Cline extension**
2. **Add to VS Code settings:**
   ```json
   {
     "cline.mcpServers": {
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
3. **Restart VS Code**

---

## Troubleshooting

**Can't find config file:**
- macOS: `~/Library/Application Support/Claude/claude_desktop_config.json`
- Windows: `%APPDATA%\Claude\claude_desktop_config.json`

**Server not working:**
```bash
# Test directly
uvx marqeta-diva-mcp

# Check installation
pip show marqeta-diva-mcp
```

**Need more help?**
- Full guide: [INTEGRATIONS.md](INTEGRATIONS.md)
- Issues: https://github.com/zvika-finally/marqeta-diva-mcp/issues

---

## Get Your Credentials

1. Contact your Marqeta representative, OR
2. Generate via Marqeta Dashboard (Reports section)

You need:
- Application Token
- Access Token
- Program Name
