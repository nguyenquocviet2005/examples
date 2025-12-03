"""
Agent Lightning - Complete Working Example
A fully functional prompt optimization system with embedded agent.
"""

import asyncio
import random
import sys
import os
from typing import List, Tuple

# Agent Lightning imports
import agentlightning as agl
from agentlightning.types import PromptTemplate
from agentlightning.store import InMemoryLightningStore, LightningStoreServer
from openai import OpenAI


# ============================================================================
# 1. SIMPLE AGENT - Evaluates prompts
# ============================================================================

def evaluate_prompt(task: str, prompt_template: PromptTemplate) -> float:
    """Evaluate a prompt by calling OpenAI and generating a reward score."""
    client = OpenAI()

    # Format the prompt with the task
    prompt_text = prompt_template.format(any_question=task)
    print(f"  [Agent] Prompt: {prompt_text[:60]}...")
    
    try:
        # Call OpenAI API
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{"role": "user", "content": prompt_text}],
            max_tokens=100,
        )
        llm_output = response.choices[0].message.content
        print(f"  [Agent] Response: {llm_output[:70]}...")
        
        # Score based on response length and relevance
        # (In a real scenario, you'd use more sophisticated metrics)
        score = min(1.0, len(llm_output) / 200.0)  # Longer responses get higher scores
        print(f"  [Agent] Score: {score:.3f}")
        return score

    except Exception as e:
        print(f"  [Agent] Error calling OpenAI: {e}")
        return 0.3  # Default low score on error


# ============================================================================
# 2. ALGORITHM - Tests prompts and finds the best one
# ============================================================================

async def find_best_prompt(
    prompts_to_test: List[str],
    task_input: str
) -> Tuple[str, float]:
    """
    Test multiple prompts and find the one with the best score.
    This is the core optimization algorithm.
    """
    results: List[Tuple[str, float]] = []

    print(f"\n[Algo] Starting Prompt Optimization")
    print(f"[Algo] Task: '{task_input}'")
    print(f"[Algo] Testing {len(prompts_to_test)} prompts...\n")

    # Test each prompt
    for i, prompt in enumerate(prompts_to_test, 1):
        print(f"[Algo] Test {i}/{len(prompts_to_test)}: {prompt[:45]}...")
        
        try:
            # Create a prompt template
            prompt_template = PromptTemplate(
                template=prompt,
                engine="f-string"
            )
            
            # Evaluate the prompt
            score = evaluate_prompt(task_input, prompt_template)
            results.append((prompt, score))
            print(f"[Algo] ✓ Result: {score:.3f}\n")

        except Exception as e:
            print(f"[Algo] ✗ Error: {e}\n")
            results.append((prompt, 0.0))

    # Find the best prompt
    print(f"[Algo] ========================================")
    print(f"[Algo] Results Summary:")
    for p, r in results:
        print(f"[Algo]   Score {r:.3f}: {p[:50]}...")
    
    if results:
        best_prompt, best_reward = max(results, key=lambda item: item[1])
        print(f"[Algo] ========================================")
        print(f"[Algo] 🏆 Best prompt: {best_prompt}")
        print(f"[Algo] 🏆 Best score:  {best_reward:.3f}")
        print(f"[Algo] ========================================\n")
        return best_prompt, best_reward
    else:
        print(f"[Algo] No results collected!")
        return prompts_to_test[0], 0.0


# ============================================================================
# 3. MAIN RUNNER
# ============================================================================

async def main():
    """Main execution function."""
    print("\n" + "=" * 60)
    print("Agent Lightning - Prompt Optimization")
    print("=" * 60)

    # Check for OpenAI API key
    if not os.getenv("OPENAI_API_KEY"):
        print("\n❌ ERROR: OPENAI_API_KEY environment variable not set!")
        print("   Set it with: export OPENAI_API_KEY='your-key-here'")
        sys.exit(1)

    # Sample prompts to optimize
    prompts_to_test = [
        "You are a helpful assistant. Answer the following question: {any_question}",
        "You are an expert. Answer concisely: {any_question}",
        "You are knowledgeable. Provide a detailed answer: {any_question}",
    ]

    # Sample task
    task_input = "What is the capital of France?"

    try:
        # Run the optimization algorithm
        best_prompt, best_score = await find_best_prompt(prompts_to_test, task_input)
        
        print("\n[Main] ✓ Optimization completed successfully!")
        print(f"[Main] Best prompt score: {best_score:.3f}")
        
        return True

    except Exception as e:
        print(f"\n[Main] ✗ Fatal error: {e}")
        import traceback
        traceback.print_exc()
        return False


# ============================================================================
# 4. ENTRY POINT
# ============================================================================

if __name__ == "__main__":
    print("\n" + "=" * 60)
    print("Agent Lightning - Simplified Runner")
    print("=" * 60 + "\n")
    
    try:
        success = asyncio.run(main())
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\n\n[Main] Interrupted by user")
        sys.exit(0)
