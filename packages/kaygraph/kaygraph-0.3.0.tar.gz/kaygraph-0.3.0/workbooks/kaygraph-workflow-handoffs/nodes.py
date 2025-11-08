"""
Node implementations for handoff workflows.
"""

import json
import logging
from typing import Dict, Any, List, Optional
from datetime import datetime
import random

from kaygraph import Node
from models import (
    AgentType, RequestType, Priority, HandoffReason,
    CustomerRequest, TriageAnalysis, AgentProfile,
    AgentResponse, HandoffContext, HandoffDecision,
    Task, TaskBreakdown, Document, DocumentAnalysis,
    ExtractedData, ValidationResult
)
from utils import call_llm

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def _clean_json_response(response: str) -> str:
    """Clean LLM response to extract JSON."""
    response = response.strip()
    
    # Remove thinking tags if present
    if "<think>" in response and "</think>" in response:
        parts = response.split("</think>")
        if len(parts) > 1:
            response = parts[-1].strip()
    
    # Remove markdown code blocks
    if response.startswith("```json"):
        response = response[7:]
    if response.endswith("```"):
        response = response[:-3]
    
    return response.strip()


# ============== Triage Nodes ==============

class TriageAgentNode(Node):
    """Triage agent that analyzes and routes requests."""
    
    def prep(self, shared: Dict[str, Any]) -> CustomerRequest:
        """Get customer request."""
        request_data = shared.get("request", {})
        if isinstance(request_data, CustomerRequest):
            return request_data
        
        # Create request from raw data
        return CustomerRequest(
            id=request_data.get("id", f"req_{datetime.now().timestamp()}"),
            customer_id=request_data.get("customer_id", "unknown"),
            content=request_data.get("content", shared.get("query", "")),
            metadata=request_data.get("metadata", {})
        )
    
    def exec(self, request: CustomerRequest) -> TriageAnalysis:
        """Analyze request and determine routing."""
        prompt = f"""Analyze this customer request and determine the best agent to handle it.

Customer Request: {request.content}

Available agent types:
- tech_support: Technical issues, bugs, crashes, performance problems
- billing: Payment issues, subscriptions, invoices, refunds
- sales: Product information, pricing, upgrades, new features
- general: General questions, basic help

Analyze the request and return a JSON object:
{{
  "request_type": "technical/billing/sales/general",
  "priority": "low/medium/high/urgent",
  "recommended_agent": "tech_support/billing/sales/general",
  "confidence": 0.0-1.0,
  "reasoning": "explanation of the analysis",
  "keywords": ["key", "words", "found"],
  "requires_escalation": false
}}

Consider priority based on:
- Urgent: System down, payment failed, security issue
- High: Major functionality broken, billing error
- Medium: Standard issues and questions
- Low: General inquiries, feature requests

Output JSON only:"""
        
        system = "You are a triage specialist who routes customer requests to the appropriate agent."
        
        try:
            response = call_llm(prompt, system, temperature=0.2)
            cleaned = _clean_json_response(response)
            data = json.loads(cleaned)
            
            return TriageAnalysis(
                request_type=RequestType(data.get("request_type", "general")),
                priority=Priority(data.get("priority", "medium")),
                recommended_agent=AgentType(data.get("recommended_agent", "general")),
                confidence=float(data.get("confidence", 0.8)),
                reasoning=data.get("reasoning", ""),
                keywords=data.get("keywords", []),
                requires_escalation=data.get("requires_escalation", False)
            )
        except Exception as e:
            logger.error(f"Triage analysis error: {e}")
            # Fallback analysis
            return TriageAnalysis(
                request_type=RequestType.GENERAL,
                priority=Priority.MEDIUM,
                recommended_agent=AgentType.GENERAL,
                confidence=0.5,
                reasoning="Error in analysis, defaulting to general agent"
            )
    
    def post(self, shared: Dict[str, Any], prep_res: CustomerRequest, 
             exec_res: TriageAnalysis) -> Optional[str]:
        """Store analysis and route to appropriate agent."""
        shared["request"] = prep_res
        shared["triage_analysis"] = exec_res
        
        # Initialize handoff context
        context = HandoffContext(
            request=prep_res,
            conversation_history=[{
                "agent": "triage",
                "action": "analyzed",
                "result": exec_res.model_dump()
            }]
        )
        shared["handoff_context"] = context
        
        # Route based on recommended agent
        return exec_res.recommended_agent.value


# ============== Specialist Agent Nodes ==============

class TechSupportAgentNode(Node):
    """Technical support specialist agent."""
    
    def prep(self, shared: Dict[str, Any]) -> Dict[str, Any]:
        """Get request and context."""
        return {
            "request": shared.get("request"),
            "context": shared.get("handoff_context"),
            "analysis": shared.get("triage_analysis")
        }
    
    def exec(self, data: Dict[str, Any]) -> AgentResponse:
        """Handle technical support request."""
        request = data["request"]
        context = data["context"]
        
        prompt = f"""You are a technical support specialist. Help the customer with their technical issue.

Customer Request: {request.content}
Priority: {data['analysis'].priority}
Keywords: {', '.join(data['analysis'].keywords)}

Previous context: {json.dumps(context.conversation_history[-3:], indent=2)}

Provide a helpful technical response. If the issue is beyond your expertise or requires billing/account access, indicate that a handoff is needed.

Return a JSON response:
{{
  "response": "your helpful response to the customer",
  "confidence": 0.0-1.0,
  "needs_handoff": false,
  "suggested_handoff": null,
  "handoff_reason": null,
  "resolution_complete": false
}}

If handoff is needed:
- suggested_handoff: "billing" (for payment/account issues) or "escalation" (for complex technical issues)
- handoff_reason: "expertise" or "escalation"

Output JSON only:"""
        
        system = "You are a technical support specialist. Be helpful, concise, and accurate."
        
        try:
            response = call_llm(prompt, system, temperature=0.3)
            cleaned = _clean_json_response(response)
            data = json.loads(cleaned)
            
            return AgentResponse(
                agent_type=AgentType.TECH_SUPPORT,
                response=data.get("response", "Let me help you with that technical issue."),
                confidence=float(data.get("confidence", 0.8)),
                needs_handoff=data.get("needs_handoff", False),
                suggested_handoff=AgentType(data["suggested_handoff"]) if data.get("suggested_handoff") else None,
                handoff_reason=HandoffReason(data["handoff_reason"]) if data.get("handoff_reason") else None,
                resolution_complete=data.get("resolution_complete", False)
            )
        except Exception as e:
            logger.error(f"Tech support error: {e}")
            return AgentResponse(
                agent_type=AgentType.TECH_SUPPORT,
                response="I'm having trouble processing your request. Let me escalate this to a senior technician.",
                confidence=0.3,
                needs_handoff=True,
                suggested_handoff=AgentType.ESCALATION,
                handoff_reason=HandoffReason.ERROR
            )
    
    def post(self, shared: Dict[str, Any], prep_res: Dict[str, Any], 
             exec_res: AgentResponse) -> Optional[str]:
        """Update context and determine next action."""
        context = shared["handoff_context"]
        context.conversation_history.append({
            "agent": "tech_support",
            "response": exec_res.response,
            "timestamp": datetime.now().isoformat()
        })
        context.previous_agents.append(AgentType.TECH_SUPPORT)
        
        shared["last_response"] = exec_res
        
        if exec_res.resolution_complete:
            return "complete"
        elif exec_res.needs_handoff and exec_res.suggested_handoff:
            context.handoff_count += 1
            return exec_res.suggested_handoff.value
        else:
            return "followup"


class BillingAgentNode(Node):
    """Billing specialist agent."""
    
    def prep(self, shared: Dict[str, Any]) -> Dict[str, Any]:
        """Get request and context."""
        return {
            "request": shared.get("request"),
            "context": shared.get("handoff_context"),
            "analysis": shared.get("triage_analysis")
        }
    
    def exec(self, data: Dict[str, Any]) -> AgentResponse:
        """Handle billing request."""
        request = data["request"]
        context = data["context"]
        
        prompt = f"""You are a billing specialist. Help the customer with their billing or payment issue.

Customer Request: {request.content}
Priority: {data['analysis'].priority if data.get('analysis') else 'medium'}

Previous context: {json.dumps(context.conversation_history[-3:], indent=2)}

Provide a helpful response about billing, payments, subscriptions, or refunds. If the issue requires technical support or management approval, indicate a handoff is needed.

Return a JSON response:
{{
  "response": "your helpful billing response",
  "confidence": 0.0-1.0,
  "needs_handoff": false,
  "suggested_handoff": null,
  "handoff_reason": null,
  "resolution_complete": false
}}

Output JSON only:"""
        
        system = "You are a billing specialist. Be clear about payment terms and policies."
        
        try:
            response = call_llm(prompt, system, temperature=0.3)
            cleaned = _clean_json_response(response)
            data = json.loads(cleaned)
            
            return AgentResponse(
                agent_type=AgentType.BILLING,
                response=data.get("response", "Let me help you with your billing inquiry."),
                confidence=float(data.get("confidence", 0.8)),
                needs_handoff=data.get("needs_handoff", False),
                suggested_handoff=AgentType(data["suggested_handoff"]) if data.get("suggested_handoff") else None,
                handoff_reason=HandoffReason(data["handoff_reason"]) if data.get("handoff_reason") else None,
                resolution_complete=data.get("resolution_complete", False)
            )
        except Exception as e:
            logger.error(f"Billing agent error: {e}")
            return AgentResponse(
                agent_type=AgentType.BILLING,
                response="I'm having trouble accessing billing information. Let me get a manager to help.",
                confidence=0.3,
                needs_handoff=True,
                suggested_handoff=AgentType.ESCALATION,
                handoff_reason=HandoffReason.ERROR
            )
    
    def post(self, shared: Dict[str, Any], prep_res: Dict[str, Any], 
             exec_res: AgentResponse) -> Optional[str]:
        """Update context and determine next action."""
        context = shared["handoff_context"]
        context.conversation_history.append({
            "agent": "billing",
            "response": exec_res.response,
            "timestamp": datetime.now().isoformat()
        })
        context.previous_agents.append(AgentType.BILLING)
        
        shared["last_response"] = exec_res
        
        if exec_res.resolution_complete:
            return "complete"
        elif exec_res.needs_handoff and exec_res.suggested_handoff:
            context.handoff_count += 1
            return exec_res.suggested_handoff.value
        else:
            return "followup"


class SalesAgentNode(Node):
    """Sales specialist agent."""
    
    def prep(self, shared: Dict[str, Any]) -> Dict[str, Any]:
        """Get request and context."""
        return {
            "request": shared.get("request"),
            "context": shared.get("handoff_context")
        }
    
    def exec(self, data: Dict[str, Any]) -> AgentResponse:
        """Handle sales inquiry."""
        request = data["request"]
        
        prompt = f"""You are a sales specialist. Help the customer with product information, pricing, or upgrades.

Customer Request: {request.content}

Provide helpful information about products, features, pricing, or upgrade options.

Return a JSON response:
{{
  "response": "your helpful sales response",
  "confidence": 0.0-1.0,
  "needs_handoff": false,
  "suggested_handoff": null,
  "handoff_reason": null,
  "resolution_complete": false
}}

Output JSON only:"""
        
        system = "You are a sales specialist. Be enthusiastic and informative about products."
        
        try:
            response = call_llm(prompt, system, temperature=0.4)
            cleaned = _clean_json_response(response)
            data = json.loads(cleaned)
            
            return AgentResponse(
                agent_type=AgentType.SALES,
                response=data.get("response", "I'd be happy to help you find the right product."),
                confidence=float(data.get("confidence", 0.8)),
                needs_handoff=data.get("needs_handoff", False),
                suggested_handoff=AgentType(data["suggested_handoff"]) if data.get("suggested_handoff") else None,
                handoff_reason=HandoffReason(data["handoff_reason"]) if data.get("handoff_reason") else None,
                resolution_complete=data.get("resolution_complete", False)
            )
        except Exception as e:
            logger.error(f"Sales agent error: {e}")
            return AgentResponse(
                agent_type=AgentType.SALES,
                response="Let me get you more information about our products.",
                confidence=0.7,
                needs_handoff=False,
                resolution_complete=False
            )
    
    def post(self, shared: Dict[str, Any], prep_res: Dict[str, Any], 
             exec_res: AgentResponse) -> Optional[str]:
        """Update context."""
        context = shared["handoff_context"]
        context.conversation_history.append({
            "agent": "sales",
            "response": exec_res.response,
            "timestamp": datetime.now().isoformat()
        })
        
        shared["last_response"] = exec_res
        
        if exec_res.resolution_complete:
            return "complete"
        elif exec_res.needs_handoff and exec_res.suggested_handoff:
            return exec_res.suggested_handoff.value
        else:
            return "followup"


class GeneralAgentNode(Node):
    """General support agent for misc queries."""
    
    def prep(self, shared: Dict[str, Any]) -> Dict[str, Any]:
        """Get request."""
        return {
            "request": shared.get("request"),
            "context": shared.get("handoff_context")
        }
    
    def exec(self, data: Dict[str, Any]) -> AgentResponse:
        """Handle general inquiry."""
        request = data["request"]
        
        return AgentResponse(
            agent_type=AgentType.GENERAL,
            response=f"I can help you with general questions about our services. Regarding '{request.content}', please feel free to ask for more specific information about technical issues, billing, or our products.",
            confidence=0.7,
            needs_handoff=False,
            resolution_complete=True
        )
    
    def post(self, shared: Dict[str, Any], prep_res: Dict[str, Any], 
             exec_res: AgentResponse) -> Optional[str]:
        """Update context."""
        shared["last_response"] = exec_res
        return "complete"


class EscalationAgentNode(Node):
    """Senior agent for escalated issues."""
    
    def prep(self, shared: Dict[str, Any]) -> Dict[str, Any]:
        """Get full context of escalated issue."""
        return {
            "request": shared.get("request"),
            "context": shared.get("handoff_context"),
            "previous_responses": [h for h in shared.get("handoff_context", {}).get("conversation_history", [])]
        }
    
    def exec(self, data: Dict[str, Any]) -> AgentResponse:
        """Handle escalated issue with full context."""
        request = data["request"]
        context = data["context"]
        
        prompt = f"""You are a senior specialist handling an escalated issue. You have access to all tools and can make exceptions to standard policies.

Original Request: {request.content}
Request ID: {request.id}
Priority: {request.priority}

Full Conversation History:
{json.dumps(context.conversation_history, indent=2)}

Previous Agents: {', '.join([a.value for a in context.previous_agents])}
Handoff Count: {context.handoff_count}

As a senior agent, provide a comprehensive resolution. You can:
- Override standard policies with justification
- Access any system or tool
- Provide compensation or special offers
- Coordinate with multiple departments

Return a JSON response:
{{
  "response": "your comprehensive resolution",
  "confidence": 0.0-1.0,
  "needs_handoff": false,
  "suggested_handoff": null,
  "handoff_reason": null,
  "resolution_complete": true
}}

Output JSON only:"""
        
        system = "You are a senior specialist with authority to resolve complex issues. Be professional and solution-oriented."
        
        try:
            response = call_llm(prompt, system, temperature=0.3)
            cleaned = _clean_json_response(response)
            data = json.loads(cleaned)
            
            return AgentResponse(
                agent_type=AgentType.ESCALATION,
                response=data.get("response", "I'm the senior specialist. Let me personally resolve this issue for you."),
                confidence=float(data.get("confidence", 0.9)),
                needs_handoff=False,
                resolution_complete=True
            )
        except Exception as e:
            logger.error(f"Escalation error: {e}")
            return AgentResponse(
                agent_type=AgentType.ESCALATION,
                response="As the senior specialist, I'll ensure this is resolved. I'll personally follow up with you within 24 hours with a complete solution.",
                confidence=0.9,
                needs_handoff=False,
                resolution_complete=True
            )
    
    def post(self, shared: Dict[str, Any], prep_res: Dict[str, Any], 
             exec_res: AgentResponse) -> Optional[str]:
        """Complete escalation."""
        context = shared["handoff_context"]
        context.conversation_history.append({
            "agent": "escalation",
            "response": exec_res.response,
            "timestamp": datetime.now().isoformat(),
            "resolution": "escalated_complete"
        })
        
        shared["last_response"] = exec_res
        return "complete"


# ============== Task Delegation Nodes ==============

class ManagerAgentNode(Node):
    """Manager agent that breaks down and delegates tasks."""
    
    def prep(self, shared: Dict[str, Any]) -> str:
        """Get complex task description."""
        return shared.get("task_description", shared.get("query", ""))
    
    def exec(self, task_description: str) -> TaskBreakdown:
        """Break down complex task into subtasks."""
        prompt = f"""You are a project manager. Break down this complex task into smaller subtasks that can be delegated to different specialists.

Task: {task_description}

Available specialists:
- data_extractor: Extracts and processes data
- document_analyzer: Analyzes documents and text
- validator: Validates data and ensures quality

Break down the task and return JSON:
{{
  "original_task": "the main task",
  "subtasks": [
    {{
      "id": "task_1",
      "description": "specific subtask description",
      "required_skills": ["skill1", "skill2"],
      "estimated_duration": 1.5,
      "priority": "high/medium/low",
      "dependencies": []
    }}
  ],
  "suggested_assignments": {{
    "task_1": "data_extractor"
  }},
  "estimated_total_time": 5.0,
  "parallel_execution": true
}}

Output JSON only:"""
        
        system = "You are an experienced project manager who excels at task decomposition and delegation."
        
        try:
            response = call_llm(prompt, system, temperature=0.3)
            cleaned = _clean_json_response(response)
            data = json.loads(cleaned)
            
            subtasks = []
            for task_data in data.get("subtasks", []):
                subtasks.append(Task(
                    id=task_data["id"],
                    description=task_data["description"],
                    required_skills=task_data.get("required_skills", []),
                    estimated_duration=float(task_data.get("estimated_duration", 1.0)),
                    priority=Priority(task_data.get("priority", "medium")),
                    dependencies=task_data.get("dependencies", [])
                ))
            
            assignments = {}
            for task_id, agent in data.get("suggested_assignments", {}).items():
                try:
                    assignments[task_id] = AgentType(agent)
                except:
                    assignments[task_id] = AgentType.GENERAL
            
            return TaskBreakdown(
                original_task=data.get("original_task", task_description),
                subtasks=subtasks,
                suggested_assignments=assignments,
                estimated_total_time=float(data.get("estimated_total_time", 5.0)),
                parallel_execution=data.get("parallel_execution", True)
            )
        except Exception as e:
            logger.error(f"Manager breakdown error: {e}")
            # Simple fallback
            return TaskBreakdown(
                original_task=task_description,
                subtasks=[
                    Task(
                        id="task_1",
                        description="Analyze the request",
                        required_skills=["analysis"],
                        estimated_duration=1.0
                    ),
                    Task(
                        id="task_2", 
                        description="Process the data",
                        required_skills=["processing"],
                        estimated_duration=2.0,
                        dependencies=["task_1"]
                    )
                ],
                suggested_assignments={
                    "task_1": AgentType.DOCUMENT_ANALYZER,
                    "task_2": AgentType.DATA_EXTRACTOR
                },
                estimated_total_time=3.0,
                parallel_execution=False
            )
    
    def post(self, shared: Dict[str, Any], prep_res: str, 
             exec_res: TaskBreakdown) -> Optional[str]:
        """Store breakdown and initiate delegation."""
        shared["task_breakdown"] = exec_res
        shared["pending_tasks"] = exec_res.subtasks.copy()
        shared["completed_tasks"] = []
        
        # For the simple example, just mark tasks as complete
        # In a real system, we'd delegate to worker agents
        for task in exec_res.subtasks:
            task.status = "completed"
            shared["completed_tasks"].append(task)
        
        return None  # Default routing


# ============== Document Processing Nodes ==============

class DocumentAnalyzerNode(Node):
    """Analyzes documents to determine processing needs."""
    
    def prep(self, shared: Dict[str, Any]) -> Document:
        """Get document to analyze."""
        doc_data = shared.get("document", {})
        if isinstance(doc_data, Document):
            return doc_data
        
        return Document(
            id=doc_data.get("id", f"doc_{datetime.now().timestamp()}"),
            content=doc_data.get("content", shared.get("content", "")),
            type=doc_data.get("type", "unknown"),
            source=doc_data.get("source", "upload"),
            metadata=doc_data.get("metadata", {})
        )
    
    def exec(self, document: Document) -> DocumentAnalysis:
        """Analyze document structure and content."""
        prompt = f"""Analyze this document and determine what processing it needs.

Document Type: {document.type}
Content Preview: {document.content[:500]}...

Analyze and return JSON:
{{
  "document_type": "invoice/contract/report/email/other",
  "key_entities": ["entity1", "entity2"],
  "summary": "brief summary of document",
  "requires_extraction": true/false,
  "confidence": 0.0-1.0
}}

Output JSON only:"""
        
        system = "You are a document analysis specialist."
        
        try:
            response = call_llm(prompt, system, temperature=0.2)
            cleaned = _clean_json_response(response)
            data = json.loads(cleaned)
            
            return DocumentAnalysis(
                document_id=document.id,
                document_type=data.get("document_type", "other"),
                key_entities=data.get("key_entities", []),
                summary=data.get("summary", "Document analyzed"),
                requires_extraction=data.get("requires_extraction", True),
                confidence=float(data.get("confidence", 0.8))
            )
        except Exception as e:
            logger.error(f"Document analysis error: {e}")
            return DocumentAnalysis(
                document_id=document.id,
                document_type="unknown",
                key_entities=[],
                summary="Analysis failed",
                requires_extraction=True,
                confidence=0.3
            )
    
    def post(self, shared: Dict[str, Any], prep_res: Document, 
             exec_res: DocumentAnalysis) -> Optional[str]:
        """Route based on analysis."""
        shared["document"] = prep_res
        shared["document_analysis"] = exec_res
        
        if exec_res.requires_extraction:
            return "extract"
        else:
            return "validate"


# ============== Response Formatting Nodes ==============

class HandoffResponseNode(Node):
    """Formats the final response with handoff history."""
    
    def prep(self, shared: Dict[str, Any]) -> Dict[str, Any]:
        """Gather all response data."""
        return {
            "request": shared.get("request"),
            "last_response": shared.get("last_response"),
            "context": shared.get("handoff_context")
        }
    
    def exec(self, data: Dict[str, Any]) -> str:
        """Format final response with context."""
        last_response = data["last_response"]
        context = data["context"]
        
        response = f"{last_response.response}\n\n"
        
        if context.handoff_count > 0:
            response += f"[Handled by {len(context.previous_agents)} agents"
            if context.handoff_count > 1:
                response += f" with {context.handoff_count} handoffs"
            response += "]\n"
        
        return response
    
    def post(self, shared: Dict[str, Any], prep_res: Dict[str, Any], 
             exec_res: str) -> Optional[str]:
        """Store final response."""
        shared["final_response"] = exec_res
        return None


class TaskCompletionNode(Node):
    """Aggregates completed tasks and generates summary."""
    
    def prep(self, shared: Dict[str, Any]) -> Dict[str, Any]:
        """Get task breakdown and results."""
        return {
            "breakdown": shared.get("task_breakdown"),
            "completed_tasks": shared.get("completed_tasks", [])
        }
    
    def exec(self, data: Dict[str, Any]) -> str:
        """Generate task completion summary."""
        breakdown = data["breakdown"]
        completed = data["completed_tasks"]
        
        summary = f"Task '{breakdown.original_task}' completed!\n\n"
        summary += f"Broke down into {len(breakdown.subtasks)} subtasks:\n"
        
        for task in breakdown.subtasks:
            status = "✓" if any(t.id == task.id for t in completed) else "✗"
            summary += f"{status} {task.description}\n"
        
        summary += f"\nTotal estimated time: {breakdown.estimated_total_time:.1f} hours"
        
        return summary
    
    def post(self, shared: Dict[str, Any], prep_res: Dict[str, Any], 
             exec_res: str) -> Optional[str]:
        """Store completion summary."""
        shared["completion_summary"] = exec_res
        return None