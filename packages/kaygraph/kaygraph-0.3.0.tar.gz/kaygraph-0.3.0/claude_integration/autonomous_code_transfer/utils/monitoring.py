"""Monitoring and alerting for autonomous agent execution.

Provides real-time progress tracking, notifications, and completion reports.
"""

import json
import logging
import smtplib
from datetime import datetime, timedelta
from typing import Dict, Any, Optional, List, Callable
from dataclasses import dataclass, asdict
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from pathlib import Path
from enum import Enum


logger = logging.getLogger(__name__)


class AlertLevel(Enum):
    """Alert severity levels."""
    INFO = "info"
    WARNING = "warning"
    ERROR = "error"
    CRITICAL = "critical"


@dataclass
class ProgressUpdate:
    """Progress update event."""
    timestamp: str
    phase: str
    message: str
    level: AlertLevel
    metadata: Dict[str, Any]


@dataclass
class ExecutionMetrics:
    """Metrics for autonomous execution."""
    start_time: datetime
    end_time: Optional[datetime] = None
    phase: str = "initialized"
    steps_completed: int = 0
    steps_total: int = 0
    files_modified: int = 0
    tests_passed: int = 0
    tests_failed: int = 0
    checkpoints_created: int = 0
    cost_usd: float = 0.0
    errors: List[str] = None

    def __post_init__(self):
        if self.errors is None:
            self.errors = []

    @property
    def duration(self) -> Optional[timedelta]:
        """Get execution duration."""
        if self.end_time:
            return self.end_time - self.start_time
        return datetime.now() - self.start_time

    @property
    def duration_str(self) -> str:
        """Get human-readable duration."""
        if duration := self.duration:
            hours, remainder = divmod(duration.total_seconds(), 3600)
            minutes, seconds = divmod(remainder, 60)
            return f"{int(hours)}h {int(minutes)}m {int(seconds)}s"
        return "N/A"

    @property
    def progress_percent(self) -> float:
        """Get progress percentage."""
        if self.steps_total == 0:
            return 0.0
        return (self.steps_completed / self.steps_total) * 100


class ProgressMonitor:
    """Monitors autonomous agent progress and sends alerts."""

    def __init__(
        self,
        task_id: str,
        webhook_url: Optional[str] = None,
        email_config: Optional[Dict[str, str]] = None,
        slack_webhook: Optional[str] = None,
        log_file: Optional[Path] = None
    ):
        """Initialize progress monitor.

        Args:
            task_id: Task identifier
            webhook_url: Generic webhook URL for notifications
            email_config: Email configuration (smtp_server, from_addr, to_addr, password)
            slack_webhook: Slack incoming webhook URL
            log_file: Optional log file path
        """
        self.task_id = task_id
        self.webhook_url = webhook_url
        self.email_config = email_config
        self.slack_webhook = slack_webhook
        self.log_file = log_file

        self.metrics = ExecutionMetrics(start_time=datetime.now())
        self.updates: List[ProgressUpdate] = []

        # Custom alert handlers
        self.alert_handlers: List[Callable[[ProgressUpdate], None]] = []

    def update(
        self,
        phase: str,
        message: str,
        level: AlertLevel = AlertLevel.INFO,
        **metadata
    ) -> None:
        """Send progress update.

        Args:
            phase: Current phase (research, planning, implementation, validation)
            message: Update message
            level: Alert level
            **metadata: Additional metadata
        """
        self.metrics.phase = phase

        update = ProgressUpdate(
            timestamp=datetime.now().isoformat(),
            phase=phase,
            message=message,
            level=level,
            metadata=metadata
        )

        self.updates.append(update)

        # Log locally
        log_method = getattr(logger, level.value, logger.info)
        log_method(f"[{phase}] {message}")

        if self.log_file:
            self._log_to_file(update)

        # Send notifications based on level
        if level in [AlertLevel.ERROR, AlertLevel.CRITICAL]:
            self._send_alert(update)
        elif level == AlertLevel.WARNING:
            # Only send warnings periodically to avoid spam
            if len(self.updates) % 5 == 0:  # Every 5 updates
                self._send_alert(update)

        # Call custom handlers
        for handler in self.alert_handlers:
            try:
                handler(update)
            except Exception as e:
                logger.error(f"Alert handler failed: {e}")

    def _log_to_file(self, update: ProgressUpdate) -> None:
        """Log update to file."""
        if not self.log_file:
            return

        try:
            self.log_file.parent.mkdir(parents=True, exist_ok=True)
            with open(self.log_file, 'a') as f:
                f.write(json.dumps(asdict(update)) + '\n')
        except Exception as e:
            logger.error(f"Failed to log to file: {e}")

    def _send_alert(self, update: ProgressUpdate) -> None:
        """Send alert through configured channels."""
        # Webhook
        if self.webhook_url:
            self._send_webhook(update)

        # Email
        if self.email_config:
            self._send_email(update)

        # Slack
        if self.slack_webhook:
            self._send_slack(update)

    def _send_webhook(self, update: ProgressUpdate) -> None:
        """Send webhook notification."""
        try:
            import httpx

            payload = {
                "task_id": self.task_id,
                "timestamp": update.timestamp,
                "phase": update.phase,
                "message": update.message,
                "level": update.level.value,
                "metadata": update.metadata
            }

            response = httpx.post(
                self.webhook_url,
                json=payload,
                timeout=10
            )
            response.raise_for_status()

        except Exception as e:
            logger.error(f"Webhook failed: {e}")

    def _send_email(self, update: ProgressUpdate) -> None:
        """Send email notification."""
        try:
            msg = MIMEMultipart('alternative')
            msg['Subject'] = f"[{update.level.value.upper()}] Autonomous Agent - {self.task_id}"
            msg['From'] = self.email_config['from_addr']
            msg['To'] = self.email_config['to_addr']

            # Create email body
            body = f"""
Autonomous Agent Alert

Task ID: {self.task_id}
Phase: {update.phase}
Level: {update.level.value.upper()}
Time: {update.timestamp}

Message:
{update.message}

Metadata:
{json.dumps(update.metadata, indent=2)}

Current Metrics:
- Progress: {self.metrics.progress_percent:.1f}%
- Steps: {self.metrics.steps_completed}/{self.metrics.steps_total}
- Duration: {self.metrics.duration_str}
- Cost: ${self.metrics.cost_usd:.2f}
"""

            msg.attach(MIMEText(body, 'plain'))

            # Send email
            with smtplib.SMTP(self.email_config['smtp_server'], 587) as server:
                server.starttls()
                server.login(
                    self.email_config['from_addr'],
                    self.email_config['password']
                )
                server.send_message(msg)

        except Exception as e:
            logger.error(f"Email failed: {e}")

    def _send_slack(self, update: ProgressUpdate) -> None:
        """Send Slack notification."""
        try:
            import httpx

            # Determine emoji and color based on level
            emoji_map = {
                AlertLevel.INFO: ":information_source:",
                AlertLevel.WARNING: ":warning:",
                AlertLevel.ERROR: ":x:",
                AlertLevel.CRITICAL: ":rotating_light:"
            }
            color_map = {
                AlertLevel.INFO: "#36a64f",
                AlertLevel.WARNING: "#ff9900",
                AlertLevel.ERROR: "#ff0000",
                AlertLevel.CRITICAL: "#990000"
            }

            payload = {
                "attachments": [{
                    "color": color_map.get(update.level, "#cccccc"),
                    "title": f"{emoji_map.get(update.level, '')} Autonomous Agent Alert",
                    "fields": [
                        {"title": "Task ID", "value": self.task_id, "short": True},
                        {"title": "Phase", "value": update.phase, "short": True},
                        {"title": "Message", "value": update.message, "short": False},
                        {"title": "Progress", "value": f"{self.metrics.progress_percent:.1f}%", "short": True},
                        {"title": "Duration", "value": self.metrics.duration_str, "short": True}
                    ],
                    "footer": "Autonomous Code Transfer Agent",
                    "ts": int(datetime.now().timestamp())
                }]
            }

            response = httpx.post(
                self.slack_webhook,
                json=payload,
                timeout=10
            )
            response.raise_for_status()

        except Exception as e:
            logger.error(f"Slack notification failed: {e}")

    def update_metrics(
        self,
        steps_completed: Optional[int] = None,
        steps_total: Optional[int] = None,
        files_modified: Optional[int] = None,
        tests_passed: Optional[int] = None,
        tests_failed: Optional[int] = None,
        checkpoints_created: Optional[int] = None,
        cost_usd: Optional[float] = None
    ) -> None:
        """Update execution metrics.

        Args:
            steps_completed: Number of steps completed
            steps_total: Total number of steps
            files_modified: Number of files modified
            tests_passed: Number of tests passed
            tests_failed: Number of tests failed
            checkpoints_created: Number of checkpoints created
            cost_usd: Cost in USD to add
        """
        if steps_completed is not None:
            self.metrics.steps_completed = steps_completed
        if steps_total is not None:
            self.metrics.steps_total = steps_total
        if files_modified is not None:
            self.metrics.files_modified += files_modified
        if tests_passed is not None:
            self.metrics.tests_passed += tests_passed
        if tests_failed is not None:
            self.metrics.tests_failed += tests_failed
        if checkpoints_created is not None:
            self.metrics.checkpoints_created += checkpoints_created
        if cost_usd is not None:
            self.metrics.cost_usd += cost_usd

    def send_completion_report(self, success: bool, final_message: str = "") -> None:
        """Send completion report.

        Args:
            success: Whether execution was successful
            final_message: Final message to include
        """
        self.metrics.end_time = datetime.now()

        level = AlertLevel.INFO if success else AlertLevel.ERROR
        status = "✅ SUCCESS" if success else "❌ FAILED"

        report = f"""
{status} - Autonomous Code Transfer Complete

Task ID: {self.task_id}
Duration: {self.metrics.duration_str}

Results:
- Phase: {self.metrics.phase}
- Steps Completed: {self.metrics.steps_completed}/{self.metrics.steps_total}
- Files Modified: {self.metrics.files_modified}
- Tests: {self.metrics.tests_passed} passed, {self.metrics.tests_failed} failed
- Checkpoints: {self.metrics.checkpoints_created}
- Cost: ${self.metrics.cost_usd:.2f}

{final_message}

Errors: {len(self.metrics.errors)}
{chr(10).join(f"  - {err}" for err in self.metrics.errors[:5])}
"""

        self.update("complete", report, level=level)

    def add_error(self, error: str) -> None:
        """Add error to metrics.

        Args:
            error: Error message
        """
        self.metrics.errors.append(error)
        self.update("error", f"Error occurred: {error}", level=AlertLevel.ERROR)

    def register_handler(self, handler: Callable[[ProgressUpdate], None]) -> None:
        """Register custom alert handler.

        Args:
            handler: Function that takes ProgressUpdate as argument
        """
        self.alert_handlers.append(handler)

    def get_summary(self) -> Dict[str, Any]:
        """Get execution summary.

        Returns:
            Dictionary with execution summary
        """
        return {
            "task_id": self.task_id,
            "phase": self.metrics.phase,
            "duration": self.metrics.duration_str,
            "progress_percent": self.metrics.progress_percent,
            "steps": f"{self.metrics.steps_completed}/{self.metrics.steps_total}",
            "files_modified": self.metrics.files_modified,
            "tests": {
                "passed": self.metrics.tests_passed,
                "failed": self.metrics.tests_failed
            },
            "checkpoints": self.metrics.checkpoints_created,
            "cost_usd": self.metrics.cost_usd,
            "errors_count": len(self.metrics.errors),
            "latest_update": self.updates[-1].message if self.updates else "N/A"
        }


# Utility for testing
if __name__ == "__main__":
    import time

    logging.basicConfig(level=logging.INFO)

    print("Testing ProgressMonitor...")

    # Create monitor (without actual notification services for testing)
    monitor = ProgressMonitor(
        task_id="test-doppler-transfer-20250105",
        log_file=Path("test_monitor.log")
    )

    print("✓ ProgressMonitor initialized")

    # Simulate workflow
    monitor.update("research", "Starting research phase", AlertLevel.INFO)
    monitor.update_metrics(steps_total=7)

    time.sleep(0.1)

    monitor.update("research", "Analyzed source codebase", AlertLevel.INFO)
    monitor.update_metrics(steps_completed=1)

    time.sleep(0.1)

    monitor.update("planning", "Creating implementation plan", AlertLevel.INFO)
    monitor.update_metrics(steps_completed=2)

    time.sleep(0.1)

    monitor.update("implementation", "Executing step 1", AlertLevel.INFO)
    monitor.update_metrics(steps_completed=3, files_modified=2, checkpoints_created=1)

    time.sleep(0.1)

    monitor.update("validation", "Running tests", AlertLevel.INFO)
    monitor.update_metrics(steps_completed=7, tests_passed=12, tests_failed=0, cost_usd=2.50)

    # Get summary
    summary = monitor.get_summary()
    print(f"\n✓ Execution Summary:")
    print(json.dumps(summary, indent=2))

    # Send completion report
    monitor.send_completion_report(success=True, final_message="All tests passed!")

    print(f"\n✓ Total updates: {len(monitor.updates)}")
    print(f"✓ Log file: {monitor.log_file}")

    # Cleanup
    if monitor.log_file.exists():
        monitor.log_file.unlink()

    print("\n✅ All tests passed!")
