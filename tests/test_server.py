import pytest
import httpx
import argparse
from unittest.mock import Mock, patch
from searxng_mcp_server.server import search, get_available_engines, get_searxng_url, SEARXNG_URL, main

@pytest.fixture
def mock_client():
    with patch('searxng_mcp_server.server.client') as mock:
        yield mock

@pytest.fixture
def mock_response():
    response = Mock(spec=httpx.Response)
    response.raise_for_status = Mock()
    return response

def test_get_searxng_url():
    test_url = "https://searx.example.com"
    with patch('argparse.ArgumentParser.parse_args', 
               return_value=argparse.Namespace(url=test_url)):
        result = get_searxng_url()
        assert result == test_url

def test_get_searxng_url_strips_trailing_slash():
    test_url = "https://searx.example.com/"
    with patch('argparse.ArgumentParser.parse_args', 
               return_value=argparse.Namespace(url=test_url)):
        result = get_searxng_url()
        assert result == "https://searx.example.com"

def test_search_basic(mock_client, mock_response):
    mock_response.json.return_value = {"results": [{"title": "Test Result"}]}
    mock_client.get.return_value = mock_response
    
    global SEARXNG_URL
    SEARXNG_URL = "https://searx.example.com"
    
    result = search("test query")
    
    mock_client.get.assert_called_once()
    call_args = mock_client.get.call_args[1]
    assert call_args["params"]["q"] == "test query"
    assert call_args["params"]["format"] == "json"
    assert call_args["params"]["pageno"] == 1
    assert call_args["params"]["safesearch"] == 1
    assert isinstance(result, dict)
    assert "results" in result

def test_search_with_all_params(mock_client, mock_response):
    mock_response.json.return_value = {"results": []}
    mock_client.get.return_value = mock_response
    
    global SEARXNG_URL
    SEARXNG_URL = "https://searx.example.com"
    
    result = search(
        query="test",
        categories="general",
        engines="google",
        language="en",
        page=2,
        time_range="day",
        safe_search=0
    )
    
    mock_client.get.assert_called_once()
    call_args = mock_client.get.call_args[1]
    assert call_args["params"]["q"] == "test"
    assert call_args["params"]["categories"] == "general"
    assert call_args["params"]["engines"] == "google"
    assert call_args["params"]["language"] == "en"
    assert call_args["params"]["pageno"] == 2
    assert call_args["params"]["time_range"] == "day"
    assert call_args["params"]["safesearch"] == 0

def test_search_http_error(mock_client):
    mock_client.get.side_effect = httpx.HTTPError("Test HTTP Error")
    
    global SEARXNG_URL
    SEARXNG_URL = "https://searx.example.com"
    
    with pytest.raises(httpx.HTTPError):
        search("test query")

def test_get_available_engines(mock_client, mock_response):
    mock_response.json.return_value = {
        "engines": [
            {"name": "google", "enabled": True},
            {"name": "bing", "enabled": True}
        ]
    }
    mock_client.get.return_value = mock_response
    
    global SEARXNG_URL
    SEARXNG_URL = "https://searx.example.com"
    
    result = get_available_engines()
    
    mock_client.get.assert_called_once()
    assert isinstance(result, dict)
    assert "engines" in result

def test_get_available_engines_http_error(mock_client):
    mock_client.get.side_effect = httpx.HTTPError("Test HTTP Error")
    
    global SEARXNG_URL
    SEARXNG_URL = "https://searx.example.com"
    
    with pytest.raises(httpx.HTTPError):
        get_available_engines()

def test_main_success():
    with patch('searxng_mcp_server.server.get_searxng_url') as mock_get_url, \
         patch('searxng_mcp_server.server.mcp.run') as mock_run:
        mock_get_url.return_value = "https://searx.example.com"
        main()
        mock_get_url.assert_called_once()
        mock_run.assert_called_once()

def test_main_failure():
    with patch('searxng_mcp_server.server.get_searxng_url') as mock_get_url:
        mock_get_url.side_effect = Exception("Test Error")
        with pytest.raises(Exception):
            main()
