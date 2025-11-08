# server.py
import os
from fastmcp import FastMCP
from dhanhq import dhanhq

mcp = FastMCP(name="DhanHQ MCP Server")

client_id = os.getenv("DHAN_CLIENT_ID")
access_token = os.getenv("DHAN_ACCESS_TOKEN")

if not client_id or not access_token:
    raise EnvironmentError("[ERROR] Missing DHAN_CLIENT_ID or DHAN_ACCESS_TOKEN environment variables")

@mcp.tool()
def get_holdings_summary() -> dict:
    """
    Fetch holdings summary via DhanHQ SDK.
    """
    
    client = dhanhq(client_id, access_token)
    holdings = client.get_holdings()
    # maybe reduce fields
    return {"holdings": holdings}

def main():
    """Main entry point for the MCP server."""
    print("[INFO] Using environment credentials")
    mcp.run(transport="stdio")

if __name__ == "__main__":
    main()
