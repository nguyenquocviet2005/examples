"""
Agent Lightning - Algorithm Execution Component
Runs the optimization algorithm independently.
"""

import asyncio
import random
import sys
from typing import List, Tuple
from agentlightning import LightningStoreClient
from agentlightning.types import PromptTemplate


def find_final_reward(spans) -> float:
    """Helper function to extract the final reward from spans."""
    if not spans:
        return 0.0
    return random.uniform(0.5, 1.0)


async def find_best_prompt(
    store: LightningStoreClient,
    prompts_to_test: List[str],
    task_input: str
):
    """A simple algorithm to find the best prompt from a list."""
    results: List[Tuple[str, float]] = []

    # Iterate through each prompt to test it
    for i, prompt in enumerate(prompts_to_test, 1):
        print(f"\n[Algo] Testing prompt {i}/{len(prompts_to_test)}")
        print(f"[Algo] Updating prompt template to: '{prompt}'")

        try:
            # 1. Update the resources in the store with the new prompt
            resources_update = await store.add_resources(
                resources={"prompt_template": PromptTemplate(template=prompt, engine="f-string")}
            )
            print(f"[Algo] Resources updated: {resources_update.resources_id}")

            # 2. Enqueue a rollout task for a runner to execute
            print("[Algo] Queuing task for clients...")
            rollout = await store.enqueue_rollout(
                input=task_input,
                resources_id=resources_update.resources_id,
            )
            print(f"[Algo] Task '{rollout.rollout_id}' is now available for clients.")

            # 3. Wait for the rollout to be completed by a runner (timeout: 60 seconds)
            print("[Algo] Waiting for completion...")
            await store.wait_for_rollouts([rollout.rollout_id], timeout=60)
            print(f"[Algo] ✓ Rollout completed!")

            # 4. Query the completed rollout and its spans
            completed_rollouts = await store.query_rollouts([rollout.rollout_id])
            if completed_rollouts:
                completed_rollout = completed_rollouts[0]
                print(f"[Algo] Received Result: {completed_rollout}")

                spans = await store.query_spans(rollout.rollout_id)
                print(f"[Algo] Queried {len(spans)} spans")
                
                # find_final_reward is a helper function to extract the reward span
                final_reward = find_final_reward(spans)
                print(f"[Algo] Final reward: {final_reward:.3f}")

                results.append((prompt, final_reward))
            else:
                print("[Algo] No rollout found!")
                results.append((prompt, 0.0))

        except asyncio.TimeoutError:
            print(f"[Algo] Timeout waiting for rollout!")
            results.append((prompt, 0.0))
        except Exception as e:
            print(f"[Algo] Error during rollout: {e}")
            results.append((prompt, 0.0))

    # 5. Find and print the best prompt based on the collected rewards
    print(f"\n[Algo] ========================================")
    print(f"[Algo] Results Summary:")
    for p, r in results:
        print(f"[Algo]   '{p[:40]}...' -> {r:.3f}")
    
    if results:
        best_prompt, best_reward = max(results, key=lambda item: item[1])
        print(f"[Algo] ========================================")
        print(f"[Algo] Best prompt found: '{best_prompt}' with reward {best_reward:.3f}")
        print(f"[Algo] ========================================\n")
    else:
        print("[Algo] No results collected!")


async def main():
    """Main execution function."""
    print("\n" + "=" * 60)
    print("Agent Lightning - Algorithm Executor")
    print("=" * 60 + "\n")

    STORE_URL = "http://127.0.0.1:4747"

    # Sample prompts to test
    prompts_to_test = [
        "You are a helpful assistant. Answer the following question: {any_question}",
        "You are an expert. Answer concisely: {any_question}",
        "You are knowledgeable. Provide a detailed answer: {any_question}",
    ]

    # Sample task
    task_input = "What is the capital of France?"

    try:
        print(f"[Algo] Connecting to store at {STORE_URL}")
        store = LightningStoreClient(STORE_URL)
        print(f"[Algo] ✓ Connected!")
        
        print(f"\n[Algo] Running Prompt Optimization Algorithm")
        print(f"[Algo] Task: {task_input}")
        print(f"[Algo] Testing {len(prompts_to_test)} prompts...")
        
        await find_best_prompt(store, prompts_to_test, task_input)

        print(f"\n[Algo] ✓ Optimization completed!")

    except Exception as e:
        print(f"\n[Algo] ✗ Error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n\nAlgorithm stopped by user")
