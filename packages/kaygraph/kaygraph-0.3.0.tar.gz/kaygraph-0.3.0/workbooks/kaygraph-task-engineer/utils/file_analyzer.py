"""
File analyzer utilities for finding one-time use and temporary files
"""

import os
import re
from pathlib import Path
from datetime import datetime, timedelta
from typing import List, Dict

def find_onetime_files(search_path: str = ".", age_days: int = 7) -> List[Dict]:
    """
    Find files that appear to be one-time use or temporary
    
    Criteria:
    - Files with temp/tmp/test in name
    - Files with timestamps in name
    - Files with .bak, .tmp, .temp extensions
    - Files not modified in X days
    - Files with UUID-like names
    - Files in temp directories
    """
    
    candidates = []
    path = Path(search_path)
    
    # Patterns for temporary files
    temp_patterns = [
        r'.*\.tmp$',
        r'.*\.temp$',
        r'.*\.bak$',
        r'.*\.backup$',
        r'.*\.old$',
        r'.*~$',  # Editor backup files
        r'test_.*',
        r'tmp_.*',
        r'temp_.*',
        r'.*_\d{8}_\d{6}.*',  # Timestamp pattern
        r'[a-f0-9]{8}-[a-f0-9]{4}-[a-f0-9]{4}-[a-f0-9]{4}-[a-f0-9]{12}',  # UUID
    ]
    
    # Compile patterns
    compiled_patterns = [re.compile(p, re.IGNORECASE) for p in temp_patterns]
    
    # Check age threshold
    age_threshold = datetime.now() - timedelta(days=age_days)
    
    for file_path in path.rglob("*"):
        if not file_path.is_file():
            continue
            
        # Skip version control
        if ".git" in file_path.parts:
            continue
            
        file_info = {
            "path": str(file_path),
            "name": file_path.name,
            "reasons": []
        }
        
        # Check patterns
        for pattern in compiled_patterns:
            if pattern.match(file_path.name):
                file_info["reasons"].append(f"Matches pattern: {pattern.pattern}")
                
        # Check age
        try:
            mtime = datetime.fromtimestamp(file_path.stat().st_mtime)
            if mtime < age_threshold:
                file_info["reasons"].append(f"Not modified in {age_days} days")
                file_info["last_modified"] = mtime.isoformat()
        except:
            pass
            
        # Check if in temp directory
        if any(part in ["temp", "tmp", "cache", ".cache"] for part in file_path.parts):
            file_info["reasons"].append("Located in temporary directory")
            
        # Only include if we found reasons
        if file_info["reasons"]:
            candidates.append(file_info)
    
    return candidates


if __name__ == "__main__":
    # Test the function
    print("Finding potential one-time use files...")
    results = find_onetime_files(".", age_days=30)
    
    print(f"\nFound {len(results)} candidates:")
    for file in results[:10]:  # Show first 10
        print(f"\n{file['path']}")
        for reason in file['reasons']:
            print(f"  - {reason}")