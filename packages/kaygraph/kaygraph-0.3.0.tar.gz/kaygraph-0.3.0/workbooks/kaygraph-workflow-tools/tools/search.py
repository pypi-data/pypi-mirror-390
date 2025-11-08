"""
Search tool implementation (mock).
In production, this would connect to a real search API.
"""

import random
from typing import Dict, Any, List
from datetime import datetime, timedelta


def search_web(query: str, num_results: int = 5) -> Dict[str, Any]:
    """
    Mock web search functionality.
    In production, use a real search API like Google, Bing, or DuckDuckGo.
    """
    # Mock search results based on query keywords
    mock_results = {
        "weather": [
            {
                "title": "Weather.com - Local Weather Forecast",
                "url": "https://weather.com",
                "snippet": "Get the latest weather forecast for your area with detailed conditions.",
                "date": datetime.now() - timedelta(hours=1)
            },
            {
                "title": "National Weather Service",
                "url": "https://weather.gov",
                "snippet": "Official weather forecasts, warnings, and meteorological products.",
                "date": datetime.now() - timedelta(hours=3)
            }
        ],
        "news": [
            {
                "title": "Breaking News - Latest World News",
                "url": "https://example.com/news",
                "snippet": "Stay updated with the latest breaking news from around the world.",
                "date": datetime.now() - timedelta(minutes=30)
            },
            {
                "title": "Technology News and Updates",
                "url": "https://example.com/tech-news",
                "snippet": "Latest developments in technology, AI, and innovation.",
                "date": datetime.now() - timedelta(hours=2)
            }
        ],
        "python": [
            {
                "title": "Python.org - Official Python Programming Language",
                "url": "https://python.org",
                "snippet": "The official home of the Python Programming Language.",
                "date": datetime.now() - timedelta(days=1)
            },
            {
                "title": "Python Tutorial - Learn Python Programming",
                "url": "https://docs.python.org/tutorial",
                "snippet": "Official Python tutorial for beginners and experienced programmers.",
                "date": datetime.now() - timedelta(days=2)
            }
        ],
        "restaurants": [
            {
                "title": "Best Restaurants Near You - Reviews & Ratings",
                "url": "https://example.com/restaurants",
                "snippet": "Find the best restaurants in your area with reviews and ratings.",
                "date": datetime.now() - timedelta(hours=5)
            },
            {
                "title": "Restaurant Reservations - Book Online",
                "url": "https://example.com/reservations",
                "snippet": "Make restaurant reservations online at top-rated establishments.",
                "date": datetime.now() - timedelta(hours=8)
            }
        ]
    }
    
    # Default results for queries not in mock data
    default_results = [
        {
            "title": f"Search Results for '{query}'",
            "url": f"https://example.com/search?q={query.replace(' ', '+')}",
            "snippet": f"Comprehensive results for your search query: {query}",
            "date": datetime.now() - timedelta(hours=random.randint(1, 24))
        },
        {
            "title": f"Learn More About {query}",
            "url": f"https://example.com/wiki/{query.replace(' ', '_')}",
            "snippet": f"Detailed information and resources about {query}",
            "date": datetime.now() - timedelta(days=random.randint(1, 7))
        },
        {
            "title": f"{query} - Latest Updates",
            "url": f"https://example.com/updates/{query.replace(' ', '-')}",
            "snippet": f"Stay informed with the latest updates about {query}",
            "date": datetime.now() - timedelta(hours=random.randint(2, 12))
        }
    ]
    
    # Find relevant results
    results = []
    query_lower = query.lower()
    
    # Check for keyword matches
    for keyword, keyword_results in mock_results.items():
        if keyword in query_lower:
            results.extend(keyword_results)
    
    # Add default results if needed
    if len(results) < num_results:
        results.extend(default_results)
    
    # Limit to requested number
    results = results[:num_results]
    
    # Format results
    formatted_results = []
    for i, result in enumerate(results):
        formatted_results.append({
            "position": i + 1,
            "title": result["title"],
            "url": result["url"],
            "snippet": result["snippet"],
            "date": result["date"].isoformat()
        })
    
    return {
        "success": True,
        "query": query,
        "num_results": len(formatted_results),
        "results": formatted_results
    }


def search_news(query: str, category: str = "general", num_results: int = 5) -> Dict[str, Any]:
    """
    Search for news articles.
    In production, use a news API like NewsAPI or Google News.
    """
    categories = {
        "general": "General News",
        "technology": "Technology News",
        "business": "Business News",
        "science": "Science News",
        "health": "Health News",
        "sports": "Sports News",
        "entertainment": "Entertainment News"
    }
    
    # Mock news results
    results = []
    for i in range(num_results):
        hours_ago = random.randint(1, 48)
        results.append({
            "position": i + 1,
            "title": f"{categories.get(category, 'General')} - {query} Update #{i+1}",
            "source": random.choice(["NewsNetwork", "DailyReport", "GlobalTimes", "TechToday"]),
            "url": f"https://news.example.com/{category}/{i+1}",
            "snippet": f"Latest developments regarding {query} in the {category} sector. This article covers recent updates and expert analysis.",
            "published": (datetime.now() - timedelta(hours=hours_ago)).isoformat(),
            "category": category
        })
    
    return {
        "success": True,
        "query": query,
        "category": category,
        "num_results": len(results),
        "results": results
    }


def search_images(query: str, num_results: int = 5) -> Dict[str, Any]:
    """
    Search for images.
    In production, use an image search API.
    """
    # Mock image results
    results = []
    for i in range(num_results):
        results.append({
            "position": i + 1,
            "title": f"{query} - Image {i+1}",
            "url": f"https://images.example.com/{query.replace(' ', '-')}-{i+1}.jpg",
            "thumbnail_url": f"https://images.example.com/thumb/{query.replace(' ', '-')}-{i+1}.jpg",
            "source": random.choice(["StockPhotos", "FreeImages", "PhotoBank", "ImageHub"]),
            "width": random.choice([800, 1024, 1200, 1920]),
            "height": random.choice([600, 768, 900, 1080]),
            "format": "JPEG"
        })
    
    return {
        "success": True,
        "query": query,
        "num_results": len(results),
        "results": results
    }


# Tool metadata for registration
TOOL_METADATA = {
    "name": "search",
    "description": "Search the web for information, news, and images",
    "parameters": {
        "type": "object",
        "properties": {
            "query": {
                "type": "string",
                "description": "Search query"
            },
            "search_type": {
                "type": "string",
                "enum": ["web", "news", "images"],
                "description": "Type of search to perform",
                "default": "web"
            },
            "num_results": {
                "type": "integer",
                "description": "Number of results to return",
                "default": 5,
                "minimum": 1,
                "maximum": 20
            },
            "category": {
                "type": "string",
                "description": "News category (for news search)",
                "enum": ["general", "technology", "business", "science", "health", "sports", "entertainment"],
                "default": "general"
            }
        },
        "required": ["query"]
    },
    "examples": [
        {"query": "artificial intelligence", "search_type": "web"},
        {"query": "climate change", "search_type": "news", "category": "science"},
        {"query": "sunset landscape", "search_type": "images", "num_results": 10}
    ]
}


if __name__ == "__main__":
    # Test the search tool
    print("Testing search tool...")
    
    # Test web search
    result = search_web("python programming")
    print(f"\nWeb search results: {result}")
    
    # Test news search
    result = search_news("artificial intelligence", category="technology")
    print(f"\nNews search results: {result}")
    
    # Test image search
    result = search_images("beautiful sunset")
    print(f"\nImage search results: {result}")