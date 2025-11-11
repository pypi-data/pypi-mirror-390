"""
Notification integrations for alert delivery.

This module provides notifier classes for sending alerts to various
destinations including Slack, Email, JIRA, Webhooks, and Console.

Example:
    >>> from pyspark_storydoc.history.notifiers import SlackNotifier
    >>> import os
    >>>
    >>> notifier = SlackNotifier(
    ...     webhook_url=os.getenv("SLACK_WEBHOOK_URL")
    ... )
    >>> notifier.send("Pipeline complexity exceeded threshold!")
"""

import json
import logging
import os
import smtplib
import time
from abc import ABC, abstractmethod
from datetime import datetime
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from typing import Any, Dict, List, Optional
from urllib import request
from urllib.error import URLError

from .models import DriftAlert, AlertSeverity

logger = logging.getLogger(__name__)


class Notifier(ABC):
    """
    Base class for notification integrations.

    All notifiers must implement the send() method and support
    retry logic and error handling.
    """

    def __init__(
        self,
        dry_run: bool = False,
        max_retries: int = 3,
        retry_delay: float = 1.0,
    ):
        """
        Initialize notifier.

        Args:
            dry_run: If True, log instead of sending (default: False)
            max_retries: Maximum retry attempts (default: 3)
            retry_delay: Delay between retries in seconds (default: 1.0)
        """
        self.dry_run = dry_run
        self.max_retries = max_retries
        self.retry_delay = retry_delay

    @abstractmethod
    def send(self, message: str, **kwargs) -> bool:
        """
        Send notification message.

        Args:
            message: Message content
            **kwargs: Additional notifier-specific parameters

        Returns:
            True if sent successfully, False otherwise
        """
        pass

    def send_alert(self, alert: DriftAlert) -> bool:
        """
        Send formatted alert notification.

        Args:
            alert: DriftAlert object

        Returns:
            True if sent successfully
        """
        message = self.format_alert(alert)
        return self.send(message, severity=str(alert.severity))

    def send_batch(self, messages: List[str]) -> Dict[str, int]:
        """
        Send multiple messages in batch.

        Args:
            messages: List of messages to send

        Returns:
            Dictionary with success/failure counts
        """
        results = {"success": 0, "failed": 0}

        for message in messages:
            if self.send(message):
                results["success"] += 1
            else:
                results["failed"] += 1

        return results

    def format_alert(self, alert: DriftAlert) -> str:
        """
        Format alert as plain text message.

        Args:
            alert: DriftAlert object

        Returns:
            Formatted message string
        """
        lines = [
            f"[{alert.severity}] {alert.title}",
            "",
            f"Pipeline: {alert.pipeline_name}",
            f"Environment: {alert.environment}",
            f"Detected: {alert.detected_at.strftime('%Y-%m-%d %H:%M:%S')}",
            "",
            f"Message: {alert.message}",
            "",
            f"Recommendation: {alert.recommendation}",
        ]

        return "\n".join(lines)

    def _retry_with_backoff(self, func, *args, **kwargs) -> bool:
        """Execute function with exponential backoff retry."""
        for attempt in range(self.max_retries):
            try:
                func(*args, **kwargs)
                return True
            except Exception as e:
                if attempt < self.max_retries - 1:
                    delay = self.retry_delay * (2 ** attempt)
                    logger.warning(
                        f"Attempt {attempt + 1} failed: {str(e)}. "
                        f"Retrying in {delay}s..."
                    )
                    time.sleep(delay)
                else:
                    logger.error(
                        f"All {self.max_retries} attempts failed: {str(e)}",
                        exc_info=True
                    )
                    return False

        return False


class ConsoleNotifier(Notifier):
    """
    Print notifications to console.

    Useful for testing and debugging.
    """

    def __init__(self, **kwargs):
        """Initialize console notifier."""
        super().__init__(**kwargs)

    def send(self, message: str, **kwargs) -> bool:
        """
        Print message to console.

        Args:
            message: Message to print
            **kwargs: Additional parameters (severity, etc.)

        Returns:
            Always True
        """
        try:
            severity = kwargs.get("severity", "INFO")

            if self.dry_run:
                logger.info(f"[DRY RUN] Would send to console:")

            print(f"\n{'=' * 80}")
            print(f"[{severity}] ALERT NOTIFICATION")
            print(f"{'=' * 80}")
            print(message)
            print(f"{'=' * 80}\n")

            logger.info("Notification sent to console")
            return True

        except Exception as e:
            logger.error(f"Failed to send console notification: {str(e)}")
            return False


class SlackNotifier(Notifier):
    """
    Send notifications to Slack via webhook.

    Requires SLACK_WEBHOOK_URL environment variable or explicit webhook_url parameter.
    """

    def __init__(
        self,
        webhook_url: Optional[str] = None,
        channel: Optional[str] = None,
        username: str = "PySpark StoryDoc",
        icon_emoji: str = ":robot_face:",
        **kwargs
    ):
        """
        Initialize Slack notifier.

        Args:
            webhook_url: Slack webhook URL (or use SLACK_WEBHOOK_URL env var)
            channel: Optional channel override
            username: Bot username (default: "PySpark StoryDoc")
            icon_emoji: Bot icon emoji (default: ":robot_face:")
            **kwargs: Additional Notifier parameters
        """
        super().__init__(**kwargs)

        self.webhook_url = webhook_url or os.getenv("SLACK_WEBHOOK_URL")
        if not self.webhook_url:
            raise ValueError(
                "Slack webhook URL required. Set SLACK_WEBHOOK_URL env var "
                "or pass webhook_url parameter"
            )

        self.channel = channel
        self.username = username
        self.icon_emoji = icon_emoji

    def send(self, message: str, **kwargs) -> bool:
        """
        Send message to Slack.

        Args:
            message: Message text
            **kwargs: Additional parameters (severity, etc.)

        Returns:
            True if sent successfully
        """
        try:
            severity = kwargs.get("severity", "INFO")

            # Format message with severity color
            color = self._get_severity_color(severity)

            payload = {
                "username": self.username,
                "icon_emoji": self.icon_emoji,
                "attachments": [
                    {
                        "color": color,
                        "text": message,
                        "footer": "PySpark StoryDoc Lineage History",
                        "ts": int(datetime.now().timestamp()),
                    }
                ],
            }

            if self.channel:
                payload["channel"] = self.channel

            if self.dry_run:
                logger.info(f"[DRY RUN] Would send to Slack: {json.dumps(payload)}")
                return True

            return self._retry_with_backoff(self._send_to_slack, payload)

        except Exception as e:
            logger.error(f"Failed to send Slack notification: {str(e)}")
            return False

    def _send_to_slack(self, payload: Dict[str, Any]):
        """Send payload to Slack webhook."""
        req = request.Request(
            self.webhook_url,
            data=json.dumps(payload).encode("utf-8"),
            headers={"Content-Type": "application/json"},
        )

        with request.urlopen(req, timeout=10) as response:
            if response.status != 200:
                raise URLError(f"Slack returned status {response.status}")

        logger.info("Notification sent to Slack successfully")

    def _get_severity_color(self, severity: str) -> str:
        """Map severity to Slack message color."""
        return {
            "INFO": "good",
            "WARNING": "warning",
            "ERROR": "danger",
            "CRITICAL": "danger",
        }.get(severity, "good")


class EmailNotifier(Notifier):
    """
    Send notifications via email using SMTP.

    Requires SMTP configuration via environment variables or parameters.
    """

    def __init__(
        self,
        smtp_host: Optional[str] = None,
        smtp_port: Optional[int] = None,
        smtp_user: Optional[str] = None,
        smtp_password: Optional[str] = None,
        from_email: Optional[str] = None,
        to_emails: Optional[List[str]] = None,
        use_tls: bool = True,
        **kwargs
    ):
        """
        Initialize email notifier.

        Args:
            smtp_host: SMTP server host (or use SMTP_HOST env var)
            smtp_port: SMTP server port (or use SMTP_PORT env var, default: 587)
            smtp_user: SMTP username (or use SMTP_USER env var)
            smtp_password: SMTP password (or use SMTP_PASSWORD env var)
            from_email: Sender email address (or use SMTP_FROM_EMAIL env var)
            to_emails: List of recipient emails (or use SMTP_TO_EMAILS env var)
            use_tls: Use TLS encryption (default: True)
            **kwargs: Additional Notifier parameters
        """
        super().__init__(**kwargs)

        self.smtp_host = smtp_host or os.getenv("SMTP_HOST")
        self.smtp_port = smtp_port or int(os.getenv("SMTP_PORT", "587"))
        self.smtp_user = smtp_user or os.getenv("SMTP_USER")
        self.smtp_password = smtp_password or os.getenv("SMTP_PASSWORD")
        self.from_email = from_email or os.getenv("SMTP_FROM_EMAIL")
        self.use_tls = use_tls

        # Parse to_emails from comma-separated string if needed
        if to_emails:
            self.to_emails = to_emails
        elif os.getenv("SMTP_TO_EMAILS"):
            self.to_emails = [
                email.strip()
                for email in os.getenv("SMTP_TO_EMAILS", "").split(",")
            ]
        else:
            self.to_emails = []

        if not all([self.smtp_host, self.smtp_user, self.from_email, self.to_emails]):
            raise ValueError(
                "Email configuration incomplete. Required: "
                "SMTP_HOST, SMTP_USER, SMTP_FROM_EMAIL, SMTP_TO_EMAILS"
            )

    def send(self, message: str, **kwargs) -> bool:
        """
        Send email notification.

        Args:
            message: Email body text
            **kwargs: Additional parameters (subject, severity, etc.)

        Returns:
            True if sent successfully
        """
        try:
            subject = kwargs.get("subject", "PySpark StoryDoc Alert")
            severity = kwargs.get("severity", "INFO")

            # Add severity to subject
            subject = f"[{severity}] {subject}"

            if self.dry_run:
                logger.info(f"[DRY RUN] Would send email to {self.to_emails}")
                logger.info(f"Subject: {subject}")
                logger.info(f"Body: {message[:200]}...")
                return True

            return self._retry_with_backoff(
                self._send_email,
                subject,
                message
            )

        except Exception as e:
            logger.error(f"Failed to send email notification: {str(e)}")
            return False

    def _send_email(self, subject: str, body: str):
        """Send email via SMTP."""
        # Create message
        msg = MIMEMultipart()
        msg["From"] = self.from_email
        msg["To"] = ", ".join(self.to_emails)
        msg["Subject"] = subject

        msg.attach(MIMEText(body, "plain"))

        # Send via SMTP
        with smtplib.SMTP(self.smtp_host, self.smtp_port, timeout=30) as server:
            if self.use_tls:
                server.starttls()

            if self.smtp_password:
                server.login(self.smtp_user, self.smtp_password)

            server.send_message(msg)

        logger.info(f"Email sent successfully to {len(self.to_emails)} recipients")


class WebhookNotifier(Notifier):
    """
    Send notifications to generic webhook endpoint via HTTP POST.

    Useful for custom integrations.
    """

    def __init__(
        self,
        webhook_url: str,
        headers: Optional[Dict[str, str]] = None,
        auth_token: Optional[str] = None,
        **kwargs
    ):
        """
        Initialize webhook notifier.

        Args:
            webhook_url: Webhook endpoint URL
            headers: Optional HTTP headers
            auth_token: Optional authorization token
            **kwargs: Additional Notifier parameters
        """
        super().__init__(**kwargs)

        self.webhook_url = webhook_url
        self.headers = headers or {}

        if auth_token:
            self.headers["Authorization"] = f"Bearer {auth_token}"

        self.headers["Content-Type"] = "application/json"

    def send(self, message: str, **kwargs) -> bool:
        """
        Send POST request to webhook.

        Args:
            message: Message text
            **kwargs: Additional data to include in payload

        Returns:
            True if sent successfully
        """
        try:
            payload = {
                "message": message,
                "timestamp": datetime.now().isoformat(),
                **kwargs
            }

            if self.dry_run:
                logger.info(f"[DRY RUN] Would POST to {self.webhook_url}")
                logger.info(f"Payload: {json.dumps(payload)}")
                return True

            return self._retry_with_backoff(self._send_webhook, payload)

        except Exception as e:
            logger.error(f"Failed to send webhook notification: {str(e)}")
            return False

    def _send_webhook(self, payload: Dict[str, Any]):
        """Send payload to webhook endpoint."""
        req = request.Request(
            self.webhook_url,
            data=json.dumps(payload).encode("utf-8"),
            headers=self.headers,
        )

        with request.urlopen(req, timeout=30) as response:
            if response.status not in (200, 201, 202):
                raise URLError(f"Webhook returned status {response.status}")

        logger.info("Notification sent to webhook successfully")


class JiraNotifier(Notifier):
    """
    Create JIRA issues for critical alerts.

    Requires JIRA API configuration via environment variables or parameters.
    """

    def __init__(
        self,
        jira_url: Optional[str] = None,
        jira_user: Optional[str] = None,
        jira_api_key: Optional[str] = None,
        project_key: Optional[str] = None,
        issue_type: str = "Bug",
        **kwargs
    ):
        """
        Initialize JIRA notifier.

        Args:
            jira_url: JIRA instance URL (or use JIRA_URL env var)
            jira_user: JIRA username (or use JIRA_USER env var)
            jira_api_key: JIRA API key (or use JIRA_API_KEY env var)
            project_key: JIRA project key (or use JIRA_PROJECT_KEY env var)
            issue_type: Issue type (default: "Bug")
            **kwargs: Additional Notifier parameters
        """
        super().__init__(**kwargs)

        self.jira_url = jira_url or os.getenv("JIRA_URL")
        self.jira_user = jira_user or os.getenv("JIRA_USER")
        self.jira_api_key = jira_api_key or os.getenv("JIRA_API_KEY")
        self.project_key = project_key or os.getenv("JIRA_PROJECT_KEY")
        self.issue_type = issue_type

        if not all([self.jira_url, self.jira_user, self.jira_api_key, self.project_key]):
            raise ValueError(
                "JIRA configuration incomplete. Required: "
                "JIRA_URL, JIRA_USER, JIRA_API_KEY, JIRA_PROJECT_KEY"
            )

        # Build API endpoint
        self.api_url = f"{self.jira_url.rstrip('/')}/rest/api/2/issue"

    def send(self, message: str, **kwargs) -> bool:
        """
        Create JIRA issue.

        Args:
            message: Issue description
            **kwargs: Additional parameters (summary, severity, etc.)

        Returns:
            True if issue created successfully
        """
        try:
            summary = kwargs.get("summary", "PySpark StoryDoc Alert")
            severity = kwargs.get("severity", "INFO")

            # Only create issues for ERROR and CRITICAL
            if severity not in ("ERROR", "CRITICAL"):
                logger.info(f"Skipping JIRA issue creation for {severity} alert")
                return True

            issue_data = {
                "fields": {
                    "project": {"key": self.project_key},
                    "summary": f"[{severity}] {summary}",
                    "description": message,
                    "issuetype": {"name": self.issue_type},
                }
            }

            if self.dry_run:
                logger.info(f"[DRY RUN] Would create JIRA issue:")
                logger.info(json.dumps(issue_data, indent=2))
                return True

            return self._retry_with_backoff(self._create_jira_issue, issue_data)

        except Exception as e:
            logger.error(f"Failed to create JIRA issue: {str(e)}")
            return False

    def _create_jira_issue(self, issue_data: Dict[str, Any]):
        """Create JIRA issue via REST API."""
        import base64

        # Basic auth
        credentials = f"{self.jira_user}:{self.jira_api_key}"
        auth_header = base64.b64encode(credentials.encode()).decode()

        req = request.Request(
            self.api_url,
            data=json.dumps(issue_data).encode("utf-8"),
            headers={
                "Content-Type": "application/json",
                "Authorization": f"Basic {auth_header}",
            },
        )

        with request.urlopen(req, timeout=30) as response:
            if response.status not in (200, 201):
                raise URLError(f"JIRA API returned status {response.status}")

            result = json.loads(response.read().decode())
            issue_key = result.get("key", "unknown")
            logger.info(f"JIRA issue created successfully: {issue_key}")


class NotifierFactory:
    """
    Factory for creating notifier instances.
    """

    @staticmethod
    def create_notifier(notifier_type: str, config: Dict[str, Any]) -> Notifier:
        """
        Create notifier instance.

        Args:
            notifier_type: Type of notifier (slack/email/jira/webhook/console)
            config: Configuration dictionary

        Returns:
            Notifier instance

        Example:
            >>> factory = NotifierFactory()
            >>> notifier = factory.create_notifier("slack", {
            ...     "webhook_url": "https://hooks.slack.com/..."
            ... })
        """
        notifier_type = notifier_type.lower()

        if notifier_type == "slack":
            return SlackNotifier(**config)
        elif notifier_type == "email":
            return EmailNotifier(**config)
        elif notifier_type == "jira":
            return JiraNotifier(**config)
        elif notifier_type == "webhook":
            return WebhookNotifier(**config)
        elif notifier_type == "console":
            return ConsoleNotifier(**config)
        else:
            raise ValueError(f"Unknown notifier type: {notifier_type}")
