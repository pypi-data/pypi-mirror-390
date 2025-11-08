"""
Node implementations for reasoning workflows.
"""

import json
import logging
try:
    import yaml
except ImportError:
    yaml = None
from typing import Dict, Any, List, Optional
from datetime import datetime
import re

from kaygraph import Node, MetricsNode
from models import (
    ReasoningType, ProblemType, ThoughtStatus,
    ThoughtStep, ReasoningPlan, ReasoningState,
    MathProblem, MathStep, MathSolution,
    LogicConstraint, LogicState,
    CodeAnalysis, CodeIssue,
    DecisionOption, DecisionFactor, DecisionAnalysis,
    ReasoningPath, MultiPathAnalysis,
    ReflectionPoint
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
    elif response.startswith("```yaml"):
        response = response[7:]
    elif response.startswith("```"):
        response = response[3:]
    
    if response.endswith("```"):
        response = response[:-3]
    
    return response.strip()


# ============== Chain-of-Thought Nodes ==============

class ProblemAnalyzerNode(Node):
    """Analyzes problem and creates initial reasoning plan."""
    
    def prep(self, shared: Dict[str, Any]) -> str:
        """Get problem statement."""
        return shared.get("problem", shared.get("query", ""))
    
    def exec(self, problem: str) -> ReasoningPlan:
        """Analyze problem and create plan."""
        prompt = f"""Analyze this problem and create a reasoning plan.

Problem: {problem}

Determine:
1. Problem type (math/logic/code/decision/analysis/creative)
2. Best reasoning approach (chain_of_thought/step_by_step/tree_of_thought/self_reflection/multi_path)
3. Initial steps needed to solve it

Return a JSON plan:
{{
  "problem": "the problem statement",
  "problem_type": "math/logic/code/decision/analysis/creative",
  "approach": "chain_of_thought/step_by_step/etc",
  "steps": [
    {{
      "id": "step_1",
      "content": "First step description",
      "reasoning_type": "analysis/calculation/deduction/etc",
      "confidence": 0.8,
      "dependencies": []
    }}
  ],
  "confidence": 0.7,
  "max_iterations": 10
}}

Create 3-5 initial steps. Output JSON only:"""
        
        system = "You are an expert problem analyzer. Break down problems into clear reasoning steps."
        
        try:
            response = call_llm(prompt, system, temperature=0.3)
            cleaned = _clean_json_response(response)
            data = json.loads(cleaned)
            
            steps = []
            for step_data in data.get("steps", []):
                steps.append(ThoughtStep(
                    id=step_data["id"],
                    content=step_data["content"],
                    reasoning_type=step_data.get("reasoning_type", "analysis"),
                    confidence=float(step_data.get("confidence", 0.8)),
                    dependencies=step_data.get("dependencies", [])
                ))
            
            return ReasoningPlan(
                problem=data.get("problem", problem),
                problem_type=ProblemType(data.get("problem_type", "analysis")),
                approach=ReasoningType(data.get("approach", "chain_of_thought")),
                steps=steps,
                confidence=float(data.get("confidence", 0.7)),
                max_iterations=data.get("max_iterations", 10)
            )
        except Exception as e:
            logger.error(f"Problem analysis error: {e}")
            # Fallback plan
            return ReasoningPlan(
                problem=problem,
                problem_type=ProblemType.ANALYSIS,
                approach=ReasoningType.STEP_BY_STEP,
                steps=[
                    ThoughtStep(
                        id="step_1",
                        content="Understand the problem",
                        reasoning_type="analysis",
                        confidence=0.5
                    ),
                    ThoughtStep(
                        id="step_2",
                        content="Identify key information",
                        reasoning_type="analysis",
                        confidence=0.5,
                        dependencies=["step_1"]
                    ),
                    ThoughtStep(
                        id="step_3",
                        content="Solve step by step",
                        reasoning_type="calculation",
                        confidence=0.5,
                        dependencies=["step_2"]
                    )
                ],
                confidence=0.5
            )
    
    def post(self, shared: Dict[str, Any], prep_res: str, exec_res: ReasoningPlan) -> Optional[str]:
        """Initialize reasoning state."""
        state = ReasoningState(plan=exec_res)
        shared["reasoning_state"] = state
        
        # Route based on approach
        return exec_res.approach.value


class ChainOfThoughtNode(MetricsNode):
    """Executes chain-of-thought reasoning with self-loop."""
    
    max_retries = 2
    wait = 1.0
    
    def prep(self, shared: Dict[str, Any]) -> ReasoningState:
        """Get current reasoning state."""
        return shared.get("reasoning_state")
    
    def exec(self, state: ReasoningState) -> Dict[str, Any]:
        """Execute next thought in the chain."""
        plan = state.plan
        
        # Find next pending step
        next_step = None
        for step in plan.steps:
            if step.status == ThoughtStatus.PENDING:
                # Check dependencies
                deps_satisfied = all(
                    dep in state.completed_steps 
                    for dep in step.dependencies
                )
                if deps_satisfied:
                    next_step = step
                    break
        
        if not next_step:
            # All steps completed or blocked
            return {
                "complete": True,
                "final_answer": self._synthesize_answer(state)
            }
        
        # Execute the step
        thought_prompt = f"""Execute this reasoning step using chain-of-thought.

Problem: {plan.problem}
Current Step: {next_step.content}
Step Type: {next_step.reasoning_type}

Previous steps completed:
{self._format_history(state)}

Think through this step carefully and show your reasoning. Then provide the result.

Return YAML response:
thought_process: |
  Your detailed thinking here...
  Show all work and reasoning...
result: "The result of this step"
confidence: 0.8
insights:
  - "Any new insights discovered"
next_steps:
  - "Any new steps to add to the plan"
issues: []  # Any issues found

Output YAML only:"""
        
        system = "You are performing careful step-by-step reasoning. Show your work clearly."
        
        try:
            response = call_llm(thought_prompt, system, temperature=0.4)
            cleaned = _clean_json_response(response)
            
            # Try YAML first, fall back to JSON-like parsing
            if yaml:
                data = yaml.safe_load(cleaned)
            else:
                # Simple parsing for mock response
                data = {}
                lines = cleaned.split('\n')
                for line in lines:
                    if 'result:' in line:
                        data['result'] = line.split('result:')[1].strip().strip('"')
                    elif 'confidence:' in line:
                        data['confidence'] = float(line.split('confidence:')[1].strip())
                    elif 'thought_process:' in line:
                        data['thought_process'] = "Mock thought process"
            
            # Update step
            next_step.status = ThoughtStatus.COMPLETED
            next_step.result = data.get("result", "")
            state.completed_steps.append(next_step.id)
            state.thought_history.append(next_step)
            
            # Add insights
            if data.get("insights"):
                state.insights.extend(data["insights"])
            
            # Add new steps if suggested
            if data.get("next_steps"):
                for i, new_step in enumerate(data["next_steps"]):
                    new_id = f"step_{len(plan.steps) + i + 1}"
                    plan.steps.append(ThoughtStep(
                        id=new_id,
                        content=new_step,
                        reasoning_type="analysis",
                        confidence=0.7,
                        dependencies=[next_step.id]
                    ))
            
            # Update confidence
            step_confidence = float(data.get("confidence", 0.8))
            state.total_confidence = (
                state.total_confidence * len(state.completed_steps) + step_confidence
            ) / (len(state.completed_steps) + 1)
            
            plan.iterations += 1
            
            return {
                "complete": False,
                "step_completed": next_step.id,
                "confidence": step_confidence
            }
            
        except Exception as e:
            logger.error(f"Chain-of-thought error: {e}")
            next_step.status = ThoughtStatus.FAILED
            next_step.error = str(e)
            
            return {
                "complete": False,
                "error": str(e)
            }
    
    def post(self, shared: Dict[str, Any], prep_res: ReasoningState, 
             exec_res: Dict[str, Any]) -> Optional[str]:
        """Determine next action."""
        state = shared["reasoning_state"]
        
        if exec_res.get("complete"):
            state.final_answer = exec_res.get("final_answer", "Unable to complete reasoning")
            return "complete"
        elif state.plan.iterations >= state.plan.max_iterations:
            state.final_answer = self._synthesize_answer(state)
            return "complete"
        else:
            # Self-loop to continue reasoning
            return "chain_of_thought"
    
    def _format_history(self, state: ReasoningState) -> str:
        """Format completed steps for context."""
        if not state.thought_history:
            return "None yet"
        
        history = []
        for step in state.thought_history[-5:]:  # Last 5 steps
            history.append(f"- {step.content}: {step.result}")
        
        return "\n".join(history)
    
    def _synthesize_answer(self, state: ReasoningState) -> str:
        """Synthesize final answer from all steps."""
        if not state.completed_steps:
            return "Unable to complete any reasoning steps"
        
        # Collect all results
        results = []
        for step in state.thought_history:
            if step.result:
                results.append(f"{step.content}: {step.result}")
        
        # Simple synthesis
        answer = "Based on the reasoning process:\n\n"
        answer += "\n".join(results)
        
        if state.insights:
            answer += "\n\nKey insights:\n"
            answer += "\n".join(f"- {insight}" for insight in state.insights)
        
        answer += f"\n\nConfidence: {state.total_confidence:.1%}"
        
        return answer


# ============== Math Reasoning Nodes ==============

class MathReasoningNode(Node):
    """Specialized node for mathematical reasoning."""
    
    def prep(self, shared: Dict[str, Any]) -> Dict[str, Any]:
        """Get problem and state."""
        return {
            "problem": shared.get("problem", ""),
            "state": shared.get("reasoning_state")
        }
    
    def exec(self, data: Dict[str, Any]) -> MathSolution:
        """Solve math problem step by step."""
        problem = data["problem"]
        
        prompt = f"""Solve this math problem step by step.

Problem: {problem}

First, identify:
1. What we know (given values)
2. What we need to find
3. The approach to use

Then solve step by step, showing all work.

Return JSON solution:
{{
  "problem": {{
    "description": "problem description",
    "known_values": {{"variable": value}},
    "unknown_variable": "what to find",
    "problem_type": "algebra/geometry/probability/etc"
  }},
  "steps": [
    {{
      "step_number": 1,
      "description": "What we're doing",
      "operation": "add/multiply/etc",
      "expression": "mathematical expression",
      "result": 42.0,
      "units": "miles/hours/etc"
    }}
  ],
  "final_answer": "The answer with units",
  "verification_method": "How we can check this"
}}

Output JSON only:"""
        
        system = "You are a math tutor. Solve problems clearly, showing all work."
        
        try:
            response = call_llm(prompt, system, temperature=0.2)
            cleaned = _clean_json_response(response)
            data = json.loads(cleaned)
            
            # Parse problem
            prob_data = data["problem"]
            math_problem = MathProblem(
                description=prob_data["description"],
                known_values=prob_data.get("known_values", {}),
                unknown_variable=prob_data.get("unknown_variable", "x"),
                problem_type=prob_data.get("problem_type", "algebra")
            )
            
            # Parse steps
            steps = []
            for step_data in data.get("steps", []):
                steps.append(MathStep(
                    step_number=step_data["step_number"],
                    description=step_data["description"],
                    operation=step_data["operation"],
                    expression=step_data["expression"],
                    result=step_data.get("result"),
                    units=step_data.get("units"),
                    verified=True
                ))
            
            return MathSolution(
                problem=math_problem,
                steps=steps,
                final_answer=data["final_answer"],
                verification_method=data.get("verification_method")
            )
            
        except Exception as e:
            logger.error(f"Math reasoning error: {e}")
            # Return simple solution
            return MathSolution(
                problem=MathProblem(
                    description=problem,
                    known_values={},
                    unknown_variable="x"
                ),
                steps=[],
                final_answer="Unable to solve mathematically"
            )
    
    def post(self, shared: Dict[str, Any], prep_res: Dict[str, Any], 
             exec_res: MathSolution) -> Optional[str]:
        """Store solution."""
        shared["math_solution"] = exec_res
        if shared.get("reasoning_state"):
            shared["reasoning_state"].final_answer = exec_res.final_answer
        return None  # Default routing


# ============== Logic Reasoning Nodes ==============

class LogicReasoningNode(Node):
    """Specialized node for logic puzzles."""
    
    def prep(self, shared: Dict[str, Any]) -> str:
        """Get logic problem."""
        return shared.get("problem", "")
    
    def exec(self, problem: str) -> LogicState:
        """Solve logic problem through deduction."""
        prompt = f"""Solve this logic problem through systematic deduction.

Problem: {problem}

Identify:
1. All entities involved
2. All constraints/rules
3. Step-by-step deductions

Return JSON:
{{
  "entities": {{"entity_name": "current_state_or_value"}},
  "constraints": [
    {{
      "id": "c1",
      "description": "constraint description",
      "entities": ["entity1", "entity2"],
      "relationship": "type of relationship",
      "satisfied": true/false
    }}
  ],
  "deductions": [
    "Step 1: From constraint X, we know...",
    "Step 2: This means..."
  ],
  "solution_valid": true/false
}}

Output JSON only:"""
        
        system = "You are a logic puzzle expert. Solve systematically through deduction."
        
        try:
            response = call_llm(prompt, system, temperature=0.2)
            cleaned = _clean_json_response(response)
            data = json.loads(cleaned)
            
            constraints = []
            for c_data in data.get("constraints", []):
                constraints.append(LogicConstraint(
                    id=c_data["id"],
                    description=c_data["description"],
                    entities=c_data["entities"],
                    relationship=c_data["relationship"],
                    satisfied=c_data.get("satisfied")
                ))
            
            return LogicState(
                entities=data.get("entities", {}),
                constraints=constraints,
                deductions=data.get("deductions", []),
                solution_valid=data.get("solution_valid", False)
            )
            
        except Exception as e:
            logger.error(f"Logic reasoning error: {e}")
            return LogicState(
                entities={},
                constraints=[],
                deductions=["Unable to parse logic problem"],
                solution_valid=False
            )
    
    def post(self, shared: Dict[str, Any], prep_res: str, exec_res: LogicState) -> Optional[str]:
        """Store logic solution."""
        shared["logic_solution"] = exec_res
        
        # Format answer
        if exec_res.solution_valid and exec_res.deductions:
            answer = "Logic puzzle solution:\n\n"
            answer += "\n".join(exec_res.deductions)
            answer += f"\n\nFinal state: {json.dumps(exec_res.entities, indent=2)}"
            
            if shared.get("reasoning_state"):
                shared["reasoning_state"].final_answer = answer
        
        return None


# ============== Self-Reflection Nodes ==============

class SelfReflectionNode(Node):
    """Node that reflects on its own reasoning."""
    
    def prep(self, shared: Dict[str, Any]) -> ReasoningState:
        """Get current reasoning state."""
        return shared.get("reasoning_state")
    
    def exec(self, state: ReasoningState) -> List[ReflectionPoint]:
        """Reflect on reasoning so far."""
        if not state or not state.thought_history:
            return []
        
        # Select thoughts to reflect on
        thoughts_to_review = state.thought_history[-3:]  # Last 3 thoughts
        
        reflections = []
        for thought in thoughts_to_review:
            prompt = f"""Reflect on this reasoning step and identify any issues.

Problem: {state.plan.problem}
Step: {thought.content}
Result: {thought.result}
Original confidence: {thought.confidence}

Consider:
1. Is the reasoning sound?
2. Are there any logical errors?
3. Could this be improved?
4. What assumptions were made?

Return JSON reflection:
{{
  "reflection": "Your reflection on this step",
  "issues_found": ["issue 1", "issue 2"],
  "corrections_made": ["correction 1"],
  "confidence_after": 0.9
}}

Output JSON only:"""
            
            system = "You are a critical thinker reviewing reasoning steps for errors and improvements."
            
            try:
                response = call_llm(prompt, system, temperature=0.3)
                cleaned = _clean_json_response(response)
                data = json.loads(cleaned)
                
                reflection = ReflectionPoint(
                    thought_id=thought.id,
                    reflection=data.get("reflection", "No issues found"),
                    issues_found=data.get("issues_found", []),
                    corrections_made=data.get("corrections_made", []),
                    confidence_before=thought.confidence,
                    confidence_after=float(data.get("confidence_after", thought.confidence))
                )
                
                reflections.append(reflection)
                
                # Update thought confidence
                thought.confidence = reflection.confidence_after
                
            except Exception as e:
                logger.error(f"Reflection error: {e}")
        
        return reflections
    
    def post(self, shared: Dict[str, Any], prep_res: ReasoningState, 
             exec_res: List[ReflectionPoint]) -> Optional[str]:
        """Apply reflections."""
        if exec_res and shared.get("reasoning_state"):
            state = shared["reasoning_state"]
            
            # Add reflection insights
            for reflection in exec_res:
                if reflection.issues_found:
                    state.insights.append(
                        f"Reflection on {reflection.thought_id}: {', '.join(reflection.issues_found)}"
                    )
        
        return None  # Continue to next node


# ============== Multi-Path Reasoning Nodes ==============

class MultiPathReasoningNode(Node):
    """Explores multiple reasoning paths in parallel."""
    
    def prep(self, shared: Dict[str, Any]) -> str:
        """Get problem."""
        return shared.get("problem", "")
    
    def exec(self, problem: str) -> MultiPathAnalysis:
        """Explore multiple solution paths."""
        prompt = f"""Explore multiple ways to solve this problem.

Problem: {problem}

Generate 3 different approaches/paths to solve this. For each path:
1. Describe the approach
2. List the key steps
3. Estimate confidence
4. Note any concerns

Return JSON:
{{
  "paths": [
    {{
      "id": "path_1",
      "description": "Approach description",
      "steps": [
        {{
          "id": "p1_s1",
          "content": "Step description",
          "reasoning_type": "type",
          "confidence": 0.8
        }}
      ],
      "confidence": 0.7,
      "result": "Expected outcome"
    }}
  ],
  "best_path_id": "path_1",
  "consensus_answer": "If paths agree"
}}

Output JSON only:"""
        
        system = "You are exploring multiple solution paths. Be creative but logical."
        
        try:
            response = call_llm(prompt, system, temperature=0.5)
            cleaned = _clean_json_response(response)
            data = json.loads(cleaned)
            
            paths = []
            for path_data in data.get("paths", []):
                steps = []
                for step_data in path_data.get("steps", []):
                    steps.append(ThoughtStep(
                        id=step_data["id"],
                        content=step_data["content"],
                        reasoning_type=step_data.get("reasoning_type", "analysis"),
                        confidence=float(step_data.get("confidence", 0.7))
                    ))
                
                paths.append(ReasoningPath(
                    id=path_data["id"],
                    description=path_data["description"],
                    steps=steps,
                    confidence=float(path_data.get("confidence", 0.7)),
                    result=path_data.get("result")
                ))
            
            return MultiPathAnalysis(
                problem=problem,
                paths=paths,
                best_path_id=data.get("best_path_id"),
                consensus_answer=data.get("consensus_answer")
            )
            
        except Exception as e:
            logger.error(f"Multi-path error: {e}")
            # Single default path
            return MultiPathAnalysis(
                problem=problem,
                paths=[
                    ReasoningPath(
                        id="default",
                        description="Standard approach",
                        steps=[],
                        confidence=0.5
                    )
                ]
            )
    
    def post(self, shared: Dict[str, Any], prep_res: str, 
             exec_res: MultiPathAnalysis) -> Optional[str]:
        """Store multi-path analysis."""
        shared["multi_path_analysis"] = exec_res
        
        # Use best path or consensus
        answer = exec_res.consensus_answer
        if not answer and exec_res.best_path_id:
            best_path = next((p for p in exec_res.paths if p.id == exec_res.best_path_id), None)
            if best_path:
                answer = best_path.result or "See detailed analysis"
        
        if answer and shared.get("reasoning_state"):
            shared["reasoning_state"].final_answer = answer
        
        return None


# ============== Decision Making Nodes ==============

class DecisionReasoningNode(Node):
    """Structured decision-making with reasoning."""
    
    def prep(self, shared: Dict[str, Any]) -> str:
        """Get decision question."""
        return shared.get("problem", "")
    
    def exec(self, question: str) -> DecisionAnalysis:
        """Analyze decision with structured reasoning."""
        prompt = f"""Help make this decision through structured analysis.

Question: {question}

Provide:
1. Key decision options (2-4)
2. Important factors to consider
3. Pros and cons for each option
4. Scoring of options on each factor
5. Recommendation with reasoning

Return JSON:
{{
  "question": "the decision question",
  "context": "relevant context",
  "options": [
    {{
      "id": "opt1",
      "name": "Option name",
      "description": "What this option entails",
      "pros": ["pro 1", "pro 2"],
      "cons": ["con 1"],
      "factors": [
        {{
          "name": "Cost",
          "description": "Financial impact",
          "weight": 0.3,
          "score": 7.0,
          "reasoning": "Why this score"
        }}
      ],
      "total_score": 7.5
    }}
  ],
  "recommendation": "Recommended option",
  "confidence": 0.8,
  "reasoning_summary": "Why this recommendation"
}}

Output JSON only:"""
        
        system = "You are a decision analyst. Provide balanced, well-reasoned analysis."
        
        try:
            response = call_llm(prompt, system, temperature=0.3)
            cleaned = _clean_json_response(response)
            data = json.loads(cleaned)
            
            options = []
            for opt_data in data.get("options", []):
                factors = []
                for f_data in opt_data.get("factors", []):
                    factors.append(DecisionFactor(
                        name=f_data["name"],
                        description=f_data["description"],
                        weight=float(f_data.get("weight", 0.5)),
                        score=float(f_data.get("score", 5.0)),
                        reasoning=f_data.get("reasoning")
                    ))
                
                options.append(DecisionOption(
                    id=opt_data["id"],
                    name=opt_data["name"],
                    description=opt_data["description"],
                    pros=opt_data.get("pros", []),
                    cons=opt_data.get("cons", []),
                    factors=factors,
                    total_score=float(opt_data.get("total_score", 5.0))
                ))
            
            return DecisionAnalysis(
                question=data.get("question", question),
                context=data.get("context", ""),
                options=options,
                recommendation=data.get("recommendation"),
                confidence=float(data.get("confidence", 0.7)),
                reasoning_summary=data.get("reasoning_summary", "")
            )
            
        except Exception as e:
            logger.error(f"Decision analysis error: {e}")
            return DecisionAnalysis(
                question=question,
                context="",
                options=[],
                confidence=0.3,
                reasoning_summary="Unable to analyze decision"
            )
    
    def post(self, shared: Dict[str, Any], prep_res: str, 
             exec_res: DecisionAnalysis) -> Optional[str]:
        """Store decision analysis."""
        shared["decision_analysis"] = exec_res
        
        # Format recommendation
        answer = f"Decision Analysis: {exec_res.question}\n\n"
        answer += f"Recommendation: {exec_res.recommendation}\n"
        answer += f"Confidence: {exec_res.confidence:.1%}\n\n"
        answer += f"Reasoning: {exec_res.reasoning_summary}"
        
        if shared.get("reasoning_state"):
            shared["reasoning_state"].final_answer = answer
        
        return None


# ============== Output Formatting Nodes ==============

class ReasoningOutputNode(Node):
    """Formats final reasoning output."""
    
    def prep(self, shared: Dict[str, Any]) -> Dict[str, Any]:
        """Gather all reasoning results."""
        return {
            "state": shared.get("reasoning_state"),
            "math_solution": shared.get("math_solution"),
            "logic_solution": shared.get("logic_solution"),
            "decision_analysis": shared.get("decision_analysis"),
            "multi_path": shared.get("multi_path_analysis")
        }
    
    def exec(self, data: Dict[str, Any]) -> str:
        """Format comprehensive output."""
        output_parts = []
        
        # Main answer
        if data["state"] and data["state"].final_answer:
            output_parts.append(data["state"].final_answer)
        
        # Math details
        if data["math_solution"]:
            sol = data["math_solution"]
            output_parts.append("\n=== Mathematical Solution ===")
            for step in sol.steps:
                output_parts.append(
                    f"Step {step.step_number}: {step.description}"
                )
                output_parts.append(f"  {step.expression} = {step.result} {step.units or ''}")
            output_parts.append(f"\nFinal Answer: {sol.final_answer}")
        
        # Logic details
        if data["logic_solution"] and data["logic_solution"].solution_valid:
            output_parts.append("\n=== Logic Solution ===")
            output_parts.append("Deduction steps:")
            for ded in data["logic_solution"].deductions:
                output_parts.append(f"- {ded}")
        
        # Decision details
        if data["decision_analysis"] and data["decision_analysis"].options:
            output_parts.append("\n=== Decision Analysis ===")
            for opt in data["decision_analysis"].options[:3]:
                output_parts.append(f"\nOption: {opt.name}")
                output_parts.append(f"Score: {opt.total_score:.1f}/10")
                if opt.pros:
                    output_parts.append(f"Pros: {', '.join(opt.pros[:2])}")
                if opt.cons:
                    output_parts.append(f"Cons: {', '.join(opt.cons[:2])}")
        
        # Multi-path summary
        if data["multi_path"] and len(data["multi_path"].paths) > 1:
            output_parts.append("\n=== Multiple Approaches Considered ===")
            for path in data["multi_path"].paths:
                output_parts.append(f"- {path.description} (confidence: {path.confidence:.1%})")
        
        # Insights if any
        if data["state"] and data["state"].insights:
            output_parts.append("\n=== Key Insights ===")
            for insight in data["state"].insights[:5]:
                output_parts.append(f"- {insight}")
        
        return "\n".join(output_parts)
    
    def post(self, shared: Dict[str, Any], prep_res: Dict[str, Any], 
             exec_res: str) -> Optional[str]:
        """Store final output."""
        shared["final_output"] = exec_res
        return None