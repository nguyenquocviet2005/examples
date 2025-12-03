# APO Storage Summary - Quick Answer

## TL;DR - How APO Selects the Best Prompt

### The Selection Algorithm
```python
best_prompt = max(prompt_and_rewards, key=lambda x: x[1])
```

**In Plain English:** 
APO picks the prompt that achieved the highest reward score out of all templates tested.

---

## Where Prompts Are Stored

### During Training (In Memory)
```python
templates_tested = []              # All unique prompts tried
rewards_by_template = {}           # Each prompt → list of rewards
```

These are **Python global variables** in your script. They're updated during training as APO tests new prompts.

### After Training (Nowhere by Default)
⚠️ **Important**: The prompts are NOT automatically saved to disk. They're lost when the script ends!

**To keep them**, save to a file:
```python
import json

best_template = max(
    rewards_by_template.items(),
    key=lambda x: max(x[1])
)[0]

with open("best_prompt.json", "w") as f:
    json.dump({"template": best_template}, f)
```

### Inside APO (Hidden)
The APO algorithm internally maintains:
- **Beam**: Top N prompts by reward
- **Best Found**: The highest reward seen
- **Generation History**: How prompts evolved

You can't directly access this, but it shows in console output like:
```
[Round 01 | Prompt v4] Best prompt not updated. Current score: 0.802 vs. history best: 0.933
```

---

## How APO Decides

### The Process

```
1. Start with baseline prompt
   ↓
2. Test it on validation set → Get average reward
   ↓
3. GPT-4 critiques the prompt (why didn't it work better?)
   ↓
4. GPT-4 generates 2 variations
   ↓
5. Test both variations → Get rewards for each
   ↓
6. Keep the best ones in the "beam"
   ↓
7. Repeat until beam_rounds complete
   ↓
8. Return: prompt with highest max reward
```

### The Decision Rule

```python
# Get the maximum reward for each template
template_max_rewards = {
    "Template A": 0.82,
    "Template B": 0.89,  ← HIGHEST
    "Template C": 0.75,
}

# Select the one with max reward
best = "Template B"
score = 0.89
```

---

## Data Structure Example

```python
# After training completes, you have:

templates_tested = [
    "Answer this question: {question}",
    "Answer this question: {question} with clarity and depth.",
    "Answer the question: {question}. Be thorough and precise.",
]

rewards_by_template = {
    "Answer this question: {question}": [0.78, 0.75, 0.82],
    "Answer this question: {question} with clarity and depth.": [0.85, 0.89, 0.88],
    "Answer the question: {question}. Be thorough and precise.": [0.81, 0.78, 0.79],
}

# Selection:
best = max(rewards_by_template.items(), key=lambda x: max(x[1]))
# Returns: ("Answer this question: {question} with clarity and depth.", [0.85, 0.89, 0.88])

best_score = 0.89
```

---

## Console Output Explained

### During Training
```
🔥 TEMPLATE BEING TESTED:
======================================================================
Answer this question: {question} with clarity and depth.
======================================================================

[Agent] 📝 Q: What is DNA?...
[Agent] 💬 A: DNA, or deoxyribonucleic acid...
[Agent] ✅ Reward: 0.825
```

This shows which template is currently being tested and what reward it got.

### At the End
```
📊 Summary: 3 unique templates were tested during training:
======================================================================

Template 1:
Answer this question: {question}
  📈 Avg Reward: 0.783 | Max Reward: 0.82 | Tested: 3 times

Template 2:
Answer this question: {question} with clarity and depth.
  📈 Avg Reward: 0.873 | Max Reward: 0.89 | Tested: 3 times

Template 3:
Answer the question: {question}. Be thorough and precise.
  📈 Avg Reward: 0.793 | Max Reward: 0.81 | Tested: 3 times

======================================================================
🏆 BEST PROMPT FOUND:
======================================================================
Answer this question: {question} with clarity and depth.

✨ Best Reward Score: 0.89
======================================================================
```

This shows:
- All templates tested
- Statistics for each (avg/max reward, test count)
- **The winning prompt** (green, at the end)
- **The winning score** (0.89)

---

## Quick Reference Table

| Aspect | Answer |
|--------|--------|
| **How does APO select best?** | By highest maximum reward (`max()` function) |
| **Where are prompts during training?** | In memory: `templates_tested` and `rewards_by_template` globals |
| **Where are prompts after training?** | Nowhere! Must explicitly save to file |
| **How many prompts tried?** | Typically 5-10 for small training |
| **How many times each tested?** | 3-8 times (for stability) |
| **Algorithm used?** | Beam search with GPT-4 critique |
| **Selection formula?** | `max(rewards_by_template.items(), key=lambda x: max(x[1]))` |
| **What's the "best score"?** | Highest single reward achieved by the winning template |
| **Can I modify it?** | Yes, edit `calculate_reward()` function |

---

## Common Patterns

### Access the Best After Training
```python
# 1. From global dict
best_template, rewards = max(
    rewards_by_template.items(),
    key=lambda x: max(x[1])
)
best_score = max(rewards)

# 2. Direct from output
# Just look at the final "🏆 BEST PROMPT FOUND:" section
```

### See All Templates Tested
```python
for i, template in enumerate(templates_tested):
    print(f"{i+1}. {template}")
    print(f"   Rewards: {rewards_by_template[template]}")
```

### Compare Baseline vs Best
```python
baseline_rewards = rewards_by_template[templates_tested[0]]
best_rewards = rewards_by_template[max(
    rewards_by_template.items(),
    key=lambda x: max(x[1])
)[0]]

baseline_avg = sum(baseline_rewards) / len(baseline_rewards)
best_avg = sum(best_rewards) / len(best_rewards)

improvement = ((best_avg - baseline_avg) / baseline_avg) * 100
print(f"Improvement: {improvement:.1f}%")
```

---

## File Locations in apo_training.py

- **Line ~30**: Define `templates_tested` and `rewards_by_template`
- **Line ~55**: Add templates when tested
- **Line ~105**: Log rewards for each template
- **Line ~240-285**: Display summary and best prompt at end

---

## Related Documentation

For more details, see:
- `APO_HOW_IT_WORKS.md` - Complete explanation of APO algorithm
- `APO_STORAGE_DETAILS.md` - Technical deep dive on storage
- `APO_CODE_REFERENCE.md` - Code-specific details with line numbers
- `APO_VISUALIZATION.md` - Visual diagrams and flowcharts

