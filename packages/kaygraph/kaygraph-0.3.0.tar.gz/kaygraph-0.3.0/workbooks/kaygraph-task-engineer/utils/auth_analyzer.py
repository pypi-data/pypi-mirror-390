"""
Authentication and authorization analysis utilities
"""

import re
from pathlib import Path
from typing import List, Dict, Optional

def check_missing_auth(file_path: str, framework: str = "unknown") -> List[Dict]:
    """
    Check for endpoints missing authentication
    
    Supports: FastAPI, Flask, Django, Express
    """
    
    issues = []
    
    try:
        content = Path(file_path).read_text()
        lines = content.splitlines()
        
        # Framework-specific patterns
        if framework.lower() in ["fastapi", "auto"]:
            issues.extend(check_fastapi_auth(lines, file_path))
        
        if framework.lower() in ["flask", "auto"]:
            issues.extend(check_flask_auth(lines, file_path))
            
        if framework.lower() in ["django", "auto"]:
            issues.extend(check_django_auth(lines, file_path))
            
        if framework.lower() in ["express", "auto"]:
            issues.extend(check_express_auth(lines, file_path))
        
        # Generic checks
        if framework == "unknown" or framework == "auto":
            issues.extend(check_generic_auth(lines, file_path))
            
    except Exception as e:
        issues.append({
            "type": "error",
            "description": f"Could not analyze {file_path}: {str(e)}",
            "severity": "low"
        })
    
    return issues


def check_fastapi_auth(lines: List[str], file_path: str) -> List[Dict]:
    """Check FastAPI endpoints for auth"""
    
    issues = []
    
    # Patterns for FastAPI endpoints
    endpoint_pattern = r'@(app|router)\.(get|post|put|delete|patch)\s*\(["\']([^"\']+)["\']'
    auth_patterns = [
        r'Depends\s*\(',
        r'current_user',
        r'get_current_user',
        r'verify_token',
        r'OAuth2PasswordBearer'
    ]
    
    # Track if we're in an endpoint
    in_endpoint = False
    endpoint_start = 0
    endpoint_path = ""
    endpoint_method = ""
    
    for i, line in enumerate(lines):
        # Check for endpoint decorator
        endpoint_match = re.search(endpoint_pattern, line)
        if endpoint_match:
            in_endpoint = True
            endpoint_start = i
            endpoint_method = endpoint_match.group(2).upper()
            endpoint_path = endpoint_match.group(3)
            continue
        
        # If we're in an endpoint definition
        if in_endpoint and line.strip().startswith("def "):
            # Check if the function has auth dependencies
            func_def_end = i
            
            # Look for auth in the next few lines (function params)
            has_auth = False
            for j in range(i, min(i + 5, len(lines))):
                if any(re.search(pattern, lines[j]) for pattern in auth_patterns):
                    has_auth = True
                    break
            
            # Check if this is a public endpoint
            is_public = any(
                pub in endpoint_path 
                for pub in ["/health", "/docs", "/openapi", "/login", "/register", "/public"]
            )
            
            if not has_auth and not is_public:
                issues.append({
                    "type": "missing_auth",
                    "severity": "high",
                    "file": file_path,
                    "line": endpoint_start + 1,
                    "description": f"{endpoint_method} {endpoint_path} endpoint missing authentication",
                    "recommendation": "Add Depends(get_current_user) to function parameters"
                })
            
            in_endpoint = False
    
    return issues


def check_flask_auth(lines: List[str], file_path: str) -> List[Dict]:
    """Check Flask endpoints for auth"""
    
    issues = []
    
    # Flask patterns
    endpoint_pattern = r'@app\.route\s*\(["\']([^"\']+)["\'].*methods=\[([^\]]+)\]'
    simple_endpoint = r'@app\.route\s*\(["\']([^"\']+)["\']'
    auth_decorators = [
        r'@login_required',
        r'@require_auth',
        r'@jwt_required',
        r'@auth\.login_required'
    ]
    
    for i, line in enumerate(lines):
        # Check for route decorator
        if "@app.route" in line or "@blueprint.route" in line:
            endpoint_match = re.search(endpoint_pattern, line) or re.search(simple_endpoint, line)
            
            if endpoint_match:
                path = endpoint_match.group(1)
                
                # Check next lines for auth decorator
                has_auth = False
                for j in range(i + 1, min(i + 5, len(lines))):
                    if any(re.search(pattern, lines[j]) for pattern in auth_decorators):
                        has_auth = True
                        break
                    if lines[j].strip().startswith("def "):
                        break
                
                # Check if public endpoint
                is_public = any(
                    pub in path 
                    for pub in ["/health", "/static", "/login", "/register", "/public"]
                )
                
                if not has_auth and not is_public:
                    issues.append({
                        "type": "missing_auth",
                        "severity": "high",
                        "file": file_path,
                        "line": i + 1,
                        "description": f"Flask route {path} missing authentication decorator",
                        "recommendation": "Add @login_required decorator before the route function"
                    })
    
    return issues


def check_django_auth(lines: List[str], file_path: str) -> List[Dict]:
    """Check Django views for auth"""
    
    issues = []
    
    # Django patterns
    view_patterns = [
        r'class\s+(\w+View)\s*\(',
        r'def\s+(\w+_view)\s*\(request'
    ]
    
    auth_patterns = [
        r'@login_required',
        r'@permission_required',
        r'LoginRequiredMixin',
        r'PermissionRequiredMixin',
        r'request\.user\.is_authenticated'
    ]
    
    # Check class-based views
    for i, line in enumerate(lines):
        if re.search(r'class\s+\w+View\s*\(', line):
            view_name = re.search(r'class\s+(\w+)', line).group(1)
            
            # Check if inherits from auth mixins
            has_auth = any(
                mixin in line 
                for mixin in ['LoginRequiredMixin', 'PermissionRequiredMixin']
            )
            
            if not has_auth and "Public" not in view_name:
                issues.append({
                    "type": "missing_auth",
                    "severity": "high",
                    "file": file_path,
                    "line": i + 1,
                    "description": f"Django view {view_name} missing authentication mixin",
                    "recommendation": "Inherit from LoginRequiredMixin"
                })
    
    return issues


def check_express_auth(lines: List[str], file_path: str) -> List[Dict]:
    """Check Express.js endpoints for auth"""
    
    issues = []
    
    # Express patterns
    endpoint_pattern = r'(app|router)\.(get|post|put|delete|patch)\s*\(["\']([^"\']+)["\']'
    auth_middleware = [
        r'authenticate',
        r'requireAuth',
        r'isAuthenticated',
        r'passport\.authenticate',
        r'jwt\.verify'
    ]
    
    for i, line in enumerate(lines):
        endpoint_match = re.search(endpoint_pattern, line)
        if endpoint_match:
            method = endpoint_match.group(2)
            path = endpoint_match.group(3)
            
            # Check if middleware is in the same line
            has_auth = any(re.search(pattern, line) for pattern in auth_middleware)
            
            # Check if public endpoint
            is_public = any(
                pub in path 
                for pub in ["/health", "/login", "/register", "/public"]
            )
            
            if not has_auth and not is_public:
                issues.append({
                    "type": "missing_auth",
                    "severity": "high",
                    "file": file_path,
                    "line": i + 1,
                    "description": f"Express {method.upper()} {path} missing auth middleware",
                    "recommendation": "Add authentication middleware to the route"
                })
    
    return issues


def check_generic_auth(lines: List[str], file_path: str) -> List[Dict]:
    """Generic auth checks for any framework"""
    
    issues = []
    
    # Look for common endpoint patterns without auth
    endpoint_indicators = [
        r'@(get|post|put|delete|patch)',
        r'\.(get|post|put|delete|patch)\s*\(',
        r'def\s+handle_',
        r'async\s+def\s+handle_'
    ]
    
    auth_indicators = [
        r'auth',
        r'token',
        r'session',
        r'current_user',
        r'is_authenticated',
        r'require_',
        r'@protected'
    ]
    
    for i, line in enumerate(lines):
        # Check if this looks like an endpoint
        if any(re.search(pattern, line, re.IGNORECASE) for pattern in endpoint_indicators):
            # Look for auth in surrounding lines
            start = max(0, i - 3)
            end = min(len(lines), i + 10)
            
            context_lines = lines[start:end]
            has_auth = any(
                any(re.search(auth_pat, ctx_line, re.IGNORECASE) for auth_pat in auth_indicators)
                for ctx_line in context_lines
            )
            
            if not has_auth:
                issues.append({
                    "type": "possible_missing_auth",
                    "severity": "medium",
                    "file": file_path,
                    "line": i + 1,
                    "description": "Possible endpoint without authentication",
                    "recommendation": "Verify this endpoint has proper authentication"
                })
    
    return issues


if __name__ == "__main__":
    # Test auth checking
    test_file = """
from fastapi import FastAPI, Depends
from auth import get_current_user

app = FastAPI()

@app.get("/public/health")
def health_check():
    return {"status": "ok"}

@app.get("/users/me")
def get_me(current_user = Depends(get_current_user)):
    return current_user

@app.post("/admin/users")
def create_user(data: dict):  # Missing auth!
    return {"created": True}
"""
    
    # Write test file
    Path("test_auth.py").write_text(test_file)
    
    # Check it
    issues = check_missing_auth("test_auth.py", "fastapi")
    print(f"Found {len(issues)} auth issues:")
    for issue in issues:
        print(f"  Line {issue['line']}: {issue['description']}")
    
    # Cleanup
    Path("test_auth.py").unlink()