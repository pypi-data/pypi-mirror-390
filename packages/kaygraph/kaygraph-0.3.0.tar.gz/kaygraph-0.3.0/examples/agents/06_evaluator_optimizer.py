"""
Example 6: Evaluator-Optimizer (Iterative Translation Refinement)

This example shows iterative refinement where:
- Generator creates initial output
- Evaluator provides specific feedback
- Generator refines based on feedback
- Process repeats until quality threshold met

Pattern: Generate → Evaluate → Refine → Evaluate → ... → Accept
"""

import asyncio
from kaygraph.agent import create_evaluator_optimizer


# =============================================================================
# MOCK LLM
# =============================================================================

iteration_state = {"count": 0, "quality_score": 5}


async def mock_llm(messages):
    """Mock LLM that simulates generation and evaluation"""
    iteration_state["count"] += 1

    # Determine if this is generation or evaluation
    system_prompt = ""
    for msg in messages:
        if msg["role"] == "system":
            system_prompt = msg["content"].lower()
            break

    # GENERATION
    if "translate" in system_prompt or "write" in system_prompt:
        if iteration_state["count"] == 1:
            # First draft - okay but needs work
            return {"content": """La casa vieja estaba sola en la colina,
sus ventanas oscuras mirando el valle abajo. Nadie había vivido allí
por muchos años."""}
        elif iteration_state["count"] == 3:
            # Second draft - better
            return {"content": """La vieja casa se alzaba solitaria sobre la colina,
sus ventanas oscuras contemplaban el valle en la penumbra. Nadie había
habitado entre sus muros durante años, y el silencio pesaba sobre ella
como un manto."""}
        else:
            # Final draft - polished
            return {"content": """La casa ancestral se erguía solitaria en lo alto de la colina,
sus ventanas oscuras como ojos ciegos contemplando el valle sumido en sombras.
Durante años nadie había habitado entre sus muros agrietados, y un silencio
sepulcral pesaba sobre ella como un manto de olvido."""}

    # EVALUATION
    else:
        if iteration_state["count"] == 2:
            # First evaluation - needs improvement
            iteration_state["quality_score"] = 6
            return {"content": """Evaluation:
- Accuracy: 7/10 (correct translation but literal)
- Fluency: 5/10 (choppy, unnatural flow)
- Cultural adaptation: 5/10 (too literal, lacks Spanish literary style)
- Emotional resonance: 6/10 (conveys meaning but not atmosphere)

Overall score: 6/10

Specific feedback:
1. Use more evocative vocabulary ("ancestral" vs "vieja")
2. Improve sentence flow - too choppy
3. Add literary devices appropriate for Spanish (personification, metaphor)
4. Enhance atmospheric elements"""}
        elif iteration_state["count"] == 4:
            # Second evaluation - getting better
            iteration_state["quality_score"] = 8
            return {"content": """Evaluation:
- Accuracy: 9/10 (excellent preservation of meaning)
- Fluency: 8/10 (much better flow, natural Spanish)
- Cultural adaptation: 7/10 (good but can be more evocative)
- Emotional resonance: 8/10 (captures mood well)

Overall score: 8/10

Specific feedback:
1. Excellent improvement in flow and vocabulary
2. Good use of literary devices
3. Minor: Could enhance the final metaphor
4. Consider stronger emotional imagery in conclusion"""}
        else:
            # Final evaluation - excellent
            iteration_state["quality_score"] = 9
            return {"content": """Evaluation:
- Accuracy: 10/10 (perfect preservation of meaning)
- Fluency: 9/10 (natural, literary Spanish)
- Cultural adaptation: 9/10 (appropriate cultural nuances)
- Emotional resonance: 10/10 (powerful atmospheric quality)

Overall score: 9/10

This translation successfully captures both the literal meaning and the
atmospheric, haunting quality of the original. The use of "ancestral,"
"erguía," and "manto de olvido" shows excellent command of literary Spanish.
Ready for publication."""}


# =============================================================================
# RUN EVALUATOR-OPTIMIZER
# =============================================================================

async def main():
    print("=" * 70)
    print("Evaluator-Optimizer Example: Literary Translation Refinement")
    print("=" * 70)
    print()

    # Original text to translate
    original_text = """The old house stood alone on the hill, its dark windows
staring down at the valley below. No one had lived there for years."""

    print("Original Text:")
    print("-" * 70)
    print(original_text)
    print()

    # Create evaluator-optimizer agent
    agent = create_evaluator_optimizer(
        llm_func=mock_llm,
        generation_prompt="""Translate the following English text to Spanish.
Focus on:
- Literary quality
- Cultural adaptation
- Maintaining emotional tone
- Natural Spanish expression""",
        evaluation_criteria="""Rate the Spanish translation on:
1. Accuracy (1-10) - Preserves original meaning
2. Fluency (1-10) - Natural Spanish flow
3. Cultural adaptation (1-10) - Appropriate for Spanish readers
4. Emotional resonance (1-10) - Captures original atmosphere

Provide overall score and specific feedback for improvement.""",
        max_iterations=3
    )

    print("✓ Created evaluator-optimizer agent")
    print()

    print("Starting iterative refinement process...")
    print("=" * 70)
    print()

    # Run the refinement loop
    result = await agent.run_interactive_async(
        shared={
            "user_input": original_text
        },
        max_iterations=6  # 3 generate + 3 evaluate cycles
    )

    # Display final result
    print()
    print("=" * 70)
    print("FINAL RESULT")
    print("=" * 70)
    print()
    print("Final Translation:")
    print("-" * 70)
    print(result.get("generated_response", "No final output"))
    print()

    print(f"Total iterations: {iteration_state['count']}")
    print(f"Final quality score: {iteration_state['quality_score']}/10")
    print()


# =============================================================================
# SHOW COMPARISON WITH OTHER PATTERNS
# =============================================================================

def show_use_cases():
    print("=" * 70)
    print("When to Use Evaluator-Optimizer")
    print("=" * 70)
    print()

    print("✓ IDEAL FOR:")
    print("  - Literary translation")
    print("  - Creative writing")
    print("  - Code optimization")
    print("  - Comprehensive reports")
    print("  - Design refinement")
    print()

    print("✗ NOT GOOD FOR:")
    print("  - Simple tasks (use single LLM call)")
    print("  - Fixed-step processes (use prompt chaining)")
    print("  - Tasks without clear evaluation criteria")
    print()

    print("KEY REQUIREMENT:")
    print("  Must have CLEAR evaluation criteria")
    print("  Improvement must be POSSIBLE from feedback")
    print()

    print("COST CONSIDERATION:")
    print("  - Each iteration = 2 LLM calls (generate + evaluate)")
    print("  - Max iterations × 2 = total cost multiplier")
    print("  - Trade cost for higher quality output")
    print()


# =============================================================================
# ALTERNATIVE: CUSTOM EVALUATION LOGIC
# =============================================================================

async def with_custom_evaluator():
    """Example with automated quality checks"""
    print("=" * 70)
    print("Alternative: Automated Quality Evaluation")
    print("=" * 70)
    print()

    def automated_quality_check(text: str) -> tuple[float, str]:
        """Custom evaluation logic without LLM"""
        score = 0.0
        feedback = []

        # Check 1: Length
        word_count = len(text.split())
        if word_count >= 50:
            score += 2.5
        else:
            feedback.append("Too short - needs more detail")

        # Check 2: Complexity
        avg_word_length = sum(len(w) for w in text.split()) / max(word_count, 1)
        if avg_word_length > 5:
            score += 2.5
        else:
            feedback.append("Use more sophisticated vocabulary")

        # Check 3: Structure
        if text.count(".") >= 3:
            score += 2.5
        else:
            feedback.append("Needs better sentence structure")

        # Check 4: Literary devices
        literary_words = ["ancestral", "contemplaban", "silencio", "manto"]
        if any(word in text.lower() for word in literary_words):
            score += 2.5

        return (score, " | ".join(feedback) if feedback else "Good quality")

    print("This approach:")
    print("  ✓ Faster (no LLM for evaluation)")
    print("  ✓ Cheaper (only generation uses LLM)")
    print("  ✓ Consistent (rule-based criteria)")
    print("  ✗ Less nuanced than LLM evaluation")
    print()


if __name__ == "__main__":
    asyncio.run(main())
    show_use_cases()
    # asyncio.run(with_custom_evaluator())
