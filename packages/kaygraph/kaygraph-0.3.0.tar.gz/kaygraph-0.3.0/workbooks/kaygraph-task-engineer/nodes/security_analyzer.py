"""
Security analysis nodes for git diffs, code review, and vulnerability detection
"""

import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../../..')))

from kaygraph import Node
import re
import json
import subprocess
from pathlib import Path
from typing import Dict, List, Any
import logging

logger = logging.getLogger(__name__)

class GitDiffAnalyzer(Node):
    """Analyzes git diffs for security issues"""
    
    def prep(self, shared):
        return {
            "commit_range": shared.get("commit_range", "HEAD~1..HEAD"),
            "target_files": shared.get("target_files", []),
            "branch": shared.get("branch", None)
        }
    
    def exec(self, prep_res):
        from utils.git_analyzer import get_diff_content, extract_changes
        
        # Get git diff
        diff_content = get_diff_content(
            prep_res["commit_range"],
            prep_res["target_files"],
            prep_res["branch"]
        )
        
        # Extract structured changes
        changes = extract_changes(diff_content)
        
        # Quick pattern-based security check
        from config import get_security_patterns
        
        security_issues = []
        
        for change in changes:
            # Check each added/modified line
            for line_info in change.get("added_lines", []):
                line_content = line_info["content"]
                
                # Check hardcoded secrets
                for pattern in get_security_patterns("hardcoded_secrets"):
                    if re.search(pattern, line_content):
                        security_issues.append({
                            "type": "hardcoded_secret",
                            "file": change["file"],
                            "line": line_info["line_num"],
                            "pattern": pattern,
                            "content": line_content[:100]
                        })
                
                # Check SQL injection risks
                for pattern in get_security_patterns("sql_injection"):
                    if re.search(pattern, line_content):
                        security_issues.append({
                            "type": "sql_injection_risk",
                            "file": change["file"],
                            "line": line_info["line_num"],
                            "pattern": pattern,
                            "content": line_content[:100]
                        })
        
        return {
            "diff_content": diff_content,
            "changes": changes,
            "quick_issues": security_issues,
            "files_changed": len(changes),
            "requires_deep_analysis": len(security_issues) > 0 or len(changes) > 5
        }
    
    def post(self, shared, prep_res, exec_res):
        shared["diff_analysis"] = exec_res
        logger.info(f"Found {len(exec_res['quick_issues'])} potential security issues in diff")
        
        if exec_res["requires_deep_analysis"]:
            return "deep_security_analysis"
        else:
            return "security_report"


class SecurityLLMAnalyzer(Node):
    """Uses LLM for deep security analysis"""
    
    def prep(self, shared):
        diff_analysis = shared.get("diff_analysis", {})
        return {
            "diff_content": diff_analysis.get("diff_content", ""),
            "changes": diff_analysis.get("changes", []),
            "quick_issues": diff_analysis.get("quick_issues", []),
            "context": shared.get("security_context", {})
        }
    
    def exec(self, prep_res):
        from utils.llm_cerebras import analyze_security
        from config import get_model_config, get_prompt
        
        # Use LLM for comprehensive analysis
        model_config = get_model_config("fast")
        prompt = get_prompt("security_analysis", "git_diff_analysis")
        
        analysis = analyze_security(
            prompt.format(diff_content=prep_res["diff_content"]),
            model=model_config["name"],
            system_prompt=get_prompt("security_analysis", "system")
        )
        
        # Combine with pattern-based findings
        if prep_res["quick_issues"]:
            analysis["pattern_based_issues"] = prep_res["quick_issues"]
            
        return analysis
    
    def post(self, shared, prep_res, exec_res):
        shared["security_analysis"] = exec_res
        
        severity = exec_res.get("severity", "none")
        logger.info(f"Security analysis complete - Severity: {severity}")
        
        if severity in ["critical", "high"]:
            return "block_changes"
        else:
            return "security_report"


class AuthChecker(Node):
    """Specifically checks for missing authentication"""
    
    def prep(self, shared):
        return {
            "files": shared.get("target_files", []),
            "framework": shared.get("framework", "unknown")
        }
    
    def exec(self, prep_res):
        from utils.auth_analyzer import check_missing_auth
        
        results = []
        
        for file_path in prep_res["files"]:
            if not Path(file_path).exists():
                continue
                
            issues = check_missing_auth(
                file_path,
                prep_res["framework"]
            )
            
            if issues:
                results.append({
                    "file": file_path,
                    "issues": issues
                })
        
        return {
            "files_checked": len(prep_res["files"]),
            "files_with_issues": len(results),
            "auth_issues": results
        }
    
    def post(self, shared, prep_res, exec_res):
        shared["auth_check_results"] = exec_res
        
        if exec_res["files_with_issues"] > 0:
            logger.warning(f"Found missing auth in {exec_res['files_with_issues']} files")
            return "auth_remediation"
        else:
            logger.info("All endpoints have proper authentication")
            return "complete"


class SecurityReporter(Node):
    """Generates security report"""
    
    def prep(self, shared):
        return {
            "task": shared.get("task"),
            "diff_analysis": shared.get("diff_analysis", {}),
            "security_analysis": shared.get("security_analysis", {}),
            "auth_check": shared.get("auth_check_results", {})
        }
    
    def exec(self, prep_res):
        # Compile comprehensive security report
        report = {
            "summary": "Security Analysis Report",
            "task": prep_res["task"],
            "findings": {
                "critical": [],
                "high": [],
                "medium": [],
                "low": []
            },
            "statistics": {
                "files_analyzed": 0,
                "issues_found": 0,
                "patterns_matched": 0
            },
            "recommendations": []
        }
        
        # Add findings from different analyses
        if prep_res["security_analysis"]:
            analysis = prep_res["security_analysis"]
            severity = analysis.get("severity", "none")
            
            if severity != "none":
                report["findings"][severity].extend(
                    analysis.get("issues", [])
                )
            
            report["statistics"]["issues_found"] += len(
                analysis.get("issues", [])
            )
        
        # Add auth check findings
        if prep_res["auth_check"] and prep_res["auth_check"]["auth_issues"]:
            for file_issues in prep_res["auth_check"]["auth_issues"]:
                for issue in file_issues["issues"]:
                    report["findings"]["high"].append({
                        "type": "missing_authentication",
                        "file": file_issues["file"],
                        "description": issue["description"],
                        "line": issue.get("line", "unknown")
                    })
        
        # Generate recommendations
        if report["findings"]["critical"]:
            report["recommendations"].append(
                "URGENT: Address critical security issues before deployment"
            )
        
        if report["findings"]["high"]:
            report["recommendations"].append(
                "Fix high-severity issues in the next sprint"
            )
        
        return report
    
    def post(self, shared, prep_res, exec_res):
        shared["security_report"] = exec_res
        
        # Print report summary
        print("\n🔒 SECURITY ANALYSIS REPORT")
        print("=" * 50)
        
        total_issues = sum(
            len(exec_res["findings"][sev]) 
            for sev in ["critical", "high", "medium", "low"]
        )
        
        print(f"Total issues found: {total_issues}")
        
        for severity in ["critical", "high", "medium", "low"]:
            count = len(exec_res["findings"][severity])
            if count > 0:
                print(f"  {severity.upper()}: {count}")
        
        if exec_res["recommendations"]:
            print("\nRecommendations:")
            for rec in exec_res["recommendations"]:
                print(f"  • {rec}")
        
        print("=" * 50)
        
        return None  # End