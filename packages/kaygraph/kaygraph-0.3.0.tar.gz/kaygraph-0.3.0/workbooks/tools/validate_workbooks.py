#!/usr/bin/env python3
"""
Validate that all workbooks can run without errors.
"""

import subprocess
import sys
import json
from pathlib import Path
from typing import Dict, List
import time

def validate_workbook(workbook_path: Path) -> Dict:
    """Validate a single workbook."""
    result = {
        "name": workbook_path.name,
        "valid": False,
        "errors": [],
        "warnings": [],
        "time": 0
    }
    
    start_time = time.time()
    
    # Check essential files
    main_py = workbook_path / "main.py"
    requirements = workbook_path / "requirements.txt"
    readme = workbook_path / "README.md"
    
    if not readme.exists():
        result["errors"].append("Missing README.md")
    
    if not requirements.exists():
        result["errors"].append("Missing requirements.txt")
    
    if not main_py.exists():
        result["warnings"].append("Missing main.py (may have alternative entry point)")
    
    # Try to import the workbook to check for syntax errors
    if main_py.exists():
        try:
            # Run with --help or --version to avoid actual execution
            proc = subprocess.run(
                [sys.executable, "-m", "py_compile", str(main_py)],
                capture_output=True,
                text=True,
                timeout=5
            )
            
            if proc.returncode != 0:
                result["errors"].append(f"Syntax error: {proc.stderr}")
            else:
                result["valid"] = len(result["errors"]) == 0
                
        except subprocess.TimeoutExpired:
            result["errors"].append("Validation timeout")
        except Exception as e:
            result["errors"].append(f"Validation error: {str(e)}")
    
    # Check for LLM dependencies
    if readme.exists():
        readme_content = readme.read_text().lower()
        if any(term in readme_content for term in ['llm', 'ai', 'gpt', 'chat', 'agent']):
            if requirements.exists():
                req_content = requirements.read_text().lower()
                if 'openai' not in req_content and 'anthropic' not in req_content:
                    result["warnings"].append("May need LLM client library (openai) in requirements.txt")
    
    result["time"] = time.time() - start_time
    return result

def generate_validation_report(results: List[Dict]):
    """Generate a validation report."""
    total = len(results)
    valid = sum(1 for r in results if r["valid"])
    errors = sum(1 for r in results if r["errors"])
    warnings = sum(1 for r in results if r["warnings"])
    
    print("\n" + "="*60)
    print("📋 WORKBOOK VALIDATION REPORT")
    print("="*60)
    
    print(f"\n📊 Summary:")
    print(f"  Total workbooks: {total}")
    print(f"  ✅ Valid: {valid}")
    print(f"  ❌ Errors: {errors}")
    print(f"  ⚠️  Warnings: {warnings}")
    
    if errors > 0:
        print(f"\n❌ Workbooks with errors:")
        for r in results:
            if r["errors"]:
                print(f"\n  {r['name']}:")
                for error in r["errors"]:
                    print(f"    - {error}")
    
    if warnings > 0:
        print(f"\n⚠️  Workbooks with warnings:")
        for r in results:
            if r["warnings"] and not r["errors"]:  # Don't repeat if already shown
                print(f"\n  {r['name']}:")
                for warning in r["warnings"]:
                    print(f"    - {warning}")
    
    # Performance stats
    total_time = sum(r["time"] for r in results)
    print(f"\n⏱️  Validation completed in {total_time:.2f} seconds")
    
    return {
        "total": total,
        "valid": valid,
        "errors": errors,
        "warnings": warnings,
        "results": results
    }

def main():
    """Run validation on all workbooks."""
    print("🔍 Validating KayGraph Workbooks...")
    print("This checks for basic issues without running the examples.")
    
    workbooks_dir = Path(".")
    workbook_dirs = sorted([
        d for d in workbooks_dir.iterdir() 
        if d.is_dir() and d.name.startswith("kaygraph-")
    ])
    
    results = []
    
    # Validate each workbook
    for i, workbook in enumerate(workbook_dirs, 1):
        print(f"\r⏳ Validating {i}/{len(workbook_dirs)}: {workbook.name}...", end="", flush=True)
        result = validate_workbook(workbook)
        results.append(result)
    
    print("\r" + " " * 80 + "\r", end="")  # Clear progress line
    
    # Generate report
    report = generate_validation_report(results)
    
    # Save detailed results
    with open("validation_report.json", "w") as f:
        json.dump(report, f, indent=2)
    
    print(f"\n📄 Detailed report saved to: validation_report.json")
    
    # Exit code based on errors
    sys.exit(0 if report["errors"] == 0 else 1)

if __name__ == "__main__":
    main()