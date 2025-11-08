"""
Customer Support System Utilities.

This module contains utility functions and classes specific to the customer
support system, including CRM integration, knowledge base management,
and metrics collection.
"""

import os
import json
import time
import logging
import asyncio
from typing import Dict, Any, List, Optional, Tuple
from dataclasses import dataclass, asdict
from datetime import datetime, timedelta

from ..utils.claude_api import ClaudeAPIClient, ClaudeConfig
from ..utils.vector_store import VectorStore, Document, SimpleVectorStore


@dataclass
class Customer:
    """Customer data structure."""
    id: str
    name: str
    email: str
    tier: str  # standard, premium, enterprise
    join_date: str
    total_tickets: int = 0
    satisfaction_score: float = 0.0
    metadata: Dict[str, Any] = None

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass
class SupportMetrics:
    """Support system metrics."""
    total_tickets: int = 0
    resolved_tickets: int = 0
    escalated_tickets: int = 0
    avg_response_time: float = 0.0
    avg_resolution_time: float = 0.0
    satisfaction_score: float = 0.0
    tickets_by_category: Dict[str, int] = None
    tickets_by_priority: Dict[str, int] = None
    timestamp: str = None

    def __post_init__(self):
        if self.tickets_by_category is None:
            self.tickets_by_category = {}
        if self.tickets_by_priority is None:
            self.tickets_by_priority = {}
        if self.timestamp is None:
            self.timestamp = datetime.now().isoformat()


class CRMIntegration:
    """
    Mock CRM integration for customer data management.

    In a real implementation, this would connect to actual CRM systems
    like Salesforce, HubSpot, or custom CRM solutions.
    """

    def __init__(self):
        self.logger = logging.getLogger(f"{__name__}.{self.__class__.__name__}")
        self.customers: Dict[str, Customer] = {}
        self._load_mock_data()

    def _load_mock_data(self):
        """Load mock customer data for demonstration."""
        mock_customers = [
            Customer(
                id="cust_001",
                name="John Doe",
                email="john.doe@company.com",
                tier="premium",
                join_date="2023-01-15",
                total_tickets=5,
                satisfaction_score=0.85
            ),
            Customer(
                id="cust_002",
                name="Jane Smith",
                email="jane.smith@startup.com",
                tier="standard",
                join_date="2023-06-20",
                total_tickets=2,
                satisfaction_score=0.92
            ),
            Customer(
                id="cust_003",
                name="Acme Corp",
                email="support@acmecorp.com",
                tier="enterprise",
                join_date="2022-11-01",
                total_tickets=15,
                satisfaction_score=0.78
            )
        ]

        for customer in mock_customers:
            self.customers[customer.id] = customer

        self.logger.info(f"Loaded {len(mock_customers)} mock customers")

    async def get_customer(self, customer_id: str) -> Optional[Customer]:
        """Retrieve customer information."""
        await asyncio.sleep(0.01)  # Simulate API call
        return self.customers.get(customer_id)

    async def update_customer_metrics(self, customer_id: str, metrics: Dict[str, Any]):
        """Update customer metrics."""
        customer = self.customers.get(customer_id)
        if customer:
            customer.total_tickets += 1
            if "satisfaction_score" in metrics:
                # Update rolling average
                old_score = customer.satisfaction_score
                new_score = metrics["satisfaction_score"]
                customer.satisfaction_score = (old_score + new_score) / 2

            self.logger.info(f"Updated metrics for customer {customer_id}")

    async def get_customer_history(self, customer_id: str) -> List[Dict[str, Any]]:
        """Get customer's ticket history."""
        await asyncio.sleep(0.02)  # Simulate database query

        # Mock history data
        history = [
            {
                "ticket_id": f"ticket_{customer_id}_001",
                "created_at": "2024-01-10T10:00:00Z",
                "category": "technical",
                "priority": "medium",
                "resolution_time": 1800,  # 30 minutes
                "satisfaction": 0.9
            },
            {
                "ticket_id": f"ticket_{customer_id}_002",
                "created_at": "2024-01-15T14:30:00Z",
                "category": "billing",
                "priority": "high",
                "resolution_time": 3600,  # 1 hour
                "satisfaction": 0.8
            }
        ]

        return history


class KnowledgeBase:
    """
    Knowledge base management for support articles and FAQs.

    This class provides search and retrieval functionality for the
    company's knowledge base articles.
    """

    def __init__(self):
        self.logger = logging.getLogger(f"{__name__}.{self.__class__.__name__}")
        self.articles: Dict[str, Dict[str, Any]] = {}
        self._load_mock_articles()

    def _load_mock_articles(self):
        """Load mock knowledge base articles."""
        mock_articles = [
            {
                "id": "kb_001",
                "title": "How to Reset Your Password",
                "content": "To reset your password, click on the 'Forgot Password' link on the login page. Enter your email address and follow the instructions sent to your email. The password reset link expires after 24 hours for security reasons.",
                "category": "account",
                "tags": ["password", "login", "security", "account"],
                "difficulty": "easy",
                "last_updated": "2024-01-01T00:00:00Z",
                "views": 1250,
                "helpful_votes": 1100
            },
            {
                "id": "kb_002",
                "title": "Common Billing Issues and Solutions",
                "content": "Common billing issues include: 1) Payment method declined - Contact your bank or update payment method. 2) Duplicate charges - These are usually pre-authorization holds that resolve automatically. 3) Invoice not received - Check spam folder or update email preferences. 4) Refund processing - Refunds take 5-7 business days to appear on your statement.",
                "category": "billing",
                "tags": ["billing", "payment", "invoice", "refund"],
                "difficulty": "medium",
                "last_updated": "2024-01-15T00:00:00Z",
                "views": 890,
                "helpful_votes": 750
            },
            {
                "id": "kb_003",
                "title": "Troubleshooting Connection Issues",
                "content": "If you're experiencing connection issues: 1) Check your internet connection by visiting other websites. 2) Clear your browser cache and cookies. 3) Try using a different browser. 4) Disable VPN or proxy temporarily. 5) Check if our service status page shows any ongoing issues. Contact support if problems persist.",
                "category": "technical",
                "tags": ["connection", "troubleshooting", "browser", "vpn"],
                "difficulty": "medium",
                "last_updated": "2024-01-20T00:00:00Z",
                "views": 2100,
                "helpful_votes": 1800
            },
            {
                "id": "kb_004",
                "title": "Product Features and Usage Guide",
                "content": "Our product includes the following key features: 1) Dashboard - Overview of your metrics and activity. 2) Analytics - Detailed reports and insights. 3) Integration - Connect with your favorite tools. 4) Collaboration - Share and work with team members. 5) Automation - Set up workflows to save time. Each feature is designed to be intuitive and user-friendly.",
                "category": "product",
                "tags": ["features", "dashboard", "analytics", "integration"],
                "difficulty": "easy",
                "last_updated": "2024-01-25T00:00:00Z",
                "views": 3400,
                "helpful_votes": 3000
            }
        ]

        for article in mock_articles:
            self.articles[article["id"]] = article

        self.logger.info(f"Loaded {len(mock_articles)} knowledge base articles")

    async def search_articles(self, query: str, category: Optional[str] = None, limit: int = 5) -> List[Dict[str, Any]]:
        """Search knowledge base articles."""
        await asyncio.sleep(0.02)  # Simulate search latency

        query_lower = query.lower()
        matching_articles = []

        for article in self.articles.values():
            # Filter by category if specified
            if category and article["category"] != category:
                continue

            # Simple text matching (in real implementation, use embedding search)
            score = 0
            if query_lower in article["title"].lower():
                score += 10
            if query_lower in article["content"].lower():
                score += 5

            # Check tag matches
            for tag in article["tags"]:
                if query_lower in tag.lower():
                    score += 3

            if score > 0:
                article_copy = article.copy()
                article_copy["relevance_score"] = score
                matching_articles.append(article_copy)

        # Sort by relevance score and limit results
        matching_articles.sort(key=lambda x: x["relevance_score"], reverse=True)
        return matching_articles[:limit]

    async def get_article_by_id(self, article_id: str) -> Optional[Dict[str, Any]]:
        """Get a specific article by ID."""
        await asyncio.sleep(0.01)  # Simulate database query
        return self.articles.get(article_id)

    async def get_popular_articles(self, limit: int = 10) -> List[Dict[str, Any]]:
        """Get most popular articles by views."""
        await asyncio.sleep(0.01)
        sorted_articles = sorted(
            self.articles.values(),
            key=lambda x: x["views"],
            reverse=True
        )
        return sorted_articles[:limit]


class SupportMetrics:
    """
    Metrics collection and analysis for the support system.

    This class tracks various performance metrics and provides
    analytics for support operations.
    """

    def __init__(self):
        self.logger = logging.getLogger(f"{__name__}.{self.__class__.__name__}")
        self.metrics_history: List[SupportMetrics] = []
        self.real_time_metrics = SupportMetrics()

    def record_ticket_created(self, category: str, priority: str):
        """Record a new ticket creation."""
        self.real_time_metrics.total_tickets += 1
        self.real_time_metrics.tickets_by_category[category] = (
            self.real_time_metrics.tickets_by_category.get(category, 0) + 1
        )
        self.real_time_metrics.tickets_by_priority[priority] = (
            self.real_time_metrics.tickets_by_priority.get(priority, 0) + 1
        )

    def record_ticket_resolved(self, resolution_time: float, satisfaction_score: float):
        """Record a ticket resolution."""
        self.real_time_metrics.resolved_tickets += 1

        # Update average resolution time
        current_avg = self.real_time_metrics.avg_resolution_time
        resolved_count = self.real_time_metrics.resolved_tickets
        self.real_time_metrics.avg_resolution_time = (
            (current_avg * (resolved_count - 1) + resolution_time) / resolved_count
        )

        # Update satisfaction score
        current_satisfaction = self.real_time_metrics.satisfaction_score
        self.real_time_metrics.satisfaction_score = (
            (current_satisfaction * (resolved_count - 1) + satisfaction_score) / resolved_count
        )

    def record_escalation(self):
        """Record a ticket escalation."""
        self.real_time_metrics.escalated_tickets += 1

    def record_response_time(self, response_time: float):
        """Record a response time."""
        # Update average response time (using exponential moving average)
        alpha = 0.1  # Smoothing factor
        self.real_time_metrics.avg_response_time = (
            alpha * response_time +
            (1 - alpha) * self.real_time_metrics.avg_response_time
        )

    def get_current_metrics(self) -> SupportMetrics:
        """Get current real-time metrics."""
        return self.real_time_metrics

    def get_metrics_summary(self, hours: int = 24) -> Dict[str, Any]:
        """Get metrics summary for the specified time period."""
        cutoff_time = datetime.now() - timedelta(hours=hours)

        # Filter metrics within time period (simplified for demo)
        recent_metrics = self.real_time_metrics  # In real implementation, filter by timestamp

        return {
            "period_hours": hours,
            "total_tickets": recent_metrics.total_tickets,
            "resolved_tickets": recent_metrics.resolved_tickets,
            "escalation_rate": (
                recent_metrics.escalated_tickets / max(recent_metrics.total_tickets, 1)
            ),
            "avg_response_time": recent_metrics.avg_response_time,
            "avg_resolution_time": recent_metrics.avg_resolution_time,
            "satisfaction_score": recent_metrics.satisfaction_score,
            "tickets_by_category": recent_metrics.tickets_by_category,
            "tickets_by_priority": recent_metrics.tickets_by_priority
        }

    def export_metrics(self, format: str = "json") -> str:
        """Export metrics in specified format."""
        if format == "json":
            return json.dumps(self.real_time_metrics.to_dict(), indent=2)
        else:
            raise ValueError(f"Unsupported export format: {format}")


class NotificationService:
    """
    Notification service for sending alerts and updates.

    This service handles sending notifications through various channels
    like email, Slack, SMS, etc.
    """

    def __init__(self):
        self.logger = logging.getLogger(f"{__name__}.{self.__class__.__name__}")
        self.notification_queue: List[Dict[str, Any]] = []

    async def send_email_notification(self, to: str, subject: str, body: str, priority: str = "normal"):
        """Send email notification."""
        await asyncio.sleep(0.1)  # Simulate email sending

        notification = {
            "type": "email",
            "to": to,
            "subject": subject,
            "body": body,
            "priority": priority,
            "sent_at": datetime.now().isoformat(),
            "status": "sent"
        }

        self.logger.info(f"Email sent to {to}: {subject}")
        return notification

    async def send_slack_notification(self, channel: str, message: str, priority: str = "normal"):
        """Send Slack notification."""
        await asyncio.sleep(0.05)  # Simulate Slack API call

        notification = {
            "type": "slack",
            "channel": channel,
            "message": message,
            "priority": priority,
            "sent_at": datetime.now().isoformat(),
            "status": "sent"
        }

        self.logger.info(f"Slack message sent to {channel}: {message[:50]}...")
        return notification

    async def send_urgent_alert(self, message: str, recipients: List[str]):
        """Send urgent alert through multiple channels."""
        notifications = []

        # Send to all recipients
        for recipient in recipients:
            # Send email
            email_notif = await self.send_email_notification(
                to=recipient,
                subject="🚨 URGENT: Support Alert",
                body=message,
                priority="urgent"
            )
            notifications.append(email_notif)

        # Send to Slack channel
        slack_notif = await self.send_slack_notification(
            channel="#support-alerts",
            message=f"🚨 URGENT: {message}",
            priority="urgent"
        )
        notifications.append(slack_notif)

        self.logger.warning(f"Urgent alert sent to {len(recipients)} recipients")
        return notifications


# Utility functions for support operations
async def create_ticket_from_webhook(webhook_data: Dict[str, Any]) -> Dict[str, Any]:
    """Create ticket from incoming webhook data."""
    required_fields = ["customer_id", "subject", "content"]
    for field in required_fields:
        if field not in webhook_data:
            raise ValueError(f"Missing required field: {field}")

    ticket = {
        "id": f"ticket_{int(time.time())}_{webhook_data['customer_id']}",
        "customer_id": webhook_data["customer_id"],
        "subject": webhook_data["subject"],
        "content": webhook_data["content"],
        "source": webhook_data.get("source", "web"),
        "created_at": time.time(),
        "metadata": webhook_data.get("metadata", {})
    }

    return ticket


def calculate_agent_workload(agent_id: str, tickets: List[Dict[str, Any]]) -> Dict[str, Any]:
    """Calculate workload metrics for a specific agent."""
    agent_tickets = [t for t in tickets if t.get("assigned_agent") == agent_id]

    if not agent_tickets:
        return {
            "agent_id": agent_id,
            "total_tickets": 0,
            "avg_resolution_time": 0,
            "satisfaction_score": 0,
            "utilization": 0
        }

    total_resolution_time = sum(t.get("resolution_time", 0) for t in agent_tickets)
    avg_resolution_time = total_resolution_time / len(agent_tickets)
    satisfaction_scores = [t.get("satisfaction_score", 0) for t in agent_tickets]
    avg_satisfaction = sum(satisfaction_scores) / len(satisfaction_scores)

    return {
        "agent_id": agent_id,
        "total_tickets": len(agent_tickets),
        "avg_resolution_time": avg_resolution_time,
        "satisfaction_score": avg_satisfaction,
        "utilization": min(1.0, len(agent_tickets) / 10)  # Assume 10 tickets is full capacity
    }


if __name__ == "__main__":
    """Test the customer support utilities."""
    import asyncio

    async def test_support_utilities():
        """Test all support utilities."""
        print("Testing Customer Support Utilities")

        # Test CRM Integration
        crm = CRMIntegration()
        customer = await crm.get_customer("cust_001")
        print(f"Retrieved customer: {customer.name if customer else 'None'}")

        # Test Knowledge Base
        kb = KnowledgeBase()
        articles = await kb.search_articles("password reset")
        print(f"Found {len(articles)} articles for 'password reset'")

        # Test Metrics
        metrics = SupportMetrics()
        metrics.record_ticket_created("technical", "high")
        metrics.record_response_time(120)  # 2 minutes
        metrics.record_ticket_resolved(1800, 0.9)  # 30 minutes, high satisfaction

        current_metrics = metrics.get_current_metrics()
        print(f"Current metrics: {current_metrics.total_tickets} tickets, "
              f"satisfaction: {current_metrics.satisfaction_score:.2f}")

        # Test Notifications
        notifications = NotificationService()
        await notifications.send_email_notification(
            "test@example.com",
            "Test Notification",
            "This is a test notification"
        )
        print("Email notification sent successfully")

        print("All utilities tested successfully!")

    # Run tests
    asyncio.run(test_support_utilities())