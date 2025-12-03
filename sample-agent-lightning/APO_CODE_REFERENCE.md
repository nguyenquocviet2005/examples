# APO Prompt Storage - Code Reference

## Quick Answer

**How APO decides the best prompt:**
- Uses **Beam Search** algorithm with `beam_width=2` 
- Selects prompt with **highest reward** from all tested templates
- Algorithm: `best_prompt = max(prompt_and_rewards, key=lambda x: x[1])`

**Where prompts are stored:**
- **During training**: In-memory global dictionaries in your Python script
  - `templates_tested` - List of all unique templates
  - `rewards_by_template` - Dict mapping templates to their reward scores
- **After training**: Nowhere! Unless you explicitly save them
- **Inside APO**: Internally managed beam state (not directly accessible)

---

## 📍 Code Locations in apo_training.py

### 1. Global Storage (Line ~30)

```python
# Track templates for summary
templates_tested = []
rewards_by_template = {}  # Track rewards for each template
```

**What it stores:**
- `templates_tested`: Every unique prompt variation tried
- `rewards_by_template`: For each prompt, a list of rewards from multiple runs

---

### 2. Where Templates Are Added (Line ~55)

```python
@agl.rollout
def qa_agent(task: QuestionTask, prompt_template: agl.PromptTemplate) -> float:
    # Track unique templates
    if prompt_template.template not in templates_tested:
        templates_tested.append(prompt_template.template)
```

**What happens:**
- Each time a new template is tested, it's added to the global list
- Only added once (checked with `if` statement)

---

### 3. Where Rewards Are Tracked (Line ~105)

```python
# Track rewards for each template
template = prompt_template.template
if template not in rewards_by_template:
    rewards_by_template[template] = []
rewards_by_template[template].append(reward)
```

**What happens:**
- For every rollout, the reward is recorded
- Same template can be tested multiple times, each gets logged

---

### 4. Best Prompt Selection (Line ~250)

```python
# Find and display the best template
if rewards_by_template:
    best_template = max(
        rewards_by_template.items(),
        key=lambda x: max(x[1])  # Get template with highest max reward
    )
    best_template_str, best_rewards = best_template
    best_score = max(best_rewards)
```

**How it works:**
- `max(..., key=lambda x: max(x[1]))` finds the template with highest single reward
- Returns: (template_string, list_of_all_rewards_for_that_template)
- `best_score = max(best_rewards)` gets the highest reward

---

### 5. End-of-Training Summary (Lines 240-270)

```python
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
```

**What it displays:**
- All templates in order
- Statistics for each (avg, max, test count)

---

### 6. Best Prompt Display (Lines 272-285)

```python
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
```

**What it shows:**
- The winning prompt in green
- The best reward score achieved

---

## 🔄 Step-by-Step Flow

### Setup Phase
```python
templates_tested = []           # Start empty
rewards_by_template = {}        # Start empty
```

### Training Phase (repeats many times)
```python
def qa_agent(..., prompt_template):
    # 1. Template is logged
    if prompt_template.template not in templates_tested:
        templates_tested.append(prompt_template.template)
    
    # 2. Prompt tested with OpenAI API
    response = client.chat.completions.create(...)
    
    # 3. Reward calculated
    reward = calculate_reward(answer, keywords)
    
    # 4. Reward logged
    template = prompt_template.template
    if template not in rewards_by_template:
        rewards_by_template[template] = []
    rewards_by_template[template].append(reward)
```

### Ending Phase
```python
# Find best
best_template = max(rewards_by_template.items(), key=lambda x: max(x[1]))[0]
best_score = max(rewards_by_template[best_template])

# Display results
print("All templates:", templates_tested)
print("All rewards:", rewards_by_template)
print("BEST:", best_template, "Score:", best_score)
```

---

## 🎯 Decision Logic

### Selecting the Best Prompt

```python
# This is the core selection logic:
best_template = max(
    rewards_by_template.items(),
    key=lambda x: max(x[1])
)
```

**Step-by-step breakdown:**

```python
# Input: rewards_by_template
{
    "Answer this question: {question}": [0.78, 0.82, 0.75],
    "Answer {question} clearly": [0.85, 0.89, 0.84],
    "Answer {question} thoroughly": [0.71, 0.75],
}

# max(x[1]) applied to each template:
{
    "Answer this question: {question}": 0.82,         # max of [0.78, 0.82, 0.75]
    "Answer {question} clearly": 0.89,                # max of [0.85, 0.89, 0.84] ← WINNER
    "Answer {question} thoroughly": 0.75,             # max of [0.71, 0.75]
}

# Final selection:
best = "Answer {question} clearly"
best_score = 0.89
```

---

## 💾 How to Save the Best Prompt

Add this after `trainer.fit()` completes:

```python
import json

# Extract best prompt
best_template = max(
    rewards_by_template.items(),
    key=lambda x: max(x[1])
)[0]

# Save to file
with open("best_prompt.json", "w") as f:
    json.dump({
        "template": best_template,
        "score": max(rewards_by_template[best_template]),
        "avg_score": sum(rewards_by_template[best_template]) / len(rewards_by_template[best_template]),
    }, f, indent=2)
```

**Output file (`best_prompt.json`):**
```json
{
  "template": "Answer this question: {question} with clarity and depth.",
  "score": 0.895,
  "avg_score": 0.862
}
```

---

## 📊 Data Structure Details

### `templates_tested`
```python
templates_tested = [
    "Answer this question: {question}",
    "Answer {question} clearly",
    "Answer {question} thoroughly",
    "Provide a clear answer to: {question}",
    # ... more templates
]
```

**Type:** `list[str]`  
**Size:** Grows with each unique template  
**Example length:** 5-10 templates for a short training run

### `rewards_by_template`
```python
rewards_by_template = {
    "Answer this question: {question}": [0.78, 0.82, 0.75, 0.79],
    "Answer {question} clearly": [0.85, 0.89, 0.84, 0.88],
    "Answer {question} thoroughly": [0.71, 0.75],
    # ... more templates
}
```

**Type:** `dict[str, list[float]]`  
**Keys:** Prompt templates  
**Values:** List of rewards (one per test of that template)  
**Size:** ~5-10 templates, each with 3-8 reward values

---

## ⚡ Performance Implications

### Memory Usage
```python
# Example with 5 templates, each tested 8 times:
- templates_tested: ~5 strings (~500 bytes total)
- rewards_by_template: 5 floats × 8 tests = 40 floats (~320 bytes)
- Total: <1 KB

# Not a concern for most runs
```

### Lookup Complexity
```python
# Finding best prompt
best = max(rewards_by_template.items(), key=lambda x: max(x[1]))
# Complexity: O(T × R) where T=templates, R=rewards per template
# For 5 templates with 8 rewards each: 40 comparisons
# Negligible impact
```

---

## 🐛 Common Issues

### Issue: Best prompt is the baseline?
**Reason:** APO didn't find better prompts  
**Check:** Are your rewards good? (>0.5?)  
**Solution:** Increase `beam_rounds`, `branch_factor`, or improve reward function

### Issue: Templates keep repeating?
**Reason:** GPT-4 generates similar variations  
**Check:** Look at `templates_tested` for duplicates  
**Solution:** Increase `gradient_batch_size` for better critique

### Issue: Best score decreased?
**Reason:** This shouldn't happen! Algorithm tracks history best  
**Check:** Review your reward function  
**Solution:** Look at actual answers - is reward calculation wrong?

---

## 🚀 Next Steps

1. **Review the best prompt**: Check the console output for `🏆 BEST PROMPT FOUND`
2. **Measure improvement**: Compare to baseline in output
3. **Use the prompt**: Replace your old prompt with the new one
4. **Save it**: Use code above to persist to JSON
5. **Iterate**: Try different datasets or reward functions

