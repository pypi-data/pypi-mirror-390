"""
Time and timezone tool implementation.
"""

from datetime import datetime, timezone, timedelta
from typing import Dict, Any, Optional
import time


# Common timezone offsets (in production, use pytz or zoneinfo)
TIMEZONE_OFFSETS = {
    "UTC": 0,
    "GMT": 0,
    "EST": -5,  # Eastern Standard Time
    "EDT": -4,  # Eastern Daylight Time
    "CST": -6,  # Central Standard Time
    "CDT": -5,  # Central Daylight Time
    "MST": -7,  # Mountain Standard Time
    "MDT": -6,  # Mountain Daylight Time
    "PST": -8,  # Pacific Standard Time
    "PDT": -7,  # Pacific Daylight Time
    "CET": 1,   # Central European Time
    "CEST": 2,  # Central European Summer Time
    "JST": 9,   # Japan Standard Time
    "IST": 5.5, # India Standard Time
    "AEST": 10, # Australian Eastern Standard Time
    "AEDT": 11, # Australian Eastern Daylight Time
}

# City to timezone mapping
CITY_TIMEZONES = {
    "new york": "EST",
    "los angeles": "PST",
    "chicago": "CST",
    "denver": "MST",
    "london": "GMT",
    "paris": "CET",
    "berlin": "CET",
    "tokyo": "JST",
    "mumbai": "IST",
    "sydney": "AEST",
    "singapore": "UTC+8",
    "dubai": "UTC+4",
}


def get_current_time(timezone_name: Optional[str] = None) -> Dict[str, Any]:
    """Get current time in specified timezone."""
    try:
        if timezone_name:
            # Check if it's a city name
            timezone_name_lower = timezone_name.lower()
            if timezone_name_lower in CITY_TIMEZONES:
                timezone_name = CITY_TIMEZONES[timezone_name_lower]
            
            # Handle UTC+X format
            if timezone_name.startswith("UTC+") or timezone_name.startswith("UTC-"):
                try:
                    offset = float(timezone_name[3:])
                    tz = timezone(timedelta(hours=offset))
                    tz_name = timezone_name
                except:
                    return {
                        "success": False,
                        "error": f"Invalid timezone format: {timezone_name}"
                    }
            elif timezone_name.upper() in TIMEZONE_OFFSETS:
                offset = TIMEZONE_OFFSETS[timezone_name.upper()]
                tz = timezone(timedelta(hours=offset))
                tz_name = timezone_name.upper()
            else:
                return {
                    "success": False,
                    "error": f"Unknown timezone: {timezone_name}. Try 'UTC', 'EST', 'PST', 'CET', 'JST', etc."
                }
        else:
            # Default to UTC
            tz = timezone.utc
            tz_name = "UTC"
        
        now = datetime.now(tz)
        
        return {
            "success": True,
            "timezone": tz_name,
            "datetime": now.isoformat(),
            "date": now.date().isoformat(),
            "time": now.time().isoformat(),
            "timestamp": now.timestamp(),
            "formatted": now.strftime("%Y-%m-%d %H:%M:%S %Z"),
            "components": {
                "year": now.year,
                "month": now.month,
                "day": now.day,
                "hour": now.hour,
                "minute": now.minute,
                "second": now.second,
                "weekday": now.strftime("%A"),
                "month_name": now.strftime("%B")
            }
        }
    except Exception as e:
        return {
            "success": False,
            "error": str(e)
        }


def convert_time(time_str: str, from_tz: str, to_tz: str) -> Dict[str, Any]:
    """Convert time between timezones."""
    try:
        # Parse the time string
        dt = datetime.fromisoformat(time_str.replace('Z', '+00:00'))
        
        # Get timezone offsets
        from_offset = TIMEZONE_OFFSETS.get(from_tz.upper(), 0)
        to_offset = TIMEZONE_OFFSETS.get(to_tz.upper(), 0)
        
        # If the datetime is naive, assume it's in the from_tz
        if dt.tzinfo is None:
            dt = dt.replace(tzinfo=timezone(timedelta(hours=from_offset)))
        
        # Convert to target timezone
        target_tz = timezone(timedelta(hours=to_offset))
        converted = dt.astimezone(target_tz)
        
        return {
            "success": True,
            "original": {
                "time": time_str,
                "timezone": from_tz
            },
            "converted": {
                "datetime": converted.isoformat(),
                "time": converted.time().isoformat(),
                "date": converted.date().isoformat(),
                "timezone": to_tz,
                "formatted": converted.strftime("%Y-%m-%d %H:%M:%S")
            },
            "difference_hours": to_offset - from_offset
        }
    except Exception as e:
        return {
            "success": False,
            "error": str(e)
        }


def time_difference(time1: str, time2: str) -> Dict[str, Any]:
    """Calculate the difference between two times."""
    try:
        dt1 = datetime.fromisoformat(time1.replace('Z', '+00:00'))
        dt2 = datetime.fromisoformat(time2.replace('Z', '+00:00'))
        
        diff = dt2 - dt1
        total_seconds = diff.total_seconds()
        
        return {
            "success": True,
            "time1": time1,
            "time2": time2,
            "difference": {
                "days": diff.days,
                "seconds": diff.seconds,
                "total_seconds": total_seconds,
                "hours": total_seconds / 3600,
                "minutes": total_seconds / 60,
                "formatted": str(diff)
            }
        }
    except Exception as e:
        return {
            "success": False,
            "error": str(e)
        }


def add_time(base_time: str, days: int = 0, hours: int = 0, minutes: int = 0) -> Dict[str, Any]:
    """Add time to a given datetime."""
    try:
        dt = datetime.fromisoformat(base_time.replace('Z', '+00:00'))
        
        # Add the time delta
        new_dt = dt + timedelta(days=days, hours=hours, minutes=minutes)
        
        return {
            "success": True,
            "original": base_time,
            "added": {
                "days": days,
                "hours": hours,
                "minutes": minutes
            },
            "result": {
                "datetime": new_dt.isoformat(),
                "date": new_dt.date().isoformat(),
                "time": new_dt.time().isoformat(),
                "formatted": new_dt.strftime("%Y-%m-%d %H:%M:%S %Z")
            }
        }
    except Exception as e:
        return {
            "success": False,
            "error": str(e)
        }


# Tool metadata for registration
TOOL_METADATA = {
    "name": "time",
    "description": "Get current time, convert between timezones, and perform time calculations",
    "parameters": {
        "type": "object",
        "properties": {
            "operation": {
                "type": "string",
                "enum": ["current", "convert", "difference", "add"],
                "description": "Time operation to perform"
            },
            "timezone": {
                "type": "string",
                "description": "Timezone name (e.g., 'UTC', 'EST', 'PST', 'Tokyo')"
            },
            "time": {
                "type": "string",
                "description": "ISO format datetime string"
            },
            "from_tz": {
                "type": "string",
                "description": "Source timezone for conversion"
            },
            "to_tz": {
                "type": "string",
                "description": "Target timezone for conversion"
            },
            "days": {
                "type": "integer",
                "description": "Days to add"
            },
            "hours": {
                "type": "integer",
                "description": "Hours to add"
            },
            "minutes": {
                "type": "integer",
                "description": "Minutes to add"
            }
        },
        "required": ["operation"]
    },
    "examples": [
        {"operation": "current", "timezone": "EST"},
        {"operation": "current", "timezone": "Tokyo"},
        {"operation": "convert", "time": "2024-01-01T12:00:00", "from_tz": "UTC", "to_tz": "JST"}
    ]
}


if __name__ == "__main__":
    # Test the time tool
    print("Testing time tool...")
    
    # Test current time
    result = get_current_time()
    print(f"\nCurrent UTC time: {result}")
    
    result = get_current_time("EST")
    print(f"\nCurrent EST time: {result}")
    
    result = get_current_time("Tokyo")
    print(f"\nCurrent Tokyo time: {result}")
    
    # Test time conversion
    result = convert_time("2024-01-01T12:00:00", "UTC", "JST")
    print(f"\nTime conversion: {result}")