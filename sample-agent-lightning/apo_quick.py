"""
APO - Quick Start Version
Simplified script to quickly test APO with minimal setup.
"""

import os
import sys
from typing import TypedDict
from openai import AsyncOpenAI, OpenAI
import agentlightning as agl


# Task definition
class SimpleTask(TypedDict):
    question: str
    keywords: list[str]


# The agent
@agl.rollout
def simple_qa(task: SimpleTask, prompt_template: agl.PromptTemplate) -> float:
    """Simple Q&A agent."""
    prompt = prompt_template.format(question=task["question"])
    
    client = OpenAI()
    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{"role": "user", "content": prompt}],
        max_tokens=100,
    )
    answer = response.choices[0].message.content
    
    # Score based on keywords
    score = sum(
        1 for kw in task["keywords"] 
        if kw.lower() in answer.lower()
    ) / len(task["keywords"])
    
    print(f"Q: {task['question']}")
    print(f"A: {answer[:60]}...")
    print(f"Score: {score:.2f}\n")
    
    return score


# Main
def main():
    if not os.getenv("OPENAI_API_KEY"):
        print("❌ Set OPENAI_API_KEY first!")
        return
    
    print("🚀 Starting APO Training...\n")
    
    # Datasets
    train = [
        SimpleTask(question="What is the capital of France?", keywords=["Paris"]),
        SimpleTask(question="What is DNA?", keywords=["genetic", "molecule"]),
    ]
    
    val = [
        SimpleTask(question="Who painted Mona Lisa?", keywords=["Leonardo", "da Vinci"]),
    ]
    
    # APO setup
    algo = agl.APO(
        AsyncOpenAI(),
        val_batch_size=1,
        gradient_batch_size=1,
        beam_width=1,
        branch_factor=1,
        beam_rounds=1,
    )
    
    # Trainer
    trainer = agl.Trainer(
        algorithm=algo,
        n_runners=2,
        initial_resources={
            "prompt_template": agl.PromptTemplate(
                template="Answer this question: {question}",
                engine="f-string"
            )
        },
        adapter=agl.TraceToMessages(),
    )
    
    # Train!
    print("Training...")
    trainer.fit(agent=simple_qa, train_dataset=train, val_dataset=val)
    print("\n✅ Done!")


if __name__ == "__main__":
    main()
