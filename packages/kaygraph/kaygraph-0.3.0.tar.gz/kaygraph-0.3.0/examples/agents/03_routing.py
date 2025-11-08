"""
Example 3: Routing (Customer Support System)

This example shows an intelligent routing system that:
- Classifies customer inquiries
- Routes to specialized handlers
- Provides appropriate responses

Pattern: Classify → Route to Specialist → Handle

Use cases:
- Customer support (billing/technical/general)
- Content moderation (spam/hate/appropriate)
- Complexity routing (simple model vs advanced model)
"""

import asyncio
from kaygraph.agent import create_router
from kaygraph import AsyncNode


# =============================================================================
# SPECIALIZED HANDLER NODES
# =============================================================================

class BillingHandler(AsyncNode):
    """Handles billing-related inquiries"""

    async def prep_async(self, shared):
        return {
            "query": shared.get("user_input", ""),
            "category": shared.get("route_category", "")
        }

    async def exec_async(self, prep_res):
        query = prep_res["query"]

        # Simulate billing system lookup
        if "charge" in query.lower() or "refund" in query.lower():
            return {
                "response": """I've reviewed your account. I see the issue with the duplicate charge.

I've initiated a refund for $29.99 which will appear in your account within 3-5 business days.

For future reference, you can view all charges in your billing dashboard.

Is there anything else I can help you with?""",
                "action_taken": "initiated_refund",
                "amount": 29.99
            }
        elif "plan" in query.lower() or "upgrade" in query.lower():
            return {
                "response": """I can help you with plan information!

Current Plans:
- Basic: $9.99/mo (1 user)
- Pro: $29.99/mo (up to 5 users, advanced features)
- Enterprise: Custom pricing (unlimited users, dedicated support)

Would you like to upgrade? I can process that for you immediately.""",
                "action_taken": "provided_plan_info"
            }
        else:
            return {
                "response": "I can help with billing questions, refunds, or plan changes. Could you provide more details?",
                "action_taken": "requested_clarification"
            }

    async def post_async(self, shared, prep_res, exec_res):
        shared["response"] = exec_res["response"]
        shared["handler"] = "billing"
        shared["action_taken"] = exec_res.get("action_taken")
        return None


class TechnicalHandler(AsyncNode):
    """Handles technical support inquiries"""

    async def exec_async(self, prep_res):
        query = prep_res["query"]

        # Simulate technical troubleshooting
        if "error" in query.lower() or "broken" in query.lower():
            return {
                "response": """I can help you troubleshoot this issue.

Common solutions:
1. Clear your browser cache and cookies
2. Try a different browser
3. Check if you're using the latest version
4. Verify your API credentials are correct

Could you tell me:
- What error message you're seeing exactly?
- Which browser/app version you're using?
- When did this start happening?

This will help me diagnose the issue more accurately.""",
                "action_taken": "provided_troubleshooting",
                "created_ticket": True
            }
        elif "api" in query.lower() or "integration" in query.lower():
            return {
                "response": """For API integration support, here's what you need:

1. API Key: Found in Settings → API Keys
2. Documentation: https://docs.example.com/api
3. Rate Limits: 1000 requests/hour
4. Support: api-support@example.com

Sample code:
```python
import requests
headers = {"Authorization": "Bearer YOUR_API_KEY"}
response = requests.get("https://api.example.com/v1/data", headers=headers)
```

Need help with a specific integration?""",
                "action_taken": "provided_api_docs"
            }
        else:
            return {
                "response": "I can help with technical issues, API integration, or bugs. What specific problem are you encountering?",
                "action_taken": "requested_details"
            }

    async def post_async(self, shared, prep_res, exec_res):
        shared["response"] = exec_res["response"]
        shared["handler"] = "technical"
        shared["action_taken"] = exec_res.get("action_taken")
        return None


class GeneralHandler(AsyncNode):
    """Handles general inquiries"""

    async def exec_async(self, prep_res):
        query = prep_res["query"]

        # Simulate general support
        if "how" in query.lower() and "work" in query.lower():
            return {
                "response": """Great question! Here's how our platform works:

1. Sign up for an account
2. Choose your plan
3. Configure your workspace
4. Invite team members
5. Start using features

We have video tutorials and documentation to help you get started:
- Quick Start Guide: https://docs.example.com/quickstart
- Video Tutorials: https://learn.example.com/videos

Would you like me to walk you through any specific feature?""",
                "action_taken": "provided_overview"
            }
        elif "feature" in query.lower() or "can" in query.lower():
            return {
                "response": """Our platform includes:

Core Features:
✓ Real-time collaboration
✓ Automated workflows
✓ Analytics dashboard
✓ API access
✓ Third-party integrations

Premium Features (Pro/Enterprise):
✓ Advanced security
✓ Custom branding
✓ Dedicated support
✓ SLA guarantees

Which features are you most interested in?""",
                "action_taken": "listed_features"
            }
        else:
            return {
                "response": """I'm here to help! I can assist with:

📘 General information about our platform
💡 Feature explanations
🎓 Getting started guidance
📊 Account information

For billing issues, type 'billing'
For technical problems, type 'technical'

How can I help you today?""",
                "action_taken": "provided_menu"
            }

    async def post_async(self, shared, prep_res, exec_res):
        shared["response"] = exec_res["response"]
        shared["handler"] = "general"
        shared["action_taken"] = exec_res.get("action_taken")
        return None


# =============================================================================
# MOCK LLM FOR CLASSIFICATION
# =============================================================================

async def mock_llm(messages):
    """Mock LLM that classifies user input"""
    # Extract user input
    user_content = ""
    for msg in messages:
        if msg["role"] == "user":
            user_content += msg["content"]

    # Simple classification logic
    content_lower = user_content.lower()

    if any(word in content_lower for word in ["charge", "bill", "payment", "refund", "plan", "subscription"]):
        return {"content": "billing"}
    elif any(word in content_lower for word in ["error", "bug", "broken", "api", "integration", "not working"]):
        return {"content": "technical"}
    else:
        return {"content": "general"}


# =============================================================================
# CREATE AND RUN ROUTER
# =============================================================================

async def main():
    print("=" * 70)
    print("Routing Example: Customer Support System")
    print("=" * 70)
    print()

    # Create specialized handlers
    handlers = {
        "billing": BillingHandler(),
        "technical": TechnicalHandler(),
        "general": GeneralHandler()
    }

    print("✓ Created 3 specialized handlers:")
    for category in handlers.keys():
        print(f"  - {category.capitalize()}Handler")
    print()

    # Create router
    router = create_router(mock_llm, handlers)

    print("✓ Created intelligent router")
    print()

    # Test different types of inquiries
    test_cases = [
        "I was charged twice for my subscription this month",
        "The API is returning a 401 error when I try to authenticate",
        "How does your platform work?",
        "I want to upgrade to the Pro plan",
        "My integration with Slack is broken",
    ]

    print("Processing customer inquiries...")
    print("=" * 70)
    print()

    for i, inquiry in enumerate(test_cases, 1):
        print(f"Inquiry #{i}")
        print("-" * 70)
        print(f"Customer: {inquiry}")
        print()

        # Run router
        result = await router.run_async({
            "user_input": inquiry
        })

        # Display results
        category = result.get("route_category", "unknown")
        handler = result.get("handler", "unknown")
        response = result.get("response", "No response")
        action = result.get("action_taken", "none")

        print(f"✓ Routed to: {category.upper()}")
        print(f"✓ Handler: {handler}")
        print(f"✓ Action: {action}")
        print()
        print("Response:")
        print(response)
        print()
        print("=" * 70)
        print()


# =============================================================================
# ADVANCED: COMPLEXITY-BASED ROUTING
# =============================================================================

class FastModelHandler(AsyncNode):
    """Handles simple queries with fast model"""
    async def exec_async(self, prep_res):
        return {"response": "Quick answer from fast model", "model": "fast"}


class CapableModelHandler(AsyncNode):
    """Handles complex queries with capable model"""
    async def exec_async(self, prep_res):
        return {"response": "Detailed answer from capable model", "model": "capable"}


async def complexity_routing_example():
    """Route based on query complexity to different models"""

    async def complexity_classifier(messages):
        """Classify as simple or complex"""
        user_content = ""
        for msg in messages:
            if msg["role"] == "user":
                user_content += msg["content"]

        # Simple heuristic: length and keywords
        if len(user_content.split()) < 10 and "?" in user_content:
            return {"content": "simple"}
        else:
            return {"content": "complex"}

    router = create_router(
        complexity_classifier,
        {
            "simple": FastModelHandler(),
            "complex": CapableModelHandler()
        }
    )

    print("Complexity-Based Routing Example")
    print("-" * 70)

    queries = [
        "What time is it?",
        "Can you explain the differences between microservices and monolithic architecture, including pros and cons?"
    ]

    for query in queries:
        result = await router.run_async({"user_input": query})
        print(f"Query: {query}")
        print(f"Model: {result.get('model')}")
        print()


if __name__ == "__main__":
    # Run main example
    asyncio.run(main())

    # Run complexity routing example
    # asyncio.run(complexity_routing_example())
