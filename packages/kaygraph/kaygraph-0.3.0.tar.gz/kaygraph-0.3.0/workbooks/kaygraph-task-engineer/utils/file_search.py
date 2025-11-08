"""
File search utilities for finding files and content
"""

import re
import os
from pathlib import Path
from typing import List, Dict, Optional

def extract_search_criteria(task: str) -> List[Dict]:
    """
    Extract search criteria from natural language task
    
    Examples:
    - "Find all Python files containing TODO comments"
    - "Search for configuration files in the src directory"
    - "Locate all .js files with console.log statements"
    """
    
    criteria = []
    
    # Extract file patterns
    file_patterns = {
        "python": r"(?:python|\.py)\s+files?",
        "javascript": r"(?:javascript|\.js)\s+files?",
        "config": r"(?:config|configuration)\s+files?",
        "markdown": r"(?:markdown|\.md)\s+files?",
        "json": r"(?:json|\.json)\s+files?",
        "all": r"all\s+files?"
    }
    
    # Extract content patterns
    content_keywords = {
        "todo": r"(?:TODO|todo)\s+(?:comments?|items?)?",
        "fixme": r"(?:FIXME|fixme)",
        "console": r"console\.log",
        "import": r"import\s+statements?",
        "function": r"function\s+(?:definitions?|declarations?)",
        "class": r"class\s+(?:definitions?|declarations?)"
    }
    
    task_lower = task.lower()
    
    # Determine file pattern
    file_ext = None
    for pattern_type, pattern in file_patterns.items():
        if re.search(pattern, task_lower):
            if pattern_type == "python":
                file_ext = "*.py"
            elif pattern_type == "javascript":
                file_ext = "*.js"
            elif pattern_type == "config":
                file_ext = "*config*"
            elif pattern_type == "markdown":
                file_ext = "*.md"
            elif pattern_type == "json":
                file_ext = "*.json"
            elif pattern_type == "all":
                file_ext = "*"
            break
    
    if not file_ext:
        file_ext = "*"  # Default to all files
    
    # Determine content pattern
    content_pattern = None
    for keyword, pattern in content_keywords.items():
        if re.search(pattern, task_lower):
            if keyword == "todo":
                content_pattern = r"(?:#|//|/\*)\s*TODO"
            elif keyword == "fixme":
                content_pattern = r"(?:#|//|/\*)\s*FIXME"
            elif keyword == "console":
                content_pattern = r"console\.log"
            elif keyword == "import":
                content_pattern = r"^import\s+"
            elif keyword == "function":
                content_pattern = r"(?:def|function|const\s+\w+\s*=\s*(?:\(|async))"
            elif keyword == "class":
                content_pattern = r"^class\s+"
            break
    
    # Extract directory hints
    dir_pattern = r"(?:in|from|within)\s+(?:the\s+)?(\S+)\s+(?:directory|folder|path)"
    dir_match = re.search(dir_pattern, task_lower)
    search_dir = dir_match.group(1) if dir_match else "."
    
    criteria.append({
        "pattern": file_ext,
        "path": search_dir,
        "content_pattern": content_pattern,
        "description": f"Search for {file_ext} files" + (f" containing {content_pattern}" if content_pattern else "")
    })
    
    return criteria


def search_files(file_pattern: str, search_path: str = ".", content_pattern: Optional[str] = None) -> List[Dict]:
    """
    Search for files matching pattern and optionally containing specific content
    """
    
    results = []
    path = Path(search_path)
    
    # Handle case where search_path doesn't exist
    if not path.exists():
        return results
    
    # Search for files
    for file_path in path.rglob(file_pattern):
        if not file_path.is_file():
            continue
            
        # Skip version control and hidden directories
        if any(part.startswith('.') for part in file_path.parts if part != '.'):
            continue
            
        file_info = {
            "path": str(file_path),
            "name": file_path.name,
            "size": file_path.stat().st_size,
            "matches": []
        }
        
        # If content pattern specified, search within file
        if content_pattern:
            try:
                content = file_path.read_text(errors='ignore')
                lines = content.splitlines()
                
                for line_num, line in enumerate(lines, 1):
                    if re.search(content_pattern, line):
                        file_info["matches"].append({
                            "line": line_num,
                            "content": line.strip()[:100]  # First 100 chars
                        })
                
                # Only include files with matches
                if file_info["matches"]:
                    results.append(file_info)
            except Exception as e:
                # Skip files we can't read
                pass
        else:
            # Include all matching files
            results.append(file_info)
    
    return results


def format_search_results(results: List[Dict], max_files: int = 20) -> str:
    """
    Format search results for display
    """
    
    output = []
    
    if not results:
        output.append("No matching files found.")
        return "\n".join(output)
    
    output.append(f"Found {len(results)} matching files:")
    
    for i, file_info in enumerate(results[:max_files]):
        output.append(f"\n{i+1}. {file_info['path']}")
        
        if file_info.get("matches"):
            output.append(f"   Matches: {len(file_info['matches'])}")
            for match in file_info["matches"][:3]:  # Show first 3 matches
                output.append(f"   Line {match['line']}: {match['content']}")
            
            if len(file_info["matches"]) > 3:
                output.append(f"   ... and {len(file_info['matches']) - 3} more matches")
    
    if len(results) > max_files:
        output.append(f"\n... and {len(results) - max_files} more files")
    
    return "\n".join(output)


if __name__ == "__main__":
    # Test search
    print("Testing file search...")
    
    # Search for Python files with TODO
    results = search_files("*.py", ".", r"TODO")
    print(format_search_results(results))