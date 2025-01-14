# /// script
# dependencies = [
#   "mcp",
#   "httpx",
# ]
# ///

import argparse
import httpx
import logging
from typing import Optional, Dict, Any
from urllib.parse import urljoin

from mcp.server.fastmcp import FastMCP

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)
logger = logging.getLogger(__name__)

def get_searxng_url() -> str:
    parser = argparse.ArgumentParser()
    parser.add_argument("--url", required=True, help="SearXNG instance URL (e.g., https://searx.example.com)")
    args = parser.parse_args()
    url = args.url.rstrip("/")
    logger.info(f"SearXNG URL configured: {url}")
    return url

# Create server
mcp = FastMCP("SearxNG MCP Server")
SEARXNG_URL = None
client = httpx.Client()

@mcp.tool()
def search(query: str, categories: Optional[str] = None, engines: Optional[str] = None, 
           language: Optional[str] = None, page: int = 1, time_range: Optional[str] = None,
           safe_search: int = 1) -> Dict[str, Any]:
    """
    Search using SearXNG
    
    Args:
        query: The search query
        categories: Optional comma-separated list of categories
        engines: Optional comma-separated list of engines
        language: Optional language code
        page: Page number (default: 1)
        time_range: Optional time range (day, month, year)
        safe_search: Safe search level (0, 1, 2)
    """
    logger.info(f"Received search request - Query: {query}")
    
    params = {
        "q": query,
        "format": "json",
        "pageno": page,
        "safesearch": safe_search
    }
    
    if categories:
        params["categories"] = categories
        logger.debug(f"Categories specified: {categories}")
    if engines:
        params["engines"] = engines
        logger.debug(f"Engines specified: {engines}")
    if language:
        params["language"] = language
        logger.debug(f"Language specified: {language}")
    if time_range:
        params["time_range"] = time_range
        logger.debug(f"Time range specified: {time_range}")
        
    logger.debug(f"Making request to SearXNG with params: {params}")
    try:
        response = client.get(urljoin(SEARXNG_URL, "/search"), params=params)
        response.raise_for_status()
        result = response.json()
        logger.info(f"Search completed successfully - Found {len(result.get('results', []))} results")
        return result
    except httpx.HTTPError as e:
        logger.error(f"HTTP error occurred during search: {str(e)}")
        raise
    except Exception as e:
        logger.error(f"Unexpected error during search: {str(e)}")
        raise

@mcp.tool()
def get_available_engines() -> Dict[str, Any]:
    """Get information about available search engines"""
    logger.info("Fetching available engines information")
    try:
        response = client.get(urljoin(SEARXNG_URL, "/config"))
        response.raise_for_status()
        result = response.json()
        logger.info("Successfully retrieved engine information")
        return result
    except httpx.HTTPError as e:
        logger.error(f"HTTP error occurred while fetching engines: {str(e)}")
        raise
    except Exception as e:
        logger.error(f"Unexpected error while fetching engines: {str(e)}")
        raise

def main():
    global SEARXNG_URL
    logger.info("Starting SearXNG MCP Server")
    try:
        SEARXNG_URL = get_searxng_url()
        logger.info("Server initialization complete")
        mcp.run()
    except Exception as e:
        logger.critical(f"Failed to start server: {str(e)}")
        raise

if __name__ == "__main__":
    main()
