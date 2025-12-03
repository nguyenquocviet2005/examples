def simple_agent(task: str, prompt_template: PromptTemplate) -> float:
    """An agent that answers a question and gets judged by an LLM."""
    client = OpenAI()

    # Generate a response using the provided prompt template
    prompt = prompt_template.format(any_question=task)
    response = client.chat.completions.create(
        model="gpt-4.1-nano", messages=[{"role": "user", "content": prompt}]
    )
    llm_output = response.choices[0].message.content
    print(f"[Rollout] LLM returned: {llm_output}")

    # This llm_output and the final score are automatically logged as spans by the Tracer
    score = random.uniform(0, 1)  # Replace with actual scoring logic if needed
    return score

async def find_best_prompt(store, prompts_to_test, task_input):
    """A simple algorithm to find the best prompt from a list."""
    results = []

    # Iterate through each prompt to test it
    for prompt in prompts_to_test:
        print(f"[Algo] Updating prompt template to: '{prompt}'")

        # 1. Update the resources in the store with the new prompt
        resources_update = await store.add_resources(
            resources={"prompt_template": prompt}
        )

        # 2. Enqueue a rollout task for a runner to execute
        print("[Algo] Queuing task for clients...")
        rollout = await store.enqueue_rollout(
            input=task_input,
            resources_id=resources_update.resources_id,
        )
        print(f"[Algo] Task '{rollout.rollout_id}' is now available for clients.")

        # 3. Wait for the rollout to be completed by a runner
        await store.wait_for_rollouts([rollout.rollout_id])

        # 4. Query the completed rollout and its spans
        completed_rollout = (await store.query_rollouts([rollout.rollout_id]))[0]
        print(f"[Algo] Received Result: {completed_rollout.model_dump_json(indent=None)}")

        spans = await store.query_spans(rollout.rollout_id)
        # We expect at least two spans: one for the LLM call and one for the final reward
        print(f"[Algo] Queried Spans:\n  - " + "\n  - ".join(str(span) for span in spans))
        # find_final_reward is a helper function to extract the reward span
        final_reward = find_final_reward(spans)
        print(f"[Algo] Final reward: {final_reward}\n")

        results.append((prompt, final_reward))

    # 5. Find and print the best prompt based on the collected rewards
    print(f"[Algo] All prompts and their rewards: {results}")
    best_prompt, best_reward = max(results, key=lambda item: item[1])
    print(f"[Algo] Best prompt found: '{best_prompt}' with reward {best_reward}")

# Connecting to Store
store = agl.LightningStoreClient("http://localhost:4747")  # or some other address
runner = LitAgentRunner[str](tracer=AgentOpsTracer())
with runner.run_context(agent=simple_agent, store=store):  # <-- where the wrapping and instrumentation happens
    await runner.iter()  # polling for new tasks forever