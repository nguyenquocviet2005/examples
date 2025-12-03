"""
APO (Automatic Prompt Optimization) - Complete Working Example
Based on official Agent Lightning documentation.

This script demonstrates how to use APO to optimize prompts for an LLM agent.
"""

import asyncio
import os
import sys
from typing import TypedDict
from openai import AsyncOpenAI, OpenAI

# Agent Lightning imports
import agentlightning as agl


# ============================================================================
# 1. DEFINE TASK STRUCTURE
# ============================================================================

class QuestionTask(TypedDict):
    """A simple question-answering task."""
    question: str
    expected_keywords: list[str]  # Keywords we expect in a good answer


# ============================================================================
# 2. TEMPLATE & REWARD TRACKING (File-Based for Multi-Process Support)
# ============================================================================

import json
from pathlib import Path
from threading import Lock

# Use file-based tracking since we have 4 parallel processes
# Each process will write to this file
TRACKING_FILE = "apo_templates_tracking.json"
tracking_lock = Lock()  # Thread-safe file access

def load_tracking_data():
    """Load tracking data from file"""
    if Path(TRACKING_FILE).exists():
        with open(TRACKING_FILE, "r") as f:
            try:
                return json.load(f)
            except:
                return {"templates": [], "rewards": {}}
    return {"templates": [], "rewards": {}}

def save_tracking_data(data):
    """Save tracking data to file (thread-safe append)"""
    with tracking_lock:
        existing = load_tracking_data()
        
        # Merge templates (deduplicate)
        all_templates = list(set(existing["templates"] + data.get("templates", [])))
        
        # Merge rewards
        all_rewards = existing["rewards"]
        for template, rewards_list in data.get("rewards", {}).items():
            if template not in all_rewards:
                all_rewards[template] = []
            all_rewards[template].extend(rewards_list)
        
        # Write back
        with open(TRACKING_FILE, "w") as f:
            json.dump({
                "templates": all_templates,
                "rewards": all_rewards
            }, f, indent=2)

def track_template(template_str: str):
    """File-based template tracking"""
    data = load_tracking_data()
    if template_str not in data["templates"]:
        data["templates"].append(template_str)
        save_tracking_data(data)

def track_reward(template_str: str, reward_score: float):
    """File-based reward tracking"""
    data = load_tracking_data()
    if template_str not in data["rewards"]:
        data["rewards"][template_str] = []
    data["rewards"][template_str].append(reward_score)
    save_tracking_data(data)


# ============================================================================
# 3. DEFINE THE AGENT USING @rollout DECORATOR
# ============================================================================

@agl.rollout
def qa_agent(task: QuestionTask, prompt_template: agl.PromptTemplate) -> float:
    """
    A simple Q&A agent that uses the provided prompt template.
    
    Args:
        task: The question task to solve
        prompt_template: The prompt template being optimized by APO
        
    Returns:
        A reward score (0.0 to 1.0) based on response quality
    """
    # Log the template being used (highlight it!)
    print("\n" + "="*70)
    print("🔥 TEMPLATE BEING TESTED:")
    print("="*70)
    print(f"\033[93m{prompt_template.template}\033[0m")  # Yellow color
    print("="*70 + "\n")
    
    # Track unique templates (thread-safe)
    track_template(prompt_template.template)
    
    # 1. Format the prompt with the task
    # Use safe formatting that handles any template variables APO might add
    import string
    try:
        template_vars = [fname for _, fname, _, _ in string.Formatter().parse(prompt_template.template) if fname]
        format_kwargs = {"question": task["question"]}
        
        # Add default values for any other variables APO might have added
        for var in template_vars:
            if var not in format_kwargs:
                format_kwargs[var] = ""  # Default to empty string for unknown variables
        
        prompt = prompt_template.format(**format_kwargs)
    except (KeyError, ValueError) as e:
        # If the template has invalid formatting, fall back to simple replacement
        print(f"[Agent] ⚠️  Warning: Template formatting failed ({e}), using fallback")
        prompt = prompt_template.template.replace("{question}", task["question"])
        # Remove any remaining template variables
        for match in string.Formatter().parse(prompt):
            if match[1] is not None:
                prompt = prompt.replace("{" + match[1] + "}", "")
    
    # 2. Call OpenAI API
    client = OpenAI()
    try:
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{"role": "user", "content": prompt}],
            max_tokens=150,
        )
        answer = response.choices[0].message.content
        print(f"[Agent] 📝 Q: {task['question'][:50]}...")
        print(f"[Agent] 💬 A: {answer[:80]}...")
        
        # 3. Calculate reward based on expected keywords
        reward = calculate_reward(answer, task["expected_keywords"])
        
        # Color code the reward: green for high, yellow for medium, red for low
        if reward >= 0.8:
            color = "\033[92m"  # Green
            emoji = "✅"
        elif reward >= 0.5:
            color = "\033[93m"  # Yellow
            emoji = "⚡"
        else:
            color = "\033[91m"  # Red
            emoji = "❌"
        
        print(f"[Agent] {emoji} Reward: {color}{reward:.3f}\033[0m\n")
        
        # Track rewards for each template (thread-safe)
        track_reward(prompt_template.template, reward)
        
        return reward
        
    except Exception as e:
        print(f"[Agent] Error: {e}")
        return 0.0


def calculate_reward(answer: str, expected_keywords: list[str]) -> float:
    """
    Score the answer based on keyword presence and length.
    
    Returns a float between 0.0 and 1.0.
    """
    answer_lower = answer.lower()
    
    # Check keyword coverage
    keyword_score = sum(
        1 for keyword in expected_keywords 
        if keyword.lower() in answer_lower
    ) / max(len(expected_keywords), 1)
    
    # Bonus for detailed answers (but cap it)
    length_score = min(1.0, len(answer) / 200.0)
    
    # Weighted combination
    final_score = keyword_score * 0.7 + length_score * 0.3
    
    return min(1.0, final_score)


# ============================================================================
# 3. BASELINE PROMPT
# ============================================================================

def baseline_prompt() -> agl.PromptTemplate:
    """The starting prompt that APO will optimize."""
    return agl.PromptTemplate(
        template="Answer this question: {question}",
        engine="f-string"
    )


# ============================================================================
# 4. CREATE DATASETS
# ============================================================================

def create_datasets():
    """Create training and validation datasets."""
    
    train_dataset = [
        QuestionTask(
            question="What is the capital of France?",
            expected_keywords=["Paris", "France"]
        ),
        QuestionTask(
            question="What is photosynthesis?",
            expected_keywords=["photosynthesis", "plants", "light", "oxygen", "carbon dioxide"]
        ),
        QuestionTask(
            question="Who wrote Romeo and Juliet?",
            expected_keywords=["Shakespeare", "William"]
        ),
        QuestionTask(
            question="What is the speed of light?",
            expected_keywords=["speed", "light", "meters", "second", "299792458"]
        ),
        QuestionTask(
            question="What is machine learning?",
            expected_keywords=["machine learning", "data", "algorithms", "patterns"]
        ),
    ]
    
    val_dataset = [
        QuestionTask(
            question="What is the largest ocean?",
            expected_keywords=["Pacific", "ocean"]
        ),
        QuestionTask(
            question="What is DNA?",
            expected_keywords=["DNA", "genetic", "molecule", "hereditary"]
        ),
        QuestionTask(
            question="Who painted the Mona Lisa?",
            expected_keywords=["Leonardo", "da Vinci"]
        ),
    ]
    
    return train_dataset, val_dataset


# ============================================================================
# 5. MAIN TRAINING FUNCTION
# ============================================================================

# ============================================================================
# 5. MAIN TRAINING FUNCTION
# ============================================================================

def main():
    """Main training function"""
    print("\n" + "=" * 70)
    print("APO (Automatic Prompt Optimization) Training")
    print("=" * 70 + "\n")
    
    # Clean up old tracking file to start fresh
    if Path(TRACKING_FILE).exists():
        Path(TRACKING_FILE).unlink()
    
    # Check API key
    if not os.getenv("OPENAI_API_KEY"):
        print("❌ ERROR: OPENAI_API_KEY not set!")
        print("   Set it with: export OPENAI_API_KEY='your-key'")
        return False
    
    print("[Setup] Creating datasets...")
    train_dataset, val_dataset = create_datasets()
    print(f"[Setup] Training samples: {len(train_dataset)}")
    print(f"[Setup] Validation samples: {len(val_dataset)}\n")
    
    # Initialize OpenAI client for APO
    print("[Setup] Initializing APO algorithm...")
    openai_client = AsyncOpenAI()
    
    # Create APO algorithm
    algo = agl.APO(
        openai_client,
        # Hyperparameters for APO
        val_batch_size=3,          # Evaluate 3 samples per validation
        gradient_batch_size=2,      # Use 2 samples to compute gradient
        beam_width=2,               # Keep top 2 prompts
        branch_factor=2,            # Generate 2 variations per prompt
        beam_rounds=1,              # Run 1 round of optimization
    )
    
    print("[Setup] ✓ APO initialized")
    print(f"[Setup] Configuration:")
    print(f"  - val_batch_size: 3")
    print(f"  - gradient_batch_size: 2")
    print(f"  - beam_width: 2")
    print(f"  - branch_factor: 2")
    print(f"  - beam_rounds: 1\n")
    
    # Create trainer
    print("[Setup] Creating Trainer...")
    trainer = agl.Trainer(
        algorithm=algo,
        n_runners=4,  # Use 4 parallel runners
        initial_resources={
            "prompt_template": baseline_prompt()
        },
        adapter=agl.TraceToMessages(),
    )
    print("[Setup] ✓ Trainer created with 4 parallel runners\n")
    
    # Display baseline prompt
    print("[Baseline] Initial prompt:")
    print(f"  '{baseline_prompt().template}'\n")
    
    # Start training
    print("=" * 70)
    print("Starting APO Training...")
    print("=" * 70 + "\n")
    
    try:
        trainer.fit(
            agent=qa_agent,
            train_dataset=train_dataset,
            val_dataset=val_dataset,
        )
        
        print("\n" + "=" * 70)
        print("✅ Training Complete!")
        print("=" * 70)
        
        # Load tracking data from file (populated by parallel workers)
        tracking_data = load_tracking_data()
        templates_tested = tracking_data["templates"]
        rewards_by_template = tracking_data["rewards"]
        
        # Show summary of templates tested
        print(f"\n📊 Summary: {len(templates_tested)} unique templates were tested during training:")
        print("=" * 70)
        for i, template in enumerate(templates_tested, 1):
            print(f"\n\033[96mTemplate {i}:\033[0m")  # Cyan color
            print(f"\033[93m{template}\033[0m")  # Yellow color
            
            # Calculate average reward for this template
            if template in rewards_by_template:
                avg_reward = sum(rewards_by_template[template]) / len(rewards_by_template[template])
                max_reward = max(rewards_by_template[template])
                print(f"  📈 Avg Reward: {avg_reward:.3f} | Max Reward: {max_reward:.3f} | Tested: {len(rewards_by_template[template])} times")
        
        # Find and display the best template
        if rewards_by_template:
            best_template = max(
                rewards_by_template.items(),
                key=lambda x: max(x[1])
            )
            best_template_str, best_rewards = best_template
            best_score = max(best_rewards)
            
            print("\n" + "=" * 70)
            print("🏆 BEST PROMPT FOUND:")
            print("=" * 70)
            print(f"\033[92m{best_template_str}\033[0m")  # Green color
            print(f"\n✨ Best Reward Score: \033[92m{best_score:.3f}\033[0m")
            print("=" * 70 + "\n")
        
        return True
        
    except Exception as e:
        print(f"\n❌ Training failed: {e}")
        import traceback
        traceback.print_exc()
        return False


# ============================================================================
# 6. ENTRY POINT
# ============================================================================

if __name__ == "__main__":
    print("\n" + "=" * 70)
    print("Agent Lightning - APO Training Script")
    print("=" * 70 + "\n")
    
    try:
        success = main()
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\n\n[Main] Training interrupted by user")
        sys.exit(0)
