# Summary: How APO Decides Best Prompt & Where It's Stored

## Your Question Answered

### How APO Decides Which Is The Best Prompt

**Algorithm:** APO uses a simple but powerful approach:
```python
best_prompt = max(prompt_and_rewards, key=lambda x: x[1])
```

**In Plain English:**
- APO tests multiple prompt variations during training
- Each prompt gets a **reward score** (0.0 to 1.0)
- APO tracks the **maximum reward** for each prompt
- **The prompt with the highest max reward wins!**

**Example:**
```
Template A: rewards = [0.78, 0.75, 0.82] → max = 0.82
Template B: rewards = [0.85, 0.89, 0.84] → max = 0.89 ✨ WINNER
Template C: rewards = [0.71, 0.75]       → max = 0.75
```

### Where Prompts Are Stored

#### During Training: In Memory

Two global variables track everything:

```python
# All unique prompts tested
templates_tested = [
    "Answer this question: {question}",
    "Answer this question: {question} with clarity and depth.",
    "Answer the question: {question}. Be thorough...",
]

# Rewards for each prompt (can be tested multiple times)
rewards_by_template = {
    "Answer this question: {question}": [0.78, 0.75, 0.82],
    "Answer this question: {question} with clarity...": [0.85, 0.89, 0.88],
    "Answer the question: {question}...": [0.81, 0.78, 0.79],
}
```

**Location:** Global variables in `apo_training.py` (defined around line 30)

#### After Training: Nowhere by Default!

⚠️ **Important Discovery:** APO doesn't automatically save prompts to disk!

**What gets printed to console:**
- All tested templates
- Statistics for each
- **The best prompt** (marked with 🏆)
- **The best score**

**What's lost when script ends:**
- All prompts (unless you save them)
- All reward scores
- All execution traces

**How to Save:**
```python
import json

best_template = max(
    rewards_by_template.items(),
    key=lambda x: max(x[1])
)[0]

with open("best_prompt.json", "w") as f:
    json.dump({"template": best_template}, f, indent=2)
```

#### Inside APO: Internal Beam State

APO maintains internal state (you can't directly access):
- **Beam**: Top 2-5 best prompts
- **Generation history**: How prompts evolved
- **Best found**: Highest reward ever achieved

You see hints in console output:
```
[Round 01 | Prompt v4] Best prompt not updated. Current score: 0.802 vs. history best: 0.933
```

---

## How It Works: Step by Step

### 1. Start with Baseline
```
Initial: "Answer this question: {question}"
Test on 3 samples → Avg reward: 0.78
```

### 2. GPT-4 Generates Variations
```
GPT-4 Input: "This prompt got 0.78 reward. How to improve?"
GPT-4 Output: "Be more specific about clarity and depth"

Generated Variations:
- V1: "Answer this question: {question} with clarity and depth."
- V2: "Answer the question: {question}. Be thorough and precise."
```

### 3. Test Variations
```
V1 tested → Avg reward: 0.87 ✅ BETTER
V2 tested → Avg reward: 0.79 ❌ WORSE
```

### 4. Keep Best in Beam
```
Beam = [V1 (0.87), Baseline (0.78)]
```

### 5. Repeat (if more rounds)
```
Generate from V1 → Test → Update beam → Repeat
```

### 6. Return Winner
```
BEST: "Answer this question: {question} with clarity and depth."
SCORE: 0.89 (improvement from 0.78)
```

---

## Selection Logic Visualization

```
Testing Phase:
  Template A → Reward 0.82 ┐
  Template B → Reward 0.89 ├─ max(0.82, 0.89, 0.75) = 0.89
  Template C → Reward 0.75 ┘
                                    ↓
Selection Result: Template B (the one with 0.89)
```

---

## Updated Code Changes

Your `apo_training.py` now includes:

### 1. **Global Storage** (Line ~30)
```python
templates_tested = []
rewards_by_template = {}
```

### 2. **Template Tracking** (Line ~55)
```python
if prompt_template.template not in templates_tested:
    templates_tested.append(prompt_template.template)
```

### 3. **Reward Logging** (Line ~105)
```python
template = prompt_template.template
if template not in rewards_by_template:
    rewards_by_template[template] = []
rewards_by_template[template].append(reward)
```

### 4. **End Summary** (Lines 240-285)
```python
# Find and display the best template
best_template = max(
    rewards_by_template.items(),
    key=lambda x: max(x[1])
)
# Shows all templates and highlights the best
```

---

## Console Output You'll See

### During Training
```
======================================================================
🔥 TEMPLATE BEING TESTED:
======================================================================
Answer this question: {question} with clarity and depth.
======================================================================

[Agent] 📝 Q: What is DNA?...
[Agent] 💬 A: DNA is a molecule that...
[Agent] ✅ Reward: 0.825
```

### End of Training
```
======================================================================
✅ Training Complete!
======================================================================

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

---

## New Documentation Created

I've created 5 comprehensive guides to explain everything:

1. **APO_STORAGE_SUMMARY.md** - Quick 3-page overview ⭐
2. **APO_HOW_IT_WORKS.md** - Full algorithm explanation
3. **APO_CODE_REFERENCE.md** - Line-by-line code details
4. **APO_STORAGE_DETAILS.md** - Technical deep dive
5. **APO_VISUALIZATION.md** - ASCII diagrams and flowcharts
6. **APO_DOCS_INDEX.md** - Navigation guide for all docs

---

## Key Takeaways

✅ **Selection Method:** Highest max reward wins  
✅ **Storage During:** Global Python dicts  
✅ **Storage After:** Only what you explicitly save  
✅ **Algorithm:** Beam search with GPT-4 critique  
✅ **Hyperparameters:** `beam_width=2`, `branch_factor=2`, etc.  
✅ **Output:** Console shows best template at end  

---

## Next Steps

1. **Set your API key:** `export OPENAI_API_KEY='your-key'`
2. **Run training:** `python apo_training.py`
3. **Check console output:** Look for 🏆 symbol
4. **Save the best:** Use the JSON save code above
5. **Read documentation:** Start with `APO_STORAGE_SUMMARY.md`

