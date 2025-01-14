from pathlib import Path
import argparse

from mcp.server.fastmcp import FastMCP

# Create server
mcp = FastMCP("Demo")

def get_search_path():
    """Get the search path from command line arguments"""
    parser = argparse.ArgumentParser(description='MCP Server with configurable search path')
    parser.add_argument('--search-path', type=str, default=str(Path.home() / "Desktop"),
                       help='Path to search for files (default: user\'s desktop)')
    args = parser.parse_args()
    return args.search_path

@mcp.resource("dir://desktop")
def desktop() -> list[str]:
    """List the files in the specified search path"""
    search_path = Path(get_search_path())
    return [str(f) for f in search_path.iterdir()]

@mcp.tool()
def add(a: int, b: int) -> int:
    """Add two numbers"""
    return a + b

def main():
    mcp.run()

if __name__ == "__main__":
    mcp.run()