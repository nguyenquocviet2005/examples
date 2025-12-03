"""
Agent Lightning - Agent Runner Component
Connects to the training server and executes tasks.
"""

import asyncio
import os
import sys
import random
from agentlightning import LitAgentRunner, AgentOpsTracer
from agentlightning.types import PromptTemplate
from openai import OpenAI


class SimpleAgent:
    """Simple agent that answers questions using prompts."""

    def __init__(self):
        self.client = OpenAI()

    async def training_rollout(self, task, rollout_id, resources):
        """Execute a single training rollout."""
        print(f"\n[Runner] Processing rollout {rollout_id}")

        # Extract prompt template from resources
        prompt_template = resources.get("prompt_template")
        if not prompt_template:
            print(f"[Runner] No prompt template in resources!")
            return 0.0

        # Format the prompt with the task
        if isinstance(prompt_template, PromptTemplate):
            prompt_text = prompt_template.format(any_question=task)
        else:
            prompt_text = str(prompt_template).format(any_question=task)

        print(f"[Runner] Task: {task}")
        print(f"[Runner] Prompt: {prompt_text[:60]}...")

        try:
            # Call OpenAI API
            response = self.client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[{"role": "user", "content": prompt_text}]
            )
            llm_output = response.choices[0].message.content
            print(f"[Runner] LLM Response: {llm_output[:100]}...")

            # Generate a reward score
            score = random.uniform(0.5, 1.0)
            print(f"[Runner] Score: {score:.2f}")
            return score

        except Exception as e:
            print(f"[Runner] ✗ Error: {e}")
            return random.uniform(0, 0.5)


async def main():
    """Start the agent runner."""
    print("\n" + "=" * 60)
    print("Agent Lightning - Agent Runner")
    print("=" * 60 + "\n")

    # Check API key
    if not os.getenv("OPENAI_API_KEY"):
        print("❌ ERROR: OPENAI_API_KEY environment variable not set!")
        sys.exit(1)

    STORE_URL = "http://127.0.0.1:4747"

    print(f"[Runner] Connecting to store at {STORE_URL}")
    print(f"[Runner] Waiting for tasks...\n")

    try:
        agent = SimpleAgent()
        runner = LitAgentRunner(
            tracer=AgentOpsTracer(),
            store_url=STORE_URL,
        )

        # This will block and continuously poll for tasks
        await runner.run(agent.training_rollout)

    except KeyboardInterrupt:
        print(f"\n[Runner] Shutting down...")
    except Exception as e:
        print(f"[Runner] ✗ Error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\nRunner stopped by user")
