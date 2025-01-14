import pytest
from mcp.server.lowlevel import Server
from searxng_mcp_server.server import fetch_website

def test_server_startup():
    """Test that the server can be initialized properly."""
    app = Server("mcp-website-fetcher")
    
    # Test registering the fetch tool
    @app.call_tool()
    async def fetch_tool(name: str, arguments: dict):
        if name != "fetch":
            raise ValueError(f"Unknown tool: {name}")
        if "url" not in arguments:
            raise ValueError("Missing required argument 'url'")
        return await fetch_website(arguments["url"])
    
    # If we get here without exceptions, the server initialized successfully
    assert app is not None
    assert app.name == "mcp-website-fetcher"
