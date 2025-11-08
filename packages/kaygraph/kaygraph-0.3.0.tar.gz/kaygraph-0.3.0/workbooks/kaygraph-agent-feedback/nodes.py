"""
Feedback nodes implementing human-in-the-loop patterns.
These nodes demonstrate approval workflows, feedback collection, and quality control.
"""

import time
import json
import logging
from typing import Dict, Any, Optional, List
from datetime import datetime
from kaygraph import Node
from utils import call_llm
from models import (
    ApprovalStatus, ApprovalRequest, ApprovalResponse,
    FeedbackType, FeedbackRequest, FeedbackResponse,
    ReviewItem, ReviewDecision, ReviewResult,
    EscalationReason, EscalationRequest, EscalationResponse,
    RefinementRequest, RefinementGuidance,
    HumanFeedbackSession
)


# ============== Content Generation Nodes ==============

class ContentGenerationNode(Node):
    """
    Generates content that requires human approval.
    """
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.logger = logging.getLogger(self.__class__.__name__)
    
    def prep(self, shared: Dict[str, Any]) -> Dict[str, Any]:
        """Prepare generation request."""
        return {
            "prompt": shared.get("prompt", ""),
            "context": shared.get("context", ""),
            "constraints": shared.get("constraints", {})
        }
    
    def exec(self, prep_res: Dict[str, Any]) -> str:
        """Generate content with LLM."""
        prompt = prep_res["prompt"]
        context = prep_res["context"]
        
        system = """You are a helpful AI assistant generating content for human review.
Always be clear, professional, and follow any provided constraints."""
        
        full_prompt = f"Context: {context}\n\nRequest: {prompt}"
        
        if prep_res["constraints"]:
            full_prompt += f"\n\nConstraints: {prep_res['constraints']}"
        
        return call_llm(full_prompt, system=system)
    
    def post(self, shared: Dict[str, Any], prep_res: Dict, exec_res: str) -> Optional[str]:
        """Store generated content for approval."""
        import uuid
        
        request_id = str(uuid.uuid4())
        
        # Determine risk level based on content
        risk_level = self._assess_risk_level(exec_res, prep_res["prompt"])
        
        approval_request = ApprovalRequest(
            request_id=request_id,
            content=exec_res,
            context=prep_res.get("context"),
            risk_level=risk_level
        )
        
        shared["approval_request"] = approval_request
        shared["generated_content"] = exec_res
        
        self.logger.info(f"Generated content for approval (risk: {risk_level})")
        
        return None  # Continue to approval
    
    def _assess_risk_level(self, content: str, prompt: str) -> str:
        """Assess risk level of generated content."""
        high_risk_keywords = ["delete", "cancel", "terminate", "legal", "financial"]
        medium_risk_keywords = ["update", "modify", "change", "edit"]
        
        content_lower = content.lower()
        prompt_lower = prompt.lower()
        
        for keyword in high_risk_keywords:
            if keyword in content_lower or keyword in prompt_lower:
                return "high"
        
        for keyword in medium_risk_keywords:
            if keyword in content_lower or keyword in prompt_lower:
                return "medium"
        
        return "low"


# ============== Approval Workflow Nodes ==============

class HumanApprovalNode(Node):
    """
    Gets human approval for generated content.
    Simulates human interaction in examples.
    """
    
    def __init__(self, auto_approve: bool = False, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.auto_approve = auto_approve
        self.logger = logging.getLogger(self.__class__.__name__)
    
    def prep(self, shared: Dict[str, Any]) -> ApprovalRequest:
        """Get approval request."""
        return shared["approval_request"]
    
    def exec(self, prep_res: ApprovalRequest) -> ApprovalResponse:
        """Simulate human approval process."""
        print(f"\n{'='*50}")
        print("APPROVAL REQUEST")
        print(f"{'='*50}")
        print(f"Risk Level: {prep_res.risk_level.upper()}")
        print(f"Generated Content:\n{prep_res.content}")
        
        if prep_res.context:
            print(f"\nContext: {prep_res.context}")
        
        print(f"{'='*50}")
        
        if self.auto_approve:
            # Auto-approve for testing
            status = ApprovalStatus.APPROVED
            comments = "Auto-approved for testing"
            modified_content = None
        else:
            # Get human input
            while True:
                response = input("\nApprove? (y/n/m for modify): ").strip().lower()
                
                if response == 'y':
                    status = ApprovalStatus.APPROVED
                    comments = input("Comments (optional): ").strip() or None
                    modified_content = None
                    break
                elif response == 'n':
                    status = ApprovalStatus.REJECTED
                    comments = input("Reason for rejection: ").strip()
                    modified_content = None
                    break
                elif response == 'm':
                    status = ApprovalStatus.MODIFIED
                    modified_content = input("Enter modified content: ").strip()
                    comments = input("Comments (optional): ").strip() or None
                    break
                else:
                    print("Please enter 'y' for yes, 'n' for no, or 'm' for modify")
        
        return ApprovalResponse(
            request_id=prep_res.request_id,
            status=status,
            comments=comments,
            modified_content=modified_content
        )
    
    def post(self, shared: Dict[str, Any], prep_res: ApprovalRequest, exec_res: ApprovalResponse) -> Optional[str]:
        """Store approval response and route."""
        shared["approval_response"] = exec_res
        
        if exec_res.status == ApprovalStatus.APPROVED:
            shared["final_content"] = prep_res.content
            self.logger.info("Content approved")
            return "approved"
        elif exec_res.status == ApprovalStatus.MODIFIED:
            shared["final_content"] = exec_res.modified_content
            self.logger.info("Content modified and approved")
            return "approved"
        else:
            self.logger.warning(f"Content rejected: {exec_res.comments}")
            return "rejected"


# ============== Feedback Collection Nodes ==============

class FeedbackCollectionNode(Node):
    """
    Collects quality feedback on AI responses.
    """
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.logger = logging.getLogger(self.__class__.__name__)
    
    def prep(self, shared: Dict[str, Any]) -> FeedbackRequest:
        """Prepare feedback request."""
        import uuid
        
        return FeedbackRequest(
            feedback_id=str(uuid.uuid4()),
            ai_response=shared.get("ai_response", ""),
            original_prompt=shared.get("original_prompt", ""),
            feedback_type=FeedbackType.QUALITY
        )
    
    def exec(self, prep_res: FeedbackRequest) -> FeedbackResponse:
        """Collect human feedback."""
        print(f"\n{'='*50}")
        print("FEEDBACK REQUEST")
        print(f"{'='*50}")
        print(f"Original Prompt: {prep_res.original_prompt}")
        print(f"AI Response: {prep_res.ai_response}")
        print(f"{'='*50}")
        
        # Get rating
        while True:
            try:
                rating_input = input("\nRate the quality (1-5): ").strip()
                rating = int(rating_input) if rating_input else None
                if rating and 1 <= rating <= 5:
                    break
                else:
                    print("Please enter a number between 1 and 5")
            except ValueError:
                print("Please enter a valid number")
        
        # Get optional feedback
        feedback_text = input("Additional feedback (optional): ").strip() or None
        
        # Get suggestions
        suggestions = []
        suggestion = input("Suggestion for improvement (optional): ").strip()
        if suggestion:
            suggestions.append(suggestion)
        
        return FeedbackResponse(
            feedback_id=prep_res.feedback_id,
            rating=rating,
            feedback_text=feedback_text,
            suggestions=suggestions
        )
    
    def post(self, shared: Dict[str, Any], prep_res: FeedbackRequest, exec_res: FeedbackResponse) -> Optional[str]:
        """Store feedback for analysis."""
        shared["feedback_response"] = exec_res
        
        # Store feedback history
        if "feedback_history" not in shared:
            shared["feedback_history"] = []
        
        shared["feedback_history"].append({
            "prompt": prep_res.original_prompt,
            "response": prep_res.ai_response,
            "rating": exec_res.rating,
            "feedback": exec_res.feedback_text,
            "timestamp": exec_res.provided_at.isoformat()
        })
        
        self.logger.info(f"Collected feedback - Rating: {exec_res.rating}/5")
        
        # Route based on rating
        if exec_res.rating >= 4:
            return "good_quality"
        elif exec_res.rating >= 3:
            return "acceptable"
        else:
            return "needs_improvement"


# ============== Quality Review Nodes ==============

class BatchReviewNode(Node):
    """
    Reviews multiple AI outputs for quality control.
    """
    
    def __init__(self, batch_size: int = 5, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.batch_size = batch_size
        self.logger = logging.getLogger(self.__class__.__name__)
    
    def prep(self, shared: Dict[str, Any]) -> List[ReviewItem]:
        """Prepare batch for review."""
        items = shared.get("review_items", [])
        
        # Convert to ReviewItem objects
        review_items = []
        for i, item in enumerate(items[:self.batch_size]):
            review_items.append(ReviewItem(
                item_id=f"item_{i}",
                content=item.get("content", ""),
                generated_at=datetime.now(),
                confidence_score=item.get("confidence", 0.8),
                category=item.get("category")
            ))
        
        return review_items
    
    def exec(self, prep_res: List[ReviewItem]) -> List[ReviewResult]:
        """Perform batch review."""
        results = []
        
        print(f"\n{'='*50}")
        print(f"BATCH REVIEW - {len(prep_res)} items")
        print(f"{'='*50}")
        
        for item in prep_res:
            print(f"\nItem: {item.item_id}")
            print(f"Category: {item.category or 'None'}")
            print(f"Confidence: {item.confidence_score:.2f}")
            print(f"Content: {item.content[:100]}..." if len(item.content) > 100 else f"Content: {item.content}")
            
            # Get decision
            while True:
                decision = input("Decision (a=accept, r=reject, m=modify, e=escalate): ").strip().lower()
                
                if decision == 'a':
                    review_decision = ReviewDecision.ACCEPT
                    quality_score = int(input("Quality score (1-10): ").strip())
                    issues = []
                    modifications = None
                    escalation_reason = None
                    break
                elif decision == 'r':
                    review_decision = ReviewDecision.REJECT
                    quality_score = int(input("Quality score (1-10): ").strip())
                    issues_input = input("Issues (comma-separated): ").strip()
                    issues = [i.strip() for i in issues_input.split(",")] if issues_input else []
                    modifications = None
                    escalation_reason = None
                    break
                elif decision == 'm':
                    review_decision = ReviewDecision.MODIFY
                    quality_score = int(input("Quality score (1-10): ").strip())
                    issues = []
                    modifications = input("Modifications needed: ").strip()
                    escalation_reason = None
                    break
                elif decision == 'e':
                    review_decision = ReviewDecision.ESCALATE
                    quality_score = None
                    issues = []
                    modifications = None
                    escalation_reason = input("Escalation reason: ").strip()
                    break
                else:
                    print("Invalid choice. Please try again.")
            
            results.append(ReviewResult(
                item_id=item.item_id,
                decision=review_decision,
                quality_score=quality_score,
                issues=issues,
                modifications=modifications,
                escalation_reason=escalation_reason
            ))
        
        return results
    
    def post(self, shared: Dict[str, Any], prep_res: List[ReviewItem], exec_res: List[ReviewResult]) -> Optional[str]:
        """Store review results."""
        shared["review_results"] = exec_res
        
        # Calculate statistics
        total = len(exec_res)
        accepted = sum(1 for r in exec_res if r.decision == ReviewDecision.ACCEPT)
        rejected = sum(1 for r in exec_res if r.decision == ReviewDecision.REJECT)
        modified = sum(1 for r in exec_res if r.decision == ReviewDecision.MODIFY)
        escalated = sum(1 for r in exec_res if r.decision == ReviewDecision.ESCALATE)
        
        avg_quality = sum(r.quality_score for r in exec_res if r.quality_score) / max(1, total - escalated)
        
        shared["review_stats"] = {
            "total": total,
            "accepted": accepted,
            "rejected": rejected,
            "modified": modified,
            "escalated": escalated,
            "acceptance_rate": accepted / total if total > 0 else 0,
            "average_quality": avg_quality
        }
        
        self.logger.info(f"Review complete - Acceptance rate: {accepted/total*100:.1f}%")
        
        return None


# ============== Escalation Nodes ==============

class EscalationDetectionNode(Node):
    """
    Detects when to escalate to human intervention.
    """
    
    def __init__(
        self,
        confidence_threshold: float = 0.7,
        risk_threshold: float = 0.8,
        *args, **kwargs
    ):
        super().__init__(*args, **kwargs)
        self.confidence_threshold = confidence_threshold
        self.risk_threshold = risk_threshold
        self.logger = logging.getLogger(self.__class__.__name__)
    
    def prep(self, shared: Dict[str, Any]) -> Dict[str, Any]:
        """Prepare query for analysis."""
        return {
            "query": shared.get("query", ""),
            "ai_response": shared.get("ai_response", ""),
            "context": shared.get("context", {})
        }
    
    def exec(self, prep_res: Dict[str, Any]) -> Optional[EscalationRequest]:
        """Determine if escalation is needed."""
        query = prep_res["query"]
        ai_response = prep_res["ai_response"]
        
        # Analyze for escalation triggers
        confidence_score = self._calculate_confidence(query, ai_response)
        risk_score = self._calculate_risk(query)
        complexity_score = self._calculate_complexity(query)
        
        # Determine escalation reason
        escalation_reason = None
        
        if confidence_score < self.confidence_threshold:
            escalation_reason = EscalationReason.LOW_CONFIDENCE
        elif risk_score > self.risk_threshold:
            escalation_reason = EscalationReason.HIGH_RISK
        elif complexity_score > 0.8:
            escalation_reason = EscalationReason.COMPLEX_QUERY
        elif self._contains_unknown_intent(query):
            escalation_reason = EscalationReason.UNKNOWN_INTENT
        
        if escalation_reason:
            import uuid
            return EscalationRequest(
                escalation_id=str(uuid.uuid4()),
                query=query,
                ai_response=ai_response,
                reason=escalation_reason,
                confidence_score=confidence_score,
                risk_score=risk_score,
                context=prep_res["context"]
            )
        
        return None
    
    def _calculate_confidence(self, query: str, response: str) -> float:
        """Calculate confidence score."""
        # Simplified confidence calculation
        if not response or len(response) < 10:
            return 0.3
        
        uncertain_phrases = ["i'm not sure", "might be", "possibly", "unclear"]
        for phrase in uncertain_phrases:
            if phrase in response.lower():
                return 0.5
        
        return 0.85
    
    def _calculate_risk(self, query: str) -> float:
        """Calculate risk score."""
        high_risk_terms = ["delete", "cancel", "legal", "medical", "financial", "emergency"]
        query_lower = query.lower()
        
        risk_count = sum(1 for term in high_risk_terms if term in query_lower)
        return min(1.0, risk_count * 0.3)
    
    def _calculate_complexity(self, query: str) -> float:
        """Calculate complexity score."""
        # Simple heuristic: longer queries with multiple clauses
        word_count = len(query.split())
        clause_count = query.count(",") + query.count(";") + 1
        
        complexity = (word_count / 50) * 0.5 + (clause_count / 5) * 0.5
        return min(1.0, complexity)
    
    def _contains_unknown_intent(self, query: str) -> bool:
        """Check for unknown intent indicators."""
        unknown_indicators = ["what do you mean", "i don't understand", "confused"]
        query_lower = query.lower()
        
        return any(indicator in query_lower for indicator in unknown_indicators)
    
    def post(self, shared: Dict[str, Any], prep_res: Dict, exec_res: Optional[EscalationRequest]) -> Optional[str]:
        """Route based on escalation decision."""
        if exec_res:
            shared["escalation_request"] = exec_res
            self.logger.warning(f"Escalating to human: {exec_res.reason}")
            return "escalate"
        else:
            self.logger.info("No escalation needed")
            return "continue"


class HumanEscalationNode(Node):
    """
    Handles escalated queries with human intervention.
    """
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.logger = logging.getLogger(self.__class__.__name__)
    
    def prep(self, shared: Dict[str, Any]) -> EscalationRequest:
        """Get escalation request."""
        return shared["escalation_request"]
    
    def exec(self, prep_res: EscalationRequest) -> EscalationResponse:
        """Handle escalated query."""
        print(f"\n{'='*50}")
        print("ESCALATION REQUIRED")
        print(f"{'='*50}")
        print(f"Reason: {prep_res.reason}")
        print(f"Query: {prep_res.query}")
        
        if prep_res.ai_response:
            print(f"\nAI Response: {prep_res.ai_response}")
        
        if prep_res.confidence_score is not None:
            print(f"Confidence: {prep_res.confidence_score:.2f}")
        if prep_res.risk_score is not None:
            print(f"Risk: {prep_res.risk_score:.2f}")
        
        print(f"{'='*50}")
        
        # Get human response
        human_response = input("\nHuman response: ").strip()
        
        # Get action
        while True:
            action = input("Action (resolved/delegated/deferred): ").strip().lower()
            if action in ["resolved", "delegated", "deferred"]:
                break
            print("Please enter: resolved, delegated, or deferred")
        
        follow_up = input("Follow-up required? (y/n): ").strip().lower() == 'y'
        notes = input("Notes (optional): ").strip() or None
        
        return EscalationResponse(
            escalation_id=prep_res.escalation_id,
            human_response=human_response,
            action_taken=action,
            follow_up_required=follow_up,
            notes=notes
        )
    
    def post(self, shared: Dict[str, Any], prep_res: EscalationRequest, exec_res: EscalationResponse) -> Optional[str]:
        """Store escalation result."""
        shared["escalation_response"] = exec_res
        shared["final_response"] = exec_res.human_response
        
        self.logger.info(f"Escalation handled: {exec_res.action_taken}")
        
        return None


# ============== Refinement Nodes ==============

class RefinementNode(Node):
    """
    Iteratively refines output based on human feedback.
    """
    
    def __init__(self, max_iterations: int = 3, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.max_iterations = max_iterations
        self.logger = logging.getLogger(self.__class__.__name__)
    
    def prep(self, shared: Dict[str, Any]) -> RefinementRequest:
        """Prepare refinement request."""
        import uuid
        
        # Get current iteration
        iteration = shared.get("refinement_iteration", 1)
        
        # Get feedback history
        previous_feedback = shared.get("refinement_feedback", [])
        
        return RefinementRequest(
            refinement_id=shared.get("refinement_id", str(uuid.uuid4())),
            iteration=iteration,
            current_output=shared.get("current_output", ""),
            original_prompt=shared.get("original_prompt", ""),
            previous_feedback=previous_feedback,
            max_iterations=self.max_iterations
        )
    
    def exec(self, prep_res: RefinementRequest) -> str:
        """Refine output based on feedback."""
        if prep_res.iteration == 1:
            # Initial generation
            prompt = prep_res.original_prompt
            return call_llm(prompt)
        else:
            # Refinement based on feedback
            system = "You are refining your previous output based on human feedback."
            
            prompt = f"""Original request: {prep_res.original_prompt}

Current output: {prep_res.current_output}

Previous feedback:
{chr(10).join(f"- {fb}" for fb in prep_res.previous_feedback)}

Please improve your response based on this feedback."""
            
            return call_llm(prompt, system=system)
    
    def post(self, shared: Dict[str, Any], prep_res: RefinementRequest, exec_res: str) -> Optional[str]:
        """Store refined output."""
        shared["current_output"] = exec_res
        shared["refinement_id"] = prep_res.refinement_id
        shared["refinement_iteration"] = prep_res.iteration
        
        self.logger.info(f"Refinement iteration {prep_res.iteration} complete")
        
        return None  # Continue to feedback


class RefinementFeedbackNode(Node):
    """
    Collects feedback for refinement iterations.
    """
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.logger = logging.getLogger(self.__class__.__name__)
    
    def prep(self, shared: Dict[str, Any]) -> Dict[str, Any]:
        """Prepare for feedback collection."""
        return {
            "refinement_id": shared.get("refinement_id"),
            "iteration": shared.get("refinement_iteration", 1),
            "current_output": shared.get("current_output", ""),
            "original_prompt": shared.get("original_prompt", "")
        }
    
    def exec(self, prep_res: Dict[str, Any]) -> RefinementGuidance:
        """Collect refinement feedback."""
        print(f"\n{'='*50}")
        print(f"REFINEMENT - Iteration {prep_res['iteration']}")
        print(f"{'='*50}")
        print(f"Original request: {prep_res['original_prompt']}")
        print(f"\nCurrent output:\n{prep_res['current_output']}")
        print(f"{'='*50}")
        
        # Check satisfaction
        satisfied = input("\nAre you satisfied with this output? (y/n): ").strip().lower() == 'y'
        
        guidance = None
        specific_changes = []
        
        if not satisfied:
            guidance = input("General guidance for improvement: ").strip()
            
            # Get specific changes
            while True:
                change = input("Specific change needed (or press Enter to finish): ").strip()
                if not change:
                    break
                specific_changes.append(change)
        
        return RefinementGuidance(
            refinement_id=prep_res["refinement_id"],
            iteration=prep_res["iteration"],
            satisfied=satisfied,
            guidance=guidance,
            specific_changes=specific_changes
        )
    
    def post(self, shared: Dict[str, Any], prep_res: Dict, exec_res: RefinementGuidance) -> Optional[str]:
        """Store feedback and determine next step."""
        # Update feedback history
        if "refinement_feedback" not in shared:
            shared["refinement_feedback"] = []
        
        if exec_res.guidance:
            shared["refinement_feedback"].append(exec_res.guidance)
        
        for change in exec_res.specific_changes:
            shared["refinement_feedback"].append(change)
        
        if exec_res.satisfied:
            shared["final_output"] = shared["current_output"]
            self.logger.info("Refinement complete - User satisfied")
            return "complete"
        else:
            # Check iteration limit
            current_iteration = shared.get("refinement_iteration", 1)
            max_iterations = shared.get("max_refinement_iterations", 3)
            
            if current_iteration >= max_iterations:
                shared["final_output"] = shared["current_output"]
                self.logger.warning("Max iterations reached")
                return "max_iterations"
            else:
                # Continue refining
                shared["refinement_iteration"] = current_iteration + 1
                self.logger.info(f"Continuing to iteration {current_iteration + 1}")
                return "refine"