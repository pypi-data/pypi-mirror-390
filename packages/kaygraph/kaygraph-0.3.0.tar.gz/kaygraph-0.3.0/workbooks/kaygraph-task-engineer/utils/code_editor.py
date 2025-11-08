"""
Code editing utilities for finding and modifying specific lines
"""

import re
import os
from pathlib import Path
from typing import List, Dict, Optional, Tuple

def extract_edit_instructions(task: str) -> List[Dict]:
    """
    Extract edit instructions from natural language task
    
    Examples:
    - "Find config.py and change line 42 from DEBUG=True to DEBUG=False"
    - "In all .py files, replace 'import os' with 'import os, sys'"
    - "Remove lines containing TODO from main.py"
    """
    
    instructions = []
    
    # Patterns for different edit types
    patterns = {
        "line_edit": r"(?:find|edit|change|modify)\s+(\S+)\s+.*?line\s+(\d+).*?(?:from|change)\s+(.+?)\s+to\s+(.+)",
        "global_replace": r"(?:in|find)\s+(.+?files?),?\s+(?:replace|change)\s+['\"](.+?)['\"]\s+(?:with|to)\s+['\"](.+?)['\"]",
        "remove_lines": r"(?:remove|delete)\s+lines?\s+containing\s+['\"]?(.+?)['\"]?\s+from\s+(\S+)",
        "add_lines": r"(?:add|insert)\s+['\"](.+?)['\"]\s+(?:to|in)\s+(\S+)\s+(?:at|after)\s+line\s+(\d+)"
    }
    
    task_lower = task.lower()
    
    for edit_type, pattern in patterns.items():
        match = re.search(pattern, task_lower)
        if match:
            if edit_type == "line_edit":
                instructions.append({
                    "type": "line_edit",
                    "file_pattern": match.group(1),
                    "line_number": int(match.group(2)),
                    "search_pattern": match.group(3).strip(),
                    "replacement": match.group(4).strip()
                })
            elif edit_type == "global_replace":
                instructions.append({
                    "type": "global_replace",
                    "file_pattern": match.group(1),
                    "search_pattern": match.group(2),
                    "replacement": match.group(3)
                })
            elif edit_type == "remove_lines":
                instructions.append({
                    "type": "remove_lines",
                    "file_pattern": match.group(2),
                    "search_pattern": match.group(1)
                })
            elif edit_type == "add_lines":
                instructions.append({
                    "type": "add_lines",
                    "file_pattern": match.group(2),
                    "content": match.group(1),
                    "line_number": int(match.group(3))
                })
    
    # If no specific patterns matched, try a general approach
    if not instructions:
        # Look for file mentions and keywords
        file_pattern = r'(\S+\.\w+)'
        files = re.findall(file_pattern, task)
        
        if files and any(word in task_lower for word in ["edit", "change", "modify", "replace"]):
            instructions.append({
                "type": "general_edit",
                "file_pattern": files[0],
                "task_description": task
            })
    
    return instructions


def apply_edits(file_pattern: str, search_pattern: str, replacement: str, options: Dict = None) -> Dict:
    """
    Apply edits to files matching pattern
    """
    
    options = options or {}
    results = {
        "files_examined": 0,
        "files_modified": 0,
        "changes_made": 0,
        "errors": [],
        "modified_files": []
    }
    
    # Find matching files
    if "*" in file_pattern:
        # Glob pattern
        for file_path in Path(".").rglob(file_pattern):
            if file_path.is_file():
                result = edit_single_file(file_path, search_pattern, replacement, options)
                merge_results(results, result)
    else:
        # Specific file
        file_path = Path(file_pattern)
        if file_path.exists() and file_path.is_file():
            result = edit_single_file(file_path, search_pattern, replacement, options)
            merge_results(results, result)
        else:
            results["errors"].append(f"File not found: {file_pattern}")
    
    return results


def edit_single_file(file_path: Path, search_pattern: str, replacement: str, options: Dict) -> Dict:
    """
    Edit a single file
    """
    
    result = {
        "files_examined": 1,
        "files_modified": 0,
        "changes_made": 0,
        "errors": [],
        "modified_files": []
    }
    
    try:
        # Read file
        content = file_path.read_text()
        original_content = content
        
        # Apply edit based on type
        edit_type = options.get("type", "global_replace")
        
        if edit_type == "line_edit":
            lines = content.splitlines(keepends=True)
            line_num = options.get("line_number", 1) - 1  # Convert to 0-based
            
            if 0 <= line_num < len(lines):
                if search_pattern in lines[line_num]:
                    lines[line_num] = lines[line_num].replace(search_pattern, replacement)
                    content = "".join(lines)
                    result["changes_made"] = 1
            else:
                result["errors"].append(f"Line {line_num + 1} out of range in {file_path}")
                
        elif edit_type == "remove_lines":
            lines = content.splitlines(keepends=True)
            new_lines = [line for line in lines if search_pattern not in line]
            
            if len(new_lines) < len(lines):
                content = "".join(new_lines)
                result["changes_made"] = len(lines) - len(new_lines)
                
        else:  # global_replace
            # Count occurrences
            occurrences = content.count(search_pattern)
            
            if occurrences > 0:
                content = content.replace(search_pattern, replacement)
                result["changes_made"] = occurrences
        
        # Write back if changed
        if content != original_content:
            file_path.write_text(content)
            result["files_modified"] = 1
            result["modified_files"].append(str(file_path))
            
    except Exception as e:
        result["errors"].append(f"Error editing {file_path}: {str(e)}")
    
    return result


def merge_results(total: Dict, partial: Dict):
    """
    Merge partial results into total
    """
    total["files_examined"] += partial["files_examined"]
    total["files_modified"] += partial["files_modified"]
    total["changes_made"] += partial["changes_made"]
    total["errors"].extend(partial["errors"])
    total["modified_files"].extend(partial["modified_files"])


if __name__ == "__main__":
    # Test extraction
    test_tasks = [
        "Find config.py and change line 42 from DEBUG=True to DEBUG=False",
        "In all .py files, replace 'import os' with 'import os, sys'",
        "Remove lines containing TODO from main.py"
    ]
    
    for task in test_tasks:
        print(f"\nTask: {task}")
        instructions = extract_edit_instructions(task)
        print(f"Instructions: {instructions}")