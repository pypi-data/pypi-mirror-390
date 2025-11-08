# DhanHQ MCP Server

A Model Context Protocol (MCP) server that provides access to DhanHQ trading platform APIs. This server allows AI assistants and other MCP clients to interact with your DhanHQ trading account.

## Features

- **Holdings Summary**: Fetch your current holdings from DhanHQ
- Extensible architecture for adding more DhanHQ API endpoints

## Prerequisites

- Python 3.10 or higher
- DhanHQ account with API access
- DhanHQ Client ID and Access Token

## Installation

### Option 1: Install from PyPI (when published)

```bash
pip install dhan-mcp-server
```

### Option 2: Install from source

```bash
git clone https://github.com/Vedhasagaran/dhan-mcp-py.git
cd dhan-mcp-py
pip install -e .
```

### Option 3: Direct installation from GitHub

```bash
pip install git+https://github.com/Vedhasagaran/dhan-mcp-py.git
```

## Configuration

### 1. Set Environment Variables

The server requires DhanHQ credentials to be set as environment variables:

**Windows (PowerShell):**
```powershell
$env:DHAN_CLIENT_ID="your_client_id"
$env:DHAN_ACCESS_TOKEN="your_access_token"
```

**Windows (Command Prompt):**
```cmd
set DHAN_CLIENT_ID=your_client_id
set DHAN_ACCESS_TOKEN=your_access_token
```

**Linux/Mac:**
```bash
export DHAN_CLIENT_ID="your_client_id"
export DHAN_ACCESS_TOKEN="your_access_token"
```

**Using .env file (recommended):**

Create a `.env` file in your project directory:
```env
DHAN_CLIENT_ID=your_client_id
DHAN_ACCESS_TOKEN=your_access_token
```

### 2. Configure MCP Client

Add the server to your MCP client configuration. The configuration file location varies by application:

- **Claude Desktop**: `%APPDATA%\Claude\claude_desktop_config.json` (Windows) or `~/Library/Application Support/Claude/claude_desktop_config.json` (Mac)
- **Other MCP Clients**: Refer to your client's documentation

Example configuration:

```json
{
  "mcpServers": {
    "dhan": {
      "command": "dhan-mcp-server",
      "env": {
        "DHAN_CLIENT_ID": "your_client_id",
        "DHAN_ACCESS_TOKEN": "your_access_token"
      }
    }
  }
}
```

**Alternative using Python directly:**

```json
{
  "mcpServers": {
    "dhan": {
      "command": "python",
      "args": ["-m", "server"],
      "env": {
        "DHAN_CLIENT_ID": "your_client_id",
        "DHAN_ACCESS_TOKEN": "your_access_token"
      }
    }
  }
}
```

## Usage

### Starting the Server Manually

If you want to run the server directly:

```bash
dhan-mcp-server
```

Or with Python:

```bash
python -m server
```

The server communicates via stdio (standard input/output) using the MCP protocol.

### Available Tools

Once connected via an MCP client, the following tools are available:

#### `get_holdings_summary`
Fetches your current holdings from DhanHQ.

**Returns:**
```json
{
  "holdings": [
    // Array of holding objects
  ]
}
```

## Development

### Setting Up Development Environment

```bash
# Clone the repository
git clone https://github.com/Vedhasagaran/dhan-mcp-py.git
cd dhan-mcp-py

# Create virtual environment
python -m venv venv

# Activate virtual environment
# Windows:
venv\Scripts\activate
# Linux/Mac:
source venv/bin/activate

# Install in editable mode with dependencies
pip install -e .
```

### Adding New Tools

To add new DhanHQ API endpoints:

1. Add a new function in `server.py` decorated with `@mcp.tool()`
2. Follow this pattern:

```python
@mcp.tool()
def your_new_tool() -> dict:
    """
    Description of what this tool does.
    """
    client = dhanhq(client_id, access_token)
    result = client.your_api_method()
    return {"data": result}
```

## Security Notes

- **Never commit credentials**: The `.gitignore` file excludes `.env` files
- **Keep tokens secure**: Access tokens provide full access to your DhanHQ account
- **Use environment variables**: Always load credentials from environment variables
- **Rotate tokens regularly**: Follow DhanHQ's security best practices

## Troubleshooting

### "Missing DHAN_CLIENT_ID or DHAN_ACCESS_TOKEN"

Ensure environment variables are set correctly. Check with:

```bash
# Windows PowerShell
echo $env:DHAN_CLIENT_ID

# Linux/Mac
echo $DHAN_CLIENT_ID
```

### MCP Client Can't Find Server

Verify the installation:

```bash
pip show dhan-mcp-server
which dhan-mcp-server  # Linux/Mac
where dhan-mcp-server  # Windows
```

## License

MIT License - see LICENSE file for details

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## Resources

- [DhanHQ API Documentation](https://dhanhq.co/docs/)
- [Model Context Protocol](https://modelcontextprotocol.io/)
- [FastMCP Documentation](https://github.com/jlowin/fastmcp)
