"""
Customer Support Node implementations.

This module contains all the node implementations for the customer support
workflow, following KayGraph patterns and production best practices.
"""

import os
import json
import time
import logging
from typing import Dict, Any, List, Optional, Tuple
from dataclasses import dataclass
from enum import Enum

from kaygraph import ValidatedNode, AsyncNode, MetricsNode
from ..utils.claude_api import ClaudeAPIClient, ClaudeConfig, structured_claude_call
from ..utils.tools import WebSearchTool


class TicketCategory(Enum):
    """Ticket categories for classification."""
    TECHNICAL = "technical"
    BILLING = "billing"
    ACCOUNT = "account"
    PRODUCT = "product"
    GENERAL = "general"


class Priority(Enum):
    """Ticket priority levels."""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    URGENT = "urgent"


class Sentiment(Enum):
    """Customer sentiment levels."""
    VERY_NEGATIVE = "very_negative"
    NEGATIVE = "negative"
    NEUTRAL = "neutral"
    POSITIVE = "positive"
    VERY_POSITIVE = "very_positive"


@dataclass
class Ticket:
    """Customer support ticket data structure."""
    id: str
    customer_id: str
    subject: str
    content: str
    category: Optional[TicketCategory] = None
    priority: Optional[Priority] = None
    sentiment: Optional[Sentiment] = None
    assigned_agent: Optional[str] = None
    created_at: Optional[str] = None
    metadata: Dict[str, Any] = None


class TicketIngestionNode(ValidatedNode):
    """
    Ingests and validates incoming customer support tickets.

    This node handles the initial processing of customer tickets,
    including validation, enrichment, and preparation for analysis.
    """

    def __init__(self):
        super().__init__(
            max_retries=3,
            wait=1,
            node_id="ticket_ingestion"
        )
        self.logger = logging.getLogger(f"{__name__}.{self.__class__.__name__}")

    def validate_input(self, ticket_data: Dict[str, Any]) -> Dict[str, Any]:
        """Validate incoming ticket data."""
        required_fields = ["id", "customer_id", "subject", "content"]
        for field in required_fields:
            if not ticket_data.get(field):
                raise ValueError(f"Missing required field: {field}")

        # Validate content length
        if len(ticket_data["content"]) < 10:
            raise ValueError("Ticket content too short")
        if len(ticket_data["content"]) > 10000:
            raise ValueError("Ticket content too long")

        # Add metadata
        ticket_data["created_at"] = ticket_data.get("created_at", time.time())
        ticket_data["metadata"] = ticket_data.get("metadata", {})

        return ticket_data

    def prep(self, shared: Dict[str, Any]) -> Dict[str, Any]:
        """Extract ticket data from shared context."""
        return shared.get("incoming_ticket", {})

    def exec(self, validated_ticket: Dict[str, Any]) -> Ticket:
        """Create Ticket object from validated data."""
        return Ticket(
            id=validated_ticket["id"],
            customer_id=validated_ticket["customer_id"],
            subject=validated_ticket["subject"],
            content=validated_ticket["content"],
            created_at=validated_ticket["created_at"],
            metadata=validated_ticket["metadata"]
        )

    def validate_output(self, ticket: Ticket) -> Ticket:
        """Validate created ticket object."""
        if not ticket.id or not ticket.content:
            raise ValueError("Invalid ticket created")
        return ticket

    def post(self, shared: Dict[str, Any], prep_res: Dict[str, Any], exec_res: Ticket) -> str:
        """Store validated ticket in shared context."""
        shared["ticket"] = exec_res
        shared["processing_stage"] = "ingestion_complete"
        self.logger.info(f"Ticket {exec_res.id} ingested successfully")
        return "sentiment_analysis"


class SentimentAnalysisNode(AsyncNode):
    """
    Analyzes customer sentiment from ticket content.

    This node uses Claude to determine the emotional state of the customer,
    which helps prioritize responses and determine appropriate escalation paths.
    """

    def __init__(self):
        super().__init__(node_id="sentiment_analysis")
        self.logger = logging.getLogger(f"{__name__}.{self.__class__.__name__}")

    async def prep(self, shared: Dict[str, Any]) -> str:
        """Extract ticket content for sentiment analysis."""
        ticket = shared.get("ticket")
        if not ticket:
            raise ValueError("No ticket found in shared context")
        return f"Subject: {ticket.subject}\n\nContent: {ticket.content}"

    async def exec(self, ticket_text: str) -> Dict[str, Any]:
        """Use Claude to analyze sentiment."""
        prompt = f"""
Analyze the customer sentiment in this support ticket:

{ticket_text}

Please provide:
1. Overall sentiment (very_negative, negative, neutral, positive, very_positive)
2. Sentiment confidence score (0-1)
3. Key emotional indicators
4. Urgency level (low, medium, high)
5. Recommended action approach

Respond in JSON format:
{{
    "sentiment": "sentiment_value",
    "confidence": 0.0,
    "emotional_indicators": ["indicator1", "indicator2"],
    "urgency": "urgency_level",
    "recommended_approach": "approach_description"
}}
"""

        schema = {
            "type": "object",
            "properties": {
                "sentiment": {"type": "string"},
                "confidence": {"type": "number"},
                "emotional_indicators": {"type": "array", "items": {"type": "string"}},
                "urgency": {"type": "string"},
                "recommended_approach": {"type": "string"}
            }
        }

        return await structured_claude_call(prompt, schema)

    async def post(self, shared: Dict[str, Any], prep_res: str, exec_res: Dict[str, Any]) -> str:
        """Store sentiment analysis results."""
        ticket = shared.get("ticket")
        if ticket:
            ticket.sentiment = Sentiment(exec_res["sentiment"])
            ticket.metadata.update({
                "sentiment_confidence": exec_res["confidence"],
                "emotional_indicators": exec_res["emotional_indicators"],
                "urgency_level": exec_res["urgency"],
                "recommended_approach": exec_res["recommended_approach"]
            })

        shared["sentiment_analysis"] = exec_res
        self.logger.info(f"Sentiment analyzed: {exec_res['sentiment']} (confidence: {exec_res['confidence']})")
        return "categorization"


class TicketCategorizationNode(AsyncNode):
    """
    Categorizes tickets into appropriate support categories.

    This node uses Claude to understand the nature of the customer's issue
    and assign it to the correct category for routing.
    """

    def __init__(self):
        super().__init__(node_id="ticket_categorization")
        self.logger = logging.getLogger(f"{__name__}.{self.__class__.__name__}")

    async def prep(self, shared: Dict[str, Any]) -> str:
        """Prepare ticket content for categorization."""
        ticket = shared.get("ticket")
        if not ticket:
            raise ValueError("No ticket found in shared context")

        return f"""
Subject: {ticket.subject}
Content: {ticket.content}
Customer Sentiment: {ticket.sentiment.value if ticket.sentiment else 'unknown'}
"""

    async def exec(self, ticket_text: str) -> Dict[str, Any]:
        """Use Claude to categorize the ticket."""
        prompt = f"""
Categorize this customer support ticket:

{ticket_text}

Available categories:
- technical: Technical issues, bugs, system problems
- billing: Payment, subscription, invoice issues
- account: Account access, profile, settings
- product: Product features, usage, how-to questions
- general: General inquiries, feedback, other

Please provide:
1. Primary category
2. Confidence score (0-1)
3. Secondary category (if applicable)
4. Keywords that led to this categorization
5. Suggested routing department

Respond in JSON format:
{{
    "primary_category": "category_value",
    "confidence": 0.0,
    "secondary_category": "category_value_or_null",
    "keywords": ["keyword1", "keyword2"],
    "suggested_department": "department_name"
}}
"""

        schema = {
            "type": "object",
            "properties": {
                "primary_category": {"type": "string"},
                "confidence": {"type": "number"},
                "secondary_category": {"type": ["string", "null"]},
                "keywords": {"type": "array", "items": {"type": "string"}},
                "suggested_department": {"type": "string"}
            }
        }

        return await structured_claude_call(prompt, schema)

    async def post(self, shared: Dict[str, Any], prep_res: str, exec_res: Dict[str, Any]) -> str:
        """Store categorization results."""
        ticket = shared.get("ticket")
        if ticket:
            ticket.category = TicketCategory(exec_res["primary_category"])
            ticket.metadata.update({
                "category_confidence": exec_res["confidence"],
                "secondary_category": exec_res.get("secondary_category"),
                "category_keywords": exec_res["keywords"],
                "suggested_department": exec_res["suggested_department"]
            })

        shared["categorization"] = exec_res
        self.logger.info(f"Ticket categorized as: {exec_res['primary_category']}")
        return "priority_assignment"


class PriorityAssignmentNode(AsyncNode):
    """
    Assigns priority levels based on multiple factors.

    This node considers sentiment, category, customer tier, and other factors
    to determine the appropriate priority level for the ticket.
    """

    def __init__(self):
        super().__init__(node_id="priority_assignment")
        self.logger = logging.getLogger(f"{__name__}.{self.__class__.__name__}")

    async def prep(self, shared: Dict[str, Any]) -> Dict[str, Any]:
        """Prepare all relevant data for priority assignment."""
        ticket = shared.get("ticket")
        if not ticket:
            raise ValueError("No ticket found in shared context")

        return {
            "sentiment": ticket.sentiment.value if ticket.sentiment else "neutral",
            "category": ticket.category.value if ticket.category else "general",
            "urgency_level": ticket.metadata.get("urgency_level", "medium"),
            "customer_tier": ticket.metadata.get("customer_tier", "standard"),
            "previous_interactions": ticket.metadata.get("previous_interactions", 0)
        }

    async def exec(self, priority_data: Dict[str, Any]) -> Dict[str, Any]:
        """Use Claude to assign priority level."""
        prompt = f"""
Assign priority level to this support ticket based on the following factors:

{json.dumps(priority_data, indent=2)}

Priority levels:
- low: Non-urgent issues, happy customers, general inquiries
- medium: Standard issues, neutral sentiment, regular requests
- high: Urgent issues, unhappy customers, technical problems
- urgent: Critical issues, very unhappy customers, service disruptions

Consider:
1. Customer sentiment and emotional state
2. Issue category and potential impact
3. Customer tier and value
4. Urgency indicators in the content

Respond in JSON format:
{{
    "priority": "priority_level",
    "reasoning": "detailed_reasoning",
    "factors_considered": ["factor1", "factor2"],
    "recommended_response_time": "timeframe",
    "escalation_risk": "low/medium/high"
}}
"""

        schema = {
            "type": "object",
            "properties": {
                "priority": {"type": "string"},
                "reasoning": {"type": "string"},
                "factors_considered": {"type": "array", "items": {"type": "string"}},
                "recommended_response_time": {"type": "string"},
                "escalation_risk": {"type": "string"}
            }
        }

        return await structured_claude_call(prompt, schema)

    async def post(self, shared: Dict[str, Any], prep_res: Dict[str, Any], exec_res: Dict[str, Any]) -> str:
        """Store priority assignment results."""
        ticket = shared.get("ticket")
        if ticket:
            ticket.priority = Priority(exec_res["priority"])
            ticket.metadata.update({
                "priority_reasoning": exec_res["reasoning"],
                "priority_factors": exec_res["factors_considered"],
                "recommended_response_time": exec_res["recommended_response_time"],
                "escalation_risk": exec_res["escalation_risk"]
            })

        shared["priority_assignment"] = exec_res
        self.logger.info(f"Priority assigned: {exec_res['priority']} - {exec_res['reasoning']}")

        # Route based on priority
        if exec_res["priority"] in ["high", "urgent"]:
            return "high_priority_workflow"
        else:
            return "standard_response"


class KnowledgeBaseSearchNode(AsyncNode):
    """
    Searches knowledge base for relevant articles and solutions.

    This node searches the company's knowledge base to find relevant articles,
    FAQs, or previous solutions that might help resolve the customer's issue.
    """

    def __init__(self):
        super().__init__(node_id="knowledge_base_search")
        self.logger = logging.getLogger(f"{__name__}.{self.__class__.__name__}")

    async def prep(self, shared: Dict[str, Any]) -> str:
        """Prepare search query from ticket content."""
        ticket = shared.get("ticket")
        if not ticket:
            raise ValueError("No ticket found in shared context")

        # Create search query from ticket content
        search_query = f"{ticket.subject} {ticket.content[:500]}"
        return search_query

    async def exec(self, search_query: str) -> Dict[str, Any]:
        """Search knowledge base for relevant articles."""
        # Mock knowledge base search (in real implementation, this would search a real KB)
        mock_articles = [
            {
                "id": "kb_001",
                "title": "How to reset your password",
                "content": "Step-by-step guide for password reset...",
                "relevance_score": 0.95,
                "category": "account"
            },
            {
                "id": "kb_002",
                "title": "Common billing issues and solutions",
                "content": "Frequently asked billing questions...",
                "relevance_score": 0.87,
                "category": "billing"
            }
        ]

        # In a real implementation, you would use embedding search or full-text search
        return {
            "query": search_query,
            "articles_found": len(mock_articles),
            "articles": mock_articles,
            "search_time": 0.15
        }

    async def post(self, shared: Dict[str, Any], prep_res: str, exec_res: Dict[str, Any]) -> str:
        """Store knowledge base search results."""
        shared["knowledge_base_results"] = exec_res
        self.logger.info(f"Found {exec_res['articles_found']} knowledge base articles")
        return "response_generation"


class ResponseGenerationNode(AsyncNode):
    """
    Generates personalized responses to customer tickets.

    This node uses Claude to craft appropriate, empathetic responses that
    address the customer's issue while incorporating knowledge base articles.
    """

    def __init__(self):
        super().__init__(node_id="response_generation")
        self.logger = logging.getLogger(f"{__name__}.{self.__class__.__name__}")

    async def prep(self, shared: Dict[str, Any]) -> Dict[str, Any]:
        """Prepare all context for response generation."""
        ticket = shared.get("ticket")
        sentiment_analysis = shared.get("sentiment_analysis", {})
        kb_results = shared.get("knowledge_base_results", {})

        if not ticket:
            raise ValueError("No ticket found in shared context")

        return {
            "ticket_subject": ticket.subject,
            "ticket_content": ticket.content,
            "customer_sentiment": sentiment_analysis.get("sentiment", "neutral"),
            "recommended_approach": sentiment_analysis.get("recommended_approach", ""),
            "category": ticket.category.value if ticket.category else "general",
            "priority": ticket.priority.value if ticket.priority else "medium",
            "kb_articles": kb_results.get("articles", [])
        }

    async def exec(self, response_context: Dict[str, Any]) -> Dict[str, Any]:
        """Generate personalized response using Claude."""
        prompt = f"""
Generate a customer support response based on this context:

{json.dumps(response_context, indent=2)}

Requirements:
1. Be empathetic and acknowledge the customer's sentiment
2. Address their specific issue directly
3. Reference relevant knowledge base articles if available
4. Provide clear next steps or solutions
5. Match the tone to the customer's emotional state
6. Include any necessary disclaimers or timelines

Generate a response that is:
- Professional yet empathetic
- Clear and actionable
- Comprehensive but concise
- Personalized to the customer's situation

Respond in JSON format:
{{
    "response": "full_response_text",
    "tone": "empathetic/professional/friendly",
    "articles_referenced": ["kb_id1", "kb_id2"],
    "next_steps": ["step1", "step2"],
    "estimated_resolution_time": "timeframe",
    "escalation_needed": true/false
}}
"""

        schema = {
            "type": "object",
            "properties": {
                "response": {"type": "string"},
                "tone": {"type": "string"},
                "articles_referenced": {"type": "array", "items": {"type": "string"}},
                "next_steps": {"type": "array", "items": {"type": "string"}},
                "estimated_resolution_time": {"type": "string"},
                "escalation_needed": {"type": "boolean"}
            }
        }

        return await structured_claude_call(prompt, schema)

    async def post(self, shared: Dict[str, Any], prep_res: Dict[str, Any], exec_res: Dict[str, Any]) -> str:
        """Store generated response."""
        shared["generated_response"] = exec_res
        self.logger.info(f"Response generated with tone: {exec_res['tone']}")

        # Check if escalation is needed
        if exec_res.get("escalation_needed", False):
            return "escalation_decision"
        else:
            return "finalize_response"


class EscalationDecisionNode(AsyncNode):
    """
    Determines if and how to escalate the ticket.

    This node evaluates whether the ticket needs human escalation
    and determines the appropriate escalation path.
    """

    def __init__(self):
        super().__init__(node_id="escalation_decision")
        self.logger = logging.getLogger(f"{__name__}.{self.__class__.__name__}")

    async def prep(self, shared: Dict[str, Any]) -> Dict[str, Any]:
        """Prepare context for escalation decision."""
        ticket = shared.get("ticket")
        response = shared.get("generated_response", {})

        return {
            "ticket_priority": ticket.priority.value if ticket.priority else "medium",
            "customer_sentiment": ticket.sentiment.value if ticket.sentiment else "neutral",
            "escalation_risk": ticket.metadata.get("escalation_risk", "low"),
            "category": ticket.category.value if ticket.category else "general",
            "response_suggested_escalation": response.get("escalation_needed", False)
        }

    async def exec(self, escalation_context: Dict[str, Any]) -> Dict[str, Any]:
        """Make escalation decision using Claude."""
        prompt = f"""
Decide on escalation for this support ticket:

{json.dumps(escalation_context, indent=2)}

Escalation options:
- no_escalation: Handle with automated response
- tier_2: Escalate to level 2 support
- specialist: Escalate to domain specialist
- manager: Escalate to support manager
- emergency: Immediate emergency escalation

Consider:
1. Ticket priority and urgency
2. Customer sentiment and emotional state
3. Technical complexity
4. Business impact
5. Previous attempts to resolve

Respond in JSON format:
{{
    "escalation_decision": "escalation_level",
    "reasoning": "detailed_reasoning",
    "escalation_priority": "low/medium/high/critical",
    "assigned_department": "department_name",
    "estimated_human_response_time": "timeframe",
    "auto_response_sent": true/false
}}
"""

        schema = {
            "type": "object",
            "properties": {
                "escalation_decision": {"type": "string"},
                "reasoning": {"type": "string"},
                "escalation_priority": {"type": "string"},
                "assigned_department": {"type": "string"},
                "estimated_human_response_time": {"type": "string"},
                "auto_response_sent": {"type": "boolean"}
            }
        }

        return await structured_claude_call(prompt, schema)

    async def post(self, shared: Dict[str, Any], prep_res: Dict[str, Any], exec_res: Dict[str, Any]) -> str:
        """Store escalation decision."""
        shared["escalation_decision"] = exec_res
        self.logger.info(f"Escalation decision: {exec_res['escalation_decision']}")

        if exec_res["escalation_decision"] == "no_escalation":
            return "finalize_response"
        else:
            return "human_escalation"


class HumanEscalationNode(AsyncNode):
    """
    Handles the human escalation process.

    This node prepares the ticket for human agent handoff,
    including all context and analysis performed so far.
    """

    def __init__(self):
        super().__init__(node_id="human_escalation")
        self.logger = logging.getLogger(f"{__name__}.{self.__class__.__name__}")

    async def prep(self, shared: Dict[str, Any]) -> Dict[str, Any]:
        """Prepare complete ticket context for human agent."""
        ticket = shared.get("ticket")
        escalation_decision = shared.get("escalation_decision", {})

        return {
            "ticket": {
                "id": ticket.id,
                "customer_id": ticket.customer_id,
                "subject": ticket.subject,
                "content": ticket.content,
                "category": ticket.category.value if ticket.category else None,
                "priority": ticket.priority.value if ticket.priority else None,
                "sentiment": ticket.sentiment.value if ticket.sentiment else None
            },
            "analysis": {
                "sentiment_analysis": shared.get("sentiment_analysis", {}),
                "categorization": shared.get("categorization", {}),
                "priority_assignment": shared.get("priority_assignment", {}),
                "escalation_decision": escalation_decision
            },
            "auto_response": shared.get("generated_response", {}),
            "knowledge_base": shared.get("knowledge_base_results", {})
        }

    async def exec(self, escalation_data: Dict[str, Any]) -> Dict[str, Any]:
        """Prepare human handoff package."""
        return {
            "escalation_package": escalation_data,
            "handoff_priority": escalation_data["analysis"]["escalation_decision"]["escalation_priority"],
            "assigned_department": escalation_data["analysis"]["escalation_decision"]["assigned_department"],
            "estimated_response_time": escalation_data["analysis"]["escalation_decision"]["estimated_human_response_time"],
            "handoff_timestamp": time.time()
        }

    async def post(self, shared: Dict[str, Any], prep_res: Dict[str, Any], exec_res: Dict[str, Any]) -> str:
        """Store escalation package and trigger human notification."""
        shared["escalation_package"] = exec_res
        self.logger.info(f"Ticket escalated to human agents: {exec_res['assigned_department']}")
        return "notify_human_agents"


class CustomerSatisfactionNode(MetricsNode):
    """
    Tracks customer satisfaction metrics.

    This node collects metrics about the support process
    and calculates customer satisfaction scores.
    """

    def __init__(self):
        super().__init__(
            node_id="customer_satisfaction",
            metrics_collector_name="support_metrics"
        )
        self.logger = logging.getLogger(f"{__name__}.{self.__class__.__name__}")

    def prep(self, shared: Dict[str, Any]) -> Dict[str, Any]:
        """Collect metrics for satisfaction analysis."""
        ticket = shared.get("ticket")
        response = shared.get("generated_response", {})
        escalation = shared.get("escalation_decision", {})

        return {
            "resolution_time": time.time() - ticket.created_at if ticket.created_at else 0,
            "sentiment_improvement": self._calculate_sentiment_improvement(ticket),
            "escalation_required": escalation.get("escalation_decision") != "no_escalation",
            "response_quality": self._assess_response_quality(response),
            "category": ticket.category.value if ticket.category else "unknown"
        }

    def exec(self, metrics_data: Dict[str, Any]) -> Dict[str, Any]:
        """Calculate satisfaction metrics."""
        base_score = 0.7  # Base satisfaction score

        # Adjust based on factors
        if metrics_data["resolution_time"] < 300:  # 5 minutes
            base_score += 0.1
        elif metrics_data["resolution_time"] > 3600:  # 1 hour
            base_score -= 0.1

        if metrics_data["sentiment_improvement"] > 0:
            base_score += 0.1

        if not metrics_data["escalation_required"]:
            base_score += 0.05

        if metrics_data["response_quality"] > 0.8:
            base_score += 0.05

        return {
            "satisfaction_score": max(0.0, min(1.0, base_score)),
            "resolution_time": metrics_data["resolution_time"],
            "escalation_rate": 1.0 if metrics_data["escalation_required"] else 0.0,
            "response_quality": metrics_data["response_quality"]
        }

    def post(self, shared: Dict[str, Any], prep_res: Dict[str, Any], exec_res: Dict[str, Any]) -> str:
        """Store satisfaction metrics."""
        shared["satisfaction_metrics"] = exec_res
        self.logger.info(f"Satisfaction score: {exec_res['satisfaction_score']:.2f}")
        return "complete"

    def _calculate_sentiment_improvement(self, ticket: Ticket) -> float:
        """Calculate potential sentiment improvement."""
        if ticket.sentiment and ticket.sentiment in [Sentiment.VERY_NEGATIVE, Sentiment.NEGATIVE]:
            return 0.3  # High potential for improvement
        elif ticket.sentiment and ticket.sentiment == Sentiment.NEUTRAL:
            return 0.1  # Moderate potential
        else:
            return 0.0  # Low potential

    def _assess_response_quality(self, response: Dict[str, Any]) -> float:
        """Assess the quality of the generated response."""
        if not response:
            return 0.0

        quality_score = 0.5  # Base score

        # Check for empathy indicators
        response_text = response.get("response", "").lower()
        if any(word in response_text for word in ["understand", "apologize", "sorry"]):
            quality_score += 0.1

        # Check for clear next steps
        if response.get("next_steps"):
            quality_score += 0.2

        # Check for appropriate tone
        if response.get("tone") in ["empathetic", "professional"]:
            quality_score += 0.2

        return min(1.0, quality_score)