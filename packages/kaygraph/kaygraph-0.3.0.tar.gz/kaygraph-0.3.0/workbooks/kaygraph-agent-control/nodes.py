"""
Control nodes implementing deterministic decision-making patterns.
These nodes handle routing, classification, and conditional logic.
"""

import json
import logging
from typing import Dict, Any, Optional, List
from pydantic import ValidationError
from kaygraph import Node
from utils import call_llm
from models import (
    IntentClassification,
    DetailedIntent,
    RoutingDecision,
    PriorityRouting,
    DecisionCriteria,
    DecisionNode,
    DecisionResult,
    ControlFactor,
    MultiCriteriaDecision,
    ThresholdCheck,
    ThresholdDecision,
    ConditionalRoute,
    Condition
)


# ============== Intent Classification Control ==============

class IntentClassificationNode(Node):
    """
    Classify user intent and route accordingly.
    Core control pattern for intent-based routing.
    """
    
    def __init__(self, confidence_threshold: float = 0.7, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.confidence_threshold = confidence_threshold
        self.logger = logging.getLogger(self.__class__.__name__)
    
    def prep(self, shared: Dict[str, Any]) -> str:
        """Get user input for classification."""
        user_input = shared.get("user_input", "")
        if not user_input:
            raise ValueError("No user input provided")
        return user_input
    
    def exec(self, prep_res: str) -> IntentClassification:
        """Classify the intent using LLM."""
        prompt = f"""Classify this user input into one of these categories:
- question: User is asking for information
- request: User wants something done
- complaint: User is expressing dissatisfaction  
- statement: User is making a statement or sharing information
- unknown: Doesn't fit other categories

Input: "{prep_res}"

Provide:
1. intent (one of the above)
2. confidence (0.0-1.0)
3. reasoning (why you chose this)
4. sub_category (optional, more specific type)

Return as JSON."""
        
        response = call_llm(
            prompt,
            system="You are an intent classification specialist. Analyze user intent accurately."
        )
        
        try:
            data = json.loads(response.strip().strip("```json").strip("```"))
            return IntentClassification(**data)
        except (json.JSONDecodeError, ValidationError) as e:
            self.logger.error(f"Classification failed: {e}")
            return IntentClassification(
                intent="unknown",
                confidence=0.0,
                reasoning="Failed to classify"
            )
    
    def post(self, shared: Dict[str, Any], prep_res: str, exec_res: IntentClassification) -> Optional[str]:
        """Route based on classified intent."""
        shared["intent_classification"] = exec_res
        
        # Route only if confidence meets threshold
        if exec_res.confidence >= self.confidence_threshold:
            self.logger.info(f"Routing to {exec_res.intent} handler (confidence: {exec_res.confidence})")
            return exec_res.intent
        else:
            self.logger.warning(f"Low confidence ({exec_res.confidence}), routing to fallback")
            return "low_confidence"


# ============== Intent Handlers ==============

class QuestionHandlerNode(Node):
    """Handle question intents."""
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.logger = logging.getLogger(self.__class__.__name__)
    
    def prep(self, shared: Dict[str, Any]) -> str:
        """Get the question."""
        return shared.get("user_input", "")
    
    def exec(self, prep_res: str) -> str:
        """Answer the question."""
        prompt = f"Answer this question concisely and accurately: {prep_res}"
        
        response = call_llm(
            prompt,
            system="You are a helpful assistant that provides clear, accurate answers."
        )
        
        return response
    
    def post(self, shared: Dict[str, Any], prep_res: str, exec_res: str) -> Optional[str]:
        """Store answer."""
        shared["response"] = exec_res
        shared["response_type"] = "answer"
        self.logger.info("Question answered")
        return None


class RequestHandlerNode(Node):
    """Handle request intents."""
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.logger = logging.getLogger(self.__class__.__name__)
    
    def prep(self, shared: Dict[str, Any]) -> str:
        """Get the request."""
        return shared.get("user_input", "")
    
    def exec(self, prep_res: str) -> str:
        """Process the request."""
        # In real implementation, this would execute the requested action
        return f"I'll help you with that request: {prep_res}\n\n[Request processed successfully]"
    
    def post(self, shared: Dict[str, Any], prep_res: str, exec_res: str) -> Optional[str]:
        """Store result."""
        shared["response"] = exec_res
        shared["response_type"] = "action_taken"
        self.logger.info("Request processed")
        return None


class ComplaintHandlerNode(Node):
    """Handle complaint intents with escalation."""
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.logger = logging.getLogger(self.__class__.__name__)
    
    def prep(self, shared: Dict[str, Any]) -> str:
        """Get the complaint."""
        return shared.get("user_input", "")
    
    def exec(self, prep_res: str) -> Dict[str, str]:
        """Handle complaint with empathy and escalation."""
        # Analyze severity
        severity_prompt = f"""Rate the severity of this complaint (1-5):
1: Minor inconvenience
2: Moderate issue
3: Significant problem
4: Major issue
5: Critical/Emergency

Complaint: {prep_res}

Return JSON with: severity (1-5), category, suggested_action"""
        
        severity_response = call_llm(severity_prompt)
        
        try:
            severity_data = json.loads(severity_response.strip().strip("```json").strip("```"))
            severity = severity_data.get("severity", 3)
        except:
            severity = 3
        
        # Generate appropriate response
        if severity >= 4:
            response = f"I sincerely apologize for this serious issue. I'm immediately escalating your complaint to our senior team. Your concern about '{prep_res}' will be addressed with highest priority."
            escalated = True
        else:
            response = f"I understand your frustration about '{prep_res}'. Let me help resolve this for you right away."
            escalated = False
        
        return {
            "response": response,
            "escalated": escalated,
            "severity": severity
        }
    
    def post(self, shared: Dict[str, Any], prep_res: str, exec_res: Dict) -> Optional[str]:
        """Store complaint handling result."""
        shared["response"] = exec_res["response"]
        shared["response_type"] = "complaint_handled"
        shared["escalated"] = exec_res["escalated"]
        
        if exec_res["escalated"]:
            self.logger.warning(f"Complaint escalated (severity: {exec_res['severity']})")
        else:
            self.logger.info("Complaint handled")
        
        return None


# ============== Decision Tree Control ==============

class DecisionTreeNode(Node):
    """
    Implement decision tree logic for complex routing.
    Evaluates multiple criteria in sequence.
    """
    
    def __init__(self, decision_tree: Dict[str, Any], *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.decision_tree = decision_tree
        self.logger = logging.getLogger(self.__class__.__name__)
    
    def prep(self, shared: Dict[str, Any]) -> Dict[str, Any]:
        """Prepare context for decision tree."""
        return {
            "input": shared.get("user_input", ""),
            "context": shared.get("context", {}),
            "metadata": shared.get("metadata", {})
        }
    
    def exec(self, prep_res: Dict[str, Any]) -> DecisionResult:
        """Traverse decision tree based on criteria."""
        path = []
        criteria_evaluated = []
        current_node = "root"
        
        # Traverse tree
        while current_node in self.decision_tree:
            node_data = self.decision_tree[current_node]
            path.append(current_node)
            
            if node_data.get("is_leaf", False):
                # Reached a decision
                return DecisionResult(
                    path_taken=path,
                    final_action=node_data["action"],
                    criteria_evaluated=criteria_evaluated,
                    confidence=0.9
                )
            
            # Evaluate criteria for this node
            criteria_met = self._evaluate_node_criteria(
                node_data,
                prep_res,
                criteria_evaluated
            )
            
            # Determine next node
            if criteria_met:
                current_node = node_data.get("yes_path", "default")
            else:
                current_node = node_data.get("no_path", "default")
        
        # Default action if tree traversal fails
        return DecisionResult(
            path_taken=path,
            final_action="default_action",
            criteria_evaluated=criteria_evaluated,
            confidence=0.5
        )
    
    def _evaluate_node_criteria(
        self, 
        node_data: Dict[str, Any], 
        context: Dict[str, Any],
        criteria_list: List[DecisionCriteria]
    ) -> bool:
        """Evaluate criteria for a decision node."""
        # Use LLM to evaluate complex criteria
        question = node_data.get("question", "")
        user_input = context.get("input", "")
        
        prompt = f"""Evaluate this decision criteria:
Question: {question}
User Input: {user_input}
Context: {json.dumps(context.get('context', {}))}

Answer with JSON: {{"answer": true/false, "reasoning": "brief explanation"}}"""
        
        response = call_llm(prompt)
        
        try:
            result = json.loads(response.strip().strip("```json").strip("```"))
            answer = result.get("answer", False)
            
            criteria = DecisionCriteria(
                criterion=question,
                value=answer,
                met=answer,
                weight=1.0
            )
            criteria_list.append(criteria)
            
            return answer
        except:
            return False
    
    def post(self, shared: Dict[str, Any], prep_res: Dict, exec_res: DecisionResult) -> Optional[str]:
        """Store decision result and route."""
        shared["decision_result"] = exec_res
        shared["decision_path"] = " → ".join(exec_res.path_taken)
        
        self.logger.info(f"Decision tree result: {exec_res.final_action}")
        return exec_res.final_action


# ============== Multi-Criteria Control ==============

class MultiCriteriaControlNode(Node):
    """
    Make decisions based on multiple weighted factors.
    Supports complex routing logic.
    """
    
    def __init__(self, factors_config: List[Dict[str, Any]], *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.factors_config = factors_config
        self.logger = logging.getLogger(self.__class__.__name__)
    
    def prep(self, shared: Dict[str, Any]) -> Dict[str, Any]:
        """Prepare input for multi-criteria evaluation."""
        return {
            "input": shared.get("user_input", ""),
            "context": shared.get("context", {})
        }
    
    def exec(self, prep_res: Dict[str, Any]) -> MultiCriteriaDecision:
        """Evaluate multiple criteria and make decision."""
        factors = []
        
        # Evaluate each factor
        for factor_config in self.factors_config:
            factor_name = factor_config["name"]
            weight = factor_config.get("weight", 1.0)
            
            # Use LLM to evaluate factor
            prompt = f"""Evaluate the '{factor_name}' factor for this input:
Input: {prep_res['input']}

Rate from 0.0 to 1.0 where:
- 0.0 = Very low/negative
- 0.5 = Neutral/moderate  
- 1.0 = Very high/positive

Consider: {factor_config.get('description', '')}

Return JSON: {{"score": 0.0-1.0, "reasoning": "brief explanation"}}"""
            
            response = call_llm(prompt)
            
            try:
                result = json.loads(response.strip().strip("```json").strip("```"))
                score = float(result.get("score", 0.5))
                
                factor = ControlFactor(
                    factor_name=factor_name,
                    value=result.get("reasoning", ""),
                    normalized_score=score,
                    weight=weight
                )
                factors.append(factor)
            except:
                # Default factor on error
                factors.append(ControlFactor(
                    factor_name=factor_name,
                    value="Error evaluating",
                    normalized_score=0.5,
                    weight=weight
                ))
        
        # Calculate total score
        total_weight = sum(f.weight for f in factors)
        if total_weight > 0:
            total_score = sum(f.weighted_score for f in factors) / total_weight
        else:
            total_score = 0.5
        
        # Make decision based on score
        if total_score >= 0.8:
            decision = "high_priority"
            reasoning = "Multiple factors indicate high importance"
        elif total_score >= 0.6:
            decision = "normal_priority"
            reasoning = "Moderate importance across factors"
        elif total_score >= 0.4:
            decision = "low_priority"
            reasoning = "Below average importance"
        else:
            decision = "defer"
            reasoning = "Very low importance, consider deferring"
        
        return MultiCriteriaDecision(
            factors=factors,
            total_score=total_score,
            decision=decision,
            reasoning=reasoning,
            threshold_met=total_score >= 0.6
        )
    
    def post(self, shared: Dict[str, Any], prep_res: Dict, exec_res: MultiCriteriaDecision) -> Optional[str]:
        """Store decision and route."""
        shared["multi_criteria_decision"] = exec_res
        shared["routing_decision"] = exec_res.decision
        
        self.logger.info(f"Multi-criteria decision: {exec_res.decision} (score: {exec_res.total_score:.2f})")
        
        # Route based on decision
        return exec_res.decision


# ============== Threshold Control ==============

class ThresholdControlNode(Node):
    """
    Control flow based on threshold checks.
    Useful for metrics-based routing.
    """
    
    def __init__(self, thresholds: List[Dict[str, Any]], *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.thresholds = thresholds
        self.logger = logging.getLogger(self.__class__.__name__)
    
    def prep(self, shared: Dict[str, Any]) -> Dict[str, Any]:
        """Get metrics for threshold checking."""
        return {
            "metrics": shared.get("metrics", {}),
            "input": shared.get("user_input", "")
        }
    
    def exec(self, prep_res: Dict[str, Any]) -> ThresholdDecision:
        """Check thresholds and decide action."""
        checks = []
        
        for threshold_config in self.thresholds:
            metric_name = threshold_config["metric"]
            threshold_value = threshold_config["threshold"]
            comparison = threshold_config.get("comparison", "greater")
            
            # Get current metric value
            if metric_name in prep_res["metrics"]:
                current_value = prep_res["metrics"][metric_name]
            else:
                # Calculate metric using LLM if not provided
                current_value = self._calculate_metric(
                    metric_name, 
                    prep_res["input"]
                )
            
            check = ThresholdCheck(
                metric_name=metric_name,
                current_value=current_value,
                threshold=threshold_value,
                comparison=comparison,
                passed=False,  # Will be auto-calculated
                action_if_passed=threshold_config.get("action_passed", "continue"),
                action_if_failed=threshold_config.get("action_failed", "stop")
            )
            checks.append(check)
        
        # Determine final action
        all_must_pass = self.thresholds[0].get("all_must_pass", False) if self.thresholds else False
        passed_checks = [c for c in checks if c.passed]
        
        if all_must_pass:
            all_passed = len(passed_checks) == len(checks)
            final_action = checks[0].action_if_passed if all_passed else checks[0].action_if_failed
        else:
            # Any check passing triggers action
            final_action = passed_checks[0].action_if_passed if passed_checks else checks[0].action_if_failed
        
        return ThresholdDecision(
            checks=checks,
            all_must_pass=all_must_pass,
            final_action=final_action,
            passed_count=len(passed_checks),
            total_count=len(checks)
        )
    
    def _calculate_metric(self, metric_name: str, input_text: str) -> float:
        """Calculate a metric value using LLM."""
        prompt = f"""Calculate the '{metric_name}' metric for this input:
"{input_text}"

Return a single number between 0 and 100."""
        
        response = call_llm(prompt)
        
        try:
            # Extract number from response
            import re
            numbers = re.findall(r'\d+\.?\d*', response)
            if numbers:
                return float(numbers[0])
        except:
            pass
        
        return 50.0  # Default middle value
    
    def post(self, shared: Dict[str, Any], prep_res: Dict, exec_res: ThresholdDecision) -> Optional[str]:
        """Store threshold results and route."""
        shared["threshold_decision"] = exec_res
        
        self.logger.info(
            f"Threshold checks: {exec_res.passed_count}/{exec_res.total_count} passed"
        )
        
        return exec_res.final_action


# ============== Fallback Handlers ==============

class LowConfidenceHandlerNode(Node):
    """Handle low confidence classifications."""
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.logger = logging.getLogger(self.__class__.__name__)
    
    def prep(self, shared: Dict[str, Any]) -> Dict[str, Any]:
        """Get original input and classification."""
        return {
            "input": shared.get("user_input", ""),
            "classification": shared.get("intent_classification")
        }
    
    def exec(self, prep_res: Dict[str, Any]) -> str:
        """Generate clarification request."""
        classification = prep_res["classification"]
        
        if classification:
            return f"I'm not quite sure I understood correctly. It seems like you might be {classification.reasoning.lower()}, but could you please clarify what you need?"
        else:
            return "I'm not sure I understood your request. Could you please rephrase or provide more details?"
    
    def post(self, shared: Dict[str, Any], prep_res: Dict, exec_res: str) -> Optional[str]:
        """Store clarification request."""
        shared["response"] = exec_res
        shared["response_type"] = "clarification_needed"
        return None


class DefaultHandlerNode(Node):
    """Default handler for unmatched routes."""
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.logger = logging.getLogger(self.__class__.__name__)
    
    def prep(self, shared: Dict[str, Any]) -> str:
        """Get input."""
        return shared.get("user_input", "")
    
    def exec(self, prep_res: str) -> str:
        """Generate default response."""
        return "I'll do my best to help with your request. Let me process this for you."
    
    def post(self, shared: Dict[str, Any], prep_res: str, exec_res: str) -> Optional[str]:
        """Store default response."""
        shared["response"] = exec_res
        shared["response_type"] = "default"
        return None