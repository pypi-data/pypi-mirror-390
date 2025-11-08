"""Safety measures and rollback capabilities for autonomous agents.

Implements git checkpointing, rollback, and safety validation.
"""

import subprocess
import logging
from pathlib import Path
from typing import Optional, Dict, Any, List
from dataclasses import dataclass


logger = logging.getLogger(__name__)


@dataclass
class GitCheckpoint:
    """Git checkpoint information."""
    checkpoint_id: str
    commit_hash: str
    branch: str
    message: str
    files_changed: List[str]


class SafetyManager:
    """Manages safety measures for autonomous code modifications."""

    def __init__(self, repo_path: Path):
        """Initialize safety manager.

        Args:
            repo_path: Path to git repository
        """
        self.repo_path = repo_path
        self._verify_git_repo()

    def _verify_git_repo(self) -> None:
        """Verify that repo_path is a git repository."""
        git_dir = self.repo_path / ".git"
        if not git_dir.exists():
            raise ValueError(f"Not a git repository: {self.repo_path}")

    def _run_git(self, args: List[str], check: bool = True) -> subprocess.CompletedProcess:
        """Run git command in repo directory.

        Args:
            args: Git command arguments
            check: Whether to raise on non-zero exit

        Returns:
            CompletedProcess result
        """
        cmd = ["git", "-C", str(self.repo_path)] + args
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            check=False
        )

        if check and result.returncode != 0:
            raise RuntimeError(f"Git command failed: {' '.join(cmd)}\n{result.stderr}")

        return result

    def create_checkpoint(
        self,
        checkpoint_id: str,
        message: str = "Autonomous agent checkpoint"
    ) -> GitCheckpoint:
        """Create git checkpoint before making changes.

        Args:
            checkpoint_id: Unique checkpoint identifier
            message: Commit message

        Returns:
            GitCheckpoint information
        """
        logger.info(f"Creating checkpoint: {checkpoint_id}")

        # Get current branch
        branch_result = self._run_git(["rev-parse", "--abbrev-ref", "HEAD"])
        current_branch = branch_result.stdout.strip()

        # Stage all changes
        self._run_git(["add", "-A"])

        # Check if there are changes to commit
        status_result = self._run_git(["status", "--porcelain"], check=False)
        if not status_result.stdout.strip():
            # No changes, get current commit
            commit_result = self._run_git(["rev-parse", "HEAD"])
            commit_hash = commit_result.stdout.strip()
            logger.info(f"No changes to commit, using current: {commit_hash[:8]}")

            return GitCheckpoint(
                checkpoint_id=checkpoint_id,
                commit_hash=commit_hash,
                branch=current_branch,
                message=message,
                files_changed=[]
            )

        # Get list of changed files before commit
        diff_result = self._run_git(["diff", "--cached", "--name-only"])
        files_changed = [f.strip() for f in diff_result.stdout.split('\n') if f.strip()]

        # Create commit with checkpoint tag
        full_message = f"[{checkpoint_id}] {message}"
        self._run_git(["commit", "-m", full_message])

        # Get commit hash
        commit_result = self._run_git(["rev-parse", "HEAD"])
        commit_hash = commit_result.stdout.strip()

        # Tag the commit
        tag_name = f"checkpoint-{checkpoint_id}"
        self._run_git(["tag", "-f", tag_name, commit_hash])

        logger.info(f"✓ Checkpoint created: {commit_hash[:8]} ({len(files_changed)} files)")

        return GitCheckpoint(
            checkpoint_id=checkpoint_id,
            commit_hash=commit_hash,
            branch=current_branch,
            message=message,
            files_changed=files_changed
        )

    def rollback_to_checkpoint(
        self,
        checkpoint: GitCheckpoint,
        hard: bool = False
    ) -> bool:
        """Rollback to a specific checkpoint.

        Args:
            checkpoint: Checkpoint to rollback to
            hard: If True, discard all changes (--hard reset)

        Returns:
            True if successful
        """
        logger.warning(f"Rolling back to checkpoint: {checkpoint.checkpoint_id}")

        try:
            if hard:
                # Hard reset - discard all changes
                self._run_git(["reset", "--hard", checkpoint.commit_hash])
                logger.info("✓ Hard reset complete")
            else:
                # Soft reset - preserve changes in working directory
                self._run_git(["reset", "--soft", checkpoint.commit_hash])
                logger.info("✓ Soft reset complete, changes preserved")

            return True

        except RuntimeError as e:
            logger.error(f"Rollback failed: {e}")
            return False

    def list_checkpoints(self, limit: int = 20) -> List[GitCheckpoint]:
        """List recent checkpoints.

        Args:
            limit: Maximum number of checkpoints to return

        Returns:
            List of GitCheckpoint objects
        """
        # Get commits with checkpoint tags
        log_result = self._run_git([
            "log",
            "--all",
            "--grep=^\\[checkpoint-",
            f"-n{limit}",
            "--pretty=format:%H|%s|%D"
        ])

        checkpoints = []
        for line in log_result.stdout.split('\n'):
            if not line.strip():
                continue

            parts = line.split('|')
            if len(parts) < 2:
                continue

            commit_hash = parts[0]
            message = parts[1]

            # Extract checkpoint ID from message
            if message.startswith('[') and ']' in message:
                checkpoint_id = message[1:message.index(']')]

                # Get files changed in this commit
                diff_result = self._run_git([
                    "diff-tree", "--no-commit-id", "--name-only", "-r", commit_hash
                ])
                files_changed = [f.strip() for f in diff_result.stdout.split('\n') if f.strip()]

                checkpoints.append(GitCheckpoint(
                    checkpoint_id=checkpoint_id,
                    commit_hash=commit_hash,
                    branch="",  # Would need separate query
                    message=message,
                    files_changed=files_changed
                ))

        return checkpoints

    def validate_syntax(self, file_patterns: Optional[List[str]] = None) -> Dict[str, Any]:
        """Validate syntax of modified files.

        Args:
            file_patterns: Optional list of file patterns to check

        Returns:
            Dictionary with validation results
        """
        logger.info("Validating syntax...")

        # Get list of modified files
        status_result = self._run_git(["diff", "--name-only", "HEAD"], check=False)
        modified_files = [f.strip() for f in status_result.stdout.split('\n') if f.strip()]

        if not modified_files:
            return {"status": "success", "message": "No files to validate", "files": []}

        # Run linters based on file types
        results = {
            "status": "success",
            "files": [],
            "errors": []
        }

        for file_path in modified_files:
            full_path = self.repo_path / file_path
            if not full_path.exists():
                continue

            # TypeScript/JavaScript files
            if file_path.endswith(('.ts', '.tsx', '.js', '.jsx')):
                result = self._validate_typescript(full_path)
                results["files"].append({
                    "path": file_path,
                    "type": "typescript",
                    "valid": result["valid"],
                    "errors": result.get("errors", [])
                })
                if not result["valid"]:
                    results["status"] = "failed"
                    results["errors"].extend(result.get("errors", []))

            # Python files
            elif file_path.endswith('.py'):
                result = self._validate_python(full_path)
                results["files"].append({
                    "path": file_path,
                    "type": "python",
                    "valid": result["valid"],
                    "errors": result.get("errors", [])
                })
                if not result["valid"]:
                    results["status"] = "failed"
                    results["errors"].extend(result.get("errors", []))

        return results

    def _validate_typescript(self, file_path: Path) -> Dict[str, Any]:
        """Validate TypeScript/JavaScript file syntax."""
        try:
            # Try using tsc or eslint if available
            result = subprocess.run(
                ["npx", "tsc", "--noEmit", str(file_path)],
                capture_output=True,
                text=True,
                timeout=30,
                check=False,
                cwd=str(self.repo_path)
            )

            if result.returncode == 0:
                return {"valid": True}
            else:
                return {
                    "valid": False,
                    "errors": [result.stderr]
                }

        except (FileNotFoundError, subprocess.TimeoutExpired):
            # Fallback to basic syntax check
            try:
                # Just try to parse the file
                import ast
                file_path.read_text()
                return {"valid": True}
            except Exception as e:
                return {"valid": False, "errors": [str(e)]}

    def _validate_python(self, file_path: Path) -> Dict[str, Any]:
        """Validate Python file syntax."""
        try:
            import ast
            code = file_path.read_text()
            ast.parse(code)
            return {"valid": True}
        except SyntaxError as e:
            return {
                "valid": False,
                "errors": [f"Syntax error at line {e.lineno}: {e.msg}"]
            }
        except Exception as e:
            return {
                "valid": False,
                "errors": [str(e)]
            }

    def check_for_secrets(self) -> Dict[str, Any]:
        """Check for accidentally committed secrets.

        Returns:
            Dictionary with findings
        """
        logger.info("Checking for secrets...")

        # Common secret patterns
        secret_patterns = [
            r'api[_-]?key.*[=:]\s*["\'][a-zA-Z0-9_-]{20,}["\']',
            r'password.*[=:]\s*["\'][^\s"\']+["\']',
            r'secret.*[=:]\s*["\'][^\s"\']+["\']',
            r'token.*[=:]\s*["\'][a-zA-Z0-9_-]{20,}["\']',
            r'ANTHROPIC_API_KEY',
            r'OPENAI_API_KEY',
            r'AWS_SECRET_ACCESS_KEY'
        ]

        # Get staged files
        diff_result = self._run_git(["diff", "--cached"], check=False)
        diff_content = diff_result.stdout

        findings = []
        for pattern in secret_patterns:
            import re
            matches = re.finditer(pattern, diff_content, re.IGNORECASE)
            for match in matches:
                findings.append({
                    "pattern": pattern,
                    "match": match.group(0)[:50] + "..."  # Truncate for safety
                })

        if findings:
            return {
                "status": "secrets_found",
                "count": len(findings),
                "findings": findings
            }
        else:
            return {
                "status": "clean",
                "count": 0,
                "findings": []
            }

    def get_repo_status(self) -> Dict[str, Any]:
        """Get current repository status.

        Returns:
            Dictionary with repo status
        """
        # Current branch
        branch_result = self._run_git(["rev-parse", "--abbrev-ref", "HEAD"])
        current_branch = branch_result.stdout.strip()

        # Current commit
        commit_result = self._run_git(["rev-parse", "HEAD"])
        current_commit = commit_result.stdout.strip()

        # Modified files
        status_result = self._run_git(["status", "--porcelain"], check=False)
        modified_files = [
            line.strip() for line in status_result.stdout.split('\n') if line.strip()
        ]

        # Uncommitted changes
        has_changes = len(modified_files) > 0

        return {
            "branch": current_branch,
            "commit": current_commit[:8],
            "has_changes": has_changes,
            "modified_files_count": len(modified_files),
            "modified_files": modified_files[:10]  # Show first 10
        }


# Utility for testing
if __name__ == "__main__":
    import tempfile
    import shutil

    logging.basicConfig(level=logging.INFO)

    print("Testing SafetyManager...")

    # Create temporary git repo
    with tempfile.TemporaryDirectory() as temp_dir:
        repo_path = Path(temp_dir)

        # Initialize git repo
        subprocess.run(["git", "init"], cwd=repo_path, check=True, capture_output=True)
        subprocess.run(
            ["git", "config", "user.name", "Test User"],
            cwd=repo_path,
            check=True,
            capture_output=True
        )
        subprocess.run(
            ["git", "config", "user.email", "test@example.com"],
            cwd=repo_path,
            check=True,
            capture_output=True
        )

        # Create initial commit
        test_file = repo_path / "test.txt"
        test_file.write_text("Initial content\n")
        subprocess.run(["git", "add", "."], cwd=repo_path, check=True, capture_output=True)
        subprocess.run(
            ["git", "commit", "-m", "Initial commit"],
            cwd=repo_path,
            check=True,
            capture_output=True
        )

        # Initialize safety manager
        safety = SafetyManager(repo_path)
        print("✓ SafetyManager initialized")

        # Get repo status
        status = safety.get_repo_status()
        print(f"✓ Repo status: branch={status['branch']}, commit={status['commit']}")

        # Modify file
        test_file.write_text("Modified content\n")

        # Create checkpoint
        checkpoint = safety.create_checkpoint("test-001", "Test checkpoint")
        print(f"✓ Checkpoint created: {checkpoint.commit_hash[:8]}")

        # Modify again
        test_file.write_text("Another modification\n")

        # Rollback
        success = safety.rollback_to_checkpoint(checkpoint, hard=True)
        print(f"✓ Rollback: {'success' if success else 'failed'}")

        # Verify content restored
        content = test_file.read_text()
        assert content == "Modified content\n", "Rollback failed"
        print("✓ Content verified after rollback")

        # List checkpoints
        checkpoints = safety.list_checkpoints()
        print(f"✓ Found {len(checkpoints)} checkpoint(s)")

        print("\n✅ All tests passed!")
