"""
Search provider implementations.
"""

import os
import json
import logging
import requests
from typing import List, Dict, Any, Optional
from datetime import datetime
import time

from models import (
    SearchProvider, SearchQuery, SearchResult, SearchResponse
)

logger = logging.getLogger(__name__)


def get_available_search_providers() -> List[SearchProvider]:
    """Get list of available search providers based on environment."""
    providers = []
    
    if os.getenv("SERP_API_KEY"):
        providers.append(SearchProvider.SERP_API)
    
    # DuckDuckGo is always available (no API key needed)
    providers.append(SearchProvider.DUCKDUCKGO)
    
    # Mock is always available
    providers.append(SearchProvider.MOCK)
    
    return providers


def search_serp_api(query: SearchQuery) -> SearchResponse:
    """
    Search using SERP API (supports Google, Bing, DuckDuckGo, etc).
    Requires SERP_API_KEY environment variable.
    """
    api_key = os.getenv("SERP_API_KEY")
    if not api_key:
        raise ValueError("SERP_API_KEY not set")
    
    url = "https://serpapi.com/search"
    
    params = {
        "api_key": api_key,
        "q": query.query,
        "num": query.num_results,
        "hl": query.language,
        "engine": "google"  # Can be changed to bing, duckduckgo, etc
    }
    
    # Add location if specified
    if query.location:
        params["location"] = query.location
    
    # Add filters
    for key, value in query.filters.items():
        params[key] = value
    
    start_time = time.time()
    
    try:
        response = requests.get(url, params=params, timeout=10)
        response.raise_for_status()
        data = response.json()
        
        # Extract organic results
        results = []
        organic_results = data.get("organic_results", [])
        
        for i, result in enumerate(organic_results[:query.num_results]):
            search_result = SearchResult(
                title=result.get("title", ""),
                url=result.get("link", ""),
                snippet=result.get("snippet", ""),
                position=i + 1,
                source=result.get("source", ""),
                date_published=_parse_date(result.get("date")),
                metadata={
                    "displayed_link": result.get("displayed_link", ""),
                    "cached_page_link": result.get("cached_page_link"),
                    "rich_snippet": result.get("rich_snippet", {})
                }
            )
            results.append(search_result)
        
        search_time = time.time() - start_time
        
        return SearchResponse(
            query=query,
            provider=SearchProvider.SERP_API,
            results=results,
            total_results=data.get("search_information", {}).get("total_results"),
            search_time=search_time
        )
        
    except Exception as e:
        logger.error(f"SERP API error: {e}")
        return SearchResponse(
            query=query,
            provider=SearchProvider.SERP_API,
            results=[],
            error=str(e)
        )


def search_duckduckgo(query: SearchQuery) -> SearchResponse:
    """
    Search using DuckDuckGo HTML API (no key required).
    Limited functionality but free.
    """
    from bs4 import BeautifulSoup
    
    url = "https://html.duckduckgo.com/html/"
    params = {"q": query.query}
    
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
    }
    
    start_time = time.time()
    
    try:
        response = requests.post(url, data=params, headers=headers, timeout=10)
        response.raise_for_status()
        
        soup = BeautifulSoup(response.text, 'html.parser')
        results = []
        
        # Find result links
        for i, result in enumerate(soup.select('.result')):
            if i >= query.num_results:
                break
            
            title_elem = result.select_one('.result__title')
            snippet_elem = result.select_one('.result__snippet')
            url_elem = result.select_one('.result__url')
            
            if title_elem and url_elem:
                # Extract URL
                url_text = url_elem.get_text(strip=True)
                if not url_text.startswith('http'):
                    url_text = 'https://' + url_text
                
                search_result = SearchResult(
                    title=title_elem.get_text(strip=True),
                    url=url_text,
                    snippet=snippet_elem.get_text(strip=True) if snippet_elem else "",
                    position=i + 1,
                    source="DuckDuckGo"
                )
                results.append(search_result)
        
        search_time = time.time() - start_time
        
        return SearchResponse(
            query=query,
            provider=SearchProvider.DUCKDUCKGO,
            results=results,
            search_time=search_time
        )
        
    except Exception as e:
        logger.error(f"DuckDuckGo error: {e}")
        return SearchResponse(
            query=query,
            provider=SearchProvider.DUCKDUCKGO,
            results=[],
            error=str(e)
        )


def search_mock(query: SearchQuery) -> SearchResponse:
    """
    Mock search for testing without API calls.
    Returns realistic-looking results.
    """
    logger.info(f"Mock search for: {query.query}")
    
    # Generate mock results based on query
    mock_results = []
    
    if "quantum computing" in query.query.lower():
        mock_results = [
            SearchResult(
                title="Quantum Computing: A Gentle Introduction - MIT",
                url="https://mitpress.mit.edu/quantum-computing",
                snippet="Quantum computing harnesses quantum mechanical phenomena to process information in fundamentally new ways...",
                position=1,
                source="MIT Press"
            ),
            SearchResult(
                title="What is Quantum Computing? - IBM",
                url="https://www.ibm.com/topics/quantum-computing",
                snippet="Quantum computing is a rapidly-emerging technology that harnesses the laws of quantum mechanics...",
                position=2,
                source="IBM"
            ),
            SearchResult(
                title="Quantum Computing Explained - Wikipedia",
                url="https://en.wikipedia.org/wiki/Quantum_computing",
                snippet="Quantum computing is a type of computation that uses quantum bits or qubits...",
                position=3,
                source="Wikipedia"
            )
        ]
    elif "restaurant" in query.query.lower():
        mock_results = [
            SearchResult(
                title="Best Restaurants Near You - Yelp",
                url="https://www.yelp.com/search?find_desc=restaurants",
                snippet="Find the best restaurants near you. Read reviews, view photos, and more...",
                position=1,
                source="Yelp"
            ),
            SearchResult(
                title="Top 10 Restaurants in Your Area",
                url="https://www.tripadvisor.com/restaurants",
                snippet="Discover the top-rated restaurants based on millions of reviews...",
                position=2,
                source="TripAdvisor"
            )
        ]
    else:
        # Generic results
        for i in range(min(3, query.num_results)):
            mock_results.append(SearchResult(
                title=f"Result {i+1} for '{query.query}'",
                url=f"https://example{i+1}.com/{query.query.replace(' ', '-')}",
                snippet=f"This is a mock search result for {query.query}. It contains relevant information about the topic...",
                position=i + 1,
                source=f"Example{i+1}.com"
            ))
    
    return SearchResponse(
        query=query,
        provider=SearchProvider.MOCK,
        results=mock_results[:query.num_results],
        total_results=len(mock_results) * 1000,  # Mock total
        search_time=0.1
    )


def _parse_date(date_str: Optional[str]) -> Optional[datetime]:
    """Parse date string from search results."""
    if not date_str:
        return None
    
    # Try common date formats
    formats = [
        "%Y-%m-%d",
        "%b %d, %Y",
        "%B %d, %Y",
        "%Y/%m/%d"
    ]
    
    for fmt in formats:
        try:
            return datetime.strptime(date_str, fmt)
        except ValueError:
            continue
    
    return None


# Tool metadata for registration (if using tool system)
SEARCH_WEB_METADATA = {
    "name": "search_web",
    "description": "Search the web for information",
    "parameters": {
        "type": "object",
        "properties": {
            "query": {
                "type": "string",
                "description": "The search query"
            },
            "num_results": {
                "type": "integer",
                "description": "Number of results to return",
                "default": 10
            },
            "search_type": {
                "type": "string",
                "enum": ["web", "news", "images", "videos"],
                "default": "web"
            }
        },
        "required": ["query"]
    }
}


if __name__ == "__main__":
    # Test search providers
    print("Available providers:", get_available_search_providers())
    
    # Test mock search
    test_query = SearchQuery(query="quantum computing latest developments")
    result = search_mock(test_query)
    
    print(f"\nMock search results for '{test_query.query}':")
    for r in result.results:
        print(f"- {r.title}")
        print(f"  {r.url}")
        print(f"  {r.snippet[:100]}...")
        print()