"""
Tool implementations for KayGraph workflows.
"""

from .weather import get_weather, get_weather_by_location, TOOL_METADATA as WEATHER_METADATA
from .calculator import calculate, solve_equation, TOOL_METADATA as CALCULATOR_METADATA
from .time_tool import (
    get_current_time, convert_time, time_difference, add_time,
    TOOL_METADATA as TIME_METADATA
)
from .search import search_web, search_news, search_images, TOOL_METADATA as SEARCH_METADATA

# Tool registry
TOOL_REGISTRY = {
    "weather": {
        "function": get_weather_by_location,
        "metadata": WEATHER_METADATA
    },
    "calculator": {
        "function": calculate,
        "metadata": CALCULATOR_METADATA
    },
    "time": {
        "function": get_current_time,
        "metadata": TIME_METADATA
    },
    "search": {
        "function": search_web,
        "metadata": SEARCH_METADATA
    }
}

__all__ = [
    "get_weather", "get_weather_by_location", 
    "calculate", "solve_equation",
    "get_current_time", "convert_time", "time_difference", "add_time",
    "search_web", "search_news", "search_images",
    "TOOL_REGISTRY"
]