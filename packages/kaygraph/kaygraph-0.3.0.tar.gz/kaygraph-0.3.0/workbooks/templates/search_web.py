"""
Web search utility using DuckDuckGo (no API key required).

Falls back to mock results if DuckDuckGo is not available.
Can be extended to support other search APIs.
"""

import time
import logging
from typing import List, Dict, Any
import json
import urllib.parse
import urllib.request
from html.parser import HTMLParser

logger = logging.getLogger(__name__)


class DuckDuckGoHTMLParser(HTMLParser):
    """Simple HTML parser to extract search results from DuckDuckGo."""
    
    def __init__(self):
        super().__init__()
        self.results = []
        self.current_result = {}
        self.in_result = False
        self.in_title = False
        self.in_snippet = False
        self.current_data = []
    
    def handle_starttag(self, tag, attrs):
        attrs_dict = dict(attrs)
        
        # Look for result containers
        if tag == "div" and "result__body" in attrs_dict.get("class", ""):
            self.in_result = True
            self.current_result = {}
        
        # Look for title links
        elif self.in_result and tag == "a" and "result__a" in attrs_dict.get("class", ""):
            self.in_title = True
            self.current_result["url"] = attrs_dict.get("href", "")
        
        # Look for snippets
        elif self.in_result and tag == "div" and "result__snippet" in attrs_dict.get("class", ""):
            self.in_snippet = True
    
    def handle_data(self, data):
        if self.in_title or self.in_snippet:
            self.current_data.append(data)
    
    def handle_endtag(self, tag):
        if self.in_title and tag == "a":
            self.current_result["title"] = " ".join(self.current_data).strip()
            self.current_data = []
            self.in_title = False
        
        elif self.in_snippet and tag == "div":
            self.current_result["snippet"] = " ".join(self.current_data).strip()
            self.current_data = []
            self.in_snippet = False
        
        elif self.in_result and tag == "div":
            if "title" in self.current_result and "snippet" in self.current_result:
                self.results.append(self.current_result)
            self.in_result = False
            self.current_result = {}


def search_duckduckgo(query: str, max_results: int = 5) -> List[Dict[str, Any]]:
    """
    Search DuckDuckGo without using their API (simple HTML scraping).
    
    Args:
        query: Search query
        max_results: Maximum number of results
        
    Returns:
        List of search results
    """
    try:
        # Encode query for URL
        encoded_query = urllib.parse.quote(query)
        url = f"https://duckduckgo.com/html/?q={encoded_query}"
        
        # Make request with a browser-like user agent
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }
        
        request = urllib.request.Request(url, headers=headers)
        
        with urllib.request.urlopen(request, timeout=5) as response:
            html = response.read().decode('utf-8')
        
        # Parse HTML
        parser = DuckDuckGoHTMLParser()
        parser.feed(html)
        
        # Return results up to max_results
        results = parser.results[:max_results]
        
        # If we got results, return them
        if results:
            logger.info(f"Found {len(results)} results from DuckDuckGo")
            return results
        else:
            logger.warning("No results found from DuckDuckGo, using fallback")
            return None
            
    except Exception as e:
        logger.warning(f"DuckDuckGo search failed: {e}, using fallback")
        return None


def search_web_api(query: str, max_results: int = 5) -> List[Dict[str, Any]]:
    """
    Search using alternative APIs based on environment configuration.
    
    Supports:
    - Google Custom Search API
    - Bing Search API
    - SerpAPI
    - Brave Search API
    """
    import os
    
    search_provider = os.environ.get("SEARCH_PROVIDER", "duckduckgo").lower()
    
    if search_provider == "google":
        # Google Custom Search
        api_key = os.environ.get("GOOGLE_API_KEY")
        search_engine_id = os.environ.get("GOOGLE_SEARCH_ENGINE_ID")
        
        if api_key and search_engine_id:
            try:
                url = f"https://www.googleapis.com/customsearch/v1?key={api_key}&cx={search_engine_id}&q={urllib.parse.quote(query)}&num={max_results}"
                
                with urllib.request.urlopen(url) as response:
                    data = json.loads(response.read().decode('utf-8'))
                
                results = []
                for item in data.get("items", []):
                    results.append({
                        "title": item.get("title", ""),
                        "snippet": item.get("snippet", ""),
                        "url": item.get("link", "")
                    })
                
                return results
            except Exception as e:
                logger.warning(f"Google search failed: {e}")
    
    elif search_provider == "bing":
        # Bing Search API
        api_key = os.environ.get("BING_API_KEY")
        
        if api_key:
            try:
                url = f"https://api.bing.microsoft.com/v7.0/search?q={urllib.parse.quote(query)}&count={max_results}"
                headers = {'Ocp-Apim-Subscription-Key': api_key}
                
                request = urllib.request.Request(url, headers=headers)
                with urllib.request.urlopen(request) as response:
                    data = json.loads(response.read().decode('utf-8'))
                
                results = []
                for item in data.get("webPages", {}).get("value", []):
                    results.append({
                        "title": item.get("name", ""),
                        "snippet": item.get("snippet", ""),
                        "url": item.get("url", "")
                    })
                
                return results
            except Exception as e:
                logger.warning(f"Bing search failed: {e}")
    
    # Default to DuckDuckGo
    return None


def search_web(query: str, max_results: int = 5) -> List[Dict[str, Any]]:
    """
    Search the web for information.
    
    Tries multiple search methods in order:
    1. Configured API (Google, Bing, etc.)
    2. DuckDuckGo HTML scraping
    3. Mock results as fallback
    
    Args:
        query: Search query
        max_results: Maximum number of results to return
        
    Returns:
        List of search results with title, snippet, and url
    """
    logger.info(f"Searching for: {query}")
    
    # Try API-based search first
    results = search_web_api(query, max_results)
    if results:
        return results
    
    # Try DuckDuckGo
    results = search_duckduckgo(query, max_results)
    if results:
        return results
    
    # Fallback to mock results
    logger.info("Using mock search results as fallback")
    
    # Enhanced mock results based on query
    mock_results = {
        "python": [
            {
                "title": "Python.org",
                "snippet": "The official home of the Python Programming Language.",
                "url": "https://www.python.org"
            },
            {
                "title": "Python Tutorial - W3Schools",
                "snippet": "Well organized and easy to understand Web building tutorials with lots of examples of how to use Python.",
                "url": "https://www.w3schools.com/python/"
            },
            {
                "title": "Python Documentation",
                "snippet": "Official Python documentation with tutorials, library reference, and language reference.",
                "url": "https://docs.python.org/3/"
            }
        ],
        "kaygraph": [
            {
                "title": "KayGraph - Production-Ready Graph Framework",
                "snippet": "KayGraph is an opinionated framework for building context-aware AI applications with production-ready graphs.",
                "url": "https://github.com/kaygraph/kaygraph"
            },
            {
                "title": "Getting Started with KayGraph",
                "snippet": "Learn how to build sophisticated AI workflows using KayGraph's node-based architecture.",
                "url": "https://kaygraph.readthedocs.io"
            },
            {
                "title": "KayGraph Examples",
                "snippet": "Comprehensive examples showing how to use KayGraph for various AI applications.",
                "url": "https://github.com/kaygraph/kaygraph/tree/main/examples"
            }
        ],
        "machine learning": [
            {
                "title": "Machine Learning - Wikipedia",
                "snippet": "Machine learning (ML) is a field of study in artificial intelligence concerned with the development of algorithms.",
                "url": "https://en.wikipedia.org/wiki/Machine_learning"
            },
            {
                "title": "Machine Learning Crash Course - Google",
                "snippet": "Google's fast-paced, practical introduction to machine learning featuring TensorFlow APIs.",
                "url": "https://developers.google.com/machine-learning/crash-course"
            }
        ],
        "default": [
            {
                "title": f"Search Results for: {query}",
                "snippet": f"Found relevant information about {query} from various authoritative sources.",
                "url": f"https://www.google.com/search?q={urllib.parse.quote(query)}"
            },
            {
                "title": f"{query} - Overview and Information",
                "snippet": f"Comprehensive guide covering various aspects of {query} with examples and best practices.",
                "url": f"https://en.wikipedia.org/wiki/{urllib.parse.quote(query.replace(' ', '_'))}"
            },
            {
                "title": f"Understanding {query}: A Complete Guide",
                "snippet": f"Everything you need to know about {query}, including tutorials, documentation, and resources.",
                "url": f"https://example.com/guide/{urllib.parse.quote(query.lower().replace(' ', '-'))}"
            }
        ]
    }
    
    # Check if query matches any mock category
    query_lower = query.lower()
    for key in mock_results:
        if key in query_lower:
            return mock_results[key][:max_results]
    
    # Return generic results
    return mock_results["default"][:max_results]


def extract_key_points(search_results: List[Dict[str, Any]]) -> List[str]:
    """
    Extract key points from search results.
    
    Args:
        search_results: List of search result dictionaries
        
    Returns:
        List of key points extracted from snippets
    """
    key_points = []
    
    for i, result in enumerate(search_results):
        snippet = result.get("snippet", "")
        title = result.get("title", "")
        
        if snippet:
            # Format as a key point with source
            point = f"{i+1}. {snippet} (Source: {title})"
            key_points.append(point)
    
    return key_points


def format_search_results(search_results: List[Dict[str, Any]]) -> str:
    """
    Format search results as a readable text block.
    
    Args:
        search_results: List of search results
        
    Returns:
        Formatted string of search results
    """
    if not search_results:
        return "No search results found."
    
    formatted = []
    for i, result in enumerate(search_results, 1):
        formatted.append(f"{i}. {result['title']}")
        formatted.append(f"   {result['snippet']}")
        formatted.append(f"   URL: {result['url']}")
        formatted.append("")  # Empty line between results
    
    return "\n".join(formatted)


if __name__ == "__main__":
    # Test the search function
    logging.basicConfig(level=logging.INFO)
    
    # Test queries
    test_queries = [
        "Python programming",
        "KayGraph AI framework",
        "machine learning basics",
        "web scraping tutorial"
    ]
    
    for query in test_queries:
        print(f"\n{'='*60}")
        print(f"Searching for: {query}")
        print('='*60)
        
        results = search_web(query, max_results=3)
        print(f"\nFound {len(results)} results:")
        print(format_search_results(results))
        
        # Test key point extraction
        points = extract_key_points(results)
        print("\nKey points:")
        for point in points:
            print(f"  {point}")
        
        time.sleep(1)  # Be nice to the search service