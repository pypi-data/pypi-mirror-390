"""
Customer Support System - Main Entry Point.

This module demonstrates the complete customer support system workflow
with real-world scenarios and comprehensive testing.
"""

import asyncio
import json
import time
import logging
from typing import Dict, Any, List

from .nodes import Ticket, TicketCategory, Priority, Sentiment
from .graphs import create_workflow, get_available_workflows
from .utils import CRMIntegration, KnowledgeBase, SupportMetrics, NotificationService, create_ticket_from_webhook


def setup_logging():
    """Setup logging for the customer support system."""
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.StreamHandler(),
            logging.FileHandler('customer_support.log')
        ]
    )


async def demo_single_ticket_workflow():
    """Demonstrate processing a single customer support ticket."""
    print("\n" + "="*60)
    print("DEMO 1: Single Ticket Processing")
    print("="*60)

    # Create the main workflow
    workflow = create_workflow("customer_support")

    # Create sample ticket data
    incoming_ticket = {
        "id": "ticket_demo_001",
        "customer_id": "cust_001",
        "subject": "Unable to access my account - password reset not working",
        "content": "I've been trying to reset my password for the past hour. I click on the forgot password link, enter my email, but I never receive the reset email. I've checked my spam folder multiple times. This is urgent as I need to access my account for work. Can someone please help me immediately?",
        "source": "email",
        "metadata": {
            "customer_tier": "premium",
            "previous_interactions": 3,
            "urgent_flag": True
        }
    }

    print(f"Processing ticket: {incoming_ticket['id']}")
    print(f"Subject: {incoming_ticket['subject']}")
    print(f"Customer: {incoming_ticket['customer_id']}")

    # Initialize shared context
    shared_context = {
        "incoming_ticket": incoming_ticket,
        "start_time": time.time(),
        "processing_stage": "starting"
    }

    try:
        # Run the workflow
        result = await workflow.run(
            start_node_name="ticket_ingestion",
            shared=shared_context
        )

        # Display results
        print("\n--- PROCESSING RESULTS ---")
        ticket = shared_context.get("ticket")
        if ticket:
            print(f"✅ Ticket processed successfully!")
            print(f"   Category: {ticket.category.value if ticket.category else 'N/A'}")
            print(f"   Priority: {ticket.priority.value if ticket.priority else 'N/A'}")
            print(f"   Sentiment: {ticket.sentiment.value if ticket.sentiment else 'N/A'}")

        # Display sentiment analysis
        sentiment = shared_context.get("sentiment_analysis")
        if sentiment:
            print(f"\n--- SENTIMENT ANALYSIS ---")
            print(f"   Sentiment: {sentiment.get('sentiment', 'N/A')}")
            print(f"   Confidence: {sentiment.get('confidence', 0):.2f}")
            print(f"   Urgency: {sentiment.get('urgency', 'N/A')}")
            print(f"   Emotional Indicators: {', '.join(sentiment.get('emotional_indicators', []))}")

        # Display generated response
        response = shared_context.get("generated_response")
        if response:
            print(f"\n--- GENERATED RESPONSE ---")
            print(f"   Tone: {response.get('tone', 'N/A')}")
            print(f"   Response: {response.get('response', 'N/A')[:200]}...")
            print(f"   Next Steps: {', '.join(response.get('next_steps', []))}")

        # Display escalation decision
        escalation = shared_context.get("escalation_decision")
        if escalation:
            print(f"\n--- ESCALATION DECISION ---")
            print(f"   Decision: {escalation.get('escalation_decision', 'N/A')}")
            print(f"   Assigned Department: {escalation.get('assigned_department', 'N/A')}")
            print(f"   Priority: {escalation.get('escalation_priority', 'N/A')}")

        # Display metrics
        metrics = shared_context.get("satisfaction_metrics")
        if metrics:
            print(f"\n--- SATISFACTION METRICS ---")
            print(f"   Satisfaction Score: {metrics.get('satisfaction_score', 0):.2f}")
            print(f"   Resolution Time: {metrics.get('resolution_time', 0):.1f}s")

        processing_time = time.time() - shared_context["start_time"]
        print(f"\n⏱️  Total Processing Time: {processing_time:.2f}s")

    except Exception as e:
        print(f"❌ Error processing ticket: {e}")
        import traceback
        traceback.print_exc()


async def demo_batch_ticket_processing():
    """Demonstrate batch processing of multiple tickets."""
    print("\n" + "="*60)
    print("DEMO 2: Batch Ticket Processing")
    print("="*60)

    # Create batch workflow
    workflow = create_workflow("batch_processing")

    # Create sample batch tickets
    batch_tickets = [
        {
            "id": "batch_001",
            "customer_id": "cust_002",
            "subject": "Question about billing cycle",
            "content": "When does my monthly billing cycle start?"
        },
        {
            "id": "batch_002",
            "customer_id": "cust_003",
            "subject": "Need help with API integration",
            "content": "I'm trying to integrate your API into my application but getting authentication errors."
        },
        {
            "id": "batch_003",
            "customer_id": "cust_001",
            "subject": "Feature request - dark mode",
            "content": "Would it be possible to add a dark mode to the dashboard?"
        }
    ]

    print(f"Processing batch of {len(batch_tickets)} tickets")

    shared_context = {
        "batch_tickets": batch_tickets,
        "start_time": time.time()
    }

    try:
        # Run batch workflow
        result = await workflow.run(
            start_node_name="batch_ticket_ingestion",
            shared=shared_context
        )

        # Display results
        processed_tickets = shared_context.get("processed_tickets", [])
        sentiment_results = shared_context.get("sentiment_results", [])
        batch_responses = shared_context.get("batch_responses", [])

        print(f"\n--- BATCH PROCESSING RESULTS ---")
        print(f"✅ Processed {len(processed_tickets)} tickets")

        for i, (ticket, sentiment, response) in enumerate(zip(processed_tickets, sentiment_results, batch_responses)):
            print(f"\nTicket {i+1}: {ticket['id']}")
            print(f"  Subject: {ticket['subject']}")
            print(f"  Sentiment: {sentiment.get('sentiment', 'N/A')}")
            print(f"  Response: {response.get('response', 'N/A')[:100]}...")

        processing_time = time.time() - shared_context["start_time"]
        print(f"\n⏱️  Total Batch Processing Time: {processing_time:.2f}s")
        print(f"📊 Average Time per Ticket: {processing_time/len(batch_tickets):.2f}s")

    except Exception as e:
        print(f"❌ Error in batch processing: {e}")


async def demo_real_time_monitoring():
    """Demonstrate real-time monitoring capabilities."""
    print("\n" + "="*60)
    print("DEMO 3: Real-Time Monitoring")
    print("="*60)

    # Create monitoring workflow
    workflow = create_workflow("real_time_monitoring")

    # Simulate current metrics
    current_metrics = {
        "volume": 45,
        "response_time": 180,  # 3 minutes
        "satisfaction": 0.82,
        "escalation_rate": 0.15  # 15%
    }

    print("Current Support Metrics:")
    print(f"  Ticket Volume: {current_metrics['volume']}")
    print(f"  Avg Response Time: {current_metrics['response_time']}s")
    print(f"  Satisfaction Score: {current_metrics['satisfaction']:.2f}")
    print(f"  Escalation Rate: {current_metrics['escalation_rate']*100:.1f}%")

    shared_context = {
        "current_metrics": current_metrics
    }

    try:
        # Run monitoring workflow
        result = await workflow.run(
            start_node_name="metrics_collector",
            shared=shared_context
        )

        # Display monitoring results
        calculated_metrics = shared_context.get("calculated_metrics", {})
        alerts = shared_context.get("alerts", [])
        notifications = shared_context.get("notifications_sent", [])

        print(f"\n--- MONITORING RESULTS ---")
        print(f"📊 Calculated Metrics:")
        for key, value in calculated_metrics.items():
            print(f"   {key}: {value}")

        if alerts:
            print(f"\n🚨 GENERATED ALERTS ({len(alerts)}):")
            for alert in alerts:
                print(f"   {alert['type'].upper()}: {alert['message']} (Severity: {alert['severity']})")

        if notifications:
            print(f"\n📤 NOTIFICATIONS SENT ({len(notifications)}):")
            for notif in notifications:
                print(f"   Alert {notif['alert_id']} sent to {notif['sent_to']}")

    except Exception as e:
        print(f"❌ Error in monitoring: {e}")


async def demo_escalation_workflow():
    """Demonstrate escalation workflow for complex issues."""
    print("\n" + "="*60)
    print("DEMO 4: Escalation Workflow")
    print("="*60)

    # Create main workflow
    workflow = create_workflow("customer_support")

    # Create complex ticket requiring escalation
    complex_ticket = {
        "id": "escalation_demo_001",
        "customer_id": "cust_003",  # Enterprise customer
        "subject": "CRITICAL: Complete system outage affecting all users",
        "content": "Our entire organization is experiencing a complete system outage. No users can access the platform, and we're losing significant revenue every minute. This started approximately 30 minutes ago. We've already tried basic troubleshooting steps. This is impacting 500+ users across multiple departments. We need immediate technical assistance and a dedicated incident response team. Please escalate this to your highest priority support level immediately.",
        "source": "phone",
        "metadata": {
            "customer_tier": "enterprise",
            "previous_interactions": 0,
            "urgent_flag": True,
            "revenue_impact": "high",
            "users_affected": 500
        }
    }

    print(f"Processing CRITICAL escalation ticket: {complex_ticket['id']}")
    print(f"Impact: {complex_ticket['metadata']['users_affected']} users affected")

    shared_context = {
        "incoming_ticket": complex_ticket,
        "start_time": time.time()
    }

    try:
        # Run workflow (should trigger escalation)
        result = await workflow.run(
            start_node_name="ticket_ingestion",
            shared=shared_context
        )

        # Display escalation results
        ticket = shared_context.get("ticket")
        escalation_decision = shared_context.get("escalation_decision")
        escalation_package = shared_context.get("escalation_package")

        print(f"\n--- ESCALATION RESULTS ---")
        if ticket:
            print(f"   Assigned Priority: {ticket.priority.value if ticket.priority else 'N/A'}")
            print(f"   Category: {ticket.category.value if ticket.category else 'N/A'}")
            print(f"   Sentiment: {ticket.sentiment.value if ticket.sentiment else 'N/A'}")

        if escalation_decision:
            print(f"\n🚨 ESCALATION DETAILS:")
            print(f"   Decision: {escalation_decision.get('escalation_decision', 'N/A')}")
            print(f"   Assigned Department: {escalation_decision.get('assigned_department', 'N/A')}")
            print(f"   Escalation Priority: {escalation_decision.get('escalation_priority', 'N/A')}")
            print(f"   Estimated Human Response: {escalation_decision.get('estimated_human_response_time', 'N/A')}")

        if escalation_package:
            print(f"\n📋 ESCALATION PACKAGE PREPARED:")
            print(f"   Priority: {escalation_package.get('handoff_priority', 'N/A')}")
            print(f"   Assigned To: {escalation_package.get('assigned_department', 'N/A')}")
            print(f"   Package Size: {len(str(escalation_package.get('escalation_package', {})))} characters")

        processing_time = time.time() - shared_context["start_time"]
        print(f"\n⏱️  Escalation Processing Time: {processing_time:.2f}s")

    except Exception as e:
        print(f"❌ Error in escalation workflow: {e}")


async def demo_integration_with_external_systems():
    """Demonstrate integration with CRM, Knowledge Base, and Notifications."""
    print("\n" + "="*60)
    print("DEMO 5: External System Integration")
    print("="*60)

    # Initialize external systems
    crm = CRMIntegration()
    knowledge_base = KnowledgeBase()
    metrics = SupportMetrics()
    notifications = NotificationService()

    # Process a ticket with full integration
    ticket_data = {
        "id": "integration_demo_001",
        "customer_id": "cust_001",
        "subject": "Integration test - multiple system coordination",
        "content": "This is a test to demonstrate how the support system integrates with CRM, knowledge base, and notification systems."
    }

    print(f"Processing ticket with full system integration: {ticket_data['id']}")

    try:
        # 1. Get customer data from CRM
        print("\n1. 📊 Retrieving customer data from CRM...")
        customer = await crm.get_customer(ticket_data["customer_id"])
        if customer:
            print(f"   Customer: {customer.name} ({customer.tier} tier)")
            print(f"   Previous Tickets: {customer.total_tickets}")
            print(f"   Satisfaction Score: {customer.satisfaction_score:.2f}")

        # 2. Search knowledge base
        print("\n2. 📚 Searching knowledge base...")
        kb_articles = await knowledge_base.search_articles("integration test", limit=3)
        print(f"   Found {len(kb_articles)} relevant articles")
        for article in kb_articles:
            print(f"   - {article['title']} (Relevance: {article.get('relevance_score', 0)})")

        # 3. Record metrics
        print("\n3. 📈 Recording support metrics...")
        metrics.record_ticket_created("technical", "medium")
        metrics.record_response_time(45)  # 45 seconds
        metrics.record_ticket_resolved(300, 0.95)  # 5 minutes, high satisfaction
        current_metrics = metrics.get_metrics_summary()
        print(f"   Current Satisfaction: {current_metrics['satisfaction_score']:.2f}")
        print(f"   Total Tickets: {current_metrics['total_tickets']}")

        # 4. Send notifications
        print("\n4. 📤 Sending notifications...")
        email_notif = await notifications.send_email_notification(
            to=customer.email if customer else "test@example.com",
            subject="Your support ticket has been resolved",
            body="We've successfully resolved your support ticket. Here are the details...",
            priority="normal"
        )
        print(f"   Email sent: {email_notif['status']}")

        slack_notif = await notifications.send_slack_notification(
            channel="#support-updates",
            message=f"Ticket {ticket_data['id']} resolved successfully",
            priority="normal"
        )
        print(f"   Slack notification sent: {slack_notif['status']}")

        # 5. Update customer metrics in CRM
        print("\n5. 🔄 Updating CRM with new metrics...")
        await crm.update_customer_metrics(ticket_data["customer_id"], {
            "satisfaction_score": 0.95
        })
        print("   Customer metrics updated in CRM")

        print("\n✅ Full system integration completed successfully!")

    except Exception as e:
        print(f"❌ Error in system integration: {e}")


async def run_all_demos():
    """Run all demonstration scenarios."""
    print("🚀 Customer Support System - Complete Demo Suite")
    print("=" * 70)

    try:
        # Run all demo scenarios
        await demo_single_ticket_workflow()
        await demo_batch_ticket_processing()
        await demo_real_time_monitoring()
        await demo_escalation_workflow()
        await demo_integration_with_external_systems()

        print("\n" + "="*70)
        print("🎉 ALL DEMOS COMPLETED SUCCESSFULLY!")
        print("="*70)

        print("\n📋 SUMMARY OF CAPABILITIES DEMONSTRATED:")
        print("✅ Single ticket processing with AI-powered analysis")
        print("✅ Batch processing for multiple tickets")
        print("✅ Real-time monitoring with alert generation")
        print("✅ Intelligent escalation workflows")
        print("✅ Integration with CRM, Knowledge Base, and Notifications")
        print("✅ Sentiment analysis and priority assignment")
        print("✅ Automated response generation")
        print("✅ Performance metrics collection")

    except Exception as e:
        print(f"\n❌ Demo suite failed: {e}")
        import traceback
        traceback.print_exc()


def print_available_workflows():
    """Print information about available workflows."""
    print("\n📋 AVAILABLE WORKFLOWS:")
    workflows = get_available_workflows()
    for name, creator in workflows.items():
        print(f"   - {name}: {creator.__name__}")


if __name__ == "__main__":
    """Main entry point for the customer support system demo."""
    setup_logging()

    print("🤖 Customer Support System with Claude + KayGraph")
    print("=" * 60)

    # Print available workflows
    print_available_workflows()

    # Run demo
    asyncio.run(run_all_demos())