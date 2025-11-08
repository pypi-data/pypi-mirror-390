"""Security Checker Droid - Factory AI Pattern Implementation.

Specialized agent for security analysis following Factory AI's security droid pattern.
"""

import logging
from pathlib import Path
from typing import Dict, Any, Optional
from datetime import datetime

from kaygraph import AsyncNode
from utils.claude_headless import ClaudeHeadless, OutputFormat, PermissionMode


logger = logging.getLogger(__name__)


class SecurityCheckerDroid(AsyncNode):
    """Factory AI-style security analysis droid.

    **Purpose**: Security specialist scanning for:
    - OWASP Top 10 vulnerabilities
    - Exposed secrets/credentials
    - Insecure dependencies
    - Authentication/authorization issues
    - Data exposure risks

    **Tools**: Read + WebSearch (for CVE lookup)
    **Model**: Inherits or uses Sonnet
    **Output**: Security report with risk levels
    """

    SECURITY_PROMPT_TEMPLATE = """# Security Checker Droid

You are a security specialist performing comprehensive security analysis.

## Operating Rules
1. Scan all code files systematically
2. Use Grep to find dangerous patterns
3. WebSearch for known CVEs in dependencies
4. Flag critical issues immediately
5. Provide remediation steps for each finding

## Scan Scope
Files to Analyze:
{files_to_scan}

Dependencies:
{dependencies}

## Security Checks

### 1. OWASP Top 10 (2023)

#### A01:2023 - Broken Access Control
- Check for missing authorization checks
- Verify role-based access control
- Look for insecure direct object references

#### A02:2023 - Cryptographic Failures
- Hard-coded passwords/keys
- Weak encryption algorithms (MD5, SHA1)
- Insecure random number generation
- Exposed secrets in logs

#### A03:2023 - Injection
- SQL injection (raw SQL queries)
- Command injection (shell exec with user input)
- LDAP injection
- NoSQL injection

#### A04:2023 - Insecure Design
- Missing security controls
- Lack of input validation
- No rate limiting
- Insecure default configurations

#### A05:2023 - Security Misconfiguration
- Debug mode enabled in production
- Exposed admin interfaces
- Default credentials
- Verbose error messages

#### A06:2023 - Vulnerable Components
- Outdated dependencies with CVEs
- Unmaintained packages
- Known vulnerable versions

#### A07:2023 - Authentication Failures
- Weak password requirements
- No MFA/2FA
- Session fixation
- Credential stuffing vulnerabilities

#### A08:2023 - Software and Data Integrity
- Unsigned packages
- No integrity checks
- Insecure deserialization
- Code injection via dependencies

#### A09:2023 - Logging and Monitoring Failures
- Sensitive data in logs
- No audit trails
- Insufficient monitoring

#### A10:2023 - Server-Side Request Forgery (SSRF)
- Unvalidated URLs
- Internal network exposure
- Cloud metadata access

### 2. Secret Detection
Scan for:
- API keys (pattern: [A-Z_]+_API_KEY)
- AWS keys (AKIA...)
- Private keys (BEGIN PRIVATE KEY)
- Passwords in code
- OAuth tokens
- Database credentials

### 3. Common Vulnerabilities
- XSS (Cross-Site Scripting)
- CSRF (Cross-Site Request Forgery)
- Path traversal
- Insecure file uploads
- XML External Entity (XXE)
- Open redirects

### 4. Code-Specific Issues
- eval() usage (Python/JavaScript)
- exec() with user input
- Dangerous file operations
- Unvalidated redirects
- Missing HTTPS enforcement

## Output Format

Generate security report with:

### 🚨 Critical Issues (Fix Immediately)
Severity: CRITICAL
Each issue should include:
- Description
- Location (file:line)
- Impact
- Remediation steps
- Example fix (if applicable)

### ⚠️ High Priority Warnings
Severity: HIGH
Security concerns that should be addressed soon.

### 📋 Medium Priority Issues
Severity: MEDIUM
Improvements that enhance security.

### ℹ️ Low Priority Notes
Severity: LOW
Best practice suggestions.

### 📊 Security Summary
- Total issues found: X
- Critical: X
- High: X
- Medium: X
- Low: X
- Overall risk level: CRITICAL / HIGH / MEDIUM / LOW
- Recommendation: BLOCK_DEPLOYMENT / FIX_BEFORE_PROD / MONITOR

### 🔗 External References
- CVE numbers for known vulnerabilities
- OWASP references
- Security advisories

## Important
- Be specific about locations (file:line)
- Provide proof-of-concept where helpful (safely!)
- Include remediation code examples
- Link to relevant security advisories
- Rate confidence level for each finding
"""

    def __init__(
        self,
        working_dir: Optional[Path] = None,
        model: str = "inherit"
    ):
        super().__init__(node_id="security_checker_droid")
        self.working_dir = working_dir
        self.model = model
        # Read + WebSearch for CVE lookup
        self.allowed_tools = ["Read", "Grep", "WebSearch"]

    async def prep(self, shared: Dict[str, Any]) -> Dict[str, Any]:
        """Prepare security scan inputs."""
        return {
            "files_to_scan": shared.get("files_to_scan", []),
            "dependencies": shared.get("dependencies", {}),
            "target_repo": shared.get("target_repo", "."),
            "task_id": shared.get("task_id", "security-scan")
        }

    async def exec(self, prep_res: Dict[str, Any]) -> Dict[str, Any]:
        """Execute security scan using Claude Code headless."""
        logger.info("🔒 Security Checker Droid starting scan...")

        # Build scan prompt
        security_prompt = self.SECURITY_PROMPT_TEMPLATE.format(
            files_to_scan="\n".join(f"- {f}" for f in prep_res["files_to_scan"]),
            dependencies="\n".join(f"- {k}: {v}" for k, v in prep_res["dependencies"].items())
        )

        # Initialize Claude
        claude = ClaudeHeadless(
            working_dir=Path(prep_res["target_repo"]),
            default_timeout=1200  # 20 minutes for thorough scan
        )

        # Execute security scan
        result = claude.execute(
            prompt=security_prompt,
            allowed_tools=self.allowed_tools,
            output_format=OutputFormat.JSON,
            permission_mode=PermissionMode.ACCEPT_EDITS,
            timeout=1200
        )

        if not result.success:
            return {
                "success": False,
                "error": result.error,
                "security_report": None
            }

        # Parse security findings
        security_content = result.output.get("result", "") if isinstance(result.output, dict) else str(result.output)

        return {
            "success": True,
            "security_content": security_content,
            "cost_usd": result.cost_usd or 0.0,
            "duration_ms": result.duration_ms
        }

    async def post(self, shared: Dict[str, Any], prep_res: Dict[str, Any], exec_res: Dict[str, Any]):
        """Save security report as artifact."""
        if not exec_res["success"]:
            logger.error(f"Security scan failed: {exec_res['error']}")
            return "scan_failed"

        # Write security artifact
        task_id = prep_res["task_id"]
        security_file = Path(f"tasks/{task_id}/security_report.md")
        security_file.parent.mkdir(parents=True, exist_ok=True)

        security_report = f"""# Security Scan Report

**Scanned**: {datetime.now().isoformat()}
**Duration**: {exec_res['duration_ms']}ms
**Cost**: ${exec_res['cost_usd']:.4f}
**Scanner**: Security Checker Droid
**Files Scanned**: {len(prep_res['files_to_scan'])}

---

{exec_res['security_content']}

---

**Generated by**: Security Checker Droid (Factory AI Pattern)
**OWASP Top 10**: 2023 Edition
"""

        security_file.write_text(security_report)

        # Parse risk level
        content_lower = exec_res["security_content"].lower()
        if "critical" in content_lower and ("🚨" in exec_res["security_content"] or "critical:" in content_lower):
            risk_level = "CRITICAL"
            action = "block_deployment"
        elif "high" in content_lower:
            risk_level = "HIGH"
            action = "fix_before_prod"
        elif "medium" in content_lower:
            risk_level = "MEDIUM"
            action = "monitor"
        else:
            risk_level = "LOW"
            action = "approved"

        # Return metadata
        shared["security_scan"] = {
            "risk_level": risk_level,
            "action": action,
            "report_path": str(security_file),
            "cost_usd": exec_res["cost_usd"],
            "files_scanned": len(prep_res["files_to_scan"])
        }

        logger.info(f"✅ Security scan complete: {risk_level} risk")
        logger.info(f"   Report: {security_file}")
        logger.info(f"   Action: {action}")

        return action  # For conditional routing


# Testing
if __name__ == "__main__":
    import asyncio

    async def test_security_checker():
        """Test security checker droid."""
        print("Testing Security Checker Droid...")

        droid = SecurityCheckerDroid()

        shared = {
            "task_id": "test-security",
            "target_repo": ".",
            "files_to_scan": [
                "src/auth.py",
                "src/api/users.py",
                "config/database.py"
            ],
            "dependencies": {
                "django": "3.2.0",
                "requests": "2.28.0",
                "cryptography": "40.0.0"
            }
        }

        prep_res = await droid.prep(shared)
        print(f"✓ Prepared security scan for {len(prep_res['files_to_scan'])} files")
        print(f"✓ Checking {len(prep_res['dependencies'])} dependencies")

        print("✅ Security Checker Droid test structure valid")

    asyncio.run(test_security_checker())
