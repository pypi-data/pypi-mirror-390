"""
Git analysis utilities for diffs, logs, and commit comparison
"""

import subprocess
import re
from typing import List, Dict, Optional
from pathlib import Path

def run_git_command(args: List[str], cwd: str = ".") -> str:
    """Run a git command and return output"""
    try:
        result = subprocess.run(
            ["git"] + args,
            capture_output=True,
            text=True,
            cwd=cwd,
            check=True
        )
        return result.stdout
    except subprocess.CalledProcessError as e:
        return f"Git error: {e.stderr}"


def get_diff_content(commit_range: str = "HEAD~1..HEAD", 
                     target_files: List[str] = None,
                     branch: str = None) -> str:
    """
    Get git diff content
    
    Examples:
    - get_diff_content("HEAD~1..HEAD")  # Last commit
    - get_diff_content("main..feature")  # Branch comparison
    - get_diff_content("abc123..def456")  # Commit range
    """
    
    args = ["diff", commit_range]
    
    if branch:
        args = ["diff", f"{branch}..HEAD"]
    
    # Add unified diff format for better parsing
    args.append("-U3")  # 3 lines of context
    
    if target_files:
        args.extend(target_files)
    
    return run_git_command(args)


def get_commit_log(num_commits: int = 10, 
                   format_string: str = None,
                   author: str = None) -> List[Dict]:
    """Get structured commit log"""
    
    args = ["log", f"-{num_commits}"]
    
    if format_string:
        args.append(f"--pretty=format:{format_string}")
    else:
        args.append("--pretty=format:%H|%an|%ae|%at|%s")
    
    if author:
        args.extend(["--author", author])
    
    output = run_git_command(args)
    
    commits = []
    for line in output.strip().split("\n"):
        if "|" in line:
            parts = line.split("|")
            commits.append({
                "hash": parts[0],
                "author": parts[1],
                "email": parts[2],
                "timestamp": parts[3],
                "message": parts[4] if len(parts) > 4 else ""
            })
    
    return commits


def extract_changes(diff_content: str) -> List[Dict]:
    """
    Extract structured changes from diff content
    
    Returns list of:
    {
        "file": "path/to/file",
        "additions": 10,
        "deletions": 5,
        "added_lines": [{"line_num": 42, "content": "..."}],
        "removed_lines": [{"line_num": 40, "content": "..."}]
    }
    """
    
    changes = []
    current_file = None
    current_changes = None
    
    lines = diff_content.split("\n")
    
    for i, line in enumerate(lines):
        # New file marker
        if line.startswith("diff --git"):
            if current_file and current_changes:
                changes.append(current_changes)
            
            # Extract filename
            match = re.search(r'a/(.*?)\s+b/(.*?)$', line)
            if match:
                current_file = match.group(2)
                current_changes = {
                    "file": current_file,
                    "additions": 0,
                    "deletions": 0,
                    "added_lines": [],
                    "removed_lines": []
                }
        
        # Line number marker
        elif line.startswith("@@"):
            # Extract line numbers: @@ -10,7 +10,8 @@
            match = re.search(r'@@ -(\d+),?(\d*) \+(\d+),?(\d*) @@', line)
            if match and current_changes:
                old_start = int(match.group(1))
                new_start = int(match.group(3))
                current_changes["line_range"] = {
                    "old": old_start,
                    "new": new_start
                }
        
        # Added line
        elif line.startswith("+") and not line.startswith("+++"):
            if current_changes:
                current_changes["additions"] += 1
                current_changes["added_lines"].append({
                    "line_num": len(current_changes["added_lines"]) + 1,
                    "content": line[1:]
                })
        
        # Removed line
        elif line.startswith("-") and not line.startswith("---"):
            if current_changes:
                current_changes["deletions"] += 1
                current_changes["removed_lines"].append({
                    "line_num": len(current_changes["removed_lines"]) + 1,
                    "content": line[1:]
                })
    
    # Don't forget the last file
    if current_file and current_changes:
        changes.append(current_changes)
    
    return changes


def get_files_changed(commit_range: str = "HEAD~1..HEAD") -> List[str]:
    """Get list of files changed in commit range"""
    
    args = ["diff", "--name-only", commit_range]
    output = run_git_command(args)
    
    return [f.strip() for f in output.strip().split("\n") if f.strip()]


def check_file_history(file_path: str, num_commits: int = 10) -> List[Dict]:
    """Get history of a specific file"""
    
    args = ["log", f"-{num_commits}", "--follow", "--pretty=format:%H|%at|%s", "--", file_path]
    output = run_git_command(args)
    
    history = []
    for line in output.strip().split("\n"):
        if "|" in line:
            parts = line.split("|")
            history.append({
                "commit": parts[0],
                "timestamp": parts[1],
                "message": parts[2] if len(parts) > 2 else ""
            })
    
    return history


def get_blame_info(file_path: str, line_start: int, line_end: int = None) -> List[Dict]:
    """Get blame information for specific lines"""
    
    if not line_end:
        line_end = line_start
    
    args = ["blame", "-L", f"{line_start},{line_end}", "--porcelain", file_path]
    output = run_git_command(args)
    
    blame_info = []
    current_blame = {}
    
    for line in output.split("\n"):
        if re.match(r'^[0-9a-f]{40}', line):
            parts = line.split()
            current_blame = {
                "commit": parts[0],
                "line": int(parts[2])
            }
        elif line.startswith("author "):
            current_blame["author"] = line[7:]
        elif line.startswith("author-time "):
            current_blame["timestamp"] = line[12:]
        elif line.startswith("\t"):
            current_blame["content"] = line[1:]
            blame_info.append(current_blame)
            current_blame = {}
    
    return blame_info


if __name__ == "__main__":
    # Test git analysis
    print("Testing git diff analysis...")
    
    # Get last commit diff
    diff = get_diff_content("HEAD~1..HEAD")
    print(f"Diff size: {len(diff)} characters")
    
    # Extract changes
    changes = extract_changes(diff)
    print(f"\nFound {len(changes)} changed files:")
    for change in changes[:3]:
        print(f"  {change['file']}: +{change['additions']} -{change['deletions']}")
    
    # Get recent commits
    commits = get_commit_log(5)
    print(f"\nRecent commits:")
    for commit in commits:
        print(f"  {commit['hash'][:8]}: {commit['message'][:50]}")