"""
Weather tool implementation.
"""

import json
import urllib.request
import urllib.error
from typing import Dict, Any, Optional


def get_coordinates(location: str) -> Optional[Dict[str, float]]:
    """Get coordinates for a location name using a geocoding service."""
    # Common city coordinates (in production, use a geocoding API)
    cities = {
        "paris": {"lat": 48.8566, "lon": 2.3522},
        "new york": {"lat": 40.7128, "lon": -74.0060},
        "london": {"lat": 51.5074, "lon": -0.1278},
        "tokyo": {"lat": 35.6762, "lon": 139.6503},
        "sydney": {"lat": -33.8688, "lon": 151.2093},
        "san francisco": {"lat": 37.7749, "lon": -122.4194},
        "berlin": {"lat": 52.5200, "lon": 13.4050},
        "mumbai": {"lat": 19.0760, "lon": 72.8777},
        "singapore": {"lat": 1.3521, "lon": 103.8198},
        "dubai": {"lat": 25.2048, "lon": 55.2708},
    }
    
    location_lower = location.lower().strip()
    return cities.get(location_lower)


def get_weather(latitude: float, longitude: float) -> Dict[str, Any]:
    """
    Get current weather for given coordinates.
    Uses Open-Meteo API (no key required).
    """
    try:
        url = f"https://api.open-meteo.com/v1/forecast?latitude={latitude}&longitude={longitude}&current=temperature_2m,wind_speed_10m,weather_code&timezone=auto"
        
        req = urllib.request.Request(url)
        with urllib.request.urlopen(req, timeout=10) as response:
            data = json.loads(response.read().decode('utf-8'))
            
            # Weather codes to descriptions
            weather_codes = {
                0: "Clear sky",
                1: "Mainly clear", 2: "Partly cloudy", 3: "Overcast",
                45: "Foggy", 48: "Depositing rime fog",
                51: "Light drizzle", 53: "Moderate drizzle", 55: "Dense drizzle",
                61: "Slight rain", 63: "Moderate rain", 65: "Heavy rain",
                71: "Slight snow", 73: "Moderate snow", 75: "Heavy snow",
                77: "Snow grains",
                80: "Slight rain showers", 81: "Moderate rain showers", 82: "Violent rain showers",
                85: "Slight snow showers", 86: "Heavy snow showers",
                95: "Thunderstorm", 96: "Thunderstorm with slight hail", 99: "Thunderstorm with heavy hail"
            }
            
            current = data.get("current", {})
            weather_code = current.get("weather_code", 0)
            
            return {
                "success": True,
                "temperature": current.get("temperature_2m"),
                "temperature_unit": "°C",
                "wind_speed": current.get("wind_speed_10m"),
                "wind_speed_unit": "km/h",
                "weather": weather_codes.get(weather_code, "Unknown"),
                "weather_code": weather_code,
                "timezone": data.get("timezone"),
                "coordinates": {
                    "latitude": latitude,
                    "longitude": longitude
                }
            }
    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "coordinates": {
                "latitude": latitude,
                "longitude": longitude
            }
        }


def get_weather_by_location(location: str) -> Dict[str, Any]:
    """Get weather for a location name."""
    coords = get_coordinates(location)
    if not coords:
        return {
            "success": False,
            "error": f"Location '{location}' not found. Try major cities like Paris, New York, London, etc."
        }
    
    result = get_weather(coords["lat"], coords["lon"])
    result["location"] = location
    return result


# Tool metadata for registration
TOOL_METADATA = {
    "name": "weather",
    "description": "Get current weather information for any location",
    "parameters": {
        "type": "object",
        "properties": {
            "location": {
                "type": "string",
                "description": "City name (e.g., 'Paris', 'New York')"
            },
            "latitude": {
                "type": "number",
                "description": "Latitude coordinate"
            },
            "longitude": {
                "type": "number",
                "description": "Longitude coordinate"
            }
        },
        "required": []
    },
    "examples": [
        {"location": "Paris"},
        {"latitude": 48.8566, "longitude": 2.3522}
    ]
}


if __name__ == "__main__":
    # Test the weather tool
    print("Testing weather tool...")
    
    # Test with city name
    result = get_weather_by_location("Paris")
    print(f"\nParis weather: {json.dumps(result, indent=2)}")
    
    # Test with coordinates
    result = get_weather(40.7128, -74.0060)  # New York
    print(f"\nNew York weather: {json.dumps(result, indent=2)}")