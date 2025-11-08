"""
Customer Support Workflow Graphs.

This module contains the graph definitions for the customer support system,
showcasing different workflow patterns and business logic.
"""

import logging
from kaygraph import Graph
from .nodes import (
    TicketIngestionNode,
    SentimentAnalysisNode,
    TicketCategorizationNode,
    PriorityAssignmentNode,
    KnowledgeBaseSearchNode,
    ResponseGenerationNode,
    EscalationDecisionNode,
    HumanEscalationNode,
    CustomerSatisfactionNode
)


def create_customer_support_workflow():
    """
    Creates the main customer support workflow graph.

    This graph handles the complete ticket processing pipeline:
    1. Ticket ingestion and validation
    2. Sentiment analysis
    3. Ticket categorization
    4. Priority assignment
    5. Knowledge base search
    6. Response generation
    7. Escalation decision (if needed)
    8. Customer satisfaction tracking

    Returns:
        Graph: The configured customer support workflow
    """
    logger = logging.getLogger(__name__)

    # Create all nodes
    ingestion = TicketIngestionNode()
    sentiment_analysis = SentimentAnalysisNode()
    categorization = TicketCategorizationNode()
    priority_assignment = PriorityAssignmentNode()
    kb_search = KnowledgeBaseSearchNode()
    response_generation = ResponseGenerationNode()
    escalation_decision = EscalationDecisionNode()
    human_escalation = HumanEscalationNode()
    satisfaction = CustomerSatisfactionNode()

    # Define the workflow connections
    # Standard flow
    ingestion >> sentiment_analysis
    sentiment_analysis >> categorization
    categorization >> priority_assignment

    # Branch based on priority
    priority_assignment - "standard_response" >> kb_search
    priority_assignment - "high_priority_workflow" >> create_high_priority_workflow()

    # Continue standard flow
    kb_search >> response_generation

    # Branch based on escalation need
    response_generation - "escalation_decision" >> escalation_decision
    response_generation - "finalize_response" >> satisfaction

    # Escalation paths
    escalation_decision - "human_escalation" >> human_escalation
    escalation_decision - "finalize_response" >> satisfaction

    # Human escalation to satisfaction
    human_escalation >> satisfaction

    logger.info("Customer support workflow created")
    return Graph(start=ingestion)


def create_high_priority_workflow():
    """
    Creates a specialized workflow for high-priority tickets.

    This workflow provides accelerated processing for urgent tickets:
    1. Immediate priority validation
    2. Escalated search parameters
    3. Senior agent response generation
    4. Direct escalation path

    Returns:
        Graph: The high-priority workflow subgraph
    """
    logger = logging.getLogger(__name__)

    # Use existing nodes but configure for high priority
    kb_search = KnowledgeBaseSearchNode()
    response_generation = ResponseGenerationNode()
    escalation_decision = EscalationDecisionNode()

    # High priority specific connections
    kb_search >> response_generation
    response_generation >> escalation_decision  # Always check escalation for high priority

    logger.info("High priority workflow created")
    return Graph(start=kb_search)


def create_escalation_workflow():
    """
    Creates a specialized workflow for ticket escalation.

    This workflow handles complex escalations:
    1. Escalation validation
    2. Specialist assignment
    3. Human handoff preparation
    4. Follow-up scheduling

    Returns:
        Graph: The escalation workflow
    """
    logger = logging.getLogger(__name__)

    # Create escalation-specific nodes
    escalation_validation = EscalationDecisionNode()
    human_handoff = HumanEscalationNode()
    follow_up = CustomerSatisfactionNode()  # Reuse for follow-up tracking

    # Escalation flow
    escalation_validation >> human_handoff
    human_handoff >> follow_up

    logger.info("Escalation workflow created")
    return Graph(start=escalation_validation)


def create_batch_processing_workflow():
    """
    Creates a workflow for processing multiple tickets in batch.

    This workflow is designed for bulk ticket processing:
    1. Batch ticket ingestion
    2. Parallel sentiment analysis
    3. Batch categorization
    4. Priority-based sorting
    5. Bulk response generation

    Returns:
        Graph: The batch processing workflow
    """
    logger = logging.getLogger(__name__)

    # Import batch processing nodes
    from kaygraph import BatchNode

    class BatchTicketIngestion(BatchNode):
        """Batch ingestion for multiple tickets."""

        def prep(self, shared):
            return shared.get("batch_tickets", [])

        def exec(self, tickets):
            # Process each ticket
            processed = []
            for ticket in tickets:
                # Validate each ticket
                if all(key in ticket for key in ["id", "customer_id", "subject", "content"]):
                    processed.append(ticket)
            return processed

        def post(self, shared, prep_res, exec_res_list):
            shared["processed_tickets"] = exec_res_list
            return "batch_sentiment"

    class BatchSentimentAnalysis(BatchNode):
        """Batch sentiment analysis using parallel processing."""

        def __init__(self):
            super().__init__(max_workers=5)  # Parallel processing

        def prep(self, shared):
            return shared.get("processed_tickets", [])

        def exec(self, ticket):
            # Simulate sentiment analysis for each ticket
            import random
            sentiments = ["positive", "neutral", "negative"]
            return {
                "ticket_id": ticket["id"],
                "sentiment": random.choice(sentiments),
                "confidence": random.uniform(0.7, 1.0)
            }

        def post(self, shared, prep_res, exec_res_list):
            shared["sentiment_results"] = exec_res_list
            return "batch_response"

    class BatchResponseGeneration(BatchNode):
        """Batch response generation."""

        def prep(self, shared):
            # Combine tickets with sentiment results
            tickets = shared.get("processed_tickets", [])
            sentiments = shared.get("sentiment_results", [])

            combined = []
            sentiment_map = {s["ticket_id"]: s for s in sentiments}

            for ticket in tickets:
                ticket["sentiment"] = sentiment_map.get(ticket["id"], {})
                combined.append(ticket)

            return combined

        def exec(self, ticket_with_sentiment):
            # Generate response for each ticket
            return {
                "ticket_id": ticket_with_sentiment["id"],
                "response": f"Response to: {ticket_with_sentiment['subject']}",
                "sentiment": ticket_with_sentiment["sentiment"]["sentiment"]
            }

        def post(self, shared, prep_res, exec_res_list):
            shared["batch_responses"] = exec_res_list
            return "complete"

    # Create batch workflow nodes
    batch_ingestion = BatchTicketIngestion()
    batch_sentiment = BatchSentimentAnalysis()
    batch_response = BatchResponseGeneration()

    # Connect batch workflow
    batch_ingestion >> batch_sentiment
    batch_sentiment >> batch_response

    logger.info("Batch processing workflow created")
    return Graph(start=batch_ingestion)


def create_real_time_monitoring_workflow():
    """
    Creates a workflow for real-time monitoring of support metrics.

    This workflow continuously monitors support operations:
    1. Ticket volume tracking
    2. Response time monitoring
    3. Satisfaction score calculation
    4. Alert generation for anomalies

    Returns:
        Graph: The real-time monitoring workflow
    """
    logger = logging.getLogger(__name__)

    class MetricsCollectorNode:
        """Node for collecting real-time metrics."""

        def __init__(self):
            self.node_id = "metrics_collector"

        def prep(self, shared):
            return shared.get("current_metrics", {})

        def exec(self, metrics_data):
            # Calculate key metrics
            return {
                "ticket_volume": metrics_data.get("volume", 0),
                "avg_response_time": metrics_data.get("response_time", 0),
                "satisfaction_score": metrics_data.get("satisfaction", 0.0),
                "escalation_rate": metrics_data.get("escalation_rate", 0.0)
            }

        def post(self, shared, prep_res, exec_res):
            shared["calculated_metrics"] = exec_res
            return "alert_check"

    class AlertGenerationNode:
        """Node for generating alerts based on metrics."""

        def __init__(self):
            self.node_id = "alert_generator"

        def prep(self, shared):
            return shared.get("calculated_metrics", {})

        def exec(self, metrics):
            alerts = []

            # Check for alert conditions
            if metrics["avg_response_time"] > 300:  # 5 minutes
                alerts.append({
                    "type": "high_response_time",
                    "severity": "warning",
                    "message": f"Average response time is {metrics['avg_response_time']}s"
                })

            if metrics["satisfaction_score"] < 0.7:
                alerts.append({
                    "type": "low_satisfaction",
                    "severity": "critical",
                    "message": f"Satisfaction score dropped to {metrics['satisfaction_score']}"
                })

            if metrics["escalation_rate"] > 0.2:
                alerts.append({
                    "type": "high_escalation_rate",
                    "severity": "warning",
                    "message": f"Escalation rate is {metrics['escalation_rate']*100:.1f}%"
                })

            return {"alerts": alerts, "metrics": metrics}

        def post(self, shared, prep_res, exec_res):
            shared["alerts"] = exec_res["alerts"]
            return "notification"

    class NotificationNode:
        """Node for sending notifications."""

        def __init__(self):
            self.node_id = "notification_sender"

        def prep(self, shared):
            return shared.get("alerts", [])

        def exec(self, alerts):
            # Send notifications for alerts
            sent_notifications = []
            for alert in alerts:
                # Simulate sending notification
                notification = {
                    "alert_id": f"alert_{len(sent_notifications)}",
                    "sent_to": "support_team",
                    "message": alert["message"],
                    "timestamp": "2024-01-01T00:00:00Z"
                }
                sent_notifications.append(notification)

            return {"sent_notifications": sent_notifications}

        def post(self, shared, prep_res, exec_res):
            shared["notifications_sent"] = exec_res["sent_notifications"]
            return "complete"

    # Create monitoring workflow nodes
    metrics_collector = MetricsCollectorNode()
    alert_generator = AlertGenerationNode()
    notification_sender = NotificationNode()

    # Connect monitoring workflow
    metrics_collector >> alert_generator
    alert_generator >> notification_sender

    logger.info("Real-time monitoring workflow created")
    return Graph(start=metrics_collector)


def get_available_workflows():
    """
    Returns a dictionary of all available workflows.

    This function provides a registry of all workflows that can be
    instantiated and used in the customer support system.

    Returns:
        Dict[str, callable]: Dictionary of workflow creation functions
    """
    return {
        "customer_support": create_customer_support_workflow,
        "high_priority": create_high_priority_workflow,
        "escalation": create_escalation_workflow,
        "batch_processing": create_batch_processing_workflow,
        "real_time_monitoring": create_real_time_monitoring_workflow
    }


def create_workflow(workflow_name: str):
    """
    Creates a specific workflow by name.

    Args:
        workflow_name (str): Name of the workflow to create

    Returns:
        Graph: The requested workflow graph

    Raises:
        ValueError: If workflow_name is not recognized
    """
    workflows = get_available_workflows()

    if workflow_name not in workflows:
        available = ", ".join(workflows.keys())
        raise ValueError(f"Unknown workflow: {workflow_name}. Available: {available}")

    return workflows[workflow_name]()


if __name__ == "__main__":
    """Demo the workflow creation."""
    import asyncio
    from kaygraph import Graph

    # Setup logging
    logging.basicConfig(level=logging.INFO)

    # Test main workflow
    print("Creating customer support workflow...")
    workflow = create_customer_support_workflow()
    print(f"Created workflow: {workflow}")

    # Test high priority workflow
    print("Creating high priority workflow...")
    high_priority_workflow = create_high_priority_workflow()
    print(f"Created high priority workflow: {high_priority_workflow}")

    # List all available workflows
    print("\nAvailable workflows:")
    for name in get_available_workflows().keys():
        print(f"  - {name}")

    print("\nAll workflows created successfully!")