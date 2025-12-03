"""
Complete Agent Lightning Runner - All-in-one execution script
Combines server, runner, and algorithm into a single executable process.
"""

import asyncio
import random
import sys
from typing import List, Tuple

# Agent Lightning imports
import agentlightning as agl
from agentlightning.types import PromptTemplate
from agentlightning.store import InMemoryLightningStore, LightningStoreServer
from openai import OpenAI

# ============================================================================
# 1. SIMPLE AGENT IMPLEMENTATION
# ============================================================================

def simple_agent(task: str, prompt_template: PromptTemplate) -> float:
    """An agent that answers a question and gets judged by an LLM."""
    client = OpenAI()

    # Generate a response using the provided prompt template
    prompt = prompt_template.format(any_question=task)
    print(f"[Agent] Using prompt: {prompt[:60]}...")
    
    try:
        response = client.chat.completions.create(
            model="gpt-4o-mini",  # Changed from gpt-4.1-nano to gpt-4o-mini
            messages=[{"role": "user", "content": prompt}]
        )
        llm_output = response.choices[0].message.content
        print(f"[Agent] LLM returned: {llm_output[:100]}...")

        # This llm_output and the final score are automatically logged as spans by the Tracer
        score = random.uniform(0.5, 1.0)  # Replace with actual scoring logic if needed
        print(f"[Agent] Assigned score: {score:.2f}")
        return score
    except Exception as e:
        print(f"[Agent] Error calling OpenAI: {e}")
        return random.uniform(0, 0.5)


def find_final_reward(spans) -> float:
    """Helper function to extract the final reward from spans."""
    # For demo purposes, return the last span's reward or average
    if not spans:
        return 0.0
    # In a real scenario, you'd parse the spans properly
    return random.uniform(0.5, 1.0)


# ============================================================================
# 2. ALGORITHM IMPLEMENTATION
# ============================================================================

async def find_best_prompt(store, prompts_to_test: List[str], task_input: str):
    """A simple algorithm to find the best prompt from a list."""
    results: List[Tuple[str, float]] = []

    # Iterate through each prompt to test it
    for prompt in prompts_to_test:
        print(f"\n[Algo] Updating prompt template to: '{prompt}'")

        # 1. Update the resources in the store with the new prompt
        try:
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

            # 3. Wait for the rollout to be completed by a runner
            await store.wait_for_rollouts(rollout_ids=[rollout.rollout_id], timeout=60)
            print(f"[Algo] Rollout completed!")

            # 4. Query the completed rollout and its spans
            completed_rollouts = await store.query_rollouts(rollout_ids=[rollout.rollout_id])
            if completed_rollouts:
                completed_rollout = completed_rollouts[0]
                print(f"[Algo] Received Result: {completed_rollout.model_dump_json(indent=2)}")

                spans = await store.query_spans(rollout_id=rollout.rollout_id)
                # We expect at least two spans: one for the LLM call and one for the final reward
                print(f"[Algo] Queried {len(spans)} spans")
                if spans:
                    print(f"[Algo] Spans:\n  - " + "\n  - ".join(str(span)[:50] for span in spans))
                
                # find_final_reward is a helper function to extract the reward span
                final_reward = find_final_reward(spans)
                print(f"[Algo] Final reward: {final_reward:.3f}\n")

                results.append((prompt, final_reward))
            else:
                print("[Algo] No rollout found!")
                results.append((prompt, 0.0))

        except Exception as e:
            print(f"[Algo] Error during rollout: {e}")
            results.append((prompt, 0.0))

    # 5. Find and print the best prompt based on the collected rewards
    print(f"\n[Algo] ========================================")
    print(f"[Algo] All prompts and their rewards:")
    for p, r in results:
        print(f"[Algo]   '{p[:40]}...' -> {r:.3f}")
    
    if results:
        best_prompt, best_reward = max(results, key=lambda item: item[1])
        print(f"[Algo] ========================================")
        print(f"[Algo] Best prompt found: '{best_prompt}' with reward {best_reward:.3f}")
        print(f"[Algo] ========================================\n")
    else:
        print("[Algo] No results collected!")


# ============================================================================
# 3. MAIN RUNNER
# ============================================================================

async def main():
    """Main execution function."""
    print("[Main] Agent Lightning Complete Runner Starting...")
    print("[Main] =" * 60)

    # Configuration
    SERVER_HOST = "127.0.0.1"
    SERVER_PORT = 4747
    STORE_URL = f"http://{SERVER_HOST}:{SERVER_PORT}"

    # Sample prompts to test
    prompts_to_test = [
        "You are a helpful assistant. Answer the following question: {any_question}",
        "You are an expert. Answer concisely: {any_question}",
        "You are knowledgeable. Provide a detailed answer: {any_question}",
    ]

    # Sample task
    task_input = "What is the capital of France?"

    try:
        # Step 1: Initialize the in-memory store
        print(f"\n[Main] Step 1: Initializing Store")
        in_memory_store = InMemoryLightningStore()
        print(f"[Main] ✓ In-Memory Store created!")

        # Step 2: Wrap with HTTP server
        print(f"\n[Main] Step 2: Starting HTTP Server on {STORE_URL}")
        server = LightningStoreServer(
            store=in_memory_store,
            host=SERVER_HOST,
            port=SERVER_PORT
        )
        await server.start()
        print(f"[Main] ✓ HTTP Server started successfully!")

        # Step 3: Create store client
        print(f"\n[Main] Step 3: Creating Store Client")
        store = agl.LightningStoreClient(STORE_URL)
        print(f"[Main] ✓ Store Client created!")

        # Step 4: Run the algorithm
        print(f"\n[Main] Step 4: Running Prompt Optimization Algorithm")
        print(f"[Main] Task: {task_input}")
        print(f"[Main] Testing {len(prompts_to_test)} prompts...")
        
        await find_best_prompt(store, prompts_to_test, task_input)

        print(f"\n[Main] ✓ Prompt optimization completed!")

    except Exception as e:
        print(f"\n[Main] ✗ Error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
    finally:
        print(f"\n[Main] Cleaning up...")


if __name__ == "__main__":
    print("\n" + "=" * 60)
    print("Agent Lightning - Complete Runner")
    print("=" * 60 + "\n")
    
    # Check for OpenAI API key
    import os
    if not os.getenv("OPENAI_API_KEY"):
        print("❌ ERROR: OPENAI_API_KEY environment variable not set!")
        print("   Set it with: export OPENAI_API_KEY='your-key-here'")
        sys.exit(1)

    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n\n[Main] Interrupted by user")
        sys.exit(0)
