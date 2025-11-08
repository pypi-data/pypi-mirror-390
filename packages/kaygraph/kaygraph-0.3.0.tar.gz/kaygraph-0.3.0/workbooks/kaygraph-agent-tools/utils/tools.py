"""
Tool implementations for external system integration.
These are the actual functions that get called when LLM requests tool usage.
"""

import json
import math
import requests
from datetime import datetime
from typing import Dict, Any, List, Optional, Callable

# Try to import pytz, fall back to basic timezone support
try:
    import pytz
    PYTZ_AVAILABLE = True
except ImportError:
    PYTZ_AVAILABLE = False


# Tool registry for easy management
TOOL_REGISTRY = {}


def register_tool(name: str, description: str, parameters: Dict[str, Any]):
    """Decorator to register tools with metadata."""
    def decorator(func: Callable):
        TOOL_REGISTRY[name] = {
            "function": func,
            "description": description,
            "parameters": parameters
        }
        return func
    return decorator


# ============== Weather Tool ==============

@register_tool(
    name="get_weather",
    description="Get current weather for a location using latitude and longitude",
    parameters={
        "type": "object",
        "properties": {
            "latitude": {"type": "number", "description": "Latitude of the location"},
            "longitude": {"type": "number", "description": "Longitude of the location"},
            "location_name": {"type": "string", "description": "Human-readable location name"}
        },
        "required": ["latitude", "longitude"]
    }
)
def get_weather(latitude: float, longitude: float, location_name: str = "") -> Dict[str, Any]:
    """
    Get current weather using Open-Meteo API (no key required).
    
    Returns weather data including temperature, wind speed, and conditions.
    """
    try:
        response = requests.get(
            "https://api.open-meteo.com/v1/forecast",
            params={
                "latitude": latitude,
                "longitude": longitude,
                "current": "temperature_2m,wind_speed_10m,weather_code,relative_humidity_2m",
                "temperature_unit": "celsius"
            },
            timeout=5
        )
        response.raise_for_status()
        
        data = response.json()
        current = data["current"]
        
        # Weather code descriptions
        weather_codes = {
            0: "Clear sky",
            1: "Mainly clear",
            2: "Partly cloudy",
            3: "Overcast",
            45: "Foggy",
            48: "Depositing rime fog",
            51: "Light drizzle",
            61: "Slight rain",
            71: "Slight snow",
            95: "Thunderstorm"
        }
        
        weather_desc = weather_codes.get(current["weather_code"], "Unknown")
        
        return {
            "location": location_name or f"{latitude}, {longitude}",
            "temperature": current["temperature_2m"],
            "unit": "°C",
            "conditions": weather_desc,
            "wind_speed": current["wind_speed_10m"],
            "humidity": current["relative_humidity_2m"],
            "observation_time": current["time"]
        }
        
    except Exception as e:
        return {
            "error": f"Weather API error: {str(e)}",
            "location": location_name or f"{latitude}, {longitude}"
        }


# ============== Calculator Tool ==============

@register_tool(
    name="calculate",
    description="Perform mathematical calculations",
    parameters={
        "type": "object",
        "properties": {
            "expression": {"type": "string", "description": "Mathematical expression to evaluate"}
        },
        "required": ["expression"]
    }
)
def calculate(expression: str) -> Dict[str, Any]:
    """
    Safely evaluate mathematical expressions.
    
    Supports: +, -, *, /, **, (), and math functions.
    """
    try:
        # Create safe namespace with math functions
        safe_dict = {
            "abs": abs,
            "round": round,
            "pow": pow,
            "sqrt": math.sqrt,
            "sin": math.sin,
            "cos": math.cos,
            "tan": math.tan,
            "pi": math.pi,
            "e": math.e,
            "log": math.log,
            "log10": math.log10
        }
        
        # Safely evaluate expression
        result = eval(expression, {"__builtins__": {}}, safe_dict)
        
        return {
            "expression": expression,
            "result": result,
            "type": type(result).__name__
        }
        
    except Exception as e:
        return {
            "error": f"Calculation error: {str(e)}",
            "expression": expression
        }


# ============== Time Tool ==============

@register_tool(
    name="get_time",
    description="Get current time in a specific timezone",
    parameters={
        "type": "object", 
        "properties": {
            "timezone": {"type": "string", "description": "Timezone name (e.g., 'US/Eastern', 'Europe/London', 'Asia/Tokyo')"}
        },
        "required": ["timezone"]
    }
)
def get_time(timezone: str) -> Dict[str, Any]:
    """Get current time in specified timezone."""
    if not PYTZ_AVAILABLE:
        # Basic timezone support without pytz
        current_time = datetime.now()
        return {
            "timezone": "UTC",
            "current_time": current_time.strftime("%Y-%m-%d %H:%M:%S"),
            "day_of_week": current_time.strftime("%A"),
            "note": "pytz not installed, showing UTC time"
        }
    
    try:
        tz = pytz.timezone(timezone)
        current_time = datetime.now(tz)
        
        return {
            "timezone": timezone,
            "current_time": current_time.strftime("%Y-%m-%d %H:%M:%S"),
            "day_of_week": current_time.strftime("%A"),
            "is_dst": bool(current_time.dst()),
            "utc_offset": str(current_time.strftime("%z"))
        }
        
    except pytz.exceptions.UnknownTimeZoneError:
        return {
            "error": f"Unknown timezone: {timezone}",
            "hint": "Use format like 'US/Eastern', 'Europe/Paris', 'Asia/Tokyo'"
        }
    except Exception as e:
        return {
            "error": f"Time error: {str(e)}",
            "timezone": timezone
        }


# ============== Search Tool (Mock) ==============

@register_tool(
    name="search_web",
    description="Search the web for information",
    parameters={
        "type": "object",
        "properties": {
            "query": {"type": "string", "description": "Search query"},
            "max_results": {"type": "integer", "description": "Maximum number of results", "default": 5}
        },
        "required": ["query"]
    }
)
def search_web(query: str, max_results: int = 5) -> Dict[str, Any]:
    """
    Mock web search - in production, use real search API.
    
    This demonstrates the pattern for search integration.
    """
    # Mock results for demonstration
    mock_results = {
        "weather": [
            {"title": "Weather.com", "snippet": "Get latest weather updates", "url": "https://weather.com"},
            {"title": "Local Weather", "snippet": "Your local forecast", "url": "https://example.com"}
        ],
        "news": [
            {"title": "Breaking News", "snippet": "Latest headlines", "url": "https://news.example.com"},
            {"title": "World News", "snippet": "Global updates", "url": "https://world.example.com"}
        ]
    }
    
    # Simple keyword matching for demo
    results = []
    for keyword, items in mock_results.items():
        if keyword in query.lower():
            results.extend(items[:max_results])
    
    if not results:
        results = [
            {"title": f"Result for: {query}", "snippet": "Generic search result", "url": "https://example.com"}
        ]
    
    return {
        "query": query,
        "results": results[:max_results],
        "total_results": len(results)
    }


# ============== Location Lookup Tool ==============

@register_tool(
    name="get_coordinates", 
    description="Get latitude and longitude coordinates for a city or location name",
    parameters={
        "type": "object",
        "properties": {
            "location": {"type": "string", "description": "City or location name (e.g., 'Paris', 'New York', 'Tokyo')"}
        },
        "required": ["location"]
    }
)
def get_coordinates(location: str) -> Dict[str, Any]:
    """
    Get coordinates for a location using Nominatim API.
    
    This is used to convert city names to lat/lon for weather queries.
    """
    # Common locations for quick lookup
    common_locations = {
        "paris": {"lat": 48.8566, "lon": 2.3522, "display": "Paris, France"},
        "london": {"lat": 51.5074, "lon": -0.1278, "display": "London, UK"},
        "new york": {"lat": 40.7128, "lon": -74.0060, "display": "New York, USA"},
        "tokyo": {"lat": 35.6762, "lon": 139.6503, "display": "Tokyo, Japan"},
        "sydney": {"lat": -33.8688, "lon": 151.2093, "display": "Sydney, Australia"},
        "moscow": {"lat": 55.7558, "lon": 37.6173, "display": "Moscow, Russia"},
        "beijing": {"lat": 39.9042, "lon": 116.4074, "display": "Beijing, China"},
        "mumbai": {"lat": 19.0760, "lon": 72.8777, "display": "Mumbai, India"},
        "cairo": {"lat": 30.0444, "lon": 31.2357, "display": "Cairo, Egypt"},
        "rio": {"lat": -22.9068, "lon": -43.1729, "display": "Rio de Janeiro, Brazil"}
    }
    
    # Check common locations first
    location_lower = location.lower()
    if location_lower in common_locations:
        loc = common_locations[location_lower]
        return {
            "location": loc["display"],
            "latitude": loc["lat"],
            "longitude": loc["lon"],
            "source": "cache"
        }
    
    # For other locations, use Nominatim API
    try:
        response = requests.get(
            "https://nominatim.openstreetmap.org/search",
            params={
                "q": location,
                "format": "json",
                "limit": 1
            },
            headers={"User-Agent": "KayGraphDemo/1.0"},
            timeout=5
        )
        response.raise_for_status()
        
        data = response.json()
        if data:
            result = data[0]
            return {
                "location": result["display_name"],
                "latitude": float(result["lat"]),
                "longitude": float(result["lon"]),
                "source": "api"
            }
        else:
            return {
                "error": f"Location not found: {location}",
                "location": location
            }
            
    except Exception as e:
        return {
            "error": f"Geocoding error: {str(e)}",
            "location": location
        }


# ============== Tool Execution ==============

def execute_tool(tool_name: str, parameters: Dict[str, Any]) -> Dict[str, Any]:
    """Execute a tool by name with given parameters."""
    if tool_name not in TOOL_REGISTRY:
        return {"error": f"Unknown tool: {tool_name}"}
    
    try:
        tool_func = TOOL_REGISTRY[tool_name]["function"]
        result = tool_func(**parameters)
        return result
    except Exception as e:
        return {
            "error": f"Tool execution error: {str(e)}",
            "tool": tool_name,
            "parameters": parameters
        }


def get_tool_descriptions() -> List[Dict[str, Any]]:
    """Get descriptions of all available tools for LLM."""
    descriptions = []
    for name, info in TOOL_REGISTRY.items():
        descriptions.append({
            "name": name,
            "description": info["description"],
            "parameters": info["parameters"]
        })
    return descriptions


def format_tool_result(result: Dict[str, Any]) -> str:
    """Format tool result for LLM consumption."""
    if "error" in result:
        return f"Tool error: {result['error']}"
    
    # Format based on tool type
    if "temperature" in result:
        # Weather result
        return (f"Weather in {result['location']}: "
                f"{result['temperature']}{result.get('unit', '°C')}, "
                f"{result.get('conditions', 'Unknown')}, "
                f"Wind: {result.get('wind_speed', 'N/A')} km/h, "
                f"Humidity: {result.get('humidity', 'N/A')}%")
    
    elif "expression" in result and "result" in result:
        # Calculator result
        return f"{result['expression']} = {result['result']}"
    
    elif "current_time" in result:
        # Time result
        return (f"Current time in {result['timezone']}: "
                f"{result['current_time']} ({result['day_of_week']})")
    
    elif "latitude" in result and "longitude" in result:
        # Coordinates result
        return (f"Coordinates for {result['location']}: "
                f"Latitude: {result['latitude']}, "
                f"Longitude: {result['longitude']}")
    
    else:
        # Generic formatting
        return json.dumps(result, indent=2)